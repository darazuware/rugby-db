import os
import re
from urllib.parse import unquote

# Config
ROOT_DIR = 'dist'
REPORT_FILE = 'link_check_report.txt'

def check_link(source_file, link):
    """Verifies if a relative link exists on disk."""
    # Skip external and non-file links
    if link.startswith(('http', '//', '#', 'mailto', 'tel', 'javascript:')):
        return True, None
    
    # Clean query and anchor
    clean_link = link.split('?')[0].split('#')[0]
    if not clean_link:
        return True, None # Just an anchor or query
        
    # Handle absolute paths within site (e.g. /index.html)
    # In our project, all links are intended to be relative for easy offline viewing or server-agnostic deployment
    if clean_link.startswith('/'):
        target = os.path.join(ROOT_DIR, clean_link.lstrip('/'))
    else:
        # Resolve relative link
        dir_name = os.path.dirname(source_file)
        target = os.path.normpath(os.path.join(dir_name, clean_link))
    
    # Check existence
    if os.path.exists(target):
        return True, None
    
    # Fallback for folder/ index.html
    if os.path.isdir(target):
        if os.path.exists(os.path.join(target, 'index.html')):
            return True, None

    return False, target

def main():
    print(f"Starting exhaustive link check in '{ROOT_DIR}'...")
    total_files = 0
    total_links = 0
    broken_links = []
    
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
            
            total_files += 1
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
                
            # Find all links in href and src
            matches = re.findall(r'(?:href|src)=["\'](.*?)["\']', content)
            
            for link in matches:
                total_links += 1
                exists, resolved_path = check_link(filepath, link)
                if not exists:
                    broken_links.append({
                        'source': filepath,
                        'link': link,
                        'target': resolved_path
                    })

    # Summary Report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=== Link Check Report ===\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Links Checked: {total_links}\n")
        f.write(f"Total Broken Links: {len(broken_links)}\n\n")
        
        if broken_links:
            f.write("Broken Link Details:\n")
            f.write("-" * 50 + "\n")
            for err in broken_links:
                f.write(f"Source: {err['source']}\n")
                f.write(f"Link:   {err['link']}\n")
                f.write(f"Target: {err['target']}\n")
                f.write("-" * 50 + "\n")
        else:
            f.write("No broken links found! Great job.\n")

    print("\nCheck Complete.")
    print(f"Total Files: {total_files}")
    print(f"Total Links: {total_links}")
    print(f"Broken Links: {len(broken_links)}")
    print(f"Detailed report saved to '{REPORT_FILE}'")

if __name__ == "__main__":
    main()
