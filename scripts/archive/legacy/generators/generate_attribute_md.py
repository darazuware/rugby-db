import json
import os
import re
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score

# Load data
players = load_unified_players()

def generate_attr_md(title, p_list, folder, filename):
    dest_dir = f"content/{folder}"
    os.makedirs(dest_dir, exist_ok=True)
    
    # Sort players
    sorted_p = sorted(p_list, key=lambda x: str(x.get('name_en', '')))
    
    # Table HTML
    table_html = '<table class="roster-table"><thead><tr><th>選手名</th><th>チーム</th><th>ポジション</th></tr></thead><tbody>'
    for p in sorted_p:
        name = p.get('name_ja') or p.get('name_en')
        en = p.get('name_en', '')
        slug = f"{slugify(en)}_{p.get('id')}"
        team = clean_team_name(p.get('team', '-'))
        pos = p.get('position', '-')
        
        link = f'[{name}](../../player/{slug}.html)' if get_player_score(p) >= 2 else name
        table_html += f'<tr><td>{link}</td><td>{team}</td><td>{pos}</td></tr>'
    table_html += '</tbody></table>'

    frontmatter = {'title': title, 'layout': 'attribute'}
    md = f"---\n{json.dumps(frontmatter, ensure_ascii=False, indent=2)}\n---\n\n# {title}\n\n{table_html}"
    
    with open(f"{dest_dir}/{filename}.md", 'w', encoding='utf-8') as f:
        f.write(md)

if __name__ == "__main__":
    years, ages, heights, weights, positions = {}, {}, {}, {}, {}

    for p in players:
        if get_player_score(p) < 2: continue
        
        # Parse logic same as attribute_pages.py
        bdate = str(p.get('birthdate', '')).strip()
        if bdate and bdate != 'nan':
            m = re.search(r'(\d{4})', bdate)
            if m:
                y = m.group(1)
                years.setdefault(y, []).append(p)
                try: ages.setdefault(str(2025 - int(y)), []).append(p)
                except: pass
        
        h = str(p.get('height', '')).replace('cm', '').strip()
        if h and h != 'nan': heights.setdefault(h, []).append(p)
        
        w = str(p.get('weight', '')).replace('kg', '').strip()
        if w and w != 'nan': weights.setdefault(w, []).append(p)
        
        pos_raw = p.get('position')
        if pos_raw and pos_raw != '-':
            for ps in str(pos_raw).replace('/', ',').split(','):
                ps = ps.strip()
                if ps: positions.setdefault(ps, []).append(p)

    print("Generating Attribute/Position MDs...")
    for y, pl in years.items(): generate_attr_md(f"{y}年生まれ", pl, "dates", y)
    for a, pl in ages.items(): generate_attr_md(f"{a}歳", pl, "ages", a)
    for h, pl in heights.items(): generate_attr_md(f"{h}cm", pl, "heights", h)
    for w, pl in weights.items(): generate_attr_md(f"{w}kg", pl, "weights", w)
    for pos, pl in positions.items(): generate_attr_md(f"{pos} 選手一覧", pl, "positions", slugify(pos))
    print("✓ Complete!")
