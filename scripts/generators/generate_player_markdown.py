import json
import os
import re
import hashlib
from player_utils import (
    load_unified_players, slugify, get_enrolment_year, 
    translate_team_name, get_canonical_school_name, 
    get_normalized_school_name,
    translate_nationality, get_team_slug, normalize_position,
    get_school_slug, get_attribute_slug, clean_team_name,
    get_player_team_link_path, process_career_history
)

def format_markdown(player, slug):
    """
    Generate Markdown content with Frontmatter for a player.
    """
    name_ja = player.get('name_ja', '不明')
    name_en = player.get('name_en', 'Unknown')
    
    # helper for cleaning nan
    def clean(val):
        s = str(val).strip()
        if s.lower() in ['nan', '不明', 'none'] or not s:
            return "-"
        return s

    # 1. Team Logic
    team_raw = player.get('team', '')
    team_ja_disp = re.sub(r'[（(]\s*\d{4}.*?[）)]', '', translate_team_name(team_raw)).strip()
    team_ja_disp = "-" if team_ja_disp.lower() == 'nan' else team_ja_disp
    team_link_path = get_player_team_link_path(player)
    
    # 2. Position Logic
    pos_raw = player.get('position', '-')
    pos_norm = normalize_position(pos_raw)
    pos_slug = get_attribute_slug(pos_norm)
    
    # 3. Attributes
    height = clean(player.get('height'))
    weight = clean(player.get('weight'))
    birth = clean(player.get('birthdate'))
    
    # Calculate age and birth year
    birth_year = "-"
    age = "-"
    if birth != '-':
        m = re.search(r'(\d{4})', birth)
        if m:
            birth_year = m.group(1)
            try:
                # Based on 2026 current year
                age = str(2026 - int(birth_year))
            except:
                pass
    
    # 4. School Logic
    hs_raw = clean(player.get('high_school'))
    hs_disp = get_normalized_school_name(hs_raw) or hs_raw
    hs_canonical = get_canonical_school_name(hs_raw) or hs_raw
    hs_slug = get_school_slug(hs_canonical)
    
    univ_raw = clean(player.get('university'))
    univ_disp = get_normalized_school_name(univ_raw) or univ_raw
    univ_canonical = get_canonical_school_name(univ_raw) or univ_raw
    univ_slug = get_school_slug(univ_canonical)
    
    rep_caps = clean(player.get('representative_caps', '-'))
    career_entries = process_career_history(player.get('career_history', []))
    
    # 5. Entrance Year
    start_year = get_enrolment_year(player)
    if not start_year or start_year == "????":
        start_year = "2025"
    
    current_team_display = f"{team_ja_disp} ({start_year}-)"
    
    # 6. Links
    team_link = f"[{team_ja_disp}]({team_link_path})" if team_link_path and team_ja_disp != '-' else team_ja_disp
    pos_link = f"[{pos_norm}](/positions/{pos_slug}.html)" if pos_slug and pos_norm != '-' else pos_norm
    
    height_link = f"[{height}cm](/heights/{height}.html)" if height != '-' else "-"
    weight_link = f"[{weight}kg](/weights/{weight}.html)" if weight != '-' else "-"
    age_link = f"[{age}歳](/ages/{age}.html)" if age != '-' else "-"
    birth_year_link = f"[{birth_year}年](/dates/{birth_year}.html)" if birth_year != '-' else "-"
    
    hs_link = f"[{hs_disp}](/schools/{hs_slug}.html)" if hs_slug and hs_disp != '-' else hs_disp
    univ_link = f"[{univ_disp}](/schools/{univ_slug}.html)" if univ_slug and univ_disp != '-' else univ_disp
    
    # Frontmatter
    md = "---\n"
    md += f"title: \"{name_ja} ({name_en})\"\n"
    md += f"name_ja: \"{name_ja}\"\n"
    md += f"name_en: \"{name_en}\"\n"
    md += f"team_ja: \"{team_ja_disp}\"\n"
    md += f"team_display: \"{current_team_display}\"\n"
    md += f"position: \"{pos_norm}\"\n"
    md += f"height: \"{height}\"\n"
    md += f"weight: \"{weight}\"\n"
    md += f"birthdate: \"{birth}\"\n"
    md += f"high_school: \"{hs_canonical}\"\n"
    md += f"university: \"{univ_canonical}\"\n"
    md += f"rep_caps: \"{rep_caps}\"\n"
    md += f"layout: player\n"
    md += f"slug: \"{slug}\"\n"
    md += "---\n\n"
    
    # Content body
    md += "### プロフィール\n\n"
    md += "| 項目 | 内容 |\n"
    md += "| :--- | :--- |\n"
    md += f"| **英語名** | {name_en} |\n"
    md += f"| **生年月日** | {birth} |\n"
    md += f"| **ポジション** | {pos_link} |\n"
    md += f"| **所属チーム** | {team_link} ({start_year}-) |\n"
    md += f"| **身長/体重** | {height_link} / {weight_link} |\n"
    md += f"| **生年/年齢** | {birth_year_link} / {age_link} |\n"
    md += f"| **出身高校** | {hs_link} |\n"
    if univ_canonical != '-':
        md += f"| **出身大学** | {univ_link} |\n"
    
    md += "\n### 代表歴\n\n"
    md += f"{rep_caps if rep_caps != '-' else 'なし'}\n\n"
    
    md += "### チーム遍歴\n\n"
    if career_entries:
        for entry in career_entries:
            team = entry['team']
            s = entry['start']
            e = entry['end']
            
            period = f"({s}-)" if s != 9999 and not e else ""
            if s != 9999 and e:
                period = f"({s}-{e})"
            
            md += f"- {team} {period}\n".strip() + "\n"
    else:
        md += "- なし\n"
    
    md += "\n---\n"
    md += "*この選手情報は RUGBY PICKS のデータベースから自動生成されました。*\n"
    
    return md

def main():
    print("Generating Player Markdown files with verified plural paths...")
    players = load_unified_players()
    
    output_dir = 'content/player'
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    for p in players:
        src = p.get('source')
        team_name = str(p.get('team') or '')
        is_league_one = False
        if src == 'league_one': is_league_one = True
        if "浦安" in team_name or "サントリー" in team_name or "パナソニック" in team_name: is_league_one = True
        if str(p.get('id', '')).startswith('lo_'): is_league_one = True
        
        if not is_league_one: continue
        
        name_en = p.get('name_en', 'unknown')
        p_id = p.get('id', '')
        slug = f"{slugify(name_en)}_{p_id}"
        file_path = os.path.join(output_dir, f"{slug}.md")
        
        content = format_markdown(p, slug)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
        
    print(f"Successfully generated {count} markdown files in {output_dir}")

if __name__ == "__main__":
    main()
