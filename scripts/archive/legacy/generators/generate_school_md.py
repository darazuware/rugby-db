import json
import os
import hashlib
from player_utils import (
    slugify, clean_team_name, load_unified_players, 
    get_player_score, get_team_slug, get_canonical_school_name,
    get_normalized_school_name, calculate_age, get_pos_rank,
    get_school_slug
)

# Load data
players = load_unified_players()
with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
    teams_detailed = json.load(f)

CONTENT_BASE = 'content/schools'
os.makedirs(CONTENT_BASE, exist_ok=True)

# Grouping logic
schools = {} # canonical -> [players]
school_types = {} # canonical -> "高校" or "大学"
prev_names_map = {} # canonical -> set(normalized)

for p in players:
    if get_player_score(p) < 2: continue
    
    def process_s(raw_name, s_type):
        if not raw_name or raw_name == '-': return
        norm = get_normalized_school_name(raw_name) or raw_name
        can = get_canonical_school_name(norm) or norm
        
        if can not in schools: schools[can] = []
        schools[can].append(p)
        school_types[can] = s_type
        
        if can != norm:
            if can not in prev_names_map: prev_names_map[can] = set()
            prev_names_map[can].add(norm)
            
    process_s(p.get('high_school'), "高校")
    process_s(p.get('university'), "大学")

def generate_school_md(can_name, alumni, s_type):
    slug = get_school_slug(can_name)
    prev_names = list(prev_names_map.get(can_name, []))
    
    # We still produce the roster table as HTML to maintain the complex data-attributes
    # which are used by the JavaScript filter.
    roster_html = '<div class="players-table-container"><table class="roster-table" id="rosterTable"><thead><tr><th>選手名</th><th>POS</th><th>年齢</th><th>チーム</th></tr></thead><tbody id="players-grid">'
    
    for p in alumni:
        p_name = p.get('name_ja') or p.get('name_en')
        p_en = p.get('name_en', '')
        p_slug = f"{slugify(p_en)}_{p.get('id')}"
        p_pos = p.get('position', '-')
        p_team = clean_team_name(p.get('team', '-'))
        p_age = calculate_age(p.get('birthdate'))
        
        # Determine norm name for this specific school connection
        p_s_norm = ""
        if s_type == "高校":
            p_s_norm = get_normalized_school_name(p.get('high_school')) or p.get('high_school')
        else:
            p_s_norm = get_normalized_school_name(p.get('university')) or p.get('university')

        p_link = f'<a href="../../player/{p_slug}.html">{p_name}</a>' if get_player_score(p) >= 2 else p_name
        
        roster_html += f'<tr class="player-row" data-school-norm="{p_s_norm}"><td>{p_link}</td><td>{p_pos}</td><td>{p_age}歳</td><td>{p_team}</td></tr>'
        
    roster_html += '</tbody></table></div>'

    frontmatter = {
        'title': can_name,
        'layout': 'school',
        'slug': slug,
        'type': s_type,
        'previous_names': prev_names
    }
    
    md_content = f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n"
    md_content += f"# {can_name}\n\n"
    if prev_names:
        md_content += f"**旧校名**: {', '.join(str(p) for p in prev_names)}\n\n"
    md_content += roster_html

    output_path = os.path.join(CONTENT_BASE, f"{slug}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    print(f"Generating {len(schools)} School MDs...")
    for s_name, alumni in schools.items():
        generate_school_md(s_name, alumni, school_types[s_name])
    print("✓ School MDs Complete!")
