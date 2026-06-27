import re

top_part = """import React, { useState, useEffect, useRef, useCallback } from "react";
import { createRoot } from "react-dom/client";
import { io } from "socket.io-client";
import {
  Captions,
  Copy,
  Expand,
  Gauge,
  Link2,
  Mic,
  MicOff,
  MonitorPlay,
  Pause,
  Play,
  RotateCcw,
  RotateCw,
  Settings2,
  Users,
  X,
  Volume2,
  VolumeX,
  Wifi,
  MessageCircle,
  Minus,
  Square,
  SkipBack,
  SkipForward,
  Monitor,
  MessageSquare,
  Maximize,
  ChevronUp,
  ChevronDown,
  FolderOpen,
  Plus
} from "lucide-react";
import "./styles.css";

const SERVER_URL = typeof process !== "undefined" && process.env.PUBLIC_TUNNEL
  ? window.location.origin
  : `http://${window.location.hostname}:3001`;

const SPEAKER_HOLD_MS = 2500;
const SEEK_FORWARD_SECONDS = 10;
const SEEK_BACK_SECONDS = 10;

function formatTime(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function parseSrt(text) {
  const cues = [];
  const blocks = text.replace(/\\r\\n/g, "\\n").split(/\\n\\s*\\n/);
  for (const block of blocks) {
    const lines = block.split("\\n");
    if (lines.length >= 3) {
      const timeLine = lines[1];
      const match = timeLine.match(/(\\d{2}):(\\d{2}):(\\d{2}),(\\d{3})\\s*-->\\s*(\\d{2}):(\\d{2}):(\\d{2}),(\\d{3})/);
      if (match) {
        const start =
          parseInt(match[1], 10) * 3600 +
          parseInt(match[2], 10) * 60 +
          parseInt(match[3], 10) +
          parseInt(match[4], 10) / 1000;
        const end =
          parseInt(match[5], 10) * 3600 +
          parseInt(match[6], 10) * 60 +
          parseInt(match[7], 10) +
          parseInt(match[8], 10) / 1000;
        const textContent = lines.slice(2).join("\\n").replace(/<[^>]+>/g, "").trim();
        cues.push({ start, end, text: textContent });
      }
    }
  }
  return cues;
}

function parseVtt(text) {
  const cues = [];
  const lines = text.replace(/\\r\\n/g, "\\n").split("\\n");
  let i = 0;
  if (lines[0].startsWith("WEBVTT")) i++;
  while (i < lines.length) {
    if (!lines[i].trim()) {
      i++;
      continue;
    }
    let timeLine = lines[i];
    if (!timeLine.includes("-->")) {
      i++;
      timeLine = lines[i];
    }
    if (!timeLine || !timeLine.includes("-->")) {
      i++;
      continue;
    }
    const match = timeLine.match(/(?:(\\d{2}):)?(\\d{2}):(\\d{2})\\.(\\d{3})\\s*-->\\s*(?:(\\d{2}):)?(\\d{2}):(\\d{2})\\.(\\d{3})/);
    if (match) {
      const h1 = match[1] ? parseInt(match[1], 10) : 0;
      const m1 = parseInt(match[2], 10);
      const s1 = parseInt(match[3], 10);
      const ms1 = parseInt(match[4], 10);
      const start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000;

      const h2 = match[5] ? parseInt(match[5], 10) : 0;
      const m2 = parseInt(match[6], 10);
      const s2 = parseInt(match[7], 10);
      const ms2 = parseInt(match[8], 10);
      const end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000;

      i++;
      const textLines = [];
      while (i < lines.length && lines[i].trim()) {
        textLines.push(lines[i].replace(/<[^>]+>/g, "").trim());
        i++;
      }
      cues.push({ start, end, text: textLines.join("\\n") });
    } else {
      i++;
    }
  }
  return cues;
}

async function readSubtitleFile(file) {
  const text = await file.text();
  return text;
}

function parseSubtitleData(text, format) {
  if (format === "vtt" || text.startsWith("WEBVTT")) return parseVtt(text);
  return parseSrt(text);
}

function findActiveCue(cues, currentTime, offsetMs = 0) {
  if (!cues || !cues.length) return null;
  const t = currentTime - offsetMs / 1000;
  let left = 0;
  let right = cues.length - 1;
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const cue = cues[mid];
    if (t >= cue.start && t <= cue.end) return cue;
    if (t < cue.start) right = mid - 1;
    else left = mid + 1;
  }
  return null;
}

function initials(name) {
  return (name || "?").slice(0, 2).toUpperCase();
}

function makeRoomId() {
  const words = ["emerald", "crimson", "azure", "nova", "pulse", "echo", "neon", "flux", "zenith", "vertex"];
  const word = words[Math.floor(Math.random() * words.length)];
  return `${word}-room`;
}

function isTypingTarget(target) {
  if (!target) return false;
  const tag = target.tagName.toLowerCase();
  return tag === "input" || tag === "textarea" || tag === "select" || target.isContentEditable;
}

function RemoteAudio({ stream, muted, volume, unlockKey, onBlocked }) {
  const audioRef = useRef(null);
  
  useEffect(() => {
    if (audioRef.current && stream) {
      audioRef.current.srcObject = stream;
      audioRef.current.play().catch(() => onBlocked());
    }
  }, [stream, unlockKey, onBlocked]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      audioRef.current.muted = muted;
    }
  }, [volume, muted]);

  return <audio ref={audioRef} autoPlay playsInline style={{ display: "none" }} />;
}

function levelPercent(level) {
  return `${Math.min(100, Math.max(0, level * 100))}%`;
}

function App() {
  const [profileReady, setProfileReady] = useState(false);
  const [name, setName] = useState(localStorage.getItem("watch-name") || "");
  const [roomId, setRoomId] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("room") || localStorage.getItem("watch-room") || makeRoomId();
  });

  const [connected, setConnected] = useState(false);
  const [health, setHealth] = useState(null);
  const [socketId, setSocketId] = useState(null);
  const [room, setRoom] = useState(null);

  const [moviePath, setMoviePath] = useState("");
  const [subtitlePathFa, setSubtitlePathFa] = useState("");
  const [subtitlePathEn, setSubtitlePathEn] = useState("");

  const [transcodeStatus, setTranscodeStatus] = useState(null);
  const [status, setStatus] = useState("");

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [mediaError, setMediaError] = useState("");
  const [playbackUnlocked, setPlaybackUnlocked] = useState(true);
  const [pendingAutoplay, setPendingAutoplay] = useState(false);

  const [userVolume, setUserVolume] = useState(1);
  const [videoMuted, setVideoMuted] = useState(false);
  const [theaterMode, setTheaterMode] = useState(false);
  const [showChrome, setShowChrome] = useState(true);
  const [seekFlash, setSeekFlash] = useState(null);

  const [subtitleSettings, setSubtitleSettings] = useState({
    mode: "both",
    size: 42,
    gap: 8,
    faOffsetMs: +120,
    enOffsetMs: -80
  });
  const [lastSubtitleMode, setLastSubtitleMode] = useState("both");

  const [micEnabled, setMicEnabled] = useState(false);
  const [micDevices, setMicDevices] = useState([]);
  const [micStatus, setMicStatus] = useState("");
  const [localMicLevel, setLocalMicLevel] = useState(0);
  const [localSpeaking, setLocalSpeaking] = useState(false);

  const [voiceState, setVoiceState] = useState({});
  const [remoteStreams, setRemoteStreams] = useState(new Map());
  const [adaptiveDucking, setAdaptiveDucking] = useState(true);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(true);
  const [defaultRemoteVoiceVolume, setDefaultRemoteVoiceVolume] = useState(1);
  const [remoteVoiceVolumes, setRemoteVoiceVolumes] = useState({});
  const [voiceBlocked, setVoiceBlocked] = useState(false);
  const [voiceUnlockKey, setVoiceUnlockKey] = useState(0);
  const [speakerToast, setSpeakerToast] = useState({ entries: [], exiting: false });

  const socketRef = useRef(null);
  const videoRef = useRef(null);
  const screenRef = useRef(null);
  const peerConnectionsRef = useRef(new Map());
  const localStreamRef = useRef(null);
  const analyserRef = useRef(null);
  const vadFrameRef = useRef(null);
  const lastVoiceEmitRef = useRef(0);
  const noiseFloorRef = useRef(0.01);
  const lastSpeakingRef = useRef(false);
  const localMicLevelRef = useRef(0);

  const applyingRemoteRef = useRef(false);
  const chromeTimerRef = useRef(null);
  const seekTimerRef = useRef(null);
  const tapTimerRef = useRef(null);
  const speakerHideTimerRef = useRef(null);
  const speakerExitTimerRef = useRef(null);

  const media = room?.media;
  const streamUrl = media ? `${SERVER_URL}/api/rooms/${roomId}/media/${media.id}/stream` : "";
  const displayMediaName = media ? media.name : "";
  const shareUrl = `${window.location.origin}/?room=${encodeURIComponent(roomId)}`;
  const shouldOfferPhoneMp4 = media && !media.hasPhoneMp4 && (media.format === "mkv" || media.format === "avi" || media.format === "webm");

  const faData = room?.subtitles?.fa;
  const enData = room?.subtitles?.en;
  const faCues = React.useMemo(() => faData ? parseSubtitleData(faData.text, faData.format) : [], [faData]);
  const enCues = React.useMemo(() => enData ? parseSubtitleData(enData.text, enData.format) : [], [enData]);

  const faCue = React.useMemo(() => findActiveCue(faCues, currentTime, subtitleSettings.faOffsetMs), [faCues, currentTime, subtitleSettings.faOffsetMs]);
  const enCue = React.useMemo(() => findActiveCue(enCues, currentTime, subtitleSettings.enOffsetMs), [enCues, currentTime, subtitleSettings.enOffsetMs]);

  const peers = room?.peers || [];
  const activeSpeakers = peers
    .map(p => ({ ...p, self: false, ...voiceState[p.id] }))
    .concat([{ id: socketId, name, self: true, speaking: localSpeaking, level: localMicLevelRef.current }])
    .filter(p => p.speaking)
    .sort((a, b) => b.level - a.level)
    .slice(0, 3);
  const anyoneSpeaking = activeSpeakers.length > 0;
  const effectiveVolume = anyoneSpeaking && adaptiveDucking ? userVolume * 0.15 : userVolume;

  const showPlayerChrome = useCallback((force = false) => {
    setShowChrome(true);
    window.clearTimeout(chromeTimerRef.current);
    if (!force && isPlaying) {
      chromeTimerRef.current = window.setTimeout(() => setShowChrome(false), 3000);
    }
  }, [isPlaying]);

  const flashSeek = useCallback((direction, seconds) => {
    setSeekFlash({ direction, seconds, id: Date.now() });
    window.clearTimeout(seekTimerRef.current);
    seekTimerRef.current = window.setTimeout(() => setSeekFlash(null), 600);
  }, []);

  const handleRemoteVoiceBlocked = useCallback(() => {
    setVoiceBlocked(true);
  }, []);

  const unlockRemoteVoice = useCallback(() => {
    setVoiceBlocked(false);
    setVoiceUnlockKey(Date.now());
  }, []);

  useEffect(() => {
    if (profileReady && name.trim()) localStorage.setItem("watch-name", name.trim());
  }, [name, profileReady]);

  useEffect(() => {
    localStorage.setItem("watch-room", roomId);
  }, [roomId]);

  useEffect(() => {
    let cancelled = false;
    const refreshHealth = () => {
      fetch(`${SERVER_URL}/api/health`)
        .then((response) => response.json())
        .then((payload) => {
          if (!cancelled) setHealth(payload);
        })
        .catch(() => {
          if (!cancelled) setHealth(null);
        });
    };
    refreshHealth();
    const timer = window.setInterval(refreshHealth, 2500);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);
"""

with open('final_fix.py', 'r') as f:
    script = f.read()

start_idx = script.find('logic_block = """\n  const emitPlayback')
end_idx = script.find('"""\n\nwith open(\'build_lan_cinema.py')

logic_block = script[start_idx + 18:end_idx]

with open('build_lan_cinema.py', 'r') as f:
    script2 = f.read()

rstart = script2.find('return_block = """') + 18
rend = script2.find('"""\n\napp =')
return_block = script2[rstart:rend]

final_app = top_part + logic_block + return_block + "\\n\\ncreateRoot(document.getElementById('root')).render(<App />);\\n"

with open('src/App.jsx', 'w') as f:
    f.write(final_app)
