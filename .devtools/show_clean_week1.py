import re
from pathlib import Path
text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
for src, dst in {"\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2014": '-', "\u2013": '-', "\u00a0": ' ', "\u00b0": ' deg'}.items():
    text = text.replace(src, dst)
text = text.replace('Exercise Set Reps Rest Notes', '\nExercise Set Reps Rest Notes')
text = text.replace('Exercise Set Reps Rest', '\nExercise Set Reps Rest')
text = text.replace('Cardio:', '\nCardio:')
text = re.sub(r'(Week \d+ / Day \d+ / [^\n]+)(\nExercise Set Reps Rest Notes)', r'\1\2', text)
week1_start = text.index('Week 1\n')
week1_end = text.index('Week 2\n')
print(text[week1_start:week1_end])
