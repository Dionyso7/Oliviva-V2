import os
import re
from urllib.parse import unquote

PROJECT_ROOT = r"C:\Users\Tom\Desktop\Olivia\OliviaLecaplain"
# Explicitly protect main pages and scripts
PROTECTED_FILES = {
    "index.html", "about-us.html", "sessions.html", "contact-us.html", 
    "404.html", "401.html", "audit_project.py", "cleanup_project.py"
}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif'}
HTML_EXTENSIONS = {'.html', '.htm'}

def get_all_files(root_dir):
    all_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            all_files.append(os.path.join(dirpath, f))
    return all_files

def normalize_path(path):
    return os.path.normpath(path).lower()

def resolve_path(base_file, relative_link):
    if relative_link.startswith('/'):
        return os.path.join(PROJECT_ROOT, relative_link.lstrip('/'))
    base_dir = os.path.dirname(base_file)
    return os.path.join(base_dir, relative_link)

def extract_links_and_assets(file_path):
    links = set()
    assets = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for match in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']*)["\']', content, re.IGNORECASE):
                link = match.group(1).split('#')[0].split('?')[0]
                if link and not link.startswith(('http', 'mailto:', 'tel:', 'javascript:')):
                    links.add(link)
            for match in re.finditer(r'<img\s+(?:[^>]*?\s+)?src=["\']([^"\']*)["\']', content, re.IGNORECASE):
                src = match.group(1).split('?')[0]
                if src:
                    assets.add(src)
            for match in re.finditer(r'srcset=["\']([^"\']*)["\']', content, re.IGNORECASE):
                for url_entry in re.split(r',\s*', match.group(1)):
                    url = url_entry.strip().split(' ')[0]
                    if url: assets.add(url)
            for match in re.finditer(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', content, re.IGNORECASE):
                url = match.group(1).split('?')[0].split('#')[0]
                if url and not url.startswith(('http', 'data:')):
                     assets.add(url)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return links, assets

def cleanup_project():
    all_files = get_all_files(PROJECT_ROOT)
    html_files = {f for f in all_files if os.path.splitext(f)[1].lower() in HTML_EXTENSIONS}
    image_files = {f for f in all_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS}
    css_files = {f for f in all_files if os.path.splitext(f)[1].lower() == '.css'}
    
    # Reachable HTML analysis
    reachable_html = set()
    queue = [os.path.join(PROJECT_ROOT, ep) for ep in PROTECTED_FILES if os.path.exists(os.path.join(PROJECT_ROOT, ep))]
    for q in queue: reachable_html.add(normalize_path(q))
        
    visited_for_links = set()
    processing_queue = list(queue)
    
    while processing_queue:
        current_file = processing_queue.pop(0)
        norm_current = normalize_path(current_file)
        if norm_current in visited_for_links: continue
        visited_for_links.add(norm_current)
        
        links, _ = extract_links_and_assets(current_file)
        for link in links:
            resolved = resolve_path(current_file, unquote(link))
            if os.path.isfile(resolved) and normalize_path(resolved) in [normalize_path(h) for h in html_files]:
                norm_resolved = normalize_path(resolved)
                if norm_resolved not in reachable_html:
                    reachable_html.add(norm_resolved)
                    processing_queue.append(resolved)

    referenced_assets = set()
    files_to_scan = reachable_html.union({normalize_path(c) for c in css_files})
    for file_path in all_files:
        if normalize_path(file_path) in files_to_scan or file_path.endswith('.js'):
             _, assets = extract_links_and_assets(file_path)
             for asset in assets:
                 resolved = resolve_path(file_path, unquote(asset))
                 if os.path.isfile(resolved):
                     referenced_assets.add(normalize_path(resolved))

    # Identify and Delete Unused
    print("--- STARTING CLEANUP ---")
    
    # Clean HTML
    for f in html_files:
        if normalize_path(f) not in reachable_html:
             if os.path.basename(f) not in PROTECTED_FILES:
                print(f"Deleting HTML: {os.path.relpath(f, PROJECT_ROOT)}")
                os.remove(f)

    # Clean Images
    for f in image_files:
        if normalize_path(f) not in referenced_assets:
             # Double check it's not a favicon or critical system image if not referenced in code (though audit logic includes all files)
             # Extra safety: Don't delete if it's in a 'protected' folder? No, reliance on audit is key.
             print(f"Deleting Image: {os.path.relpath(f, PROJECT_ROOT)}")
             os.remove(f)

    print("--- CLEANUP COMPLETE ---")

if __name__ == "__main__":
    cleanup_project()
