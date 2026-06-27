import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

# The top part of App.jsx until the missing logic
top_part_idx = app.find('    return (')
if top_part_idx == -1:
    top_part_idx = app.find('  return (')

top_part = app[:top_part_idx]

logic_block = """
  const emitPlayback = useCallback((patch = {}) => {
    const video = videoRef.current;
    if (!video || !socketRef.current) return;
    socketRef.current.emit("playback:set", {
      playing: patch.playing ?? !video.paused,
      currentTime: patch.currentTime ?? video.currentTime,
      duration: Number.isFinite(video.duration) ? video.duration : duration,
      rate: patch.rate ?? video.playbackRate
    });
  }, [duration]);

  const applyPlaybackState = useCallback((state, force = false) => {
    const video = videoRef.current;
    if (!video || !state) return;
    const targetTime = state.playing ? state.currentTime + (Date.now() - state.updatedAt) / 1000 : state.currentTime;
    const drift = Math.abs(video.currentTime - targetTime);
    applyingRemoteRef.current = true;
    video.playbackRate = state.rate || 1;
    if (force || drift > 0.35) {
      video.currentTime = Math.max(0, targetTime);
    }
    if (state.playing && video.paused) {
      video
        .play()
        .then(() => {
          setPlaybackUnlocked(true);
          setPendingAutoplay(false);
          setIsPlaying(true);
        })
        .catch(() => {
          setPendingAutoplay(true);
          setIsPlaying(false);
          setStatus("Click Enable playback.");
        });
    }
    if (!state.playing && !video.paused) {
      video.pause();
      setIsPlaying(false);
      setPendingAutoplay(false);
    }
    window.setTimeout(() => {
      applyingRemoteRef.current = false;
    }, 180);
  }, []);

  const ensurePeerConnection = useCallback((peerId) => {
    if (peerConnectionsRef.current.has(peerId)) return peerConnectionsRef.current.get(peerId);

    const pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        socketRef.current?.emit("signal", { to: peerId, data: { candidate: event.candidate } });
      }
    };

    pc.ontrack = (event) => {
      const [stream] = event.streams;
      if (!stream) return;
      setRemoteStreams((previous) => {
        const next = new Map(previous);
        next.set(peerId, stream);
        return next;
      });
    };

    localStreamRef.current?.getTracks().forEach((track) => {
      if (!pc.getSenders().some((sender) => sender.track?.id === track.id)) {
        pc.addTrack(track, localStreamRef.current);
      }
    });

    peerConnectionsRef.current.set(peerId, pc);
    return pc;
  }, []);

  const makeOffer = useCallback(async (peerId) => {
    const pc = ensurePeerConnection(peerId);
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socketRef.current?.emit("signal", { to: peerId, data: { description: pc.localDescription } });
  }, [ensurePeerConnection]);

  const renegotiateAll = useCallback(() => {
    [...peerConnectionsRef.current.keys()].forEach((peerId) => {
      makeOffer(peerId).catch(() => setStatus("Voice negotiation failed."));
    });
  }, [makeOffer]);

  useEffect(() => {
    if (!profileReady) return undefined;
    const socket = io(SERVER_URL, { transports: ["websocket", "polling"] });
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnected(true);
      socket.emit("room:join", { roomId, name }, ({ socketId: id, state }) => {
        setSocketId(id);
        setRoom(state);
        setSubtitleSettings(state.subtitleSettings);
        setVoiceState(() => {
          const next = {};
          state.peers.forEach((peer) => {
            next[peer.id] = { speaking: Boolean(peer.speaking), level: Number(peer.level || 0) };
          });
          return next;
        });
        if (state.subtitleSettings?.mode && state.subtitleSettings.mode !== "off") {
          setLastSubtitleMode(state.subtitleSettings.mode);
        }
        state.peers
          .filter((peer) => peer.id !== id)
          .forEach((peer) => ensurePeerConnection(peer.id));
      });
    });

    socket.on("disconnect", () => setConnected(false));
    socket.on("room:state", (state) => {
      setRoom(state);
      setSubtitleSettings(state.subtitleSettings);
      setVoiceState((previous) => {
        const next = { ...previous };
        state.peers.forEach((peer) => {
          next[peer.id] = { speaking: Boolean(peer.speaking), level: Number(peer.level || 0) };
        });
        return next;
      });
      if (state.subtitleSettings?.mode && state.subtitleSettings.mode !== "off") {
        setLastSubtitleMode(state.subtitleSettings.mode);
      }
    });
    socket.on("media:transcode", (payload) => {
      setTranscodeStatus(payload);
      setStatus(payload.message);
      if (payload.status === "done") {
        setMediaError("");
        setPlaybackUnlocked(false);
        setPendingAutoplay(false);
      }
    });
    socket.on("playback:state", (state) => {
      setRoom((previous) => (previous ? { ...previous, playback: state } : previous));
      if (state.origin !== socket.id) applyPlaybackState(state);
    });
    socket.on("subtitle:settings", (settings) => {
      setSubtitleSettings(settings);
      if (settings?.mode && settings.mode !== "off") setLastSubtitleMode(settings.mode);
    });
    socket.on("voice:activity", ({ id, speaking, level }) => {
      if (id === socket.id) return;
      setVoiceState((previous) => ({
        ...previous,
        [id]: { speaking: Boolean(speaking), level: Number(level || 0) }
      }));
    });
    socket.on("peer:joined", ({ id }) => {
      ensurePeerConnection(id);
      makeOffer(id).catch(() => setStatus("Could not connect voice."));
    });
    socket.on("peer:left", ({ id }) => {
      peerConnectionsRef.current.get(id)?.close();
      peerConnectionsRef.current.delete(id);
      setRemoteStreams((previous) => {
        const next = new Map(previous);
        next.delete(id);
        return next;
      });
      setVoiceState((previous) => {
        const next = { ...previous };
        delete next[id];
        return next;
      });
    });
    socket.on("signal", async ({ from, data }) => {
      const pc = ensurePeerConnection(from);
      try {
        if (data.description) {
          await pc.setRemoteDescription(data.description);
          if (data.description.type === "offer") {
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            socket.emit("signal", { to: from, data: { description: pc.localDescription } });
          }
        }
        if (data.candidate) await pc.addIceCandidate(data.candidate);
      } catch {
        setStatus("WebRTC error.");
      }
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
      peerConnectionsRef.current.forEach((pc) => pc.close());
      peerConnectionsRef.current.clear();
    };
  }, [applyPlaybackState, ensurePeerConnection, makeOffer, name, profileReady, roomId]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (isTypingTarget(event.target)) return;
      const key = event.key.toLowerCase();
      if (event.key === "Escape") {
        setTheaterMode(false);
        return;
      }
      if (!media) return;
      if (event.code === "Space") {
        event.preventDefault();
        togglePlay();
        showPlayerChrome();
      }
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        seekBy(-SEEK_BACK_SECONDS);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        seekBy(SEEK_FORWARD_SECONDS);
      }
      if (key === "c") {
        event.preventDefault();
        toggleSubtitles();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  });

  useEffect(() => {
    document.body.classList.toggle("no-scroll", theaterMode);
    return () => document.body.classList.remove("no-scroll");
  }, [theaterMode]);

  useEffect(() => {
    const onFullscreenChange = () => {
      if (!document.fullscreenElement) setTheaterMode(false);
    };
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", onFullscreenChange);
  }, []);

  useEffect(() => {
    showPlayerChrome(!isPlaying);
    return () => window.clearTimeout(chromeTimerRef.current);
  }, [isPlaying, showPlayerChrome]);

  useEffect(() => () => window.clearTimeout(tapTimerRef.current), []);

  useEffect(() => {
    window.clearTimeout(speakerHideTimerRef.current);
    window.clearTimeout(speakerExitTimerRef.current);

    if (activeSpeakers.length) {
      setSpeakerToast({ entries: activeSpeakers, exiting: false });
      return undefined;
    }

    speakerHideTimerRef.current = window.setTimeout(() => {
      setSpeakerToast((current) => current.entries.length ? { ...current, exiting: true } : current);
      speakerExitTimerRef.current = window.setTimeout(() => {
        setSpeakerToast({ entries: [], exiting: false });
      }, 260);
    }, SPEAKER_HOLD_MS);

    return () => {
      window.clearTimeout(speakerHideTimerRef.current);
      window.clearTimeout(speakerExitTimerRef.current);
    };
  }, [activeSpeakers]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;
    video.volume = effectiveVolume;
    video.muted = videoMuted;
    return undefined;
  }, [effectiveVolume, videoMuted]);

  useEffect(() => {
    const video = videoRef.current;
    let frame;
    const tick = () => {
      if (video) {
        setCurrentTime(video.currentTime || 0);
        setDuration(Number.isFinite(video.duration) ? video.duration : 0);
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      if (room?.playback?.playing) applyPlaybackState(room.playback);
    }, 2200);
    return () => window.clearInterval(timer);
  }, [applyPlaybackState, room?.playback]);

  function setRoomAndUrl(nextRoomId) {
    const clean = nextRoomId.trim() || makeRoomId();
    setRoomId(clean);
    window.history.replaceState(null, "", `?room=${encodeURIComponent(clean)}`);
  }

  async function postJson(url, body) {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Request failed.");
    return payload;
  }

  async function loadMovie() {
    try {
      setStatus("Preparing the movie...");
      await postJson(`${SERVER_URL}/api/rooms/${roomId}/media`, { path: moviePath });
      setStatus("Movie is ready.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function uploadMovieFile(file) {
    if (!file) return;
    try {
      setStatus(`Copying movie: ${file.name}`);
      setMoviePath(file.name);
      const form = new FormData();
      form.append("movie", file);
      const response = await fetch(`${SERVER_URL}/api/rooms/${roomId}/media-upload`, {
        method: "POST",
        body: form
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Movie upload failed.");
      setPlaybackUnlocked(false);
      setPendingAutoplay(false);
      setMediaError("");
      setTranscodeStatus(null);
      setStatus("Movie is ready.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function makePhoneSafeMp4() {
    if (!media) return;
    try {
      setTranscodeStatus({ status: "starting", message: "Starting phone-safe MP4 conversion..." });
      setStatus("Starting conversion...");
      const response = await fetch(`${SERVER_URL}/api/rooms/${roomId}/media/${media.id}/phone-mp4`, {
        method: "POST"
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "MP4 conversion failed.");
      setStatus("Converting MP4.");
    } catch (error) {
      setTranscodeStatus({ status: "failed", message: error.message });
      setStatus(error.message);
    }
  }

  async function loadSubtitle(slot) {
    const subtitlePath = slot === "fa" ? subtitlePathFa : subtitlePathEn;
    try {
      await postJson(`${SERVER_URL}/api/rooms/${roomId}/subtitles/${slot}`, { path: subtitlePath });
      setStatus(slot === "fa" ? "Persian subtitle loaded." : "English subtitle loaded.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function uploadSubtitleFile(slot, file) {
    if (!file) return;
    try {
      const text = await readSubtitleFile(file);
      const ext = file.name.split(".").pop() || "srt";
      await postJson(`${SERVER_URL}/api/rooms/${roomId}/subtitles/${slot}/text`, {
        text,
        name: file.name,
        format: ext,
        label: slot === "fa" ? "Persian" : "English"
      });
      if (slot === "fa") setSubtitlePathFa(file.name);
      if (slot === "en") setSubtitlePathEn(file.name);
      setStatus(slot === "fa" ? "Persian subtitle synced." : "English subtitle synced.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  function updateSubtitleSettings(patch) {
    const next = { ...subtitleSettings, ...patch };
    if (next.mode && next.mode !== "off") setLastSubtitleMode(next.mode);
    setSubtitleSettings(next);
    socketRef.current?.emit("subtitle:settings", next);
  }

  function toggleSubtitles() {
    const nextMode = subtitleSettings.mode === "off" ? lastSubtitleMode : "off";
    updateSubtitleSettings({ mode: nextMode });
    setStatus(nextMode === "off" ? "Subtitles hidden." : "Subtitles shown.");
    showPlayerChrome();
  }

  function seekTo(nextTime) {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = Math.max(0, Math.min(nextTime, duration || nextTime));
    emitPlayback({ currentTime: video.currentTime });
    showPlayerChrome();
  }

  function seekBy(deltaSeconds) {
    const video = videoRef.current;
    if (!video || !media) return;
    const nextTime = video.currentTime + deltaSeconds;
    seekTo(nextTime);
    flashSeek(deltaSeconds > 0 ? "forward" : "back", Math.abs(deltaSeconds));
  }

  async function togglePlay() {
    const video = videoRef.current;
    if (!video || !media) return;
    setPlaybackUnlocked(true);
    if (video.paused) {
      try {
        await video.play();
      } catch {
        setPendingAutoplay(true);
        setStatus("The browser blocked playback.");
        return;
      }
      setPendingAutoplay(false);
      emitPlayback({ playing: true });
      showPlayerChrome();
    } else {
      video.pause();
      emitPlayback({ playing: false });
      showPlayerChrome(true);
    }
  }

  function setRate(rate) {
    const video = videoRef.current;
    if (!video) return;
    video.playbackRate = rate;
    emitPlayback({ rate });
  }

  function startVad(stream) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 1024;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyserRef.current = { audioContext, analyser };
    const samples = new Uint8Array(analyser.frequencyBinCount);

    const loop = () => {
      if (!analyserRef.current) return;
      analyser.getByteTimeDomainData(samples);
      let sum = 0;
      for (const sample of samples) {
        const centered = (sample - 128) / 128;
        sum += centered * centered;
      }
      const rms = Math.sqrt(sum / samples.length);
      const threshold = Math.max(0.045, noiseFloorRef.current * 4.4);
      if (rms < threshold) noiseFloorRef.current = noiseFloorRef.current * 0.96 + rms * 0.04;
      const speaking = rms > threshold;
      const level = Math.max(0, Math.min(1, (rms - noiseFloorRef.current) * 9));
      localMicLevelRef.current = level;
      setLocalMicLevel(level);
      const now = Date.now();
      if (now - lastVoiceEmitRef.current > 120) {
        lastVoiceEmitRef.current = now;
        socketRef.current?.emit("voice:activity", { speaking, level });
      }
      if (speaking !== lastSpeakingRef.current) {
        lastSpeakingRef.current = speaking;
        setLocalSpeaking(speaking);
      }
      vadFrameRef.current = requestAnimationFrame(loop);
    };
    vadFrameRef.current = requestAnimationFrame(loop);
  }

  function stopVad() {
    if (vadFrameRef.current) cancelAnimationFrame(vadFrameRef.current);
    if (analyserRef.current) {
      analyserRef.current.audioContext.close();
      analyserRef.current = null;
    }
    setLocalSpeaking(false);
    setLocalMicLevel(0);
    socketRef.current?.emit("voice:activity", { speaking: false, level: 0 });
  }

  async function toggleMic() {
    if (micEnabled) {
      localStreamRef.current?.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
      setMicEnabled(false);
      setMicStatus("Mic off");
      stopVad();
      socketRef.current?.emit("voice:activity", { speaking: false, level: 0 });
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      localStreamRef.current = stream;
      setMicEnabled(true);
      setMicStatus("Mic connected");
      startVad(stream);
      peerConnectionsRef.current.forEach(pc => {
        stream.getTracks().forEach(track => {
          if (!pc.getSenders().some(s => s.track?.id === track.id)) {
            pc.addTrack(track, stream);
          }
        });
      });
      renegotiateAll();
    } catch (e) {
      setMicStatus("Mic access denied");
    }
  }

  async function refreshMicDevices() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      setMicDevices(devices.filter(d => d.kind === 'audioinput'));
    } catch (e) {}
  }

  function copyShareLink() {
    navigator.clipboard.writeText(shareUrl);
    setStatus("Link copied!");
  }

  function unlockPlayback() {
    const video = videoRef.current;
    if (!video) return;
    video.muted = true;
    video.play().then(() => {
      video.muted = videoMuted;
      setPlaybackUnlocked(true);
      setPendingAutoplay(false);
      setIsPlaying(true);
    }).catch(() => {});
  }

  function onVideoLoaded() {
    const video = videoRef.current;
    if (!video) return;
    setDuration(video.duration);
    if (room?.playback) {
      applyPlaybackState(room.playback, true);
    }
  }

  function handleScreenPointerUp(e) {
    if (e.target.closest('.lan-transport') || e.target.closest('.unlock-overlay')) return;
    togglePlay();
  }

  function setRemoteVolume(id, vol) {
    setRemoteVoiceVolumes(prev => ({...prev, [id]: vol}));
  }

  function saveProfile(e) {
    e.preventDefault();
    if (name.trim()) setProfileReady(true);
  }

  function toggleTheaterMode() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
      setTheaterMode(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setTheaterMode(false);
    }
  }
"""

with open('build_lan_cinema.py', 'r') as f:
    script = f.read()

# get the return block from build_lan_cinema
start = script.find('return_block = """') + len('return_block = """')
end = script.find('"""\n\napp =')
return_block = script[start:end]

final_app = top_part + logic_block + return_block + "\\n\\ncreateRoot(document.getElementById('root')).render(<App />);\\n"

with open('src/App.jsx', 'w') as f:
    f.write(final_app)
