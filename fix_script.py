import re

with open('src/App.jsx', 'r') as f:
    app = f.read()

with open('build_lan_cinema.py', 'r') as f:
    script = f.read()

# Instead of re.sub, we'll do string replacement to avoid escape issues
script = script.replace("app = re.sub(r'  return \([\\s\\S]*\}\);?\\n?\}', return_block, app)", """
start_idx = app.find('  return (')
if start_idx != -1:
    app = app[:start_idx] + return_block
""")

with open('build_lan_cinema.py', 'w') as f:
    f.write(script)
