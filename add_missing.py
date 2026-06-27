import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

# 1. Add Transcoding button and Status to Movie File section
movie_file_section = """                 <div className="file-meta">
                   <span className={media ? "success-text" : "muted-text"}>{media ? "File loaded" : "No file"}</span>
                   <span className="muted-text">{media ? formatBytes(media.size) : '0 GB'}</span>
                 </div>
                 {shouldOfferPhoneMp4 && (
                   <button className="button primary mt-2" onClick={makePhoneSafeMp4} style={{fontSize: '12px', padding: '4px 8px'}}>
                     Convert to phone safe MP4
                   </button>
                 )}
                 {transcodeStatus && (
                   <div className="transcode-status mt-2" style={{fontSize: '12px', color: 'var(--accent)'}}>
                     {transcodeStatus.message}
                   </div>
                 )}"""
app = re.sub(r'<div className="file-meta">[\s\S]*?</div>', movie_file_section, app)


# 2. Add Voice Blocked Overlay and Media Error Overlay to Video Container
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
              <button className="unlock-overlay" onClick={unlockRemoteVoice} style={{background: 'rgba(5, 213, 154, 0.9)', color: '#000', top: '20px', bottom: 'auto', height: 'auto', padding: '10px 20px'}}>
                <Mic size={22} /> Click to hear voice chat
              </button>
            )}"""
app = re.sub(r'\{media && \(\!playbackUnlocked \|\| pendingAutoplay\) && \([\s\S]*?</button>\n\s*\)\}', overlays, app)

# 3. Add App Status Text to Top Bar (beside Share Link)
topbar_center = """        <div className="topbar-center">
          <div className="room-badge">
            <span className="room-label">Room:</span>
            <span className="room-id">{roomId}</span>
            <button onClick={copyShareLink} className="copy-btn"><Copy size={14}/></button>
          </div>
          <button className="share-btn" onClick={copyShareLink}>
            <Link2 size={14} /> Share Link
          </button>
          {status && <span className="status-toast" style={{marginLeft: '12px', fontSize: '13px', color: 'var(--text-muted)'}}>{status}</span>}
        </div>"""
app = re.sub(r'<div className="topbar-center">[\s\S]*?</button>\n\s*</div>', topbar_center, app)

# 4. Connect Subtitle Position
# First, update subtitle layer styles
subtitle_layer = """            {media && (
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
app = re.sub(r'\{media && \(\n\s*<div className="subtitle-layer" style=\{\{.*?borderRadius: subtitleSettings\.bg \? \'12px\' : \'0\',\n\s*\}\}>', subtitle_layer, app, flags=re.DOTALL)

# Then connect the position select
pos_select = """                <div className="input-group">
                  <label>Position</label>
                  <select className="lan-select w-full" value={subtitleSettings.position || 'bottom'} onChange={(e) => updateSubtitleSettings({position: e.target.value})}>
                    <option value="bottom">Bottom Center</option>
                    <option value="top">Top Center</option>
                  </select>
                </div>"""
app = re.sub(r'<div className="input-group">\n\s*<label>Position</label>\n\s*<select className="lan-select w-full">\n\s*<option>Bottom Center</option>\n\s*</select>\n\s*</div>', pos_select, app)

with open('src/App.jsx', 'w') as f:
    f.write(app)
