import sys
import os
from PIL import Image, ImageOps
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale
from tqdm import tqdm


class ImageManager:
    def __init__(self, inputdir, outputdir):
        self.inputdir = inputdir
        self.outputdir = outputdir

    def get_pbar(self, filter_func=lambda x: x):
        pbar = []
        for file in os.scandir(path=self.inputdir):
            pbar.append(file.path)
        pbar = [x for x in pbar if filter_func]
        progressbar = tqdm(pbar)
        return progressbar

    def get_file_name(self, filename):
        inputdir_rel = self.inputdir.rpartition("/")[2]
        return f"{self.outputdir}/{filename}".replace(inputdir_rel, "")

    def add_mask(self, mask_file):
        for filename in self.get_pbar():
            src = Image.open(filename)
            mask = Image.open(mask_file)
            mask = mask.convert("L")

            mask = mask.resize(src.size, Image.BILINEAR)
            out = ImageOps.fit(src, mask.size, centering=(0.5, 0.5))

            out.putalpha(mask)

            if (
                out.mode in ("RGBA")
                and filename.endswith(".jpg")
                or filename.endswith(".jpeg")
            ):
                # jpg has no alpha so just save as a png instead, could probably find a better way to add mask to jpg
                filename = filename.replace(".jpg", ".png").replace(".jpeg", ".png")
            out.save(self.get_file_name(filename))

    def add_frame_to_center(self, frame_file):
        for filename in self.get_pbar():
            input_image = Image.open(filename).convert("RGBA")
            frame_image = Image.open(frame_file).convert("RGBA")

            frame_size = frame_image.size
            input_size = input_image.size
            frame_pos = (
                (input_size[0] - frame_size[0]) // 2,
                (input_size[1] - frame_size[1]) // 2,
            )

            crop_box = (
                frame_pos[0],
                frame_pos[1],
                frame_pos[0] + frame_size[0],
                frame_pos[1] + frame_size[1],
            )

            input_image = input_image.crop(crop_box)

            output_image = Image.new("RGBA", frame_size)
            output_image.paste(input_image, (0, 0), input_image)
            output_image.paste(frame_image, (0, 0), frame_image)

            output_image.save(self.get_file_name(filename))

    def split_grid(self, xPieces, yPieces):
        xPieces = int(xPieces)
        yPieces = int(yPieces)

        for i, filename in enumerate(self.get_pbar()):
            fname, file_extension = os.path.splitext(filename)
            image = Image.open(filename)
            imgwidth, imgheight = image.size
            height = imgheight // yPieces
            width = imgwidth // xPieces
            for i in range(0, yPieces):
                for j in range(0, xPieces):
                    box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
                    a = image.crop(box)
                    a.save(
                        self.get_file_name(fname)
                        + "-"
                        + str(i)
                        + "-"
                        + str(j)
                        + file_extension
                    )

    def compress_images_in_dir(self, filetype, dds_compression=""):
        pbar = self.get_pbar(lambda f: True if f.endswith(filetype) else False)
        for filename in pbar:
            save_filename = self.get_file_name(filename)
            if filetype == ".dds":
                # DDS files get compressed differently
                image = Image.open(filename)
                image2 = image.convert(dds_compression.upper())
                image2.save(save_filename)
            elif filetype in (".jpg", ".jpeg", ".png"):
                # Not entirely sure how this works but it's really good lossless png and jpg compression
                abs_image_path = os.getcwd() + "/" + filename

                image = Image.open(abs_image_path, "r")
                pix_val = list(image.getdata())

                templs = [round(x, -1) for sets in pix_val for x in sets]
                if image.mode in ("RGBA", "p"):
                    new_pix = list(
                        tuple(templs[i : i + 4]) for i in range(0, len(templs), 4)
                    )
                elif image.mode in ("RGB"):
                    new_pix = list(
                        tuple(templs[i : i + 3]) for i in range(0, len(templs), 3)
                    )

                image2 = Image.new(image.mode, image.size)
                image2.putdata(new_pix)

                if image.mode in ("RGBA", "p"):
                    image2.save(save_filename, "PNG")
                elif image.mode in ("RGB"):
                    image2.save(save_filename, "JPEG")
            else:
                image = Image.open(filename, "r")
                image.save(save_filename)

    def resize_images_in_dir(self, resize_x, resize_y):
        resize_x = int(resize_x)
        resize_y = int(resize_y)
        for filename in self.get_pbar():
            image = Image.open(filename)
            image = image.resize((resize_x, resize_y))
            filename = filename.replace(self.inputdir, self.outputdir)
            image.save(filename)

    def downscale_images_in_dir(self, downscale_factor):
        for filename in self.get_pbar():
            image = Image.open(filename)
            downscaled_image = image.resize(
                (image.size[0] // downscale_factor, image.size[1] // downscale_factor)
            )
            downscaled_image.save(self.get_file_name(filename))

    def convert_images_in_dir(self, old, new):
        for filename in self.get_pbar():
            src = Image.open(filename)
            filename = filename.replace(old, new).replace(self.inputdir, self.outputdir)
            src.save(filename)

    def make_all_multiple_of_four(self):
        # For GPU texture compression to work texture resolution must be a multiple of 4
        pbar = self.get_pbar(lambda f: True if f.endswith(old) else False)
        for filename in pbar:
            image = Image.open(filename)
            imgwidth, imgheight = image.size
            while imgwidth % 4 != 0:
                imgwidth -= 1
            while imgheight % 4 != 0:
                imgheight -= 1
            image = image.resize((imgwidth, imgheight))
            image.save(self.get_file_name(filename))

    def tint_images_in_dir(self, tint="#ffffff"):
        for filename in self.get_pbar():
            src = Image.open(filename)
            if src.mode not in ["RGB", "RGBA"]:
                raise TypeError("Unsupported source image mode: {}".format(src.mode))
            src.load()

            tr, tg, tb = getrgb(tint)
            tl = getcolor(tint, "L")  # tint color's overall luminosity
            if not tl:
                tl = 1  # avoid division by zero
            tl = float(tl)  # compute luminosity preserving tint factors
            sr, sg, sb = map(
                lambda tv: tv / tl, (tr, tg, tb)
            )  # per component adjustments

            # create look-up tables to map luminosity to adjusted tint
            # (using floating-point math only to compute table)
            luts = (
                tuple(map(lambda lr: int(lr * sr + 0.5), range(256)))
                + tuple(map(lambda lg: int(lg * sg + 0.5), range(256)))
                + tuple(map(lambda lb: int(lb * sb + 0.5), range(256)))
            )
            lum = grayscale(src)  # 8-bit luminosity version of whole image
            if Image.getmodebands(src.mode) < 4:
                merge_args = (src.mode, (lum, lum, lum))  # for RGB verion of grayscale
            else:  # include copy of src image's alpha layer
                a = Image.new("L", src.size)
                a.putdata(src.getdata(3))
                merge_args = (
                    src.mode,
                    (lum, lum, lum, a),
                )  # for RGBA verion of grayscale
                luts += tuple(range(256))  # for 1:1 mapping of copied alpha values

            result = Image.merge(*merge_args).point(luts)
            filename = filename.replace(self.inputdir, self.outputdir)
            result.save(filename)


def terminal_green(string):
    return "\033[92m{}\033[00m".format(string)


def terminal_cyan(string):
    return "\033[96m{}\033[00m".format(string)


def main():
    try:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        mode = sys.argv[3]
        if mode not in (
            "-convert",
            "-grid",
            "-mask",
            "-compress",
            "-resize",
            "-tint",
            "-frame",
            "-downscale",
        ):
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
            case "-tint":
                tint_color = sys.argv[4]
            case "-frame":
                frame_file = sys.argv[4]
            case "-downscale":
                downscale_factor = int(sys.argv[4])

    except (IndexError, RuntimeError):
        print(
            "Incorrect arguments. Valid arguments are: -convert, -grid, -mask, -compress, -tint, -frame, -downscale, or -resize"
        )
        return

    image = ImageManager(input_dir, output_dir)
    match mode:
        case "-mask":
            image.add_mask(mask_file)
        case "-grid":
            image.split_grid(grid_x, grid_y)
        case "-convert":
            image.convert_images_in_dir(input_format, output_format)
        case "-compress":
            image.compress_images_in_dir(compress_format, dds_compression)
        case "-resize":
            image.resize_images_in_dir(resize_x, resize_y)
        case "-tint":
            image.tint_images_in_dir(tint_color)
        case "-frame":
            image.add_frame_to_center(frame_file)
        case "-downscale":
            image.downscale_images_in_dir(downscale_factor)


if __name__ == "__main__":
    main()
