
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

# Extract script content
script_lines = lines[script_start+1:script_end]
script_content = ''.join(script_lines)

# Find what's at positions 31960 and 31971
pos1 = 31960
pos2 = 31971

# Show character context - find line number for these positions
lines_before_pos1 = script_content[:pos1].count('\n')
lines_before_pos2 = script_content[:pos2].count('\n')

# Get the line content for each position
line_start_pos1 = script_content.rfind('\n', 0, pos1) + 1
line_end_pos1 = script_content.find('\n', pos1)
line_content_1 = script_content[line_start_pos1:line_end_pos1] if line_end_pos1 != -1 else script_content[line_start_pos1:]

line_start_pos2 = script_content.rfind('\n', 0, pos2) + 1
line_end_pos2 = script_content.find('\n', pos2)
line_content_2 = script_content[line_start_pos2:line_end_pos2] if line_end_pos2 != -1 else script_content[line_start_pos2:]

print("Position 31960 (unclosed brace):")
print(f"  Line number in script: {lines_before_pos1 + 1} (file line {lines_before_pos1 + script_start + 2})")
print(f"  Character offset in line: {pos1 - line_start_pos1}")
print(f"  Line content: {line_content_1}")
print(f"  Character at position: '{script_content[pos1]}'")
print(f"  Surrounding: ...{script_content[pos1-30:pos1+30]}...")
print()

print("Position 31971 (unclosed paren):")
print(f"  Line number in script: {lines_before_pos2 + 1} (file line {lines_before_pos2 + script_start + 2})")
print(f"  Character offset in line: {pos2 - line_start_pos2}")
print(f"  Line content: {line_content_2}")
print(f"  Character at position: '{script_content[pos2]}'")
print(f"  Surrounding: ...{script_content[pos2-30:pos2+30]}...")
