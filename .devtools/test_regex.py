import re
block = "Leg Press 4 10-12 90 secondsMay want to use knee sleeves, knee wraps, etc. Stretch in between sets. Hack Squat 4 10-12 90 secondsOptional: Use a foam roller behind your shoulders Split Squat with Barbell Plate4 10-12 90 secondsUse a training journal. This is important to track your progress. Stiff Legged Deadlifts 4 10-12 90 seconds Can use dumbbells, barbells, smith machine, whatever is available Lying Hamstring Curls 4 10-12 90 seconds Seated Leg Curls 4 10-12 90 seconds Standing Calf Press 6 10-12 60 seconds"
block = block.replace('\n', ' ')
block = re.sub(r'\s+', ' ', block)
block = re.sub(r'([a-z])([A-Z])', r'\1 \2', block)
block = re.sub(r'([A-Za-z])(\d)', r'\1 \2', block)
block = re.sub(r'(\d)([A-Za-z])', r'\1 \2', block)
pattern = re.compile(r'([A-Za-z][^0-9]*?)\s+(\d+)\s+([0-9A-Za-z-/]+)\s+([0-9A-Za-z +/().,\'"-]*?)(?=(?:[A-Za-z][^0-9]*?\s+\d+\s+[0-9A-Za-z-/]+)|$)')
for m in pattern.finditer(block):
    name = m.group(1).strip()
    sets = m.group(2)
    reps = m.group(3)
    rest_notes = m.group(4).strip()
    print('---', name, sets, reps, rest_notes)
