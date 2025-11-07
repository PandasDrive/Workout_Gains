import re
from pathlib import Path
text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
week1_start = text.index('Week 1\n')
week2_start = text.index('Week 2\n')
week1_text = text[week1_start:week2_start]
print('day headers', re.findall(r'Week 1 / Day (\d+) / ([^\n]+)', week1_text))
print('exercise headers', len(re.findall(r'Exercise Set Reps Rest', week1_text)))
