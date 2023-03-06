import argparse
import os
import random

from PIL import Image
from PIL import ImageFont, ImageDraw, ImageColor

MARGIN = 4

MIDDLE = 'middle'  # index 0 on UI
TOP = 'top'        # 1 on UI
BOTTOM = 'bottom'  # 2 on UI
EVERYWHERE_RANDOM = 'everywhere randomly'  # 3 on UI


class Watermark:
    def __init__(self):
        self.text_color = None
        self.back_color = None
        self.font = None

    def add(self, image: Image, watermark_position: int, watermark_text: str, transparency: int) -> Image:
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        w, h = image.size
        x, y = int(w / 2), int(h / 2)
        if x > y:
            font_size = y
        elif y > x:
            font_size = x
        else:
            font_size = x

        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.font = ImageFont.truetype(f"{this_dir}/arial.ttf", int(font_size / 12))
        draw = ImageDraw.Draw(image, "RGBA")
        text_width, text_height = draw.textsize(watermark_text, font=self.font)
        self.back_color = ImageColor.getrgb("pink") + (transparency,)
        self.text_color = ImageColor.getrgb("black") + (transparency,)

        if watermark_position == EVERYWHERE_RANDOM:
            y = 0
            count = int(image.height / (4 * text_height + 4))
            for i in range(count):
                x = random.randint(0, image.width - text_width)
                y += 4 * text_height + 2
                image = self.draw_one_watermark(image, text_height, text_width,
                                                watermark_text, x, y)
            return image
        x = 0
        y = 0
        if watermark_position == MIDDLE:
            x = (image.width - text_width) / 2
            y = (image.height + text_height) / 2
        if watermark_position == TOP:
            x = (image.width - text_width) / 2
            y = 0
        if watermark_position == BOTTOM:
            x = (image.width - text_width) / 2
            y = image.height - text_height
        image = self.draw_one_watermark(image, text_height, text_width, watermark_text, x, y)
        return image

    def draw_one_watermark(self, image: Image, text_height: int,
                           text_width: int, watermark_text: str, x: int, y: int) -> Image:
        txt_img = Image.new("RGBA", (image.width, image.height), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.rounded_rectangle((x - MARGIN, y - MARGIN, x + text_width + MARGIN, y + text_height + MARGIN),
                                   MARGIN - 1, fill=self.back_color)
        txt_draw.text((x, y), watermark_text, fill=self.text_color, font=self.font)
        return Image.alpha_composite(image, txt_img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', default='faked tg.me/dsxquyibot')
    parser.add_argument('--transparency', default='30')
    parser.add_argument('--position', default='bottom')
    parser.add_argument('--image-path')
    parser.add_argument('--out')
    args = parser.parse_args()
    watermark = Watermark()
    print(args.image_path)
    img = Image.open(args.image_path)
    img = watermark.add(img, watermark_position=args.position, watermark_text=args.text,
                        transparency=int(args.transparency))
    img.save(args.out)
