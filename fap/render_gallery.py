#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
import os

GAP_SIZE = 35
MAX_SIZE = 300
FONT_SIZE = 30
TEXT_HEIGHT = 40

def resize_image(image, max_size):
    """Resize an image to fit within max_size while maintaining aspect ratio"""
    ratio = min(max_size / image.width, max_size / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    # temporary
    x, y = new_size
    if x != max_size and y != max_size:
        raise Exception(f'wrong resize: {(image.width, image.height, max_size)}')
    # temporary
    return image.resize(new_size, Image.LANCZOS)


def render_gallery(input_directory, output_path, fontpath):
    files = os.listdir(input_directory)
    square_root = (len(files)) ** 0.5 + 1

    if len(files) < 4:
        max_picture_width = len(files)
    elif square_root < 4:
        max_picture_width = 4
    else:
        max_picture_width = round(square_root+0.5)

    width = max_picture_width * MAX_SIZE + (max_picture_width+1) * GAP_SIZE
    height = ((len(files) - 1) // max_picture_width + 1) * (MAX_SIZE + TEXT_HEIGHT) + ((len(files) - 1) // max_picture_width + 2) * GAP_SIZE

    MAIN = 0xD
    ALPHA = 0xAA
    base_image = Image.new('RGBA', (width, height), color=(MAIN, MAIN, MAIN, ALPHA))
    draw = ImageDraw.Draw(base_image)

    font = ImageFont.truetype(fontpath, FONT_SIZE)

    for i, file in enumerate(files):
        try:
            image = Image.open(f'{input_directory}/{file}')
        except:
            # if the file is not an image, use a placeholder
            image = Image.new('RGBA', (MAX_SIZE, MAX_SIZE), color='gray')

        row = i // max_picture_width
        col = i % max_picture_width
        x = GAP_SIZE + col * (MAX_SIZE + GAP_SIZE)
        y = GAP_SIZE + row * (MAX_SIZE + TEXT_HEIGHT + GAP_SIZE)

        image = resize_image(image, MAX_SIZE)

        # center the image in its allocated space
        paste_x = x + (MAX_SIZE - image.width) // 2
        paste_y = y + (MAX_SIZE - image.height) // 2
        base_image.paste(image, (paste_x, paste_y), image.convert('RGBA'))

        # add text under the image
        text_y = y + MAX_SIZE + 5  # 5 pixels gap between image and text
        text_width = draw.textlength(file, font=font)
        text_x = x + (MAX_SIZE - text_width) // 2  # center the text
        draw.text((text_x, text_y), file, fill='white', font=font)

    base_image.save(output_path)
