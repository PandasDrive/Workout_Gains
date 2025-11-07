from pathlib import Path
content = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
print(content[content.find('Week 1 / Day 1'):content.find('Cardio: 20 minutes AM')+60])
