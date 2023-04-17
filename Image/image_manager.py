import sys
import os
import re
import numpy as np
from wand import image as WandImage
from PIL import Image
from tqdm import tqdm

class ImageManager:

	def add_mask(self, mask_file):
		pbar = []

		for file in os.scandir(path="input"):
			filename = file.path
			pbar.append(file.path)

		progressbar = tqdm(pbar)

		for i, filename in enumerate(progressbar):
			src = np.array(Image.open(filename))
			mask = np.array(Image.open(mask_file).resize(src.shape[1::-1], Image.BILINEAR))

			mask = mask / 255
			dst = src * mask
			outfile = f'output\\{filename}'.replace("input\\", "")
			Image.fromarray(dst.astype(np.uint8)).save(outfile)

	def split_grid(self, input, xPieces, yPieces):
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

	def compress_images_in_dir(self, filetype, dds_compression="dxt1"):
		# Only works for .png, .jpg, or .dds files
		print(f"Compressing {filetype} files...")
		pbar = []

		for file in os.scandir(path="input"):
			if file.name.endswith(filetype):
				filename = file.path
				pbar.append(file.path)

		progressbar = tqdm(pbar)
		for i, filename in enumerate(progressbar):
			old_file_name = os.getcwd() + "\\" + filename
			if filetype == ".dds":
				with WandImage.Image(filename=filename) as img:
					img.options['dds:mipmaps'] = '0'
					img.options['dds:compression'] = dds_compression  # dxt1/dxt3/dxt5
					filename = filename.replace("input", "output")
					img.save(filename=filename)
			if filetype in (".jpg", ".jpeg", ".png"):
				abs_image_path = os.getcwd() + "\\" + filename

				(only_image_path, image_info) = os.path.split(abs_image_path)
				im = Image.open(abs_image_path, "r")
				pix_val = list(im.getdata())

				templs = [round(x, -1) for sets in pix_val for x in sets]
				if im.mode in ("RGBA", "p"):
					new_pix = list(tuple(templs[i:i + 4]) for i in range(0, len(templs), 4))
				elif im.mode in ("RGB"):
					new_pix = list(tuple(templs[i:i + 3]) for i in range(0, len(templs), 3))

				im2 = Image.new(im.mode, im.size)
				im2.putdata(new_pix)

				filename = filename.replace(old, new).replace("input", "output")
				if im.mode in ("RGBA", "p"):
					im2.save(filename, "PNG")
				elif im.mode in ("RGB"):
					im2.save(filename, "JPEG")

				im.close()
				im2.close()
			if "_temporaryimagefile" in old_file_name and os.path.exists(old_file_name):
				try:
					os.remove(old_file_name)
				except OSError as e:
					print("Error: %s - %s." % (e.filename, e.strerror))

	def convert_images_in_dir(self, old, new, resize=[], new_file_name=False):

		print(f"Converting {old} files to {new} files...")
		pbar = []

		for file in os.scandir(path="input"):
			if file.name.endswith(old):
				filename = file.path
				pbar.append(file.path)

		progressbar = tqdm(pbar)
		made_temp = False
		for i, filename in enumerate(progressbar):
			# Resize
			if resize:
				with WandImage.Image(filename=filename) as img:
					img.resize(resize[0], resize[1])
					if not made_temp:
						name = filename.split("\\")[1]
						name = name.split(".")[0] + "_temporaryimagefile." + name.split(".")[1]
						filename = filename.split("\\")[0] + "\\" + name
						filename = filename.replace("input", "output")
					img.save(filename=filename)
			# Convert
			with WandImage.Image(filename=filename) as img:
				old_file_name = os.getcwd() + "\\" + filename
				filename = filename.replace(old, new).replace("input", "output").replace("_temporaryimagefile", "")
				if new_file_name:
					filename = re.sub(new_file_name[0], f"{new_file_name[1]}{i + 1}", filename)
					img.save(filename=filename)
				else:
					img.save(filename=filename)
				img.close()
				if "_temporaryimagefile" in old_file_name and os.path.exists(old_file_name):
					try:
						os.remove(old_file_name)
					except OSError as e:
						print("Error: %s - %s." % (e.filename, e.strerror))

def main(im):
	try:
		arg1 = sys.argv[1]
		if arg1 not in ("-convert", "-grid", "-mask", "-compress"):
			raise (IndexError)
		if arg1 == "-convert":
			input_format = sys.argv[2].replace("-", ".")
			output_format = sys.argv[3].replace("-", ".")
		if arg1 == "-compress":
			compress_format = sys.argv[2].replace("-", ".")
			if compress_format == ".dds":
				dds_compression = sys.argv[3].replace("-", "")
	except IndexError:
		print("Incorrect arguments. Valid arguments are: -convert, -grid, -mask, -compress")
		return

	if arg1 == "-mask":
		im.add_mask("masks\\event_picture_alpha_big.dds")

	if arg1 == "-grid":
		im.split_grid("input/", 2, 2)

	if arg1 == "-convert":
		im.convert_images_in_dir(input_format, output_format)

	if arg1 == "-compress":
		if compress_format == ".dds":
			im.compress_images_in_dir(compress_format, dds_compression=dds_compression)
		else:
			im.compress_images_in_dir(compress_format)

if __name__ == '__main__':
	im = ImageManager()
	main(im)
