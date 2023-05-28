from PIL import Image

image = Image.open('input/heightmap.png')
downscale_factor = 4
downscaled_image = image.resize((image.size[0] // downscale_factor, image.size[1] // downscale_factor))
downscaled_image.save('output/heightmap.png')
