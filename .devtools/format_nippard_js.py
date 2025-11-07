import json
from pathlib import Path

data = json.loads(Path('.devtools/nippard_data.json').read_text(encoding='utf-8'))

INDENT_STEP = '    '

def format_js(value, current_indent):
    next_indent = current_indent + INDENT_STEP
    if isinstance(value, dict):
        items = list(value.items())
        if not items:
            return '{}'
        lines = ['{']
        for idx, (key, val) in enumerate(items):
            formatted = format_js(val, next_indent)
            if '\n' in formatted:
                formatted = formatted.replace('\n', '\n' + next_indent)
            line = f"{next_indent}{key}: {formatted}"
            if idx < len(items) - 1:
                line += ','
            lines.append(line)
        lines.append(current_indent + '}')
        return '\n'.join(lines)
    if isinstance(value, list):
        if not value:
            return '[]'
        lines = ['[']
        for idx, item in enumerate(value):
            formatted = format_js(item, next_indent)
            if '\n' in formatted:
                formatted = formatted.replace('\n', '\n' + next_indent)
            line = f"{next_indent}{formatted}"
            if idx < len(value) - 1:
                line += ','
            lines.append(line)
        lines.append(current_indent + ']')
        return '\n'.join(lines)
    if isinstance(value, str):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return str(value)

js_literal = format_js(data, INDENT_STEP * 4)  # start at 16 spaces
Path('.devtools/nippard_weeks_js.txt').write_text(js_literal, encoding='utf-8')
print('Wrote formatted JS literal to .devtools/nippard_weeks_js.txt')
