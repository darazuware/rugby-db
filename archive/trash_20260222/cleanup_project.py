import os
import shutil
import glob

# Configuration
FOLDERS = {
    'logs': ['*log', '*.txt'],
    'archive': ['test_*.py', 'debug_*.py', 'inspect_*.py', 'list_models.py', 'pages.zip', 'sample_pages'],
    'data_sources': ['*.xlsx', '*.csv', 'team_colors_raw.json', 'rugby_checkpoint.json'],
    'utils': ['create_split_zips.py', 'deploy_sftp.py', 'unzip.php']
}

# Exemptions (Files to KEEP in root)
KEEP_FILES = [
    'unified_player_database_final.json',  # Master DB
    'rugby_players.json',
    'rugby_teams.json',
    'rugby_leagues.json',
    'news_article_1_transfer.txt', # Used by news system demo? Actually logs/txt catches this.
    'requirements.txt',
    'venv'
]

def main():
    print("Starting cleanup...")
    
    # Create directories
    for folder in FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

    # Move files
    for folder, patterns in FOLDERS.items():
        for pattern in patterns:
            # Handle both files and directories
            for match in glob.glob(pattern):
                if match in FOLDERS: continue # Don't move the folders themselves
                if match in KEEP_FILES: continue
                if match == "cleanup_project.py": continue
                if match == "unified_player_database_final.json": continue # Safety
                
                # Check if it's a main script or database implied by wildcard
                # e.g. *.csv matches the master data
                if "unified_player_database" in match and "final" in match: continue
                
                dest = os.path.join(folder, match)
                
                try:
                    shutil.move(match, dest)
                    print(f"Moved {match} -> {folder}/")
                except Exception as e:
                    print(f"Error moving {match}: {e}")

    print("\nCleanup complete!")
    print("Core scripts and master data remain in the root directory.")

if __name__ == "__main__":
    main()
