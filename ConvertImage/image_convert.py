# Convert Images in input directory to different formats and optionally compress or resize them.

import os
import re
from wand import image
from tqdm import tqdm


def convert_images_in_dir(old, new, compress=False, resize=False, new_file_name=False):
    if compress:
        pass
        c_str = "and compressing"
    else:
        c_str = ""

    print(f"Converting {c_str} {old} files to {new} files...")
    pbar = []

    for file in os.scandir(path="input"):
        if file.name.endswith(old):
            filename = file.path
            pbar.append(file.path)

    progressbar = tqdm(pbar)
    for i, filename in enumerate(progressbar):
        # Compress
        if compress:
            with image.Image(filename=filename) as img:
                img.compression_quality = 80  # doesn't work for .png
                img.save(filename=filename)

        # Resize
        if resize:
            with image.Image(filename=filename) as img:
                img.resize(1224, 950)
                img.save(filename=filename)
        # Convert
        with image.Image(filename=filename) as img:
            filename = filename.replace(old, new).replace("input", "output")
            if new == ".dds":
                img.options['dds:mipmaps'] = '0'
                img.options['dds:compression'] = 'dxt1'  # dxt1/dxt3/dxt5
            if new_file_name:
                filename = re.sub(new_file_name[0], f"{new_file_name[1]}{i + 1}", filename)
                img.save(filename=filename)
            else:
                img.save(filename=filename)


if __name__ == '__main__':
    convert_images_in_dir(".png", ".jpg", resize=True)
