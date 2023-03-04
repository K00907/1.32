import random

from PIL import ImageDraw, ImageColor, ImageFont, Image

import gradio as gr

from modules import scripts_postprocessing
from modules.processing import process_images
from modules.ui_components import FormRow

MARGIN = 4

EVERYWHERE_RANDOM = 'everywhere randomly'

BOTTOM = 'bottom'

TOP = 'top'

MIDDLE = 'middle'


class Script(scripts_postprocessing.ScriptPostprocessing):
    order = 4000
    name = "Watermark"
    font = None
    text_color = None
    back_color = None
    transparency = 70

    def ui(self):
        with FormRow():
            info = gr.HTML("<p style=\"margin-bottom:0.75em\">Watermark</p>")

        with FormRow():
            watermark_enabled = gr.Checkbox(label="Enable Watermark", value=True, elem_id="watermark_enabled")

        with FormRow():
            watermark_position = gr.Radio(
                label="Watermark Position", choices=[MIDDLE, TOP, BOTTOM, EVERYWHERE_RANDOM],
                value=MIDDLE, elem_id="watermark_position")

        with FormRow():
            watermark_text = gr.Textbox(label="Watermark Text", lines=1, elem_id="watermark_text")

        with FormRow():
            transparency = gr.Slider(minimum=0, maximum=255, step=1, label="Transparency", value=90,
                                     elem_id="transparency")
        return {"info": info, "watermark_position": watermark_position,
                "watermark_text": watermark_text, "watermark_enabled": watermark_enabled,
                "transparency": transparency}

    def process(self, img: scripts_postprocessing.PostprocessedImage, info,
                watermark_position: str, watermark_text: str, watermark_enabled: bool, transparency: int):
        if not watermark_enabled:
            return img
        if not watermark_text or watermark_text == "":
            return img
        self.transparency = transparency
        img.image = self.add_watermark(img.image, watermark_position, watermark_text)
        return img

    def add_watermark(self, img: Image, watermark_position: int, watermark_text: str):
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        x, y = int(w / 2), int(h / 2)
        if x > y:
            font_size = y
        elif y > x:
            font_size = x
        else:
            font_size = x

        self.font = ImageFont.truetype("arial.ttf", int(font_size / 12))
        draw = ImageDraw.Draw(img, "RGBA")
        text_width, text_height = draw.textsize(watermark_text, font=self.font)
        self.back_color = ImageColor.getrgb("pink") + (self.transparency,)
        self.text_color = ImageColor.getrgb("black") + (self.transparency,)

        if watermark_position == EVERYWHERE_RANDOM:
            y = 0
            count = int(img.height / (4 * text_height + 4))
            for i in range(count):
                x = random.randint(0, img.width - text_width)
                y += 4 * text_height + 2
                img = self.draw_one_watermark(img, text_height, text_width,
                                              watermark_text, x, y)
            return img
        x = 0
        y = 0
        if watermark_position == MIDDLE:
            x = (img.width - text_width) / 2
            y = (img.height + text_height) / 2
        if watermark_position == TOP:
            x = (img.width - text_width) / 2
            y = 0
        if watermark_position == BOTTOM:
            x = (img.width - text_width) / 2
            y = img.height - text_height
        img = self.draw_one_watermark(img, text_height, text_width, watermark_text, x, y)
        return img

    def draw_one_watermark(self, img: Image, text_height: int,
                           text_width: int, watermark_text: str, x: int, y: int) -> Image:
        txt_img = Image.new("RGBA", (img.width, img.height), (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.rounded_rectangle((x - MARGIN, y - MARGIN, x + text_width + MARGIN, y + text_height + MARGIN),
                                   MARGIN - 1, fill=self.back_color)
        txt_draw.text((x, y), watermark_text, fill=self.text_color, font=self.font)
        return Image.alpha_composite(img, txt_img)



