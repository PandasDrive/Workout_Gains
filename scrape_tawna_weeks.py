import requests
import re
import json
from bs4 import BeautifulSoup

week_ranges = {
    3: range(15, 22),
    4: range(22, 29),
    5: range(29, 36),
    6: range(36, 43),
    7: range(43, 50),
    8: range(50, 57)
}
base = 'https://www.kaged.com/blogs/tawnas-bikini-trainer/tbt-day-{0:02d}'
tasks = {
    3: 'Shift to three steady-state sessions (25 min at 135-150 bpm), layer in 3-second eccentrics on key lifts, and keep posing daily.',
    4: 'Hold steady with three cardio sessions, chase progressive overload without sacrificing form, and continue daily posing practice.',
    5: 'New split kicks in—keep three steady-state sessions, track pumps and midsection tightness, and rehearse stage transitions.',
    6: 'Match or beat Week 5 numbers while staying precise, maintain three cardio sessions, and polish presentation work.',
    7: 'Push conditioning with tight rest, keep three cardio sessions, and run full posing walkthroughs after lifts.',
    8: 'Final polish week: prioritize recovery, maintain three steady-state sessions, and rehearse stage presentation daily.'
}

weeks_output = []
for week, days in week_ranges.items():
    week_days = []
    for index, actual_day in enumerate(days, start=1):
        html = requests.get(base.format(actual_day)).text
        title_match = re.search(r'Day\s*\d+\s*:\s*([^\n<]+)', html, flags=re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'Training Day'
        title = title.replace('&amp;', '&')
        if title.lower() == 'rest day':
            title = 'Rest Day'

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        exercises = []
        if table:
            for row in table.select('tbody tr'):
                cell = row.find('td')
                if not cell:
                    continue
                text = ' '.join(cell.stripped_strings)
                text = re.sub(r'\s+', ' ', text).strip()
                if not text:
                    continue
                match = re.match(r'(.+?)\s*Sets?:\s*([^R]+)Reps?:\s*(.+)', text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    sets = match.group(2).strip()
                    reps = match.group(3).strip()
                else:
                    name = text
                    sets = ''
                    reps = ''
                name = name.replace('&amp;', '&')
                reps = reps.replace('&amp;', '&')
                name = name.replace('Superset: Preacher Curl Triceps Dip Machine', 'Superset: Preacher Curl -> Triceps Dip Machine')
                name = name.replace('EZ-Bar Curl/ Skullcrusher Superset', 'Superset: EZ-Bar Curl -> Skullcrusher')
                name = name.replace('Delt Blaster', 'Delt Blaster Giant Set')
                name = name.replace('One-Arm Cable lateral Raise', 'One-Arm Cable Lateral Raise')
                reps = re.sub(r'(?<=\d)\s+(?=\d)', '', reps)
                exercises.append({
                    'name': name,
                    'sets': sets,
                    'reps': reps,
                    'rest': '',
                    'notes': ''
                })
        cardio_base = 'Steady-state cardio: 25 min at 135-150 bpm (count this toward your 3 weekly sessions from Week 3 onward).'
        if not exercises:
            if actual_day == 56:
                cardio = 'Optional celebration: light movement, stretching, and posing practice—no required cardio today.'
            else:
                cardio = 'Optional active recovery: light walk, mobility, or yoga. No required cardio session today.'
        else:
            cardio = cardio_base
            if 'Back & Arms' in title:
                cardio = cardio_base + ' Add 5 min vacuum holds after cardio.'
        if actual_day == 49:
            title = 'Rest Day'
        week_days.append({
            'day': actual_day,
            'title': title,
            'cardio': cardio,
            'exercises': exercises
        })
    weeks_output.append({
        'week': week,
        'task': tasks[week],
        'days': week_days
    })

print(json.dumps(weeks_output, indent=2))
