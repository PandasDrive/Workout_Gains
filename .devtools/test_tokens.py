import re
block = "Leg Press 4 10-12 90 seconds May want to use knee sleeves, knee wraps, etc. Stretch in between sets. Hack Squat 4 10-12 90 seconds Optional: Use a foam roller behind your shoulders Split Squat with Barbell Plate 4 10-12 90 seconds Use a training journal. This is important to track your progress. Stiff Legged Deadlifts 4 10-12 90 seconds Can use dumbbells, barbells, smith machine, whatever is available Lying Hamstring Curls 4 10-12 90 seconds Seated Leg Curls 4 10-12 90 seconds Standing Calf Press 6 10-12 60 seconds"
tokens = block.split()
print(tokens)
indices = [i for i,t in enumerate(tokens) if t.isdigit()]
print(indices)
