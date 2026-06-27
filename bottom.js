  return (
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
                   <button className="icon-btn" onClick={() => togglePlay()}><Square fill="currentColor" size={14} style={{marginLeft: '2px'}}/></button>
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
                    <input type="text" value={moviePath || displayMediaName} readOnly placeholder="D:\Movies\Dune.Part.Two.mkv" />
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
}

createRoot(document.getElementById("root")).render(<App />);
