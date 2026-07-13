import subprocess
import time
import sys
import os

def run_step(script_name):
    print(f"\n{'='*50}")
    print(f"Starting: {script_name}")
    print(f"{'='*50}\n")
    start = time.time()
    try:
        subprocess.run([sys.executable, script_name], check=True)
        elapsed = (time.time() - start) / 60
        print(f"\n>>> {script_name} completed in {elapsed:.1f} minutes.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n!!! Error running {script_name}: {e}")
        sys.exit(1) 

def main():
    print("Starting Deep Data Merge & Site Update...")
    
    # 1. Merge the deep data (Wiki + Youth)
    if os.path.exists('player_history_deep.json') or os.path.exists('foreign_youth_data.json'):
        run_step("merge_deep_data.py")
    else:
        print("Warning: No deep data files found yet. Scrapers might still be running.")
        val = input("Continue anyway? (y/n): ")
        if val.lower() != 'y':
            sys.exit(0)

    # 2. Regenerate the site
    run_step("finalize_site.py")
    
    print("\n" + "="*50)
    print("UPDATE COMPLETE")
    print("New data (Schools, U20 stats) is now live on the site.")
    print("="*50)

if __name__ == "__main__":
    main()
