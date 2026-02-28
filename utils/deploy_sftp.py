import os
import ftplib
import sys

# ==========================================
# CONFIGURATION
# ==========================================
HOST = 'ftp.your-server.com'
USER = 'your-username'
PASS = 'your-password'
REMOTE_DIR = 'public_html/rugbypick.com' # Change this to your target folder
LOCAL_DIR = 'pages'
# ==========================================

def upload_files(ftp, local_path, remote_path):
    # Ensure remote dir exists
    try:
        ftp.mkd(remote_path)
        print(f"Created remote directory: {remote_path}")
    except:
        pass # Directory likely exists
    
    ftp.cwd(remote_path)
    
    for item in os.listdir(local_path):
        local_item = os.path.join(local_path, item)
        
        if os.path.isfile(local_item):
            print(f"Uploading: {item}")
            with open(local_item, 'rb') as f:
                ftp.storbinary(f'STOR {item}', f)
        elif os.path.isdir(local_item):
            upload_files(ftp, local_item, item)
            ftp.cwd('..') # Go back up after finishing subdirectory

def main():
    print(f"Connecting to {HOST}...")
    try:
        ftp = ftplib.FTP(HOST)
        ftp.login(USER, PASS)
        print("Connected!")
        
        # Determine upload root
        # ftp.cwd(REMOTE_DIR) # Uncomment if you want to upload INTO a specific folder
        
        print(f"Starting upload from local '{LOCAL_DIR}' to remote server...")
        upload_files(ftp, LOCAL_DIR, REMOTE_DIR)
        
        # Upload index.html separately as it is in root
        if os.path.exists('index.html'):
             print("Uploading root index.html...")
             with open('index.html', 'rb') as f:
                ftp.storbinary('STOR index.html', f)

        print("\nUpload Complete!")
        ftp.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if HOST == 'ftp.your-server.com':
        print("Please edit this script and set your HOST, USER, and PASS.")
    else:
        main()
