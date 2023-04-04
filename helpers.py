from os.path import basename, splitext

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def get_id(filepath):
    return splitext(basename(filepath))[0]


def preprocess_image(image_path, preprocessor=None, to_uint=False):
    image = Image.open(image_path)
    if not image.mode == "RGB":
        image = image.convert("RGB")
    image = np.array(image).astype(np.uint8)
    if preprocessor is not None:
        image = preprocessor(image=image)["image"]

    if to_uint:
        return image.astype('uint8')

    image = (image / 127.5 - 1.0).astype(np.float32)
    return image


def save_image(image: np.array, filepath: str):
    Image.fromarray(image).save(filepath)


def crop_to_content(image: np.array, padding: int = 0) -> np.array:
    box = get_bounding_box(image, padding=padding)
    return image[box['top']:box['bottom'], box['left']:box['right'], :]


def get_bounding_box(image: np.array, padding: int = 0) -> dict:
    # where the image is not white
    is_content = image.astype('float32').sum(-1) != 3 * 255

    # for each row: determine the min index and the max index
    hs, ws = np.where(is_content)

    h, w, _ = image.shape

    padding = padding // 2

    return {
        'left': max(ws.min() - padding, 0),
        'right': min(ws.max() + padding, w),
        'top': max(hs.min() - padding, 0),
        'bottom': min(hs.max() + padding, h),
    }


def show_crop(image, left, top, right, bottom):
    xy = (left, top)
    w = right - left
    h = bottom - top
    _, ax = plt.subplots(1, figsize=(6, 6))
    ax.imshow(image)
    # plt.axis('off')
    rect = patches.Rectangle(xy, w, h, linewidth=1,
                             edgecolor='r', facecolor='none')

    # Add the patch to the Axes
    ax.add_patch(rect)
