import os.path
import numpy as np
from PIL import Image

if __name__ == '__main__':

    input_1 = "input/test.dds"
    outputPath = "sliced"
    frames = 18
    im = Image.open(input_1)
    x_width, y_height = im.size
    y_height = min([1000, y_height])
    outputFileFormat = "{0}-{1}.png"
    baseName = "frame_1"

    edges = np.linspace(0, x_width, frames+1)
    for i, (start, end) in enumerate(zip(edges[:-1], edges[1:])):
        box = (start, 0, end, y_height)
        a = im.crop(box)
        a.load()
        outputName = os.path.join(outputPath, outputFileFormat.format(baseName, str(i + 1)))
        a.save(outputName, "png")
