from pathlib import Path

index_path = Path('index.html')
weeks_js = Path('.devtools/nippard_weeks_js.txt').read_text(encoding='utf-8')
content = index_path.read_text(encoding='utf-8')
start = content.index('weeks: ')
start_bracket = content.index('[', start)
depth = 0
end_index = None
for i in range(start_bracket, len(content)):
    ch = content[i]
    if ch == '[':
        depth += 1
    elif ch == ']':
        depth -= 1
        if depth == 0:
            end_index = i
            break
if end_index is None:
    raise SystemExit('Could not find matching closing bracket for weeks array.')
replacement = 'weeks: ' + weeks_js
updated = content[:start] + replacement + content[end_index + 1:]
index_path.write_text(updated, encoding='utf-8')
print('Reformatted nippard weeks block')
