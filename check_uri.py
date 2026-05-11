import re
with open('index.html','r') as f:
    content = f.read()

# Count how many src assignments
count = content.count('.src = "')
print(f"Total .src assignments: {count}")

# Check for doubled prefix
double = content.count('base64,data:')
bad = content.count('data:image/png;base64,data:image/png')
print(f"Doubled 'base64,data:' occurrences: {double}")
print(f"Doubled full prefix occurrences: {bad}")

# For each wallTex.*.src, show the first 80 chars of the URI
pattern = r'wallTex\.(\w+)\.src = "(data:image/png;base64,[^"]{0,80})'
for m in re.finditer(pattern, content):
    name = m.group(1)
    uri_prefix = m.group(2)
    # Check if doubled
    if uri_prefix.count('data:image') > 1:
        print(f"  BROKEN: wallTex.{name}.src = \"{uri_prefix}...")
    else:
        print(f"  OK: wallTex.{name}.src = \"{uri_prefix}...")
