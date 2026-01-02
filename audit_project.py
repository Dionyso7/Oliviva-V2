import os
import re
from urllib.parse import unquote

PROJECT_ROOT = r"C:\Users\Tom\Desktop\Olivia\OliviaLecaplain"
ENTRY_POINTS = ["index.html", "404.html", "401.html"] # Add 404 and 401 as they are standard utility pages
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
    # Handle absolute paths (starting with /)
    if relative_link.startswith('/'):
        return os.path.join(PROJECT_ROOT, relative_link.lstrip('/'))
    
    # Handle relative paths
    base_dir = os.path.dirname(base_file)
    return os.path.join(base_dir, relative_link)

def extract_links_and_assets(file_path):
    links = set()
    assets = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # HTML Links (a href)
            for match in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']*)["\']', content, re.IGNORECASE):
                link = match.group(1).split('#')[0].split('?')[0]
                if link and not link.startswith(('http', 'mailto:', 'tel:', 'javascript:')):
                    links.add(link)

            # Image sources (img src)
            for match in re.finditer(r'<img\s+(?:[^>]*?\s+)?src=["\']([^"\']*)["\']', content, re.IGNORECASE):
                src = match.group(1).split('?')[0]
                if src:
                    assets.add(src)

            # Image sources (srcset)
            for match in re.finditer(r'srcset=["\']([^"\']*)["\']', content, re.IGNORECASE):
                srcset = match.group(1)
                urls = re.split(r',\s*', srcset)
                for url_entry in urls:
                    url = url_entry.strip().split(' ')[0]
                    if url:
                        assets.add(url)

            # CSS references (url()) - covers inline styles and css files
            for match in re.finditer(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', content, re.IGNORECASE):
                url = match.group(1).split('?')[0].split('#')[0]
                if url and not url.startswith(('http', 'data:')):
                     assets.add(url)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        
    return links, assets

def audit_project():
    all_files = get_all_files(PROJECT_ROOT)
    
    html_files = {f for f in all_files if os.path.splitext(f)[1].lower() in HTML_EXTENSIONS}
    image_files = {f for f in all_files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS}
    css_files = {f for f in all_files if os.path.splitext(f)[1].lower() == '.css'}
    
    # Reachable HTML analysis
    reachable_html = set()
    queue = [os.path.join(PROJECT_ROOT, ep) for ep in ENTRY_POINTS if os.path.exists(os.path.join(PROJECT_ROOT, ep))]
    
    # Mark entry points as reachable
    for q in queue:
        reachable_html.add(normalize_path(q))
        
    visited_for_links = set()
    
    # Simple BFS for HTML reachability
    processing_queue = list(queue)
    while processing_queue:
        current_file = processing_queue.pop(0)
        norm_current = normalize_path(current_file)
        
        if norm_current in visited_for_links:
            continue
        visited_for_links.add(norm_current)
        
        links, _ = extract_links_and_assets(current_file)
        
        for link in links:
            resolved = resolve_path(current_file, unquote(link))
            if os.path.isfile(resolved) and normalize_path(resolved) in [normalize_path(h) for h in html_files]:
                norm_resolved = normalize_path(resolved)
                if norm_resolved not in reachable_html:
                    reachable_html.add(norm_resolved)
                    processing_queue.append(resolved)

    # Asset Reference analysis (Scan ALL reachable HTML + ALL CSS files)
    referenced_assets = set()
    files_to_scan = reachable_html.union({normalize_path(c) for c in css_files})
    
    for file_path in all_files:
        # Scan everything just to be safe? No, let's scan reachable HTML and all CSS.
        # Check if file is reachable HTML or CSS or JS
        if normalize_path(file_path) in files_to_scan or file_path.endswith('.js'):
             _, assets = extract_links_and_assets(file_path)
             for asset in assets:
                 resolved = resolve_path(file_path, unquote(asset))
                 if os.path.isfile(resolved):
                     referenced_assets.add(normalize_path(resolved))

    # Identify Unused
    unused_html = []
    for f in html_files:
        if normalize_path(f) not in reachable_html:
            unused_html.append(f)
            
    unused_images = []
    for f in image_files:
        if normalize_path(f) not in referenced_assets:
            unused_images.append(f)

    # Output Report
    print("--- AUDIT REPORT ---")
    print("\n[UNUSED HTML FILES]")
    for f in sorted(unused_html):
        print(os.path.relpath(f, PROJECT_ROOT))
        
    print("\n[UNUSED IMAGE FILES]")
    for f in sorted(unused_images):
        print(os.path.relpath(f, PROJECT_ROOT))

if __name__ == "__main__":
    audit_project()
