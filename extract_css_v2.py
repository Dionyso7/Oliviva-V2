import re

css_path = r'c:\Users\Tom\Desktop\Olivia\OliviaLecaplain\css\sophrologie-exemple.webflow.css'

with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find occurrences of the class and surrounding text
params = ['.about-us-img-tecker-img', '.about-us-img-tecker-wrapper', '.about-us-img-tecker-inner']

for p in params:
    print(f"--- Searching for {p} ---")
    # Finding the index
    idx = content.find(p)
    if idx != -1:
        # Print a chunk around it
        start = max(0, idx)
        end = min(len(content), idx + 300)
        print(content[start:end])
    else:
        print("Not found")

# Search for animation definition
print("\n--- Searching for @keyframes ---")
# This might be huge, so let's look for "keyframes" + any word that looks like it might belong to the ticker
# Maybe search for "animation" property near the classes
