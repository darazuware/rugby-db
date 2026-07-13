import os
import re
import json
from player_utils import load_unified_players, slugify

def generate_redirect_map():
    players = load_unified_players()
    pid_to_slug = {}
    name_to_slug = {}
    
    for p in players:
        slug = slugify(p.get('name_en', ''))
        pid = p.get('id')
        if pid:
            pid_to_slug[str(pid)] = slug
        
        name_ja = p.get('name_ja')
        if name_ja:
            name_to_slug[name_ja] = slug
            
        name_en = p.get('name_en')
        if name_en:
            name_to_slug[name_en] = slug

    old_files_dir = 'dist/player'
    if not os.path.exists(old_files_dir):
        print(f"Directory {old_files_dir} not found.")
        return

    redirects = []
    files = [f for f in os.listdir(old_files_dir) if f.endswith('.html')]
    
    print(f"Analyzing {len(files)} files...")
    
    for f_name in files:
        # Try to extract ID from filename like "name_lo_12345.html"
        m_id = re.search(r'(lo_\d+|ar_\d+)', f_name)
        slug = None
        
        if m_id:
            pid = m_id.group(1)
            slug = pid_to_slug.get(pid)
            
        if not slug:
            # Fallback: Try to match name part
            name_part = f_name.replace('.html', '').split('_')[0]
            # Clean up name_part (it might have dashes)
            name_norm = name_part.replace('-', ' ').strip()
            # This is less reliable but might work for Top 14 players
            # Check if any player's name_en slugified matches name_part slugified
            slug = slugify(name_norm)
            
        if slug:
            # Old Path -> New Path
            redirects.append(f"Redirect 301 /player/{f_name} /player/{slug}/")
            
            # Additional safety: if file has a hyphen, also redirect the underscore version
            if '-' in f_name:
                alt_name = f_name.replace('-', '_')
                if alt_name != f_name:
                    redirects.append(f"Redirect 301 /player/{alt_name} /player/{slug}/")
            # If file has an underscore, also redirect the hyphen version
            elif '_' in f_name:
                alt_name = f_name.replace('_', '-')
                if alt_name != f_name:
                    redirects.append(f"Redirect 301 /player/{alt_name} /player/{slug}/")
        else:
            print(f"Could not map: {f_name}")

    output_path = 'data/player_redirects.htaccess'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(redirects))
    
    print(f"Generated {len(redirects)} redirect rules in {output_path}")

if __name__ == "__main__":
    generate_redirect_map()
