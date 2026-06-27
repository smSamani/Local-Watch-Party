with open('top.js', 'r') as f:
    top_js = f.read()

with open('logic.js', 'r') as f:
    logic_js = f.read()

with open('bottom.js', 'r') as f:
    bottom_js = f.read()

with open('src/App.jsx', 'w') as f:
    f.write(top_js + '\n' + logic_js + '\n' + bottom_js)
