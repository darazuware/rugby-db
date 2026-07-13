import os
import glob
import re
import yaml # pyyaml

def verify():
    player_files = glob.glob('src/content/players/*.md')
    team_files = glob.glob('src/content/teams/*.md')
    
    team_slugs = {os.path.basename(f).replace('.md', '') for f in team_files}
    
    print(f"Verifying {len(player_files)} player files against {len(team_slugs)} teams...")
    
    league_counts = {}
    errors = []
    for f in player_files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            # フロントマターの分離
            match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
            if not match:
                errors.append(f"{os.path.basename(f)}: Frontmatter not found.")
                continue
                
            fm_text = match.group(1)
            body = match.group(2)
            
            # フロントマターのチェック (簡易)
            try:
                fm = yaml.safe_load(fm_text)
                league = fm.get('league', 'unknown')
                league_counts[league] = league_counts.get(league, 0) + 1
                
                required = ['title', 'team', 'league']
                for req in required:
                    if not fm.get(req):
                        errors.append(f"{os.path.basename(f)}: Missing required field '{req}'")
            except Exception as e:
                errors.append(f"{os.path.basename(f)}: YAML parse error: {e}")
            
            # 本文内リンクのチェック
            links = re.findall(r'\[.+?\]\(/teams/(.+?)\)', body)
            for link in links:
                if link not in team_slugs:
                    errors.append(f"{os.path.basename(f)}: Broken team link '/teams/{link}'")
                    
    print("\nLeague Statistics:")
    for league, count in sorted(league_counts.items()):
        print(f"  - {league}: {count} files")
                    
    if errors:
        print(f"Found {len(errors)} issues:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more.")
    else:
        print("No issues found. Integrity check passed!")

if __name__ == "__main__":
    verify()
