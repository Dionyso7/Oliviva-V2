import re

css_path = r'c:\Users\Tom\Desktop\Olivia\OliviaLecaplain\css\sophrologie-exemple.webflow.css'

with open(css_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Function to extract rule for a selector
def extract_rule(selector, content):
    pattern = re.escape(selector) + r'\s*\{([^}]*)\}'
    match = re.search(pattern, content)
    if match:
        return match.group(0)
    return "Not found"

print("--- Rules ---")
print(extract_rule('.about-us-img-tecker-img', content))
print(extract_rule('.about-us-img-tecker-wrapper', content))
print(extract_rule('.about-us-img-tecker-inner', content))

print("\n--- Animation Keyframes ---")
# Look for animation names in the content
inner_rule = extract_rule('.about-us-img-tecker-inner', content)
if inner_rule != "Not found":
    print(f"Inner Rule: {inner_rule}")
