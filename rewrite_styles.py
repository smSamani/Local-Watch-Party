import re

with open('src/styles.css', 'r') as f:
    css = f.read()

# Replace root variables
css = re.sub(
    r':root \{.*?\n\}',
    ''':root {
  color-scheme: dark;
  --bg: #000000;
  --panel: #1c1c1e;
  --panel-2: #2c2c2e;
  --line: rgba(255, 255, 255, 0.1);
  --text: #f5f5f7;
  --muted: #ebebf599;
  --soft: rgba(255, 255, 255, 0.05);
  --accent: #0a84ff;
  --accent-2: #bf5af2;
  --danger: #ff453a;
  --glass: rgba(25, 25, 25, 0.45);
  --glass-strong: rgba(15, 15, 15, 0.65);
  --glass-line: rgba(255, 255, 255, 0.15);
  --glass-highlight: rgba(255, 255, 255, 0.1);
  --shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}''',
    css,
    flags=re.DOTALL
)

# Replace body background
css = re.sub(
    r'body \{[^}]*background:[^}]*\}',
    '''body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background-color: #000000;
  background-image:
    radial-gradient(circle at 10% 0%, rgba(10, 132, 255, 0.25) 0%, transparent 45%),
    radial-gradient(circle at 90% 90%, rgba(191, 90, 242, 0.2) 0%, transparent 45%),
    radial-gradient(circle at 50% 50%, rgba(10, 132, 255, 0.05) 0%, transparent 60%);
  background-attachment: fixed;
}''',
    css
)

# Replace welcome-layer background
css = re.sub(
    r'\.welcome-layer \{[^}]*background:[^}]*\}',
    '''.welcome-layer {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: 22px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}''',
    css
)

# Fix glass components
css = re.sub(
    r'\.welcome-card \{[^}]*\}',
    '''.welcome-card {
  display: grid;
  gap: 16px;
  width: min(420px, 100%);
  padding: 32px;
  border: 1px solid var(--glass-line);
  border-radius: 24px;
  background: var(--glass-strong);
  backdrop-filter: blur(40px) saturate(1.8);
  -webkit-backdrop-filter: blur(40px) saturate(1.8);
  box-shadow: inset 0 1px 1px var(--glass-highlight), var(--shadow);
}''',
    css
)

css = re.sub(
    r'\.transport,\s*\.status-strip,\s*\.panel-section \{[^}]*\}',
    '''.transport,
.status-strip,
.panel-section {
  border: 1px solid var(--glass-line);
  border-radius: 18px;
  background: var(--glass);
  backdrop-filter: blur(30px) saturate(1.5);
  -webkit-backdrop-filter: blur(30px) saturate(1.5);
  box-shadow: inset 0 1px 1px var(--glass-highlight), var(--shadow);
}''',
    css
)

# Replace buttons to look like Apple glass buttons
css = re.sub(
    r'\.icon-button,\s*\.play-button,\s*\.button,\s*\.input-action button,\s*\.segmented button,\s*\.share-box \{[^}]*\}',
    '''.icon-button,
.play-button,
.button,
.input-action button,
.segmented button,
.share-box {
  border: 1px solid var(--glass-line);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  cursor: pointer;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 2px 8px rgba(0, 0, 0, 0.1);
}''',
    css
)

css = re.sub(
    r'\.icon-button:hover,\s*\.play-button:hover,\s*\.button:hover,\s*\.input-action button:hover,\s*\.segmented button:hover,\s*\.share-box:hover \{[^}]*\}',
    '''.icon-button:hover,
.play-button:hover,
.button:hover,
.input-action button:hover,
.segmented button:hover,
.share-box:hover {
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1), 0 4px 12px rgba(0, 0, 0, 0.2);
}''',
    css
)

# Primary button
css = re.sub(
    r'\.button\.primary \{[^}]*\}',
    '''.button.primary {
  border: none;
  background: var(--text);
  color: #000;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(255, 255, 255, 0.25);
}''',
    css
)

css = css.replace(
    '.brand-mark {\n  display: grid;\n  place-items: center;\n  width: 42px;\n  height: 42px;\n  border: 1px solid rgba(66, 214, 173, 0.42);\n  border-radius: 8px;\n  background: linear-gradient(145deg, rgba(66, 214, 173, 0.2), rgba(85, 185, 255, 0.12));\n  color: var(--accent);\n}',
    '''.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  color: var(--text);
  backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
}'''
)

# Fix teal colors
css = css.replace('rgba(66, 214, 173, ', 'rgba(10, 132, 255, ')
css = css.replace('rgba(85, 185, 255, ', 'rgba(191, 90, 242, ')
css = css.replace('#42d6ad', '#0a84ff')
css = css.replace('#55b9ff', '#bf5af2')
css = css.replace('rgba(255, 102, 122, ', 'rgba(255, 69, 58, ')
css = css.replace('#ff667a', '#ff453a')

# Replace play button specifics
css = re.sub(
    r'\.play-button \{[^}]*\}',
    '''.play-button {
  display: grid;
  place-items: center;
  width: 52px;
  height: 44px;
  background: var(--text);
  color: #000;
  border: none;
  border-radius: 14px;
}''',
    css
)

css = css.replace('border: 2px solid #dffff7;', 'border: 2px solid #ffffff;')
css = css.replace('background: linear-gradient(135deg, #42d6ad, #55b9ff);', '') # handled by primary
css = css.replace('color: #04100f;', '')
css = css.replace('color: #04100d;', '')
css = css.replace('color: #dcefff;', 'color: #fff;')

with open('src/styles.css', 'w') as f:
    f.write(css)

