# printable_card.py
from PIL import Image
import io

TEMPLATE_PATH = "assets/template.jpeg"   # A4 template (1131 x 1600)

# Blank area at the top of the template where the AI image goes
# (the sponsor / school / Robokalam artwork starts at ~y=850).
IMAGE_BOX_TOP = 40
IMAGE_BOX_BOTTOM = 830
IMAGE_BOX_SIDE_MARGIN = 60

A4_WIDTH_INCHES = 8.27


def generate_printable_card(name, school, goal, captured_img, ai_img, logo_file=None):
    """
    Place the AI-generated image, scaled to fit and centered,
    in the blank top area of the template.
    """
    card = Image.open(TEMPLATE_PATH).convert("RGB")
    W, H = card.size

    box_w = W - 2 * IMAGE_BOX_SIDE_MARGIN
    box_h = IMAGE_BOX_BOTTOM - IMAGE_BOX_TOP

    # Scale to fit inside the box, keeping aspect ratio
    scale = min(box_w / ai_img.width, box_h / ai_img.height)
    new_size = (int(ai_img.width * scale), int(ai_img.height * scale))
    ai_resized = ai_img.convert("RGB").resize(new_size, Image.LANCZOS)

    x = (W - new_size[0]) // 2
    y = IMAGE_BOX_TOP + (box_h - new_size[1]) // 2
    card.paste(ai_resized, (x, y))

    return card


def card_to_pdf_bytes(card):
    """Export the card as a single-page A4 PDF."""
    dpi = card.width / A4_WIDTH_INCHES
    out = io.BytesIO()
    card.convert("RGB").save(out, "PDF", resolution=dpi)
    return out.getvalue()
