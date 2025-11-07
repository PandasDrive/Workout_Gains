from pathlib import Path
path = Path('index.html')
content = path.read_text(encoding='utf-8')
needle = 'const programs = '
start = content.find(needle)
if start == -1:
    raise SystemExit('programs block not found')
brace_start = content.find('{', start)
if brace_start == -1:
    raise SystemExit('opening brace not found')
depth = 0
end = None
for idx in range(brace_start, len(content)):
    ch = content[idx]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end = idx + 1
            break
if end is None:
    raise SystemExit('matching brace not found')
if end < len(content) and content[end] == ';':
    end += 1
replacement = "const programs = window.programs || {};\n        if (!Object.keys(programs).length) {\n            console.warn(\"Program data is not loaded.\");\n        }"
new_content = content[:start] + replacement + content[end:]
path.write_text(new_content, encoding='utf-8')
