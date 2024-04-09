# Convert Sound in input directory to different formats and optionally compress.

import os
import sys
from pydub import AudioSegment
from tqdm import tqdm


def convert_audio_in_dir(oldformat, newformat, compress=False):
    if compress:
        pass
        c_str = "and compressing"
    else:
        c_str = ""

    print(f"Converting {c_str} {oldformat} files to {newformat} files...")
    pbar = []
    for file in os.scandir(path="input"):
        if not file.name.endswith("." + oldformat):
            print(f"Skipping {file.name}\n")
            continue
        pbar.append(file.path)

    progressbar = tqdm(pbar)
    seperator = "/" if sys.platform != "win32" else "\\"
    for i, filepath in enumerate(progressbar):
        # To wav
        filepath = os.getcwd() + seperator + filepath
        sound = AudioSegment.from_file(filepath)
        filename = filepath.replace("input", "output").replace(oldformat, newformat)
        new_name = filepath.replace("input\\", "")
        if compress:
            sound.export(filename, format=newformat, bitrate="128k")
        else:
            sound.export(filename, format=newformat)
        if i == 0:
            print(f"\t\t\t\tConverted {new_name} to {newformat}", end='')
        else:
            print(f"\t\tConverted {new_name} to {newformat}", end='')

if __name__ == '__main__':
    #convert_audio_in_dir("wav", "mp3", compress=True)
    convert_audio_in_dir("mp3", "opus", compress=False)
