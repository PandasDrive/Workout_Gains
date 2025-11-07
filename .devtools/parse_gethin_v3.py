import re
import json
from pathlib import Path

raw_text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
replacements = {
    '\u2019': "'",
    '\u201c': '"',
    '\u201d': '"',
    '\u2014': '-',
    '\u2013': '-',
    '\u00a0': ' ',
    '\u00b0': ' deg'
}
for src, dst in replacements.items():
    raw_text = raw_text.replace(src, dst)

# Weekly tasks
week_tasks = {}
task_section = raw_text.split('Weekly Tasks', 1)[-1]
for line in task_section.splitlines():
    line = line.strip()
    if line.startswith('Week '):
        parts = line.split(None, 2)
        if len(parts) >= 3 and parts[1].isdigit():
            week_tasks[int(parts[1])] = parts[2]

pattern = re.compile(r'Week\s+(\d+)\s*/\s*Day\s+(\d+)\s*/\s*([^\n]+)')
matches = list(pattern.finditer(raw_text))

weeks = {}

for idx, match in enumerate(matches):
    week_num = int(match.group(1))
    day_num = int(match.group(2))
    title = match.group(3).strip()
    title = title.replace('Exercise Set Reps Rest Notes', '').replace('Exercise Set Reps Rest', '').strip()
    start = match.end()
    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
    section = raw_text[start:end]

    cardio = ''
    cardio_match = re.search(r'Cardio:\s*([^\n]+)', section)
    if cardio_match:
        cardio = cardio_match.group(1).strip()

    exercise_text = section.split('Cardio:')[0]
    exercise_text = exercise_text.replace('\n', ' ')
    exercise_text = re.sub(r'\s+', ' ', exercise_text)
    exercise_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', exercise_text)
    exercise_text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', exercise_text)
    exercise_text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', exercise_text)

    exercises = []
    ex_pattern = re.compile(r'''(
        [A-Za-z0-9&.,()/"' -]+?
    )\s+(\d+)\s+([0-9A-Za-z-/]+)\s+([0-9A-Za-z+/().,'" -]*?(?:seconds|min|minutes|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A|cardio|Cardio))''', re.IGNORECASE | re.VERBOSE)

    pos = 0
    while True:
        match_ex = ex_pattern.search(exercise_text, pos)
        if not match_ex:
            break
        name = match_ex.group(1).strip()
        sets = match_ex.group(2).strip()
        reps = match_ex.group(3).strip()
        rest = match_ex.group(4).strip()
        pos = match_ex.end()
        next_match = ex_pattern.search(exercise_text, pos)
        notes = exercise_text[pos:next_match.start()].strip() if next_match else exercise_text[pos:].strip()
        if notes.lower().startswith('cardio'):
            notes = ''
        exercises.append({
            'name': name,
            'sets': sets,
            'reps': reps,
            'rest': rest,
            'notes': notes
        })
    if week_num not in weeks:
        weeks[week_num] = {
            'week': week_num,
            'task': week_tasks.get(week_num, ''),
            'days': []
        }
    weeks[week_num]['days'].append({
        'day': day_num,
        'title': title,
        'cardio': cardio,
        'exercises': exercises
    })

week_list = []
for week_num in sorted(weeks.keys()):
    days_sorted = sorted(weeks[week_num]['days'], key=lambda x: x['day'])
    for d in days_sorted:
        d['cardio'] = d['cardio'] or ''
    weeks[week_num]['days'] = days_sorted
    week_list.append(weeks[week_num])

Path('.devtools/gethin_data.json').write_text(json.dumps(week_list, ensure_ascii=False, indent=2), encoding='utf-8')
print('Weeks parsed:', len(week_list))
