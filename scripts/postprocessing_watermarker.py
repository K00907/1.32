import gradio as gr

from modules import scripts_postprocessing
from modules.ui_components import FormRow
from scripts.watermark import MIDDLE, TOP, BOTTOM, EVERYWHERE_RANDOM, Watermark


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
        watermark = Watermark()
        img.image = watermark.add(img.image, watermark_position, watermark_text, transparency)
        return img
