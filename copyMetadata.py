import exiftool
import sys

def copy_metadata(source_path, target_path):
    try:
        with exiftool.ExifTool() as et:
            et.execute("-TagsFromFile", source_path, "-All:All", target_path)
        
        print(f"Metadata copied from '{source_path}' to '{target_path}' successfully.")

    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    copy_metadata(sys.argv[1], sys.argv[2])