import re

# Read the file
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find script block
script_start = None
script_end = None
for i, line in enumerate(lines):
    if '<script>' in line and 'src=' not in line:
        script_start = i
    if '</script>' in line and script_start is not None:
        script_end = i
        break

if script_start is None or script_end is None:
    print("Script block not found")
else:
    print(f"Script block: lines {script_start+1} to {script_end+1}")
    
    # Extract script content
    script_lines = lines[script_start+1:script_end]
    script_content = ''.join(script_lines)
    
    # Simple character-by-character analysis
    depth = 0
    paren_depth = 0
    bracket_depth = 0
    in_string = False
    in_template = False
    string_char = None
    
    for i, char in enumerate(script_content):
        if char == '`' and (i == 0 or script_content[i-1] != '\\'):
            in_template = not in_template
        elif not in_template:
            if char in ('"', "'") and (i == 0 or script_content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
        
        if not in_string and not in_template:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            elif char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
        
        if depth < 0 or paren_depth < 0 or bracket_depth < 0:
            # Find line number where this happened
            line_num = script_content[:i].count('\n') + script_start + 2
            print(f"ERROR at position {i} (line approx {line_num})")
            print(f"  Brace depth: {depth}, Paren depth: {paren_depth}, Bracket depth: {bracket_depth}")
            print(f"  Character context: ...{script_content[max(0,i-20):min(len(script_content),i+20)]}...")
            break
    
    if depth == 0 and paren_depth == 0 and bracket_depth == 0:
        print(f"✓ All braces/parens/brackets match!")
    else:
        print(f"Final depths - Braces: {depth}, Parens: {paren_depth}, Brackets: {bracket_depth}")
