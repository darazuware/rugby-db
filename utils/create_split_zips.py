import os
import zipfile
import shutil
import math

# Config
SOURCE_DIR = 'dist'
OUTPUT_DIR = os.path.join('data', 'upload_batches')
FILES_PER_ZIP = 1000

def zip_folder(folder_path, output_path, relative_to=SOURCE_DIR):
    """Zips a folder entirely."""
    print(f"Zipping {folder_path} -> {output_path} ...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.startswith('.'): continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, relative_to)
                zipf.write(file_path, arcname)

def zip_large_folder_split(folder_name, limit=FILES_PER_ZIP):
    """Splits a flat folder into multiple zips if it has many files."""
    folder_path = os.path.join(SOURCE_DIR, folder_name)
    if not os.path.exists(folder_path):
        print(f"Skipping {folder_name} (not found)")
        return

    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.startswith('.')]
    total = len(all_files)
    
    if total <= limit:
        # Just zip it normally
        zip_name = os.path.join(OUTPUT_DIR, f'{folder_name}.zip')
        zip_folder(folder_path, zip_name)
    else:
        chunks = math.ceil(total / limit)
        print(f"Total {total} files in {folder_name}. Splitting into {chunks} zips.")
        for i in range(chunks):
            start = i * limit
            end = start + limit
            batch = all_files[start:end]
            
            zip_name = os.path.join(OUTPUT_DIR, f'{folder_name}_part{i+1}.zip')
            print(f"  Creating {zip_name} ({len(batch)} files)...")
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in batch:
                    file_path = os.path.join(folder_path, file)
                    arcname = os.path.join(folder_name, file)
                    zipf.write(file_path, arcname)

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # 1. Zip folders that are usually small or structured
    folders_to_zip = ['leagues', 'teams', 'positions', 'news', 'ages', 'dates', 'heights', 'pages']
    for folder in folders_to_zip:
        folder_path = os.path.join(SOURCE_DIR, folder)
        if os.path.exists(folder_path):
            zip_name = os.path.join(OUTPUT_DIR, f'{folder}.zip')
            zip_folder(folder_path, zip_name)

    # 2. Large folders that might need splitting
    zip_large_folder_split('player')
    zip_large_folder_split('schools')

    # 3. Root Files
    root_zip_path = os.path.join(OUTPUT_DIR, 'root_files.zip')
    print(f"Creating {root_zip_path} ...")
    with zipfile.ZipFile(root_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        root_items = ['index.html', 'logo.png', 'favicon.ico']
        for item in root_items:
            item_path = os.path.join(SOURCE_DIR, item)
            if os.path.exists(item_path):
                zipf.write(item_path, item)
            elif os.path.exists(item): # Fallback to local root
                zipf.write(item, item)
    
    # 4. Create a README instruction for extraction
    readme_path = os.path.join(OUTPUT_DIR, 'README_UPLOAD.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("RugbyPick Upload Instructions:\n\n")
        f.write("1. Upload all .zip files to your server (usually public_html/ or a subfolder).\n")
        f.write("2. Extract root_files.zip first.\n")
        f.write("3. Extract other zips. Use unzip_pages.php or server file manager.\n")
        f.write("4. Ensure 'player', 'teams', 'leagues', etc. folders are in the same level as index.html.\n")

    print("\nBatch ZIP creation complete!")
    print(f"Files are in '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    main()
