import re

def rebuild_app():
    with open('src/App.jsx', 'r') as f:
        app = f.read()

    # Extract the contents of the sections
    media_setup = re.search(r'<section className="panel-section">\s*<div className="section-title">\s*<Settings2 size=\{18\} />\s*<h2>Media setup</h2>\s*</div>(.*?)<div className="hint">.*?</div>\s*</section>', app, re.DOTALL)
    
    subtitles = re.search(r'<section className="panel-section">\s*<div className="section-title">\s*<Captions size=\{18\} />\s*<h2>Subtitles</h2>\s*</div>(.*?)</div>\s*</section>', app, re.DOTALL)
    
    people = re.search(r'<section className="panel-section people-panel">\s*<div className="section-title">\s*<Users size=\{18\} />\s*<h2>People</h2>\s*</div>(.*?)</div>\s*</section>', app, re.DOTALL)
    
    status = re.search(r'<div className="status-strip">(.*?)</div>', app, re.DOTALL)

    # Rebuild the workspace
    workspace = f'''
      <section className="workspace">
        <div className="player-section">
          <div className="movie-title-bar">
            <span>{{displayMediaName}}</span>
          </div>
          <div
            className={{`screen ${{showChrome ? "chrome-visible" : "chrome-hidden"}}`}}
            ref={{screenRef}}
            onPointerMove={{() => showPlayerChrome()}}
            onPointerUp={{handleScreenPointerUp}}
          >
            <video
              ref={{videoRef}}
              src={{streamUrl}}
              playsInline
              preload="metadata"
              onLoadedMetadata={{onVideoLoaded}}
              onPlay={{() => setIsPlaying(true)}}
              onPause={{() => setIsPlaying(false)}}
              onCanPlay={{() => setMediaError("")}}
              onError={{() => {{
                if (!media) return;
                setIsPlaying(false);
                setMediaError("This browser could not play this file. MP4 with H.264/AAC is the safest format; MKV/HEVC often fails on phones and browsers.");
              }}}}
              onEnded={{() => emitPlayback({{ playing: false, currentTime: duration }})}}
            />
            {{media && theaterMode && (
              <div className="theater-movie-title chrome-item">{{displayMediaName}}</div>
            )}}
            {{!media && (
              <div className="empty-state">
                <MonitorPlay size={{44}} />
                <h2>Choose a movie file first</h2>
                <p>This laptop serves the movie with byte-range streaming. Your friend only needs the room link.</p>
              </div>
            )}}
            {{media && (
              <div className="subtitle-layer" style={{{{ "--subtitle-size": `${{subtitleSettings.size}}px`, "--subtitle-gap": `${{subtitleSettings.gap}}px` }}}}>
                {{(subtitleSettings.mode === "both" || subtitleSettings.mode === "fa") && faCue && (
                  <div className="subtitle-line subtitle-fa" dir="rtl">{{faCue.text}}</div>
                )}}
                {{(subtitleSettings.mode === "both" || subtitleSettings.mode === "en") && enCue && (
                  <div className="subtitle-line subtitle-en">{{enCue.text}}</div>
                )}}
              </div>
            )}}
            {{media && theaterMode && (
              <div className="tap-zones" aria-hidden="true">
                <div className="tap-zone left"><RotateCcw size={{34}} /><span>{{SEEK_BACK_SECONDS}}</span></div>
                <div className="tap-zone center">{{isPlaying ? <Pause size={{38}} /> : <Play size={{38}} />}}</div>
                <div className="tap-zone right"><RotateCw size={{34}} /><span>{{SEEK_FORWARD_SECONDS}}</span></div>
              </div>
            )}}
            {{seekFlash && (
              <div className={{`seek-flash ${{seekFlash.direction}}`}}>
                {{seekFlash.direction === "forward" ? "+" : "-"}}{{seekFlash.seconds}}s
              </div>
            )}}
            {{media && (!playbackUnlocked || pendingAutoplay) && (
              <button className="unlock-overlay" onClick={{unlockPlayback}}>
                <Play size={{22}} />
                Enable playback on this device
              </button>
            )}}
            {{media && mediaError && (
              <div className="media-error">
                <span>{{mediaError}}</span>
                <a href={{streamUrl}} target="_blank" rel="noreferrer">Open raw stream</a>
              </div>
            )}}
            <div className={{`ducking-indicator chrome-item ${{anyoneSpeaking && adaptiveDucking ? "active" : ""}}`}}>
              <Gauge size={{15}} />
              {{anyoneSpeaking && adaptiveDucking ? "Adaptive ducking" : "Cinema audio"}}
            </div>
            {{theaterMode && speakerToast.entries.length > 0 && (
              <div className={{`speaker-toast ${{speakerToast.exiting ? "exiting" : ""}}`}}>
                {{speakerToast.entries.map((speaker) => (
                  <div className="speaker-toast-row" key={{speaker.id}} style={{{{ "--level": levelPercent(speaker.level) }}}}>
                    <span className="avatar small">{{initials(speaker.name)}}</span>
                    <span>{{speaker.self ? "You" : speaker.name}}</span>
                    <span className="wave-bars" aria-hidden="true">
                      <i /><i /><i /><i />
                    </span>
                  </div>
                ))}}
              </div>
            )}}
            {{theaterMode && (
              <button className="theater-close chrome-item" onClick={{toggleTheaterMode}} title="Exit theater mode">
                <X size={{20}} />
              </button>
            )}}
          </div>

          <div className={{`transport ${{showChrome ? "chrome-visible" : "chrome-hidden"}}`}}>
            <div className="scrub-row">
              <span>{{formatTime(currentTime)}}</span>
              <input
                type="range"
                min="0"
                max={{duration || 0}}
                value={{Math.min(currentTime, duration || currentTime)}}
                step="0.05"
                onChange={{(event) => seekTo(Number(event.target.value))}}
                disabled={{!media}}
              />
              <span>{{formatTime(duration)}}</span>
            </div>
            <div className="control-row">
              <button className="icon-button seek-button" onClick={{() => seekBy(-SEEK_BACK_SECONDS)}} disabled={{!media}} title={{`${{SEEK_BACK_SECONDS}} seconds back`}}>
                <RotateCcw size={{21}} />
                <span>{{SEEK_BACK_SECONDS}}</span>
              </button>
              <button className="play-button" onClick={{togglePlay}} disabled={{!media}} title="Play / Pause">
                {{isPlaying ? <Pause size={{26}} /> : <Play size={{26}} />}}
              </button>
              <button className="icon-button seek-button" onClick={{() => seekBy(SEEK_FORWARD_SECONDS)}} disabled={{!media}} title={{`${{SEEK_FORWARD_SECONDS}} seconds forward`}}>
                <RotateCw size={{21}} />
                <span>{{SEEK_FORWARD_SECONDS}}</span>
              </button>
              <div className="divider" />
              <button className={{`icon-button ${{videoMuted ? "muted" : ""}}`}} onClick={{() => setVideoMuted((value) => !value)}} disabled={{!media}} title="Mute movie audio">
                {{videoMuted ? <VolumeX size={{19}} /> : <Volume2 size={{19}} />}}
              </button>
              <input
                className="short-range"
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={{userVolume}}
                onChange={{(event) => setUserVolume(Number(event.target.value))}}
              />
              <select onChange={{(event) => setRate(Number(event.target.value))}} value={{videoRef.current?.playbackRate || 1}} disabled={{!media}}>
                <option value="0.75">0.75x</option>
                <option value="1">1x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
              </select>
              <button className={{`icon-button ${{theaterMode ? "active" : ""}}`}} onClick={{toggleTheaterMode}} disabled={{!media}} title="Theater fullscreen">
                {{theaterMode ? <X size={{19}} /> : <Expand size={{19}} />}}
              </button>
              <button className={{`button mic ${{micEnabled ? "on" : ""}}`}} onClick={{toggleMic}}>
                {{micEnabled ? <Mic size={{17}} /> : <MicOff size={{17}} />}}
                {{micEnabled ? "Mic on" : "Mic off"}}
              </button>
              <button className={{`icon-button ${{voiceOutputEnabled ? "" : "muted"}}`}} onClick={{toggleVoiceOutput}} title="Remote voice audio">
                {{voiceOutputEnabled ? <Volume2 size={{19}} /> : <VolumeX size={{19}} />}}
              </button>
              {{voiceBlocked && (
                <button className="button" onClick={{unlockRemoteVoice}}>
                  Enable voice audio
                </button>
              )}}
            </div>
          </div>
        </div>

        <div className="cards-grid">
          <section className="panel-card card-yellow">
            <div className="card-header">
              <Captions size={{28}} className="icon-yellow" />
              <div>
                <h2>Subtitles</h2>
                <p>FA+EN, Timing, Size</p>
              </div>
            </div>
            {subtitles.group(1)}
          </section>

          <section className="panel-card card-green">
            <div className="card-header">
              <Users size={{28}} className="icon-green" />
              <div>
                <h2>People & Voice</h2>
                <p>Voice, Mic, Volume</p>
              </div>
            </div>
            {people.group(1)}
          </section>

          <section className="panel-card card-blue">
            <div className="card-header">
              <MonitorPlay size={{28}} className="icon-blue" />
              <div>
                <h2>Media Setup</h2>
                <p>Local File, MP4 Build</p>
              </div>
            </div>
            {media_setup.group(1)}
          </section>

          <section className="panel-card card-red">
            <div className="card-header">
              <Settings2 size={{28}} className="icon-red" />
              <div>
                <h2>Network & Status</h2>
                <p>Socket, Network, Sync</p>
              </div>
            </div>
            <div className="status-strip-vertical">
              {status.group(1)}
            </div>
          </section>
        </div>
      </section>
'''
    
    # Replace the old workspace with the new workspace
    new_app = re.sub(r'<section className="workspace">.*?</aside>\s*</section>', workspace, app, flags=re.DOTALL)
    
    with open('src/App.jsx', 'w') as f:
        f.write(new_app)

def rebuild_styles():
    with open('src/styles.css', 'r') as f:
        css = f.read()

    new_root = '''
:root {
  color-scheme: dark;
  --bg: #0B0B0B;
  --panel: rgba(26, 26, 26, 0.4);
  --panel-red: rgba(48, 21, 26, 0.4);
  --line: rgba(255, 255, 255, 0.08);
  --line-red: rgba(248, 113, 113, 0.15);
  --text: #F3F4F6;
  --muted: #9CA3AF;
  
  --accent-yellow: #FACC15;
  --accent-green: #4ADE80;
  --accent-blue: #60A5FA;
  --accent-red: #F87171;
  --accent: #60A5FA; /* default to blue for standard accents */
  --accent-2: #3B82F6;
  --danger: #EF4444;
  
  --glass: rgba(26, 26, 26, 0.4);
  --glass-strong: rgba(15, 15, 15, 0.7);
  --glass-line: rgba(255, 255, 255, 0.08);
  --glass-highlight: rgba(255, 255, 255, 0.03);
  --shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
  
  --radius-xl: 24px;
  --radius-lg: 16px;
  --radius-md: 10px;
  
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background-color: var(--bg);
  background-image: none;
}
'''
    
    css = re.sub(r':root \{.*?\}\s*body \{.*?\}', new_root, css, flags=re.DOTALL)
    
    # Redefine workspace and layout
    layout_css = '''
.workspace {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1540px;
  margin: 0 auto;
}

.player-section {
  width: 100%;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 20px;
}

.panel-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(24px) saturate(1.2);
  -webkit-backdrop-filter: blur(24px) saturate(1.2);
  transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s;
}

.panel-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.panel-card.card-red {
  background: var(--panel-red);
  border-color: var(--line-red);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.card-header h2 {
  font-size: 19px;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.card-header p {
  font-size: 13px;
  color: var(--muted);
  margin: 2px 0 0;
}

.icon-yellow { color: var(--accent-yellow); }
.icon-green { color: var(--accent-green); }
.icon-blue { color: var(--accent-blue); }
.icon-red { color: var(--accent-red); }

.status-strip-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 14px;
  color: var(--text);
}
'''
    
    css = re.sub(r'\.workspace \{.*?\}', layout_css, css, flags=re.DOTALL)
    
    # Remove old .player-column and .side-panel classes
    css = re.sub(r'\.player-column,\s*\.side-panel \{.*?\}', '', css, flags=re.DOTALL)
    css = re.sub(r'\.side-panel \{.*?\}', '', css, flags=re.DOTALL)
    
    # Re-style transport
    css = re.sub(r'\.transport,\s*\.status-strip,\s*\.panel-section \{.*?\}', 
                 '''.transport { border: 1px solid var(--line); border-radius: var(--radius-lg); background: var(--panel); backdrop-filter: blur(24px); box-shadow: var(--shadow); margin-top: 16px; padding: 14px 18px; }''', css, flags=re.DOTALL)
    
    # Update status strip styles to work vertically
    css = re.sub(r'\.status-strip \{.*?\}', '', css, flags=re.DOTALL)
    
    with open('src/styles.css', 'w') as f:
        f.write(css)

rebuild_app()
rebuild_styles()
