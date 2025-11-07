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

rest_split = re.compile(r'(.*?(?:seconds?|minutes?|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A))(.*)', re.IGNORECASE)

def parse_block(block):
    tokens = block.replace('\n', ' ').split()
    tokens = [t for t in tokens if t not in {'Exercise', 'Set', 'Reps', 'Rest', 'Notes'}]
    exercises = []
    i = 0
    while i < len(tokens):
        # Skip stray tokens
        while i < len(tokens) and not tokens[i].isdigit():
            # Ensure next token exists
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                break
            name_candidate = tokens[i]
            name_tokens = []
            while i < len(tokens) and not tokens[i].isdigit():
                name_tokens.append(tokens[i])
                i += 1
            break
        else:
            break
        name_tokens = []
        while i < len(tokens) and not tokens[i].isdigit():
            name_tokens.append(tokens[i])
            i += 1
        if i >= len(tokens):
            break
        name = ' '.join(name_tokens).strip()
        sets = tokens[i]
        i += 1
        if i >= len(tokens):
            break
        reps = tokens[i]
        i += 1
        rest_note_tokens = []
        while i < len(tokens) and not tokens[i].isdigit():
            rest_note_tokens.append(tokens[i])
            i += 1
        rest_note_text = ' '.join(rest_note_tokens).strip()
        rest = ''
        notes = ''
        if rest_note_text:
            m = rest_split.match(rest_note_text)
            if m:
                rest = m.group(1).strip()
                notes = m.group(2).strip()
            else:
                rest = rest_note_text
        exercises.append({
            'name': name,
            'sets': sets,
            'reps': reps,
            'rest': rest,
            'notes': notes
        })
    return exercises

week_data = []
for week in range(1, 13):
    week_marker = f'Week {week}\n'
    if week_marker not in raw_text:
        continue
    start = raw_text.index(week_marker)
    if week < 12:
        next_marker = raw_text.find(f'Week {week + 1}\n')
    else:
        next_marker = -1
    week_text = raw_text[start: next_marker if next_marker != -1 else len(raw_text)]

    day_headers = []
    for day_match in re.finditer(rf'Week {week} / Day (\d+) / ([^\n]+)', week_text):
        day_num = int(day_match.group(1))
        title = day_match.group(2).strip()
        title = title.replace('Exercise Set Reps Rest Notes', '').strip()
        day_headers.append({'day': day_num, 'title': title})

    cardio_entries = [m.strip() for m in re.findall(r'Cardio:\s*([^\n]+)', week_text)]
    exercise_matches = list(re.finditer('Exercise Set Reps Rest Notes', week_text))
    exercise_blocks = []
    for idx, ex_match in enumerate(exercise_matches):
        block_start = ex_match.end()
        next_cardio = week_text.find('Cardio:', block_start)
        if next_cardio == -1:
            continue
        block_text = week_text[block_start:next_cardio].strip()
        if block_text:
            exercise_blocks.append(block_text)
    day_headers_sorted = sorted(day_headers, key=lambda d: d['day'])
    days = []
    exercise_idx = 0
    cardio_idx = 0
    for day_info in day_headers_sorted:
        cardio = cardio_entries[cardio_idx].strip() if cardio_idx < len(cardio_entries) else ''
        cardio_idx += 1
        exercises = []
        if exercise_idx < len(exercise_blocks):
            exercises = parse_block(exercise_blocks[exercise_idx])
            exercise_idx += 1
        days.append({
            'day': day_info['day'],
            'title': day_info['title'],
            'cardio': cardio,
            'exercises': exercises
        })
    week_data.append({
        'week': week,
        'task': week_tasks.get(week, ''),
        'days': days
    })

Path('.devtools/gethin_data.json').write_text(json.dumps(week_data, ensure_ascii=False, indent=2), encoding='utf-8')
print('Weeks parsed:', len(week_data))
