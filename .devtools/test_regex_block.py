import re
block = "Leg Press 4 10-12 90 seconds May want to use knee sleeves, knee wraps, etc. Stretch in between sets. Hack Squat 4 10-12 90 seconds Optional: Use a foam roller behind your shoulders Split Squat with Barbell Plate 4 10-12 90 seconds Use a training journal. This is important to track your progress. Stiff Legged Deadlifts 4 10-12 90 seconds Can use dumbbells, barbells, smith machine, whatever is available Lying Hamstring Curls 4 10-12 90 seconds Seated Leg Curls 4 10-12 90 seconds Standing Calf Press 6 10-12 60 seconds"
pattern = re.compile(r'([A-Za-z0-9&:/(),\'"\- ]+?)\s+(\d+)\s+([0-9A-Za-z-\/]+)\s+([0-9A-Za-z +\/().,\-]*?(?:seconds?|minutes?|Failure|failure|rest|Rest|AM|PM|Only|only|per side|per muscle|N/A))\s*(.*?)(?=(?:[A-Za-z0-9&:/(),\'"\- ]+?\s+\d+\s+[0-9A-Za-z-\/]+)|$)')
for m in pattern.finditer(block):
    print({
        'name': m.group(1).strip(),
        'sets': m.group(2),
        'reps': m.group(3),
        'rest': m.group(4).strip(),
        'notes': m.group(5).strip()
    })
