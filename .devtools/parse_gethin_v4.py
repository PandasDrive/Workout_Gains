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

# Extract weekly tasks
week_tasks = {}
task_section = raw_text.split('Weekly Tasks', 1)[-1]
current_week = None
for line in task_section.splitlines():
    stripped = line.strip()
    if not stripped:
        continue
    if '/ Day' in stripped:
        break
    if stripped.startswith('Week '):
        parts = stripped.split(None, 2)
        if len(parts) >= 3 and parts[1].isdigit():
            current_week = int(parts[1])
            week_tasks[current_week] = parts[2]
        elif len(parts) >= 2 and parts[1].isdigit():
            current_week = int(parts[1])
            week_tasks[current_week] = ''
        else:
            current_week = None
    elif current_week is not None:
        week_tasks[current_week] = (week_tasks[current_week] + ' ' + stripped).strip()

pattern = re.compile(r'Week\s+(\d+)\s*/\s*Day\s+(\d+)\s*/\s*([^\n]+)')
matches = list(pattern.finditer(raw_text))

weeks = {}

ex_start_pattern = re.compile(r'.*\d+\s+[0-9A-Za-z-/]+\s+')
line_pattern = re.compile(r'^(.*?)(\d+)\s+([0-9A-Za-z-/]+)\s+(.+)$')
rest_split_pattern = re.compile(r'([0-9A-Za-z +/().,-]*?(?:seconds|min|minutes|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A))(.*)', re.IGNORECASE)

for idx, match in enumerate(matches):
    week_num = int(match.group(1))
    raw_day_num = int(match.group(2))
    title = match.group(3).strip()
    title = title.replace('Exercise Set Reps Rest Notes', '').replace('Exercise Set Reps Rest', '').strip()
    day_num = ((raw_day_num - 1) % 7) + 1

    start = match.end()
    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
    section = raw_text[start:end]

    cardio_match = re.search(r'Cardio:\s*([^\n]+)', section)
    cardio = cardio_match.group(1).strip() if cardio_match else ''

    lines = [line.rstrip() for line in section.splitlines()]
    exercises = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('Cardio:'):
            i += 1
            continue
        combined = line
        j = i
        while not ex_start_pattern.match(combined) and j + 1 < len(lines):
            j += 1
            combined = (combined + ' ' + lines[j].strip()).strip()
        m_line = line_pattern.match(combined)
        if not m_line:
            i = j + 1
            continue
        name = m_line.group(1).strip()
        sets = m_line.group(2).strip()
        reps = m_line.group(3).strip()
        rest_notes = m_line.group(4).strip()
        rest_match = rest_split_pattern.match(rest_notes)
        if rest_match:
            rest = rest_match.group(1).strip()
            notes = rest_match.group(2).strip()
        else:
            rest = rest_notes
            notes = ''

        note_lines = []
        k = j + 1
        while k < len(lines):
            note_line = lines[k].strip()
            if not note_line:
                k += 1
                continue
            if note_line.startswith('Cardio:') or ex_start_pattern.match(note_line):
                break
            note_lines.append(note_line)
            k += 1
        if note_lines:
            notes = (notes + ' ' + ' '.join(note_lines)).strip()
        exercises.append({
            'name': name,
            'sets': sets,
            'reps': reps,
            'rest': rest,
            'notes': notes
        })
        i = k

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
    days = sorted(weeks[week_num]['days'], key=lambda d: d['day'])
    for day in days:
        day['cardio'] = day['cardio'] or ''
    if len(days) < 7:
        # pad missing days with placeholders
        existing = {d['day'] for d in days}
        for dnum in range(1, 8):
            if dnum not in existing:
                days.append({'day': dnum, 'title': f'Day {dnum}', 'cardio': '', 'exercises': []})
        days.sort(key=lambda d: d['day'])
    weeks[week_num]['days'] = days
    week_list.append(weeks[week_num])

Path('.devtools/gethin_data.json').write_text(json.dumps(week_list, ensure_ascii=False, indent=2), encoding='utf-8')
print('Weeks parsed:', len(week_list))
