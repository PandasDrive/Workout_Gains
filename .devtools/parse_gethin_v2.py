import re
import json
from pathlib import Path

raw_text = Path('WorkoutPrograms/legacy_program_text.txt').read_text(encoding='utf-8')
raw_text = raw_text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2014', '-').replace('\u2013', '-').replace('\u00a0', ' ').replace('\u00b0', ' deg')

# Weekly tasks
week_tasks = {}
tasks_section = raw_text.split('Weekly Tasks', 1)[-1]
for line in tasks_section.splitlines():
    line = line.strip()
    if not line or not line.startswith('Week '):
        continue
    parts = line.split(None, 2)
    if len(parts) >= 3 and parts[1].isdigit():
        week_tasks[int(parts[1])] = parts[2]

# Split by weeks using markers "==== PAGE" to ensure boundaries
def get_week_text(week_num):
    pattern = f'Week {week_num}\n'
    idx = raw_text.find(pattern)
    if idx == -1:
        return ''
    next_idx = raw_text.find(f'Week {week_num + 1}\n') if week_num < 12 else -1
    return raw_text[idx: next_idx if next_idx != -1 else len(raw_text)]

all_weeks = []
for week in range(1, 13):
    week_text = get_week_text(week)
    if not week_text:
        continue
    # Extract day titles
    day_matches = re.findall(rf'Week {week} / Day (\d+) / ([^\n]+)', week_text)
    day_titles = {}
    for day, title in day_matches:
        day_int = int(day)
        clean_title = title.replace('Exercise Set Reps Rest Notes', '').replace('Exercise Set Reps Rest', '').strip()
        day_titles[day_int] = clean_title
    # Ensure 7 days even if some missing titles (use placeholders)
    titles_ordered = [day_titles.get(i, f'Day {i}') for i in range(1, 8)]

    # Find cardio lines
    cardio_lines = [m.strip() for m in re.findall(r'Cardio:\s*([^\n]+)', week_text)]
    # pad to 7 entries
    while len(cardio_lines) < 7:
        cardio_lines.append('')

    # Extract exercise blocks
    block_pattern = re.compile(r'Exercise Set Reps Rest Notes([^C]+)Cardio:', re.DOTALL)
    blocks = block_pattern.findall(week_text)

    days = []
    block_index = 0
    cardio_index = 0

    for day_idx, title in enumerate(titles_ordered, start=1):
        cardio_text = cardio_lines[cardio_index].strip() if cardio_index < len(cardio_lines) else ''
        cardio_index += 1
        exercises = []
        if block_index < len(blocks):
            block = blocks[block_index]
            block_index += 1
            # preprocess block
            block = block.replace('\n', ' ')
            block = re.sub(r'\s+', ' ', block)
            block = re.sub(r'([A-Za-z])([0-9])', r'\1 \2', block)
            block = re.sub(r'(seconds|min|Failure)([A-Z])', r'\1 \2', block)
            entries = []
            pattern = re.compile(r'([A-Za-z0-9\-&,/() ]+?)\s+(\d+)\s+([0-9A-Za-z\-+/]+)\s+([0-9A-Za-z\-+/ ]*(?:seconds|min|minutes|Failure|failure|AM|PM|rest|Rest|only|N/A|no rest|per side|per muscle|None|Cardio|s))\s*', re.IGNORECASE)
            pos = 0
            while pos < len(block):
                match = pattern.match(block, pos)
                if not match:
                    break
                name = match.group(1).strip()
                sets = match.group(2).strip()
                reps = match.group(3).strip()
                rest = match.group(4).strip()
                pos = match.end()
                # notes are text until next match start
                next_match = pattern.match(block, pos)
                if next_match:
                    notes_end = next_match.start()
                else:
                    notes_end = len(block)
                notes = block[pos:notes_end].strip()
                pos = notes_end
                exercises.append({
                    'name': name,
                    'sets': sets,
                    'reps': reps,
                    'rest': rest,
                    'notes': notes
                })
        days.append({
            'day': day_idx,
            'title': title,
            'cardio': cardio_text,
            'exercises': exercises
        })

    all_weeks.append({
        'week': week,
        'task': week_tasks.get(week, ''),
        'days': days
    })

Path('.devtools/gethin_data.json').write_text(json.dumps(all_weeks, ensure_ascii=False, indent=2), encoding='utf-8')
print('Weeks parsed:', len(all_weeks))
