from PIL import Image
import os 

def cut_images(target_directory, output_directory, tile_size=(320, 320)):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(target_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(target_directory, filename)
            with Image.open(image_path) as img:
                for i in range(0, img.width, tile_size[0]):
                    for j in range(0, img.height, tile_size[1]):
                        box = (i, j, min(i + tile_size[0], img.width), min(j + tile_size[1], img.height))
                        cut_image = img.crop(box)
                        if cut_image.size == tile_size:
                            cut_image.save(os.path.join(output_directory, f'{filename[:-4]}_{i}_{j}.png'))



if __name__ == "__main__":
    target_directory = None
    output_directory = None
    while True:
        target_directory = input("Enter target directory: ")
        if os.path.exists(target_directory):
            break
        else:
            print("Invalid path for target directory.")

    output_directory = input("Enter output directory: ")
    print()

    cut_images(target_directory, output_directory)
    