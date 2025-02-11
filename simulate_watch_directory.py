import shutil
import time
import os
import sys

def copy_files_one_by_one(source_folder, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)


    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    if not files:
        print(f"No files found in '{source_folder}'. Exiting.")
        return
    
    for file in files:
        source_path = os.path.join(source_folder, file)
        destination_path = os.path.join(destination_folder, file)
        

        shutil.copy2(source_path, destination_path)
        print(f"Copied '{source_path}' to '{destination_path}'")

        time.sleep(4)

    print("All files copied successfully. Exiting.")


if __name__ == "__main__":
    copy_files_one_by_one(sys.argv[1], sys.argv[2])