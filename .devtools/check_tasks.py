import re
from pathlib import Path
raw_text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
raw_text = raw_text.replace('\u2019', "'")
section = raw_text.split('Weekly Tasks', 1)[-1]
for line in section.splitlines():
    if line.strip().startswith('Week '):
        parts = line.strip().split(None, 2)
        print(parts)
