import sys
import os
import re
from wand import image as WandImage
from PIL import Image, ImageOps
from tqdm import tqdm

class ImageManager:

	def __init__(self, inputdir, outputdir):
		self.inputdir = inputdir
		self.outputdir = outputdir

	def get_pbar(self, filter_func=False):
		pbar = []
		for file in os.scandir(path=self.inputdir):
			pbar.append(file.path)
		if filter_func:
			pbar = list(filter(filter_func, pbar))
		progressbar = tqdm(pbar)
		return progressbar

	def get_file_name(self, filename):
		inputdir_rel = self.inputdir.rpartition("\\")[2]
		return f'{self.outputdir}\\{filename}'.replace(inputdir_rel, "")

	def add_mask(self, mask_file):
		for i, filename in enumerate(self.get_pbar()):
			src = Image.open(filename)
			mask = Image.open(mask_file)
			mask = mask.convert("L")
			width, height = src.size

			mask = mask.resize(src.size, Image.BILINEAR)
			out = ImageOps.fit(src, mask.size, centering=(0.5, 0.5))

			out.putalpha(mask)

			if out.mode in ("RGBA") and filename.endswith(".jpg") or filename.endswith(".jpeg"):
				# jpg has no alpha so just save as a png instead, could probably find a better way to add mask to jpg
				filename = filename.replace(".jpg", ".png").replace(".jpeg", ".png")
			out.save(self.get_file_name(filename))

	def split_grid(self, xPieces, yPieces):
		xPieces = int(xPieces)
		yPieces = int(yPieces)

		for i, filename in enumerate(self.get_pbar()):
			fname, file_extension = os.path.splitext(filename)
			im = Image.open(filename)
			imgwidth, imgheight = im.size
			height = imgheight // yPieces
			width = imgwidth // xPieces
			for i in range(0, yPieces):
				for j in range(0, xPieces):
					box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
					a = im.crop(box)
					a.save(self.get_file_name(fname) + "-" + str(i) + "-" + str(j) + file_extension)

	def compress_images_in_dir(self, filetype, dds_compression=""):
		# Only works for .png, .jpg, or .dds files
		pbar = self.get_pbar(lambda f: True if f.endswith(filetype) else False)
		for i, filename in enumerate(pbar):
			if filetype == ".dds":
				with WandImage.Image(filename=filename) as img:
					img.options['dds:mipmaps'] = '0'
					img.options['dds:compression'] = dds_compression  # dxt1/dxt3/dxt5
					img.save(filename=self.get_file_name(filename))
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

				filename = self.get_file_name(filename)
				if im.mode in ("RGBA", "p"):
					im2.save(filename, "PNG")
				elif im.mode in ("RGB"):
					im2.save(filename, "JPEG")

	def resize_images_in_dir(self, resize_x, resize_y):
		resize_x = int(resize_x)
		resize_y = int(resize_y)
		for i, filename in enumerate(self.get_pbar()):
			with WandImage.Image(filename=filename) as img:
				img.resize(resize_x, resize_y)
				filename = filename.replace(self.inputdir, self.outputdir)
				img.save(filename=filename)

	def convert_images_in_dir(self, old, new):
		pbar = self.get_pbar(lambda f: True if f.endswith(old) else False)
		for i, filename in enumerate(pbar):
			with WandImage.Image(filename=filename) as img:
				filename = filename.replace(old, new).replace(self.inputdir, self.outputdir)
				img.save(filename=filename)

def terminal_green(string):
	return "\033[92m{}\033[00m".format(string)

def terminal_cyan(string):
	return "\033[96m{}\033[00m".format(string)

def main():
	try:
		input_dir = sys.argv[1]
		output_dir = sys.argv[2]
		mode = sys.argv[3]
		if mode not in ("-convert", "-grid", "-mask", "-compress", "-resize"):
			raise (RuntimeError)

		match mode:
			case "-mask":
				mask_file = sys.argv[4]
			case "-grid":
				grid_x = sys.argv[4]
				grid_y = sys.argv[5]
			case "-convert":
				input_format = sys.argv[4]
				if not input_format.startswith("."):
					input_format = "." + input_format
				output_format = sys.argv[5]
				if not output_format.startswith("."):
					output_format = "." + output_format
			case "-compress":
				compress_format = sys.argv[4]
				dds_compression = "dxt5"
				if not compress_format.startswith("."):
					compress_format = "." + compress_format
				if compress_format == ".dds":
					enter_dds = terminal_green("Enter DDS Compression format ")
					dds_formats = terminal_cyan("dxt1/dxt3/dxt5")
					dds_compression = input(f"\n{enter_dds}({dds_formats}): ")
			case "-resize":
				resize_x = sys.argv[4]
				resize_y = sys.argv[5]

	except (IndexError, RuntimeError):
		print("Incorrect arguments. Valid arguments are: -convert, -grid, -mask, -compress, or -resize")
		return

	im = ImageManager(input_dir, output_dir)
	match mode:
		case "-mask":
			im.add_mask(mask_file)
		case "-grid":
			im.split_grid(grid_x, grid_y)
		case "-convert":
			im.convert_images_in_dir(input_format, output_format)
		case "-compress":
			im.compress_images_in_dir(compress_format, dds_compression)
		case "-resize":
			im.resize_images_in_dir(resize_x, resize_y)

if __name__ == '__main__':
	main()
