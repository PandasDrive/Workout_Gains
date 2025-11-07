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
raw_text = raw_text.replace('Exercise Set Reps Rest Notes', '\nExercise Set Reps Rest Notes')
raw_text = raw_text.replace('Exercise Set Reps Rest', '\nExercise Set Reps Rest')
raw_text = raw_text.replace('Cardio:', '\nCardio:')
raw_text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', raw_text)
raw_text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', raw_text)
raw_text = re.sub(r'(\d+-\d+)(\d+-\d+)', r'\1 \2', raw_text)

week_tasks = {}
task_section = raw_text.split('Weekly Tasks', 1)[-1]
current_week = None
for line in task_section.splitlines():
    stripped = line.strip()
    if not stripped:
        continue
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

line_pattern = re.compile(r'(.+?)\s+(\d+)\s+([0-9A-Za-z-/]+)\s+(.+)')
rest_pattern = re.compile(r'([0-9A-Za-z +/().,-]*?(?:seconds?|minutes?|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A))(.*)', re.IGNORECASE)


def parse_block(block):
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    exercises = []
    current = None
    pending = ''
    for idx, line in enumerate(lines):
        has_digits = bool(re.search(r'\d+\s+[0-9A-Za-z-/]+', line))
        if has_digits:
            if pending:
                line = pending + ' ' + line
                pending = ''
            line = re.sub(r'([A-Za-z])(\d)', r'\1 \2', line)
            line = re.sub(r'(\d)([A-Za-z])', r'\1 \2', line)
            m = line_pattern.match(line)
            if not m:
                continue
            name = m.group(1).strip()
            sets = m.group(2).strip()
            reps = m.group(3).strip()
            rest_notes = m.group(4).strip()
            rest = ''
            notes = ''
            rest_match = rest_pattern.match(rest_notes)
            if rest_match:
                rest = rest_match.group(1).strip()
                notes = rest_match.group(2).strip()
            else:
                rest = rest_notes
            current = {
                'name': name,
                'sets': sets,
                'reps': reps,
                'rest': rest,
                'notes': notes
            }
            exercises.append(current)
        else:
            next_line = ''
            for j in range(idx + 1, len(lines)):
                if lines[j].strip():
                    next_line = lines[j].strip()
                    break
            next_has_digits = bool(re.search(r'\d+\s+[0-9A-Za-z-/]+', next_line)) if next_line else False
            line_clean = line.strip()
            if next_has_digits and not line_clean.endswith(('.', '!', '?')) and not re.search(r'seconds?$', line_clean, re.IGNORECASE):
                pending = (pending + ' ' + line_clean).strip()
            elif next_has_digits and line_clean.endswith(':'):
                pending = (pending + ' ' + line_clean).strip()
            elif current is not None:
                current['notes'] = (current['notes'] + ' ' + line_clean).strip()
    return exercises

def process_week(week):
    week_marker = f'Week {week}\n'
    if week_marker not in raw_text:
        return None
    start = raw_text.index(week_marker)
    if week < 12:
        next_marker = raw_text.find(f'Week {week + 1}\n')
    else:
        next_marker = -1
    week_text = raw_text[start: next_marker if next_marker != -1 else len(raw_text)]

    day_headers = []
    for match in re.finditer(rf'Week {week} / Day (\d+) / ([^\n]+)', week_text):
        day_num = int(match.group(1))
        title = match.group(2).strip().replace('Exercise Set Reps Rest Notes', '').strip()
        day_headers.append({'day': day_num, 'title': title})

    cardio_entries = [m.strip() for m in re.findall(r'Cardio:\s*([^\n]+)', week_text)]
    exercise_blocks = []
    for match in re.finditer('Exercise Set Reps Rest Notes', week_text):
        start_block = match.end()
        next_cardio = week_text.find('Cardio:', start_block)
        if next_cardio == -1:
            continue
        block_text = week_text[start_block:next_cardio].strip()
        if block_text:
            exercise_blocks.append(block_text)

    day_headers.sort(key=lambda d: d['day'])
    days = []
    exercise_idx = 0
    cardio_idx = 0
    for header in day_headers:
        cardio = cardio_entries[cardio_idx].strip() if cardio_idx < len(cardio_entries) else ''
        cardio_idx += 1
        exercises = []
        if exercise_idx < len(exercise_blocks):
            exercises = parse_block(exercise_blocks[exercise_idx])
            exercise_idx += 1
        days.append({
            'day': header['day'],
            'title': header['title'],
            'cardio': cardio,
            'exercises': exercises
        })
    return {
        'week': week,
        'task': week_tasks.get(week, ''),
        'days': days
    }

weeks = []
for week in range(1, 13):
    week_info = process_week(week)
    if week_info:
        weeks.append(week_info)

Path('.devtools/gethin_data.json').write_text(json.dumps(weeks, ensure_ascii=False, indent=2), encoding='utf-8')
print('Weeks parsed:', len(weeks))
