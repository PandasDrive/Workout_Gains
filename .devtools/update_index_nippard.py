import json
from pathlib import Path

root = Path('index.html')
data_path = Path('.devtools/nippard_data.json')
weeks = json.loads(data_path.read_text(encoding='utf-8'))
weeks_json = json.dumps(weeks, ensure_ascii=False, indent=12)
indent = ' ' * 16
weeks_block = 'weeks: ' + weeks_json.replace('\n', '\n' + indent)
content = root.read_text(encoding='utf-8')
target = 'weeks: [] // We can add this data later'
if target not in content:
    raise SystemExit('Target string not found in index.html')
updated = content.replace(target, weeks_block)
root.write_text(updated, encoding='utf-8')
print('Updated index.html with Nippard data')
