import re

with open('src/styles.css', 'r') as f:
    css = f.read()

# Refine root and colors
css = re.sub(
    r':root \{.*?\n\}',
    ''':root {
  color-scheme: dark;
  --bg: #030303;
  --panel: rgba(20, 20, 20, 0.35);
  --panel-2: rgba(30, 30, 30, 0.4);
  --line: rgba(255, 255, 255, 0.1);
  --text: #ffffff;
  --muted: #a1a1aa;
  --soft: rgba(255, 255, 255, 0.04);
  --accent: #8b5cf6;
  --accent-2: #ec4899;
  --danger: #f43f5e;
  --glass: rgba(17, 17, 17, 0.5);
  --glass-strong: rgba(10, 10, 10, 0.75);
  --glass-line: rgba(255, 255, 255, 0.08);
  --glass-highlight: rgba(255, 255, 255, 0.03);
  --shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
  font-family: "Outfit", "Inter", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}''',
    css,
    flags=re.DOTALL
)

css = re.sub(
    r'body \{[^}]*background-image:[^}]*\}',
    '''body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background-color: #000;
  background-image: 
    radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.25), transparent 50%),
    radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.2), transparent 50%),
    radial-gradient(circle at 50% 80%, rgba(56, 182, 212, 0.15), transparent 50%);
  background-attachment: fixed;
}''',
    css
)

css = re.sub(
    r'\.transport,\s*\.status-strip,\s*\.panel-section \{[^}]*\}',
    '''.transport,
.status-strip,
.panel-section {
  border: 1px solid var(--glass-line);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(30, 30, 30, 0.4), rgba(15, 15, 15, 0.4));
  backdrop-filter: blur(40px) saturate(150%);
  -webkit-backdrop-filter: blur(40px) saturate(150%);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.06), 0 20px 40px rgba(0, 0, 0, 0.4);
}''',
    css
)

css = re.sub(
    r'\.icon-button,\s*\.play-button,\s*\.button,\s*\.input-action button,\s*\.segmented button,\s*\.share-box \{[^}]*\}',
    '''.icon-button,
.play-button,
.button,
.input-action button,
.segmented button,
.share-box {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
  color: var(--text);
  cursor: pointer;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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
  border-color: rgba(255, 255, 255, 0.2);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}''',
    css
)

css = re.sub(
    r'\.button\.primary \{[^}]*\}',
    '''.button.primary {
  border: none;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #fff;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(236, 72, 153, 0.4);
}''',
    css
)

css = re.sub(
    r'input\[type="range"\]::-webkit-slider-thumb \{[^}]*\}',
    '''input[type="range"]::-webkit-slider-thumb {
  width: 20px;
  height: 20px;
  margin-top: -7px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 12px var(--accent);
  -webkit-appearance: none;
  transition: transform 0.2s;
}''',
    css
)

# Overwrite css
with open('src/styles.css', 'w') as f:
    f.write(css)

