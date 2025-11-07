from pathlib import Path
js_path = Path('data/program-data.js')
content = js_path.read_text(encoding='utf-8')
weeks_lines = Path('.devtools/nippard_weeks_js.txt').read_text(encoding='utf-8').splitlines()
formatted_lines = []
if weeks_lines:
    formatted_lines.append('    weeks: ' + weeks_lines[0])
    formatted_lines.extend('    ' + line for line in weeks_lines[1:])
replacement = '\n'.join(formatted_lines)
content = content.replace('    weeks: []', replacement, 1)
js_path.write_text(content, encoding='utf-8')
