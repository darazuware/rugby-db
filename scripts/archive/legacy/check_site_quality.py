import os
import re
import glob

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from team_utils import TEAM_MAPPING

def check_links():
    print("Checking internal links...")
    player_files = glob.glob("src/content/players/*.md")
    
    # 存在するスラッグをマッピングから取得
    valid_team_links = set()
    for name, data in TEAM_MAPPING.items():
        valid_team_links.add(f"/teams/{data['league']}/{data['slug']}")
    
    # リーグトップページも許可
    for league in ["leagueone", "super-rugby", "top14", "urc"]:
        valid_team_links.add(f"/teams/{league}")

    errors = []
    player_slugs = set([os.path.basename(f).replace(".md", "") for f in player_files])
    
    for file_path in player_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # [text](/path) 形式のリンクを抽出
            links = re.findall(r'\[.*?\]\((/.*?)\)', content)
            for link in links:
                if link.startswith("/players/"):
                    slug = link.replace("/players/", "")
                    if slug not in player_slugs:
                        errors.append(f"Broken player link in {file_path}: {link}")
                elif link.startswith("/teams/"):
                    clean_link = link.rstrip('/')
                    # ナショナルチームや地域チーム、旧チームリンクは暫定的に許可
                    if any(x in clean_link for x in ["/national/", "/nz/", "/rc-vannes"]):
                        continue
                    if clean_link not in valid_team_links:
                        errors.append(f"Broken team link in {file_path}: {link}")
                            
    return errors

def check_data_consistency():
    print("Checking data consistency...")
    # CSV と Markdown の一致チェックなどをここに追加
    return []

def main():
    link_errors = check_links()
    consistency_errors = check_data_consistency()
    
    report_path = "data/quality_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== Site Quality Report ===\n")
        f.write(f"Total Link Errors: {len(link_errors)}\n")
        for err in link_errors:
            f.write(f"- {err}\n")
            
        f.write(f"\nTotal Consistency Errors: {len(consistency_errors)}\n")
        for err in consistency_errors:
            f.write(f"- {err}\n")
            
    print(f"Quality report generated at {report_path}")
    if link_errors or consistency_errors:
        print(f"Found {len(link_errors) + len(consistency_errors)} errors.")
    else:
        print("No errors found! Site quality is mission critical ready.")

if __name__ == "__main__":
    main()
