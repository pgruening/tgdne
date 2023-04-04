import os
from glob import glob
from os.path import basename, join, splitext

import numpy as np
from DLBio.helpers import check_mkdir
from skimage.transform import resize
from tqdm import tqdm

from helpers import crop_to_content, preprocess_image, save_image

IMAGE_FOLDER = 'guitar_images'
TARGET_FOLDER = 'guitar_images_downsampled'
check_mkdir(TARGET_FOLDER)

SPLIT_FILES = 'split_files'
check_mkdir(SPLIT_FILES)

DESIRED_SHAPE = (3 * 148, 148)
PERC_TRAIN = .9


def downsample_and_save():
    for image_path in tqdm(glob(join(IMAGE_FOLDER, '*.jpg'))):
        image = preprocess_image(image_path, to_uint=True)
        image = crop_to_content(image, padding=4)
        image = resize(
            image, DESIRED_SHAPE,
            order=3,  # spline interpolation order
            anti_aliasing=True,  # gaussian filtering before downsampling
            mode='constant', cval=1  # padding with white borders range: [0,1]
        )
        new_filepath = set_ext(
            join(TARGET_FOLDER, basename(image_path)), '.png'
        )
        save_image((255 * image).astype('uint8'), new_filepath)


def create_train_test_splitfiles():
    images_ = list(glob(join(TARGET_FOLDER, '*.png')))

    num_train = round(PERC_TRAIN * len(images_))
    rperm = np.random.permutation(len(images_))

    train = list(np.array(images_)[rperm[:num_train]])
    test = list(np.array(images_)[rperm[num_train:]])

    for name, file_list in {'train': train, 'test': test}.items():
        with open(join(SPLIT_FILES, f'guitar_{name}.txt'), 'w') as file:
            for x in file_list:
                file.write(join(os.getcwd(), x) + '\n')


def set_ext(filepath: str, new_ext: str) -> str:
    out = splitext(filepath)[0]
    return out + '.png'


if __name__ == '__main__':
    # downsample_and_save()
    create_train_test_splitfiles()
