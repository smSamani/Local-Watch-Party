import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

# 1. Update imports
new_imports = '''import {
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
} from "lucide-react";'''
app = re.sub(r'import \{\s*Captions,[\s\S]*?\} from "lucide-react";', new_imports, app)

# 2. Replace return block
return_block = '''  return (
    <div className={`lan-app ${theaterMode ? "theater-mode" : ""}`}>
      {!profileReady && (
        <div className="welcome-layer">
          <form className="welcome-card" onSubmit={saveProfile}>
            <span className="brand-mark"><MonitorPlay size={22} /></span>
            <h1>Join LAN CINEMA</h1>
            <p>Enter your display name to continue.</p>
            <label className="field">
              <input
                autoFocus
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Your name"
              />
            </label>
            <button className="button primary wide" type="submit">Enter Room</button>
          </form>
        </div>
      )}
      
      {/* Top Bar */}
      <header className="lan-topbar">
        <div className="topbar-left">
          <MonitorPlay className="lan-logo-icon" size={24} />
          <div className="lan-brand">
            <h1>LAN CINEMA</h1>
            <p>Watch Together. Locally.</p>
          </div>
        </div>
        
        <div className="topbar-center">
          <div className="room-badge">
            <span className="room-label">Room:</span>
            <span className="room-id">{roomId}</span>
            <button onClick={copyShareLink} className="copy-btn"><Copy size={14}/></button>
          </div>
          <button className="share-btn" onClick={copyShareLink}>
            <Link2 size={14} /> Share Link
          </button>
        </div>
        
        <div className="topbar-right">
          <div className="users-count">
            <Users size={16} />
            <span>{peers.length + 1} / 8</span>
            <span className="dot ok" />
          </div>
          <div className="avatar-group">
            <div className="avatar-pill self">
              <span className="avatar-img-placeholder">
                <img src={`https://api.dicebear.com/7.x/initials/svg?seed=${name}&backgroundColor=0c131a&textColor=d1d5db`} alt="" />
              </span>
              <span className="avatar-name">You (Host)</span>
              <span className="host-crown">👑</span>
            </div>
            {peers.map(peer => (
              <div className="avatar-pill" key={peer.id}>
                <span className="avatar-img-placeholder">
                  <img src={`https://api.dicebear.com/7.x/initials/svg?seed=${peer.name}&backgroundColor=0c131a&textColor=d1d5db`} alt="" />
                </span>
                <span className="avatar-name">{peer.name}</span>
              </div>
            ))}
          </div>
          <div className="window-controls">
            <button><MessageCircle size={18}/></button>
            <button><Settings2 size={18}/></button>
            <button><Minus size={18}/></button>
            <button><Square size={14}/></button>
            <button><X size={18}/></button>
          </div>
        </div>
      </header>

      <div className="lan-workspace">
        <div className="lan-main-col">
          <div 
            className={`lan-video-container ${showChrome ? "chrome-visible" : "chrome-hidden"}`}
            ref={screenRef}
            onPointerMove={() => showPlayerChrome()}
            onPointerUp={handleScreenPointerUp}
          >
            <video
              ref={videoRef}
              src={streamUrl}
              playsInline
              preload="metadata"
              onLoadedMetadata={onVideoLoaded}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onCanPlay={() => setMediaError("")}
              onError={() => {
                if (!media) return;
                setIsPlaying(false);
                setMediaError("Playback error.");
              }}
              onEnded={() => emitPlayback({ playing: false, currentTime: duration })}
            />
            {!media && (
              <div className="empty-state">
                <MonitorPlay size={44} />
                <h2>No movie selected</h2>
                <p style={{color: 'var(--text-muted)'}}>Use the Host Controls panel to load a file.</p>
              </div>
            )}
            
            {media && (
              <div className="subtitle-layer" style={{ "--subtitle-size": `${subtitleSettings.size}px`, "--subtitle-gap": `${subtitleSettings.gap}px` }}>
                {(subtitleSettings.mode === "both" || subtitleSettings.mode === "fa") && faCue && (
                  <div className="subtitle-line subtitle-fa" dir="rtl">{faCue.text}</div>
                )}
                {(subtitleSettings.mode === "both" || subtitleSettings.mode === "en") && enCue && (
                  <div className="subtitle-line subtitle-en">{enCue.text}</div>
                )}
              </div>
            )}
            
            <div className={`lan-transport ${showChrome ? 'visible' : ''}`}>
               <div className="scrub-row">
                 <span>{formatTime(currentTime)}</span>
                 <input
                   type="range"
                   className="scrub-slider"
                   min="0"
                   max={duration || 0}
                   value={Math.min(currentTime, duration || currentTime)}
                   step="0.05"
                   onChange={(event) => seekTo(Number(event.target.value))}
                   disabled={!media}
                 />
                 <span>-{formatTime(Math.max(0, duration - currentTime))}</span>
               </div>
               
               <div className="control-row">
                 <div className="control-left">
                   <button onClick={() => setVideoMuted(!videoMuted)} className="icon-btn">
                     {videoMuted ? <VolumeX size={18}/> : <Volume2 size={18}/>}
                   </button>
                   <input type="range" className="vol-slider" min="0" max="1" step="0.01" value={userVolume} onChange={(e) => setUserVolume(Number(e.target.value))} />
                   <span className="vol-text">{Math.round(userVolume*100)}%</span>
                   <button className="icon-btn people-btn"><Users size={18}/> <span className="badge">{peers.length+1}</span></button>
                 </div>
                 
                 <div className="control-center">
                   <button className="icon-btn" onClick={() => seekBy(-10)}><RotateCcw size={20}/></button>
                   <button className="icon-btn"><SkipBack size={20}/></button>
                   <button className="play-btn" onClick={togglePlay}>
                     {isPlaying ? <Pause fill="currentColor" size={24}/> : <Play fill="currentColor" size={24}/>}
                   </button>
                   <button className="icon-btn"><SkipForward size={20}/></button>
                   <button className="icon-btn" onClick={() => seekBy(10)}><RotateCw size={20}/></button>
                   <button className="icon-btn"><Square fill="currentColor" size={14} style={{marginLeft: '2px'}}/></button>
                 </div>
                 
                 <div className="control-right">
                   <button className="icon-btn"><Monitor size={18}/></button>
                   <button className="icon-btn" onClick={toggleSubtitles}><MessageSquare size={18}/></button>
                   <button className="icon-btn" onClick={toggleTheaterMode}><Maximize size={18}/></button>
                 </div>
               </div>
            </div>
            
            {media && (!playbackUnlocked || pendingAutoplay) && (
              <button className="unlock-overlay" onClick={unlockPlayback}>
                <Play size={22} /> Enable playback
              </button>
            )}
          </div>
          
          <div className="lan-voice-panel">
            <button className={`mic-toggle-btn ${micEnabled ? "on" : "off"}`} onClick={toggleMic}>
              {micEnabled ? <Mic size={28}/> : <MicOff size={28}/>}
              <span>{micEnabled ? "Mic On" : "Mic Off"}</span>
            </button>
            
            <div className="ducking-section">
              <div className="ducking-header">
                <span>Adaptive Ducking</span>
              </div>
              <div className="ducking-controls">
                <div className="fake-waveform">
                  <div className="bar" style={{height: '40%'}}></div>
                  <div className="bar" style={{height: '70%'}}></div>
                  <div className="bar" style={{height: '100%'}}></div>
                  <div className="bar" style={{height: '60%'}}></div>
                  <div className="bar" style={{height: '30%'}}></div>
                  <div className="bar" style={{height: '80%'}}></div>
                  <div className="bar" style={{height: '50%'}}></div>
                  <div className="bar" style={{height: '90%'}}></div>
                </div>
                <label className="switch">
                  <input type="checkbox" checked={adaptiveDucking} onChange={(e) => setAdaptiveDucking(e.target.checked)} />
                  <span className="slider round"></span>
                </label>
              </div>
            </div>
            
            <div className="voice-activity-section">
               <span className="section-label">Voice Activity</span>
               <div className="voice-meters">
                 <div className="meter-row">
                   <span className="meter-name">You</span>
                   <div className="meter-bars">
                     {Array.from({length: 15}).map((_, i) => <div key={i} className={`meter-segment ${localMicLevel > i/15 ? 'active' : ''}`} />)}
                   </div>
                 </div>
                 {peers.slice(0,1).map(peer => {
                    const voice = voiceState[peer.id] || {level: 0};
                    return (
                      <div className="meter-row" key={peer.id}>
                        <span className="meter-name">{peer.name}</span>
                        <div className="meter-bars">
                          {Array.from({length: 15}).map((_, i) => <div key={i} className={`meter-segment ${voice.level > i/15 ? 'active' : ''}`} />)}
                        </div>
                      </div>
                    )
                 })}
                 {peers.length === 0 && (
                   <div className="meter-row">
                     <span className="meter-name" style={{opacity: 0.5}}>Aria</span>
                     <div className="meter-bars">
                       {Array.from({length: 15}).map((_, i) => <div key={i} className={`meter-segment`} style={{opacity: 0.2}} />)}
                     </div>
                   </div>
                 )}
               </div>
            </div>
            
            <div className="audio-mode-section">
               <span className="section-label">Audio Mode</span>
               <select className="lan-select" value={voiceOutputEnabled ? "ducking" : "muted"} onChange={(e) => setVoiceOutputEnabled(e.target.value === "ducking")}>
                 <option value="ducking">Ducking (Auto)</option>
                 <option value="muted">Muted</option>
               </select>
               <span className="audio-mode-desc">Lowering movie volume when someone talks.</span>
            </div>
          </div>
          
          <footer className="lan-status-bar">
             <div className="status-item">
               Server: <span className="highlight-id">{roomId}</span> 
               <span className="status-badge">Online</span>
             </div>
             <div className="status-item">
               Local IP: <span className="highlight-white">{health?.lanIps?.[0] || '192.168.1.42'}</span>
             </div>
             <div className="status-item">
               <Wifi size={14} className="accent-icon"/> Quality: <span className="highlight-white">LAN (Excellent)</span>
             </div>
             <div className="status-item">
               <Gauge size={14} className="accent-icon"/> Latency: <span className="highlight-white">4 ms</span>
             </div>
          </footer>
        </div>

        <aside className="lan-sidebar">
          <div className="sidebar-section">
             <div className="section-header">
                <h3>HOST CONTROLS</h3>
                <ChevronUp size={16} className="chevron"/>
             </div>
             <div className="section-content">
               <div className="input-group">
                 <label>Movie File</label>
                 <div className="file-input-wrapper">
                    <input type="text" value={moviePath || displayMediaName} readOnly placeholder="D:\\Movies\\Dune.Part.Two.mkv" />
                    <button className="folder-btn" onClick={() => document.getElementById('movie-upload').click()}><FolderOpen size={16}/></button>
                    <input id="movie-upload" type="file" style={{display:'none'}} accept="video/*,.mkv,.mp4,.m4v,.mov,.webm,.ogg,.ogv" onChange={(e) => uploadMovieFile(e.target.files?.[0])} />
                 </div>
                 <div className="file-meta">
                   <span className={media ? "success-text" : "muted-text"}>{media ? "File loaded" : "No file"}</span>
                   <span className="muted-text">{media ? formatBytes(media.size) : '0 GB'}</span>
                 </div>
               </div>
               
               <div className="input-group">
                 <label>Subtitles</label>
                 <div className="file-input-wrapper mb-2">
                    <select className="lang-select">
                      <option>فارسی (Persian)</option>
                    </select>
                    <input type="text" value={subtitlePathFa} placeholder="Movie.fa.srt" onChange={(e) => setSubtitlePathFa(e.target.value)} />
                    <button className="clear-btn" onClick={() => setSubtitlePathFa('')}><X size={14}/></button>
                    <button className="folder-btn" onClick={() => document.getElementById('fa-upload').click()}><FolderOpen size={16}/></button>
                    <input id="fa-upload" type="file" style={{display:'none'}} onChange={(e) => uploadSubtitleFile("fa", e.target.files?.[0])} />
                 </div>
                 <div className="file-input-wrapper">
                    <select className="lang-select">
                      <option>English</option>
                    </select>
                    <input type="text" value={subtitlePathEn} placeholder="Movie.en.srt" onChange={(e) => setSubtitlePathEn(e.target.value)} />
                    <button className="clear-btn" onClick={() => setSubtitlePathEn('')}><X size={14}/></button>
                    <button className="folder-btn" onClick={() => document.getElementById('en-upload').click()}><FolderOpen size={16}/></button>
                    <input id="en-upload" type="file" style={{display:'none'}} onChange={(e) => uploadSubtitleFile("en", e.target.files?.[0])} />
                 </div>
               </div>
             </div>
          </div>
          
          <div className="sidebar-section">
             <div className="section-header">
                <h3>ROOM & CONNECTION</h3>
                <ChevronDown size={16} className="chevron"/>
             </div>
             <div className="section-content">
               <div className="input-group">
                 <label>Room Link</label>
                 <div className="file-input-wrapper">
                   <input type="text" value={shareUrl} readOnly />
                   <button className="folder-btn" onClick={copyShareLink}><Copy size={16}/></button>
                 </div>
               </div>
               <div className="input-group">
                 <label>Or share this code with your friend:</label>
                 <div className="file-input-wrapper">
                   <input type="text" value={roomId.toUpperCase()} className="code-input" readOnly />
                   <button className="folder-btn" onClick={copyShareLink}><Copy size={16}/></button>
                 </div>
               </div>
               <div className="connection-status">
                 <div className="conn-left">
                   <Wifi size={18} className="muted-icon"/>
                   <div className="conn-texts">
                     <div className="muted-text">Connection</div>
                     <div className="white-text">Peers: {peers.length}</div>
                   </div>
                 </div>
                 <div className="conn-right">
                   <span className="success-text">{health ? 'Excellent' : 'Connecting'}</span>
                   <span className="dot ok"></span>
                 </div>
               </div>
             </div>
          </div>
          
          <div className="sidebar-section">
             <div className="section-header">
                <h3>SUBTITLES</h3>
                <ChevronUp size={16} className="chevron"/>
             </div>
             <div className="section-content">
                <div className="slider-group">
                  <label>Size</label>
                  <span className="slider-label-a">A</span>
                  <input type="range" min="18" max="64" value={subtitleSettings.size} onChange={(e) => updateSubtitleSettings({size: Number(e.target.value)})} className="lan-slider" />
                  <div className="number-box">{subtitleSettings.size} <span className="unit">px</span></div>
                </div>
                
                <div className="offset-group">
                  <label>Persian Offset</label>
                  <div className="stepper">
                    <button onClick={() => updateSubtitleSettings({faOffsetMs: subtitleSettings.faOffsetMs - 50})}><Minus size={14}/></button>
                    <div className="step-val">{subtitleSettings.faOffsetMs > 0 ? `+${subtitleSettings.faOffsetMs}` : subtitleSettings.faOffsetMs} ms</div>
                    <button onClick={() => updateSubtitleSettings({faOffsetMs: subtitleSettings.faOffsetMs + 50})}><Plus size={14}/></button>
                  </div>
                </div>
                
                <div className="offset-group">
                  <label>English Offset</label>
                  <div className="stepper">
                    <button onClick={() => updateSubtitleSettings({enOffsetMs: subtitleSettings.enOffsetMs - 50})}><Minus size={14}/></button>
                    <div className="step-val">{subtitleSettings.enOffsetMs > 0 ? `+${subtitleSettings.enOffsetMs}` : subtitleSettings.enOffsetMs} ms</div>
                    <button onClick={() => updateSubtitleSettings({enOffsetMs: subtitleSettings.enOffsetMs + 50})}><Plus size={14}/></button>
                  </div>
                </div>
                
                <div className="preview-box">
                  <div className="preview-fa" dir="rtl">گاهی برای پیدا کردن پاسخ، باید مسیرت را گم کنی.</div>
                  <div className="preview-en">Sometimes you have to get lost to find the answer.</div>
                </div>
                
                <div className="input-group mt-3">
                  <label>Display Mode</label>
                  <select className="lan-select w-full" value={subtitleSettings.mode} onChange={(e) => updateSubtitleSettings({mode: e.target.value})}>
                    <option value="both">Both Languages (Stacked)</option>
                    <option value="fa">Persian Only</option>
                    <option value="en">English Only</option>
                    <option value="off">Off</option>
                  </select>
                </div>
                
                <div className="input-group">
                  <label>Position</label>
                  <select className="lan-select w-full">
                    <option>Bottom Center</option>
                  </select>
                </div>
                
                <div className="bg-check-group">
                  <label className="checkbox-label">
                    <input type="checkbox" />
                    <span className="check-box"></span>
                    Background
                  </label>
                  <div className="color-picker">
                    <div className="color-swatch"></div>
                    <ChevronDown size={14}/>
                  </div>
                  <span className="opacity-val">70%</span>
                </div>
             </div>
          </div>
        </aside>
      </div>
      
      {[...remoteStreams.entries()].map(([id, stream]) => (
        <RemoteAudio
          key={id}
          stream={stream}
          muted={!voiceOutputEnabled}
          volume={remoteVoiceVolumes[id] ?? defaultRemoteVoiceVolume}
          unlockKey={voiceUnlockKey}
          onBlocked={handleRemoteVoiceBlocked}
        />
      ))}
    </div>
  );
}'''


start_idx = app.find('  return (')
if start_idx != -1:
    app = app[:start_idx] + return_block


with open('src/App.jsx', 'w') as f:
    f.write(app)

css = '''
:root {
  color-scheme: dark;
  --bg: #060B10;
  --panel: #0C131A;
  --panel-light: #121A22;
  --border: #1E2B38;
  --accent: #05D59A;
  --accent-hover: #04b381;
  --text-main: #E5E7EB;
  --text-muted: #6B7280;
  --red: #EF4444;
  --danger: #EF4444;
  
  --radius-lg: 12px;
  --radius-md: 8px;
  --radius-sm: 6px;
  
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background-color: var(--bg);
  overflow-x: hidden;
}

body.no-scroll { overflow: hidden; }
* { box-sizing: border-box; }
button, input, select { font: inherit; }
button { color: inherit; cursor: pointer; border: none; background: none; }

.lan-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 16px;
  gap: 16px;
}

.welcome-layer {
  position: fixed; inset: 0; z-index: 200; display: grid; place-items: center;
  background: rgba(0,0,0,0.8); backdrop-filter: blur(8px);
}
.welcome-card {
  background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 32px; width: 400px; display: flex; flex-direction: column; gap: 16px; text-align: center;
}
.welcome-card input {
  width: 100%; padding: 12px; border-radius: var(--radius-md); border: 1px solid var(--border);
  background: var(--panel-light); color: var(--text-main); outline: none;
}
.button.primary {
  background: var(--accent); color: #000; font-weight: 600; padding: 12px; border-radius: var(--radius-md);
}

.lan-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 48px;
  flex-shrink: 0;
}

.topbar-left { display: flex; align-items: center; gap: 12px; }
.lan-logo-icon { color: var(--accent); }
.lan-brand h1 { margin: 0; font-size: 16px; font-weight: 700; letter-spacing: 0.5px; }
.lan-brand p { margin: 2px 0 0; font-size: 11px; color: var(--text-muted); }

.topbar-center { display: flex; align-items: center; gap: 16px; }
.room-badge {
  display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted);
}
.room-id { color: var(--accent); font-weight: 500; }
.copy-btn { color: var(--text-muted); display: flex; align-items: center; transition: color 0.2s; }
.copy-btn:hover { color: var(--text-main); }
.share-btn {
  display: flex; align-items: center; gap: 6px; border: 1px solid var(--accent);
  color: var(--accent); padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500;
  transition: all 0.2s;
}
.share-btn:hover { background: rgba(5, 213, 154, 0.1); }

.topbar-right { display: flex; align-items: center; gap: 24px; }
.users-count { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-muted); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); }
.dot.ok { background: var(--accent); box-shadow: 0 0 8px var(--accent); }

.avatar-group { display: flex; align-items: center; gap: 8px; }
.avatar-pill {
  display: flex; align-items: center; gap: 8px; background: var(--panel); border: 1px solid var(--border);
  padding: 4px 12px 4px 4px; border-radius: 20px; font-size: 12px;
}
.avatar-pill.self { border-color: rgba(255,255,255,0.1); }
.avatar-img-placeholder {
  width: 24px; height: 24px; border-radius: 50%; overflow: hidden; background: var(--panel-light);
}
.avatar-img-placeholder img { width: 100%; height: 100%; object-fit: cover; }
.host-crown { font-size: 12px; }

.window-controls { display: flex; align-items: center; gap: 16px; color: var(--text-muted); }
.window-controls button:hover { color: var(--text-main); }

.lan-workspace {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.lan-main-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.lan-video-container {
  flex: 1;
  background: #000;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.lan-video-container video {
  width: 100%; height: 100%; object-fit: contain;
}

.empty-state {
  position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: var(--text-muted); gap: 16px;
}
.empty-state h2 { color: var(--text-main); margin: 0; }

.subtitle-layer {
  position: absolute; bottom: 80px; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; gap: var(--subtitle-gap, 6px);
  pointer-events: none; z-index: 10;
}
.subtitle-line {
  font-size: var(--subtitle-size, 34px); color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.8), 0 0 8px rgba(0,0,0,0.8);
  text-align: center; max-width: 90%; white-space: pre-wrap; font-weight: 600;
}

.lan-transport {
  position: absolute; bottom: 0; left: 0; right: 0; padding: 24px 32px 16px;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  opacity: 0; transition: opacity 0.3s;
}
.lan-transport.visible { opacity: 1; }

.scrub-row { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.scrub-slider {
  flex: 1; -webkit-appearance: none; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; outline: none;
}
.scrub-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: var(--accent);
  box-shadow: 0 0 8px var(--accent); cursor: pointer;
}

.control-row { display: flex; justify-content: space-between; align-items: center; }
.control-left, .control-center, .control-right { display: flex; align-items: center; gap: 16px; }
.icon-btn { color: var(--text-main); display: flex; align-items: center; justify-content: center; transition: color 0.2s; }
.icon-btn:hover { color: var(--accent); }

.vol-slider { width: 60px; -webkit-appearance: none; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; }
.vol-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 10px; height: 10px; border-radius: 50%; background: #fff; }
.vol-text { font-size: 12px; color: var(--text-muted); width: 30px; }

.people-btn { background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; gap: 6px; }
.people-btn .badge { font-size: 10px; background: var(--accent); color: #000; padding: 0 4px; border-radius: 10px; font-weight: 700; }

.play-btn {
  width: 44px; height: 44px; border-radius: 50%; border: 2px solid var(--accent); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
}

.lan-voice-panel {
  display: flex; gap: 16px; height: 100px;
}
.lan-voice-panel > * {
  background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 16px;
}
.mic-toggle-btn {
  width: 90px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
  font-size: 12px; font-weight: 500; transition: all 0.2s;
}
.mic-toggle-btn.on { color: var(--accent); }
.mic-toggle-btn.off { color: var(--text-muted); }

.ducking-section { flex: 1.2; display: flex; flex-direction: column; justify-content: space-between; }
.ducking-header { font-size: 12px; color: var(--text-muted); }
.ducking-controls { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; }
.fake-waveform { display: flex; gap: 3px; height: 24px; align-items: center; }
.fake-waveform .bar { width: 4px; background: var(--accent); border-radius: 2px; opacity: 0.8; }

.switch { position: relative; display: inline-block; width: 40px; height: 22px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--panel-light); transition: .4s; border-radius: 34px; border: 1px solid var(--border); }
.slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: var(--text-muted); transition: .4s; border-radius: 50%; }
input:checked + .slider { border-color: var(--accent); }
input:checked + .slider:before { transform: translateX(18px); background-color: var(--accent); }

.voice-activity-section { flex: 2; display: flex; flex-direction: column; gap: 12px; }
.section-label { font-size: 12px; color: var(--text-muted); }
.voice-meters { display: flex; flex-direction: column; gap: 8px; }
.meter-row { display: flex; align-items: center; gap: 12px; }
.meter-name { width: 30px; font-size: 12px; color: var(--text-main); }
.meter-bars { display: flex; gap: 2px; flex: 1; }
.meter-segment { height: 8px; flex: 1; background: var(--panel-light); border-radius: 1px; }
.meter-segment.active { background: var(--accent); }

.audio-mode-section { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 8px; }
.audio-mode-desc { font-size: 11px; color: var(--text-muted); }

.lan-select {
  background: var(--panel-light); border: 1px solid var(--border); color: var(--text-main);
  padding: 8px 12px; border-radius: var(--radius-md); font-size: 13px; outline: none; appearance: none;
}
.w-full { width: 100%; }

.lan-status-bar {
  display: flex; align-items: center; gap: 32px; padding: 0 16px; height: 32px;
  font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border); margin-top: -8px;
}
.status-item { display: flex; align-items: center; gap: 8px; }
.highlight-id { color: var(--text-main); font-family: monospace; }
.highlight-white { color: var(--text-main); }
.status-badge { border: 1px solid var(--accent); color: var(--accent); padding: 2px 6px; border-radius: 4px; font-size: 10px; }
.accent-icon { color: var(--accent); }

/* Sidebar */
.lan-sidebar {
  width: 320px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-section { border-bottom: 1px solid var(--border); }
.sidebar-section:last-child { border-bottom: none; }
.section-header {
  display: flex; justify-content: space-between; align-items: center; padding: 16px;
  color: var(--accent); cursor: pointer;
}
.section-header h3 { margin: 0; font-size: 11px; font-weight: 700; letter-spacing: 1px; }

.section-content { padding: 0 16px 20px; display: flex; flex-direction: column; gap: 16px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-size: 12px; color: var(--text-main); }

.file-input-wrapper {
  display: flex; background: var(--panel-light); border: 1px solid var(--border); border-radius: var(--radius-md);
  overflow: hidden; height: 36px;
}
.file-input-wrapper input[type="text"] {
  flex: 1; background: none; border: none; padding: 0 12px; color: var(--text-muted); font-size: 12px; outline: none;
}
.file-input-wrapper .code-input { letter-spacing: 2px; color: var(--text-main); }
.folder-btn, .clear-btn {
  width: 36px; display: grid; place-items: center; border-left: 1px solid var(--border); color: var(--text-muted);
}
.folder-btn:hover, .clear-btn:hover { background: rgba(255,255,255,0.05); color: var(--text-main); }

.file-meta { display: flex; justify-content: space-between; font-size: 11px; }
.success-text { color: var(--accent); }
.muted-text { color: var(--text-muted); }
.white-text { color: var(--text-main); font-size: 13px; }

.mb-2 { margin-bottom: 8px; }
.mt-3 { margin-top: 12px; }

.lang-select {
  background: none; border: none; border-right: 1px solid var(--border); padding: 0 8px;
  color: var(--text-main); font-size: 12px; outline: none; width: 110px;
}

.connection-status { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.conn-left { display: flex; gap: 12px; align-items: center; }
.muted-icon { color: var(--text-muted); }
.conn-texts { display: flex; flex-direction: column; gap: 4px; font-size: 11px; }

.slider-group { display: flex; align-items: center; gap: 12px; }
.slider-group label { font-size: 12px; width: 40px; }
.slider-label-a { font-size: 14px; font-weight: 600; }
.lan-slider { flex: 1; -webkit-appearance: none; height: 2px; background: var(--border); border-radius: 1px; }
.lan-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: var(--accent); border: 2px solid var(--bg); box-shadow: 0 0 0 1px var(--accent); }
.number-box { background: var(--panel-light); border: 1px solid var(--border); padding: 4px 8px; border-radius: 4px; font-size: 12px; display: flex; gap: 4px;}
.number-box .unit { color: var(--text-muted); }

.offset-group { display: flex; justify-content: space-between; align-items: center; }
.offset-group label { font-size: 12px; color: var(--text-muted); }
.stepper { display: flex; align-items: center; background: var(--panel-light); border: 1px solid var(--border); border-radius: var(--radius-md); overflow: hidden; }
.stepper button { width: 28px; height: 28px; display: grid; place-items: center; color: var(--text-muted); }
.stepper button:hover { background: rgba(255,255,255,0.05); color: var(--text-main); }
.step-val { width: 70px; text-align: center; font-size: 12px; border-left: 1px solid var(--border); border-right: 1px solid var(--border); }

.preview-box { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px; margin-top: 8px; display: flex; flex-direction: column; gap: 8px; align-items: center; text-align: center; }
.preview-fa { color: var(--accent); font-size: 14px; font-weight: 600; }
.preview-en { color: var(--text-muted); font-size: 12px; }

.bg-check-group { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); cursor: pointer; }
.checkbox-label input { display: none; }
.check-box { width: 14px; height: 14px; border: 1px solid var(--border); border-radius: 3px; display: inline-block; }
.color-picker { display: flex; align-items: center; gap: 6px; background: var(--panel-light); border: 1px solid var(--border); padding: 4px 8px; border-radius: 4px; }
.color-swatch { width: 16px; height: 10px; background: #000; border-radius: 2px; }
.opacity-val { font-size: 12px; color: var(--text-main); margin-left: auto; }
'''

with open('src/styles.css', 'w') as f:
    f.write(css)

