import re
import json
from pathlib import Path

text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
lines = [line.rstrip() for line in text.splitlines()]

# Extract weekly tasks
week_tasks = {}
in_tasks = False
for line in lines:
    if 'Weekly Tasks' in line:
        in_tasks = True
        continue
    if in_tasks:
        if not line.strip():
            continue
        if line.strip().startswith('Week '):
            parts = line.strip().split(None, 2)
            if len(parts) >= 3:
                try:
                    week_num = int(parts[1])
                    task = parts[2]
                    week_tasks[week_num] = task
                    continue
                except ValueError:
                    pass
        # stop when we hit non task lines (like 'This program ...')
        if line.strip().startswith('This program'):
            break

content = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
# Replace fancy quotes/characters
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
    content = content.replace(src, dst)

# Regex to find all week/day sections
pattern = re.compile(r'(Week\s+(\d+)\s*/\s*Day\s+(\d+)\s*/\s*[^\n]+)')
matches = list(pattern.finditer(content))

weeks = {}
for idx, match in enumerate(matches):
    header = match.group(1)
    week_num = int(match.group(2))
    day_num = int(match.group(3))
    start = match.end()
    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
    section = content[start:end]
    # Determine day title from header
    title = header.split('/')[-1].strip()

    if week_num not in weeks:
        weeks[week_num] = {'week': week_num, 'task': week_tasks.get(week_num, ''), 'days': []}

    # Extract cardio
    cardio_match = re.search(r'Cardio:\s*([^\n]+)', section)
    cardio = cardio_match.group(1).strip() if cardio_match else ''

    # Extract exercise portion before first Cardio
    exercise_text = section.split('Cardio:')[0]
    # Remove table header
    exercise_text = exercise_text.replace('Exercise Set Reps Rest Notes', ' ')
    exercise_text = exercise_text.replace('Exercise Set Reps Rest', ' ')
    exercise_lines = [line.strip() for line in exercise_text.splitlines()]

    exercises = []
    buffer = ''
    for line in exercise_lines:
        if not line:
            continue
        if line.startswith('Week '):
            continue
        candidate = (buffer + ' ' + line).strip()
        candidate = re.sub(r'\s+', ' ', candidate)
        m = re.match(r'(.+?)\s+(\d+)\s+([0-9A-Za-z\-/]+)\s+(.+)', candidate)
        if m:
            name = m.group(1).strip()
            sets = m.group(2).strip()
            reps = m.group(3).strip()
            rest_and_notes = m.group(4).strip()
            # heuristically split rest and notes
            rest_match = re.match(r'([0-9A-Za-z\-/+ ]*(?:seconds|second|min|minutes|Failure|failure|AM|PM|per side|per muscle|only|no rest|Rest|None|N/A|Cardio)[A-Za-z0-9 \-/+]*)\s*(.*)', rest_and_notes)
            if rest_match:
                rest = rest_match.group(1).strip()
                notes = rest_match.group(2).strip()
            else:
                rest = ''
                notes = rest_and_notes
            exercises.append({
                'name': name,
                'sets': sets,
                'reps': reps,
                'rest': rest,
                'notes': notes
            })
            buffer = ''
        else:
            buffer = candidate

    weeks[week_num]['days'].append({
        'day': len(weeks[week_num]['days']) + 1,
        'title': title,
        'cardio': cardio,
        'exercises': exercises
    })

week_list = [weeks[num] for num in sorted(weeks.keys())]
Path('.devtools/gethin_data.json').write_text(json.dumps(week_list, indent=2), encoding='utf-8')
print('Parsed weeks:', len(week_list))
