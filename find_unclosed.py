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
    # Extract script content
    script_lines = lines[script_start+1:script_end]
    script_content = ''.join(script_lines)
    
    # Character-by-character analysis
    depth = 0
    paren_depth = 0
    bracket_depth = 0
    in_string = False
    in_template = False
    string_char = None
    
    last_brace_pos = -1
    last_paren_pos = -1
    last_bracket_pos = -1
    
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
                last_brace_pos = i
            elif char == '}':
                depth -= 1
            elif char == '(':
                paren_depth += 1
                last_paren_pos = i
            elif char == ')':
                paren_depth -= 1
            elif char == '[':
                bracket_depth += 1
                last_bracket_pos = i
            elif char == ']':
                bracket_depth -= 1
    
    print("Final depths - Braces: {}, Parens: {}, Brackets: {}".format(depth, paren_depth, bracket_depth))
    print()
    
    if depth > 0:
        # Find last opening brace position and convert to line number
        line_num = script_content[:last_brace_pos].count('\n') + script_start + 2
        print("MISSING CLOSING BRACE: Last unclosed brace at position {}, which is around line {}".format(last_brace_pos, line_num))
        # Show context
        context_start = max(0, last_brace_pos - 50)
        context_end = min(len(script_content), last_brace_pos + 100)
        context = script_content[context_start:context_end]
        print("Context: ...{}...".format(context.replace('\n', ' ')))
        print()
    
    if paren_depth > 0:
        # Find last opening paren position
        line_num = script_content[:last_paren_pos].count('\n') + script_start + 2
        print("MISSING CLOSING PAREN: Last unclosed paren at position {}, which is around line {}".format(last_paren_pos, line_num))
        # Show context
        context_start = max(0, last_paren_pos - 50)
        context_end = min(len(script_content), last_paren_pos + 100)
        context = script_content[context_start:context_end]
        print("Context: ...{}...".format(context.replace('\n', ' ')))
