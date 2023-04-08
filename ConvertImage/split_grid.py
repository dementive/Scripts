from PIL import Image
import os
from tqdm import tqdm


def split_grid(input, xPieces, yPieces):
    pbar = []

    for file in os.scandir(path="input"):
        filename = file.path
        pbar.append(file.path)

    progressbar = tqdm(pbar)
    for i, filename in enumerate(progressbar):
        fname, file_extension = os.path.splitext(filename)
        im = Image.open(filename)
        imgwidth, imgheight = im.size
        height = imgheight // yPieces
        width = imgwidth // xPieces
        for i in range(0, yPieces):
            for j in range(0, xPieces):
                box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
                a = im.crop(box)
                fname = fname.replace("input\\", "output\\")
                a.save(fname + "-" + str(i) + "-" + str(j) + file_extension)


if __name__ == '__main__':
    split_grid("input/", 2, 2)
