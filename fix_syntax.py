import re

with open('top.js', 'r') as f:
    top_js = f.read()

with open('logic.js', 'r') as f:
    logic_js = f.read()

with open('bottom.js', 'r') as f:
    bottom_js = f.read()

app = top_js + '\\n' + logic_js + '\\n' + bottom_js

# Replace literal \n that might break Python evaluation
app = top_js + '\n' + logic_js + '\n' + bottom_js

# 0. Fix SERVER_URL
app = app.replace('typeof process !== "undefined" && process.env.PUBLIC_TUNNEL', 'window.location.hostname.includes("trycloudflare.com")')

# 1. Add pingMs state and update ping interval
state_inject = """  const [speakerToast, setSpeakerToast] = useState({ entries: [], exiting: false });
  const [pingMs, setPingMs] = useState(0);"""
app = app.replace('  const [speakerToast, setSpeakerToast] = useState({ entries: [], exiting: false });', state_inject)

# 2. Add ping calculation in health check interval
app = app.replace(
"""    const refreshHealth = () => {
      fetch(`${SERVER_URL}/api/health`)
        .then((response) => response.json())
        .then((payload) => {
          if (!cancelled) setHealth(payload);
        })
        .catch(() => {
          if (!cancelled) setHealth(null);
        });
    };""",
"""    const refreshHealth = () => {
      const start = Date.now();
      fetch(`${SERVER_URL}/api/health`)
        .then((response) => response.json())
        .then((payload) => {
          if (!cancelled) {
            setHealth(payload);
            setPingMs(Date.now() - start);
          }
        })
        .catch(() => {
          if (!cancelled) setHealth(null);
        });
    };""")

# 3. Fix Window Controls
window_controls = """          <div className="window-controls">
            <button onClick={toggleSubtitles} title="Subtitles"><MessageCircle size={18}/></button>
            <button onClick={() => document.documentElement.requestFullscreen()} title="Fullscreen"><Square size={14}/></button>
            <button onClick={() => window.location.href = '/'} title="Leave Room"><X size={18}/></button>
          </div>"""
app = re.sub(r'<div className="window-controls">[\s\S]*?</div>', window_controls, app)

# 4. Fix Transport Controls
transport_controls = """                 <div className="control-center">
                   <button className="icon-btn" onClick={() => seekBy(-10)}><RotateCcw size={20}/></button>
                   <button className="icon-btn" onClick={() => seekTo(0)}><SkipBack size={20}/></button>
                   <button className="play-btn" onClick={togglePlay}>
                     {isPlaying ? <Pause fill="currentColor" size={24}/> : <Play fill="currentColor" size={24}/>}
                   </button>
                   <button className="icon-btn" onClick={() => seekTo(duration)}><SkipForward size={20}/></button>
                   <button className="icon-btn" onClick={() => seekBy(10)}><RotateCw size={20}/></button>
                   <button className="icon-btn" onClick={() => { seekTo(0); if (isPlaying) togglePlay(); }}><Square fill="currentColor" size={14} style={{marginLeft: '2px'}}/></button>
                 </div>"""
app = re.sub(r'<div className="control-center">[\s\S]*?</div>', transport_controls, app)

# 5. Fix Waveform Animation
waveform = """              <div className="ducking-controls">
                <div className={`fake-waveform ${anyoneSpeaking && adaptiveDucking ? 'animating' : ''}`}>
                  <div className="bar" style={{height: '40%'}}></div>
                  <div className="bar" style={{height: '70%'}}></div>
                  <div className="bar" style={{height: '100%'}}></div>
                  <div className="bar" style={{height: '60%'}}></div>
                  <div className="bar" style={{height: '30%'}}></div>
                  <div className="bar" style={{height: '80%'}}></div>
                  <div className="bar" style={{height: '50%'}}></div>
                  <div className="bar" style={{height: '90%'}}></div>
                </div>"""
app = re.sub(r'<div className="ducking-controls">\n\s*<div className="fake-waveform">\n(?:\s*<div className="bar" style=\{\{height: \'[\d]+%\'\}\}></div>\n){8}\s*</div>', waveform, app)

# 6. Remove Fake Aria User
app = re.sub(r'\{peers\.length === 0 && \(\s*<div className="meter-row">\s*<span className="meter-name" style=\{\{opacity: 0\.5\}\}>Aria</span>\s*<div className="meter-bars">\s*\{Array\.from\(\{length: 15\}\)\.map\(\(_, i\) => <div key=\{i\} className={`meter-segment`} style=\{\{opacity: 0\.2\}\} />\)\}\s*</div>\s*</div>\s*\)\}', '', app)

# 7. Fix Status Bar IP and Ping
status_bar = """          <footer className="lan-status-bar">
             <div className="status-item">
               Server: <span className="highlight-id">{roomId}</span> 
               <span className="status-badge">Online</span>
             </div>
             <div className="status-item">
               Local IP: <span className="highlight-white">{health?.lanIps?.[0] || '127.0.0.1'}</span>
             </div>
             <div className="status-item">
               <Wifi size={14} className="accent-icon"/> Quality: <span className="highlight-white">LAN (Excellent)</span>
             </div>
             <div className="status-item">
               <Gauge size={14} className="accent-icon"/> Latency: <span className="highlight-white">{pingMs} ms</span>
             </div>
          </footer>"""
app = re.sub(r'<footer className="lan-status-bar">[\s\S]*?</footer>', status_bar, app)

# 8. Fix Subtitle Sidebar Controls
subtitle_sidebar = """                <div className="preview-box" style={{ 
                    fontSize: `${Math.max(12, subtitleSettings.size * 0.4)}px`,
                    background: subtitleSettings.bg ? `rgba(0,0,0,${(subtitleSettings.bgOpacity ?? 70) / 100})` : 'transparent'
                }}>
                  {subtitleSettings.mode !== 'en' && <div className="preview-fa" dir="rtl">گاهی برای پیدا کردن پاسخ، باید مسیرت را گم کنی.</div>}
                  {subtitleSettings.mode !== 'fa' && <div className="preview-en">Sometimes you have to get lost to find the answer.</div>}
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
                
                <div className="bg-check-group mt-3">
                  <label className="checkbox-label" style={{flex: 1}}>
                    <input type="checkbox" checked={subtitleSettings.bg || false} onChange={(e) => updateSubtitleSettings({bg: e.target.checked})} />
                    <span className="check-box" style={{ background: subtitleSettings.bg ? 'var(--accent)' : 'transparent', borderColor: subtitleSettings.bg ? 'var(--accent)' : 'var(--border)' }}></span>
                    Background
                  </label>
                  <input type="range" min="0" max="100" value={subtitleSettings.bgOpacity ?? 70} onChange={(e) => updateSubtitleSettings({bgOpacity: Number(e.target.value)})} style={{width: '80px'}} className="lan-slider" />
                  <span className="opacity-val" style={{width: '32px', textAlign: 'right'}}>{subtitleSettings.bgOpacity ?? 70}%</span>
                </div>"""
app = re.sub(r'<div className="preview-box">[\s\S]*?<span className="opacity-val">70%</span>\n\s*</div>', subtitle_sidebar, app)

# 9. Add Transcoding button and Status to Movie File section
movie_file_section = """                 <div className="file-meta">
                   <span className={media ? "success-text" : "muted-text"}>{media ? "File loaded" : "No file"}</span>
                   <span className="muted-text">{media ? formatBytes(media.size) : '0 GB'}</span>
                 </div>
                 {shouldOfferPhoneMp4 && (
                   <button className="button primary mt-2" onClick={makePhoneSafeMp4} style={{fontSize: '12px', padding: '4px 8px', borderRadius: '4px'}}>
                     Convert to phone safe MP4
                   </button>
                 )}
                 {transcodeStatus && (
                   <div className="transcode-status mt-2" style={{fontSize: '12px', color: 'var(--accent)'}}>
                     {transcodeStatus.message}
                   </div>
                 )}"""
app = re.sub(r'<div className="file-meta">[\s\S]*?</div>', movie_file_section, app)


# 10. Add Voice Blocked Overlay and Media Error Overlay to Video Container
overlays = """            {media && (!playbackUnlocked || pendingAutoplay) && (
              <button className="unlock-overlay" onClick={unlockPlayback}>
                <Play size={22} /> Enable playback
              </button>
            )}
            {mediaError && (
              <div className="unlock-overlay" style={{background: 'rgba(200,30,30,0.8)'}}>
                {mediaError}
              </div>
            )}
            {voiceBlocked && (
              <button className="unlock-overlay" onClick={unlockRemoteVoice} style={{background: 'rgba(5, 213, 154, 0.9)', color: '#000', top: '20px', bottom: 'auto', height: 'auto', padding: '10px 20px', borderRadius: '8px'}}>
                <Mic size={22} /> Click to hear voice chat
              </button>
            )}"""
app = app.replace("""            {media && (!playbackUnlocked || pendingAutoplay) && (
              <button className="unlock-overlay" onClick={unlockPlayback}>
                <Play size={22} /> Enable playback
              </button>
            )}""", overlays)

# 11. Add App Status Text to Top Bar
# We just use string replace on the Link2 button instead of complex regex
link_button = """          <button className="share-btn" onClick={copyShareLink}>
            <Link2 size={14} /> Share Link
          </button>"""
link_button_new = """          <button className="share-btn" onClick={copyShareLink}>
            <Link2 size={14} /> Share Link
          </button>
          {status && <span className="status-toast" style={{marginLeft: '12px', fontSize: '13px', color: 'var(--accent)'}}>{status}</span>}"""
app = app.replace(link_button, link_button_new)

# 12. Connect Subtitle Position
subtitle_layer_orig = """            {media && (
              <div className="subtitle-layer" style={{ 
                "--subtitle-size": `${subtitleSettings.size}px`, 
                "--subtitle-gap": `${subtitleSettings.gap}px`
              }}>"""
subtitle_layer_new = """            {media && (
              <div className="subtitle-layer" style={{ 
                "--subtitle-size": `${subtitleSettings.size}px`, 
                "--subtitle-gap": `${subtitleSettings.gap}px`,
                backgroundColor: subtitleSettings.bg ? `rgba(0,0,0,${(subtitleSettings.bgOpacity ?? 70) / 100})` : 'transparent',
                padding: subtitleSettings.bg ? '16px 32px' : '0',
                borderRadius: subtitleSettings.bg ? '12px' : '0',
                top: subtitleSettings.position === 'top' ? '40px' : 'auto',
                bottom: subtitleSettings.position === 'top' ? 'auto' : '100px',
                transform: subtitleSettings.position === 'top' ? 'translateX(-50%)' : 'translateX(-50%)'
              }}>"""
app = app.replace(subtitle_layer_orig, subtitle_layer_new)

pos_select_orig = """                <div className="input-group">
                  <label>Position</label>
                  <select className="lan-select w-full">
                    <option>Bottom Center</option>
                  </select>
                </div>"""
pos_select_new = """                <div className="input-group">
                  <label>Position</label>
                  <select className="lan-select w-full" value={subtitleSettings.position || 'bottom'} onChange={(e) => updateSubtitleSettings({position: e.target.value})}>
                    <option value="bottom">Bottom Center</option>
                    <option value="top">Top Center</option>
                  </select>
                </div>"""
app = app.replace(pos_select_orig, pos_select_new)

with open('src/App.jsx', 'w') as f:
    f.write(app)
