import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

# 1. Add pingMs state and update ping interval
state_inject = """  const [speakerToast, setSpeakerToast] = useState({ entries: [], exiting: false });
  const [pingMs, setPingMs] = useState(0);"""
app = app.replace('  const [speakerToast, setSpeakerToast] = useState({ entries: [], exiting: false });', state_inject)

# 2. Add ping calculation in health check interval
health_effect = """  useEffect(() => {
    let cancelled = false;
    const refreshHealth = () => {
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
    };"""
app = re.sub(r'  useEffect\(\(\) => \{\n    let cancelled = false;\n    const refreshHealth = \(\) => \{\n      fetch\(`\$\{SERVER_URL\}/api/health`\)\n        \.then\(\(response\) => response\.json\(\)\)\n        \.then\(\(payload\) => \{\n          if \(!cancelled\) setHealth\(payload\);\n        \}\)', health_effect, app)

# 3. Fix Window Controls
window_controls = """          <div className="window-controls">
            <button onClick={toggleSubtitles} title="Subtitles"><MessageCircle size={18}/></button>
            <button onClick={() => document.documentElement.requestFullscreen()} title="Fullscreen"><Square size={14}/></button>
            <button onClick={() => window.location.href = '/'} title="Leave Room"><X size={18}/></button>
          </div>"""
app = re.sub(r'<div className="window-controls">[\s\S]*?</div>', window_controls, app)

# 4. Fix Subtitle Layer Background
subtitle_layer = """            {media && (
              <div className="subtitle-layer" style={{ 
                "--subtitle-size": `${subtitleSettings.size}px`, 
                "--subtitle-gap": `${subtitleSettings.gap}px`,
                backgroundColor: subtitleSettings.bg ? `rgba(0,0,0,${(subtitleSettings.bgOpacity ?? 70) / 100})` : 'transparent',
                padding: subtitleSettings.bg ? '16px 32px' : '0',
                borderRadius: subtitleSettings.bg ? '12px' : '0',
              }}>"""
app = re.sub(r'\{media && \(\n\s*<div className="subtitle-layer" style=\{\{ "--subtitle-size": `\$\{subtitleSettings\.size\}px`, "--subtitle-gap": `\$\{subtitleSettings\.gap\}px` \}\}>', subtitle_layer, app)

# 5. Fix Transport Controls
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

# 6. Fix Waveform Animation
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

# 7. Remove Fake Aria User
app = re.sub(r'\{peers\.length === 0 && \(\s*<div className="meter-row">\s*<span className="meter-name" style=\{\{opacity: 0\.5\}\}>Aria</span>\s*<div className="meter-bars">\s*\{Array\.from\(\{length: 15\}\)\.map\(\(_, i\) => <div key=\{i\} className={`meter-segment`} style=\{\{opacity: 0\.2\}\} />\)\}\s*</div>\s*</div>\s*\)\}', '', app)

# 8. Fix Status Bar IP and Ping
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

# 9. Fix Subtitle Sidebar Controls
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


with open('src/App.jsx', 'w') as f:
    f.write(app)
