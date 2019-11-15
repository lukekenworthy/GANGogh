"""
A script designed to:
1) resize all of the downloaded images to desired dimension (DEFAULT 64x64 pixels) and
2) rename images in folders from 1.png to n.png for ease of use in training
"""

import os
import random
import PIL
from PIL import Image
from pathlib import Path

original_images_dir = Path("./portrait")

# Set your own resized_images_dir
resized_images_dir = Path("./small/")


def resize_image(base_path, dest_path):
    """
    Source: https://opensource.com/life/15/2/resize-images-python
    """
    TARGET_BASEWIDTH = 64

    img = Image.open(base_path)

    # wpercent = TARGET_BASEWIDTH / float(img.size[0])
    # hsize = int((float(img.size[1]) * float(wpercent)))

    img = img.resize((TARGET_BASEWIDTH, TARGET_BASEWIDTH), PIL.Image.ANTIALIAS)
    img.save(dest_path)


for subdir, dirs, files in os.walk(original_images_dir):
    # print(subdir)
    # exit()
    # style = subdir[2:]
    style = subdir
    name = style
    dest_dir = Path.joinpath(resized_images_dir, name)

    if len(style) < 1:
        continue

    dest_dir.mkdir(parents=True, exist_ok=True)

    style = Path(style)
    i = 0
    for f in files:
        source = Path.joinpath(style, f)
        try:
            dest_path = Path.joinpath(dest_dir, str(i) + ".png")
            resize_image(source, dest_path)
            i += 1
        except Exception as e:
            print(e)
            print("missed it: " + source)
