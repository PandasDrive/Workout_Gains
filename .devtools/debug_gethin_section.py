import re
from pathlib import Path

content = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
content = content.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2014', '-').replace('\u2013', '-').replace('\u00a0', ' ').replace('\u00b0', ' deg')
pattern = re.compile(r'(Week\s+(\d+)\s*/\s*Day\s+(\d+)\s*/\s*[^\n]+)')
matches = list(pattern.finditer(content))
print('matches', len(matches))
first = matches[0]
second = matches[1]
print(content[first.end():second.start()][:500])
