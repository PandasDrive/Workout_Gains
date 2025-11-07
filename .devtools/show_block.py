import re
from pathlib import Path
raw_text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
raw_text = raw_text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2014', '-').replace('\u2013', '-').replace('\u00a0', ' ').replace('\u00b0', ' deg')
week1_start = raw_text.index('Week 1\n')
week2_start = raw_text.index('Week 2\n')
week1_text = raw_text[week1_start:week2_start]
block_pattern = re.compile(r'Exercise Set Reps Rest Notes(.*?)Cardio:', re.DOTALL)
blocks = block_pattern.findall(week1_text)
print('blocks', len(blocks))
for i, block in enumerate(blocks[:1], start=1):
    print('Block', i)
    print(block)
