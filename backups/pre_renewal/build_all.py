import os
import sys
import subprocess

def run_script(path, args=None):
    cmd = [sys.executable, path]
    if args:
        cmd.extend(args)
    
    print(f"--- Running: {os.path.basename(path)} ---")
    env = os.environ.copy()
    env["PYTHONPATH"] = "scripts"
    
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"Error in {path}")
        return False
    return True

def main():
    # 実行順序が重要
    scripts = [
        "scripts/generators/generate_index_pages.py",
        "scripts/generators/generate_player_pages.py",
        "scripts/generators/generate_school_pages.py"
    ]
    
    for s in scripts:
        if not run_script(s):
            sys.exit(1)
            
    print("\n✓ All pages generated successfully!")

if __name__ == "__main__":
    main()
