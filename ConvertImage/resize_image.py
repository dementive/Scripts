from PIL import Image

im = Image.open('input/test.png')

newsize = (850, 850)
im2 = im.resize((newsize), resample=Image.BOX)

# im2 = im.resize( [int(4 * s) for s in im.size] )

im2 = im2.save("output/test.png")
