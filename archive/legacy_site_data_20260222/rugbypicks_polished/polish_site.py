import subprocess
import sys
import time
import os

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    start = time.time()
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✓ {script_name} finished in {time.time() - start:.1f}s\n")
    except subprocess.CalledProcessError as e:
        print(f"!!! Error running {script_name}: {e}")
        sys.exit(1)

def main():
    print("Starting Site Polish Sequence...")
    
    # 1. Clean Stale News (Important!)
    print("Cleaning stale news categories...")
    os.system("rm -rf pages/category")
    
    # 2. Generators
    scripts = [
        "scripts/generate_player_pages.py", # Base content
        "scripts/generate_team_pages.py",
        "scripts/generate_league_pages.py",
        "scripts/generate_news_article_pages.py", # New content
        "scripts/generate_index_pages.py", # Navigation & Indices
        "scripts/fix_missing_mauger.py" # Manual fix
    ]
    
    for s in scripts:
        run_script(s)

    # 3. Check Links
    print("Verifying Links...")
    os.system("python3 scripts/check_internal_links.py | head -n 20")
    
    print("\n✓ SITE POLISH COMPLETE!")

if __name__ == "__main__":
    main()
