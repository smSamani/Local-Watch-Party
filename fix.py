import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

good_cards_grid = '''        <div className="cards-grid">
          <section className="panel-card card-yellow">
            <div className="card-header">
              <Captions size={28} className="icon-yellow" />
              <div>
                <h2>Subtitles</h2>
                <p>FA+EN, Timing, Size</p>
              </div>
            </div>
            <div className="segmented">
              {["both", "fa", "en", "off"].map((mode) => (
                <button
                  key={mode}
                  className={subtitleSettings.mode === mode ? "selected" : ""}
                  onClick={() => updateSubtitleSettings({ mode })}
                >
                  {mode === "both" ? "FA+EN" : mode.toUpperCase()}
                </button>
              ))}
            </div>
            <label className="field">
              Persian subtitle file
              <input
                type="file"
                accept=".srt,.vtt,text/plain"
                onChange={(event) => uploadSubtitleFile("fa", event.target.files?.[0])}
              />
              <div className="input-action">
                <input value={subtitlePathFa} onChange={(event) => setSubtitlePathFa(event.target.value)} placeholder="/path/movie.fa.srt" />
                <button onClick={() => loadSubtitle("fa")}>Load</button>
              </div>
            </label>
            <label className="field">
              English subtitle file
              <input
                type="file"
                accept=".srt,.vtt,text/plain"
                onChange={(event) => uploadSubtitleFile("en", event.target.files?.[0])}
              />
              <div className="input-action">
                <input value={subtitlePathEn} onChange={(event) => setSubtitlePathEn(event.target.value)} placeholder="/path/movie.en.srt" />
                <button onClick={() => loadSubtitle("en")}>Load</button>
              </div>
            </label>
            <div className="subtitle-counts">
              <span>FA cues: {faCues.length}</span>
              <span>EN cues: {enCues.length}</span>
            </div>
            <label className="field">
              Subtitle size: {subtitleSettings.size}px
              <input
                type="range"
                min="18"
                max="64"
                value={subtitleSettings.size}
                onChange={(event) => updateSubtitleSettings({ size: Number(event.target.value) })}
              />
            </label>
            {subtitleSettings.mode === "both" && (
              <div className="subtitle-gap-control">
                <span>FA/EN gap: {subtitleSettings.gap}px</span>
                <div>
                  <button onClick={() => updateSubtitleSettings({ gap: subtitleSettings.gap - 2 })}>-</button>
                  <input
                    type="range"
                    min="0"
                    max="48"
                    value={subtitleSettings.gap}
                    onChange={(event) => updateSubtitleSettings({ gap: Number(event.target.value) })}
                  />
                  <button onClick={() => updateSubtitleSettings({ gap: subtitleSettings.gap + 2 })}>+</button>
                </div>
              </div>
            )}
            <div className="offset-grid">
              <label>
                FA offset (ms)
                <input
                  type="number"
                  step="50"
                  value={subtitleSettings.faOffsetMs}
                  onChange={(event) => updateSubtitleSettings({ faOffsetMs: Number(event.target.value) })}
                />
              </label>
              <label>
                EN offset (ms)
                <input
                  type="number"
                  step="50"
                  value={subtitleSettings.enOffsetMs}
                  onChange={(event) => updateSubtitleSettings({ enOffsetMs: Number(event.target.value) })}
                />
              </label>
            </div>
          </section>

          <section className="panel-card card-green">
            <div className="card-header">
              <Users size={28} className="icon-green" />
              <div>
                <h2>People & Voice</h2>
                <p>Voice, Mic, Volume</p>
              </div>
            </div>
            <div className="people-header">
              <button className="share-box" onClick={copyShareLink}>
                <Copy size={16} />
                <span>{shareUrl}</span>
              </button>
              <div className="network-note">
                <Wifi size={15} />
                {(health?.publicUrl || SERVER_URL).replace(/^https?:\\/\\//, "")}
              </div>
            </div>
            <div className="peer-list">
              {peers.map((peer) => {
                const isSelf = peer.id === socketId;
                const voice = isSelf
                  ? { speaking: localSpeaking, level: localMicLevel }
                  : voiceState[peer.id] || { speaking: peer.speaking, level: peer.level || 0 };
                const volume = isSelf ? 1 : remoteVoiceVolumes[peer.id] ?? defaultRemoteVoiceVolume;
                return (
                  <div className={`peer-row ${voice.speaking ? "active" : ""}`} key={peer.id}>
                    <span className={isSelf ? "avatar self" : "avatar"}>{initials(peer.name)}</span>
                    <div className="peer-main">
                      <div className="peer-name-line">
                        <span>{peer.name}{isSelf ? " · you" : ""}</span>
                        {voice.speaking && <span className="speaking">speaking</span>}
                      </div>
                      <div className="mic-meter" style={{ "--level": levelPercent(voice.level) }}>
                        <span />
                      </div>
                      {!isSelf && (
                        <label className="peer-volume">
                          <Volume2 size={13} />
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={volume}
                            onChange={(event) => setRemoteVolume(peer.id, Number(event.target.value))}
                          />
                          <span>{Math.round(volume * 100)}%</span>
                        </label>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="people-controls">
              <label className="toggle-row">
                <input type="checkbox" checked={adaptiveDucking} onChange={(event) => setAdaptiveDucking(event.target.checked)} />
                <span>Adaptive mic ducking</span>
              </label>
              <label className="toggle-row">
                <input type="checkbox" checked={voiceOutputEnabled} onChange={(event) => setVoiceOutputEnabled(event.target.checked)} />
                <span>Remote voice audio</span>
              </label>
              <label className="field voice-volume">
                Default remote voice: {Math.round(defaultRemoteVoiceVolume * 100)}%
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={defaultRemoteVoiceVolume}
                  onChange={(event) => setDefaultRemoteVoiceVolume(Number(event.target.value))}
                />
              </label>
              <button className="button" onClick={refreshMicDevices}>Check mic devices</button>
            </div>
            {micStatus && <div className="mic-status">{micStatus}</div>}
            {micDevices.length > 0 && (
              <div className="mic-device-list">
                {micDevices.map((device, index) => (
                  <span key={device.deviceId || index}>{device.label || `Microphone ${index + 1}`}</span>
                ))}
              </div>
            )}
          </section>

          <section className="panel-card card-blue">
            <div className="card-header">
              <MonitorPlay size={28} className="icon-blue" />
              <div>
                <h2>Media Setup</h2>
                <p>Local File, MP4 Build</p>
              </div>
            </div>
            <label className="field">
              Movie file picker
              <input
                type="file"
                accept="video/*,.mkv,.mp4,.m4v,.mov,.webm,.ogg,.ogv"
                onChange={(event) => uploadMovieFile(event.target.files?.[0])}
              />
            </label>
            <label className="field">
              Absolute path fallback
              <input
                value={moviePath}
                onChange={(event) => setMoviePath(event.target.value)}
                placeholder="/Users/soroushsamani/Movies/movie.mp4"
              />
            </label>
            <button className="button wide primary" onClick={loadMovie}>Load movie from laptop</button>
            {media && (
              <button
                className="button wide"
                onClick={makePhoneSafeMp4}
                disabled={transcodeStatus?.status === "running" || transcodeStatus?.status === "starting"}
                title="Convert MKV/HEVC files to MP4 H.264/AAC for phones and browsers"
              >
                {transcodeStatus?.status === "running" || transcodeStatus?.status === "starting"
                  ? "Converting phone-safe MP4..."
                  : shouldOfferPhoneMp4
                    ? "Make phone-safe MP4"
                    : "Rebuild phone-safe MP4"}
              </button>
            )}
            {transcodeStatus?.message && (
              <div className={`hint transcode-note ${transcodeStatus.status === "failed" ? "error" : ""}`}>
                {transcodeStatus.message}
              </div>
            )}
            <div className="hint">
              MP4 with H.264 video and AAC audio is the safest format for phones. MKV, x265, and HEVC can show a black screen on some browsers.
            </div>
          </section>

          <section className="panel-card card-red">
            <div className="card-header">
              <Settings2 size={28} className="icon-red" />
              <div>
                <h2>Network & Status</h2>
                <p>Socket, Network, Sync</p>
              </div>
            </div>
            <div className="status-strip-vertical">
              <div className="status-row">
                <span className={connected ? "dot ok" : "dot"} />
                <span>{connected ? "Socket connected" : "Connecting..."}</span>
              </div>
              <div className="status-row">
                <span>Room: {roomId}</span>
              </div>
              <div className="status-row">
                <span>{media ? `${displayMediaName} · ${formatBytes(media.size)}` : "No movie selected"}</span>
              </div>
              <div className="status-row">
                <span>Status: {status || "Ready"}</span>
              </div>
            </div>
          </section>
        </div>
      </section>
'''

# Find <div className="cards-grid"> up to </section> before {[...remoteStreams.entries()]
pattern = re.compile(r'<div className="cards-grid">.*?</section>\s*</section>\s*(?=\{\[\.\.\.remoteStreams)', re.DOTALL)
if pattern.search(app):
    app = pattern.sub(good_cards_grid + '\n', app)
else:
    # If pattern failed, maybe it's broken. Let's find <div className="cards-grid"> and everything up to <main> end minus remote streams
    pattern2 = re.compile(r'<div className="cards-grid">.*?(?=\{\[\.\.\.remoteStreams)', re.DOTALL)
    app = pattern2.sub(good_cards_grid + '\n', app)

with open('src/App.jsx', 'w') as f:
    f.write(app)
