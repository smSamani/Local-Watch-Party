with open('src/styles.css', 'a') as f:
    f.write('''
/* Waveform Animation */
@keyframes duck-bar {
  0% { transform: scaleY(0.7); opacity: 0.8; }
  100% { transform: scaleY(1.3); opacity: 1; }
}
.fake-waveform.animating .bar {
  animation: duck-bar 0.4s infinite alternate ease-in-out;
}
.fake-waveform.animating .bar:nth-child(even) {
  animation-duration: 0.5s;
  animation-delay: 0.1s;
}
.fake-waveform.animating .bar:nth-child(3n) {
  animation-duration: 0.35s;
  animation-delay: 0.2s;
}

/* Background Checkbox Fixes */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 13px;
  user-select: none;
}
.checkbox-label input {
  display: none;
}
.check-box {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  border: 1px solid var(--border);
  transition: all 0.2s;
}
.checkbox-label:hover .check-box {
  border-color: var(--text-muted);
}
''')
