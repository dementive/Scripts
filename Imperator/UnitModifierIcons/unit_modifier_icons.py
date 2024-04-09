# import os
# from PIL import Image, ImageOps
# from tqdm import tqdm


# class ImageManager:
#     def __init__(self, inputdir, outputdir):
#         self.inputdir = inputdir
#         self.outputdir = outputdir

#     def get_pbar(self, filter_func=lambda x: x):
#         pbar = []
#         for file in os.scandir(path=self.inputdir):
#             pbar.append(file.path)
#         pbar = [x for x in pbar if filter_func]
#         progressbar = tqdm(pbar)
#         return progressbar

#     def get_file_name(self, filename):
#         inputdir_rel = self.inputdir.rpartition("/")[2]
#         return f"{self.outputdir}/{filename}".replace(inputdir_rel, "")

#     def create_terrain_icons(self, downscale_factor):
#         for filename in self.get_pbar():
#             image = Image.open(filename)
#             downscaled_image = image.resize(
#                 (image.size[0] // downscale_factor, image.size[1] // downscale_factor)
#             )
#             downscaled_image.save(self.get_file_name(filename))

from PIL import Image
from pathlib import Path


def create_terrain_icon(unit_icon, terrain_icon):
    unit_image = Image.open(unit_icon)
    terrain_image = Image.open(terrain_icon)

    resized_terrain = terrain_image.resize((30, 30))
    resized_unit = unit_image.resize((25, 25))

    new_image = Image.new("RGBA", (50, 50))

    position = (0, new_image.height - resized_terrain.height)
    new_image.paste(resized_terrain, position)

    position2 = (
        new_image.width - resized_unit.width + 1,
        -1,
    )
    new_image.alpha_composite(resized_unit, position2)

    new_image.save(f"output/{unit_icon.stem}_{terrain_icon.stem}_combat_bonus.dds")


def create_other_unit_icon(unit_icon, other_icon):
    unit_image = Image.open(unit_icon)
    icon_image = Image.open(other_icon)

    resized_unit = unit_image.resize((30, 30))

    new_image = icon_image

    position = (0, new_image.height - resized_unit.height)
    new_image.alpha_composite(resized_unit, position)

    new_image.save(f"output/{unit_icon.stem}_{other_icon.stem}.dds")


# create_other_unit_icon()


def get_files_in_directory(directory):
    # Create a Path object for the directory
    directory_path = Path(directory)

    # Get the list of files in the directory
    files = [file for file in directory_path.iterdir() if file.is_file()]

    return files


other_modifier_icons = get_files_in_directory("other_modifier_icons")
terrain_icons = get_files_in_directory("terrain_icons")
unit_icons = get_files_in_directory("unit_icons")

for i in unit_icons:
    for j in terrain_icons:
        create_terrain_icon(i, j)

# for i in unit_icons:
#     for j in other_modifier_icons:
#         create_other_unit_icon(i, j)
