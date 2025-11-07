import json
from pathlib import Path
nippard_json = Path('.devtools/nippard_data.json').read_text(encoding='utf-8')
weeks = json.loads(nippard_json)
js_literal = json.dumps(weeks, indent=2)
Path('.devtools/nippard_weeks_js.txt').write_text(js_literal, encoding='utf-8')
