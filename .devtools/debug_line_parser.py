import re
block = "Leg Press 4 10-12 90 secondsMay want to use knee sleeves, \nknee wraps, etc. Stretch in  \nbetween sets.  \nHack Squat 4 10-12 90 secondsOptional: Use a foam roller behind  \nyour shoulders\nSplit Squat with  \nBarbell Plate4 10-12 90 secondsUse a training journal. This is \nimportant to track your progress.\nStiff Legged Deadlifts 4 10-12 90 seconds Can use dumbbells, barbells, smith \nmachine, whatever is available\nLying Hamstring Curls 4 10-12 90 seconds\nSeated Leg Curls 4 10-12 90 seconds\nStanding Calf Press 6 10-12 60 seconds"
lines = [line.strip() for line in block.splitlines() if line.strip()]
pattern = re.compile(r'(.+?)\s+(\d+)\s+([0-9A-Za-z-/]+)\s+(.+)')
rest_pattern = re.compile(r'([0-9A-Za-z +/().,-]*?(?:seconds|min|minutes|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A))(.*)', re.IGNORECASE)
exercises = []
current = None
pending = ''
for idx, line in enumerate(lines):
    print('line:', line)
    if re.search(r'\d+\s+[0-9A-Za-z-/]+', line):
        if pending:
            line = pending + ' ' + line
            pending = ''
            print('after pending:', line)
        line = re.sub(r'([A-Za-z])(\d)', r'\1 \2', line)
        line = re.sub(r'(\d)([A-Za-z])', r'\1 \2', line)
        print('after spacing:', line)
        m = pattern.match(line)
        if not m:
            continue
        name = m.group(1).strip()
        sets = m.group(2).strip()
        reps = m.group(3).strip()
        rest_notes = m.group(4).strip()
        rest_match = rest_pattern.match(rest_notes)
        if rest_match:
            rest = rest_match.group(1).strip()
            notes = rest_match.group(2).strip()
        else:
            rest = rest_notes
            notes = ''
        current = {'name': name, 'sets': sets, 'reps': reps, 'rest': rest, 'notes': notes}
        exercises.append(current)
    else:
        next_line = ''
        for j in range(idx+1, len(lines)):
            if lines[j].strip():
                next_line = lines[j].strip()
                break
        if next_line and re.search(r'\d+\s+[0-9A-Za-z-/]+', next_line):
            pending = (pending + ' ' + line).strip()
            print('pending assigned:', pending)
        elif current is not None:
            current['notes'] = (current['notes'] + ' ' + line).strip()

print(exercises)
