""" Creates batches of images to feed into the training network conditioned by genre, uses upsampling when creating batches to account for uneven distributuions """


import numpy as np
import imageio
import time
import random
import os
from pathlib import Path
from PIL import Image

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

# Set the dimension of images you want to be passed in to the network
DIM = 64

# Set your own path to images
src_img_path = os.path.normpath(settings.RESIZED_IMAGES_PATH)

# This dictionary should be updated to hold the absolute number of images associated with each genre used during training
styles = {
    "dataset": 300,
}

styleNum = {k: i for i, k in enumerate(styles.keys())}

curPos = {k: 0 for k in styles.keys()}

testNums = {}
trainNums = {}

# Generate test set of images made up of 1/20 of the images (per genre)
for k, v in styles.items():
    # put a twentieth of paintings in here
    nums = range(v)
    random.shuffle(list(nums))
    testNums[k] = nums[0 : v // 20]
    trainNums[k] = nums[v // 20 :]


def inf_gen(gen):
    while True:
        for (images, labels) in gen():
            yield images, labels


def make_generator(files, batch_size, n_classes):
    if batch_size % n_classes != 0:
        raise ValueError(
            "Batch size {} must be divisible by num classes {}".format(batch_size, n_classes)
        )

    class_batch = batch_size // n_classes

    generators = []

    def get_epoch():

        while True:

            images = np.zeros((batch_size, 3, DIM, DIM), dtype="int32")
            labels = np.zeros((batch_size, n_classes))
            n = 0
            for style in styles:
                styleLabel = styleNum[style]
                curr = curPos[style]
                for _ in range(class_batch):
                    if curr == styles[style]:
                        curr = 0
                        random.shuffle(list(files[style]))

                    img_path = Path(src_img_path, style, str(curr) + ".png")
                    image = Image.open(img_path).convert(mode="RGB")
                    image = np.asarray(image)

                    images[n % batch_size] = image.transpose(2, 0, 1)
                    labels[n % batch_size, int(styleLabel)] = 1
                    n += 1
                    curr += 1
                curPos[style] = curr

            # randomize things but keep relationship between a conditioning vector and its associated image
            rng_state = np.random.get_state()
            np.random.shuffle(images)
            np.random.set_state(rng_state)
            np.random.shuffle(labels)
            yield (images, labels)

    return get_epoch


def load(batch_size):
    return (
        make_generator(trainNums, batch_size, len(styles)),
        make_generator(testNums, batch_size, len(styles)),
    )


# Testing code to validate that the logic in generating batches is working properly and quickly
if __name__ == "__main__":
    train_gen, valid_gen = load(100)
    t0 = time.time()
    for i, batch in enumerate(train_gen(), start=1):
        a, b = batch
        print("time ", str(time.time() - t0))
        if i == 1000:
            break
        t0 = time.time()
