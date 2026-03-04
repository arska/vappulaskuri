#!/usr/bin/env python3
"""Generate an OG image for Vappulaskuri with the countdown to Vappu."""

import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import cairosvg

WIDTH = 1200
HEIGHT = 630
SCRIPT_DIR = Path(__file__).parent
FINNISH_TZ = timezone(timedelta(hours=2))


def create_gradient(width: int, height: int) -> Image.Image:
    """Create background gradient matching the site aesthetic."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient stops: midnight blue -> deep purple -> purple -> pink -> gold
    stops = [
        (0.00, (11, 16, 38)),    # #0b1026
        (0.25, (26, 27, 75)),    # #1a1b4b
        (0.45, (58, 45, 110)),   # #3a2d6e
        (0.60, (107, 58, 125)),  # #6b3a7d
        (0.75, (194, 86, 110)),  # #c2566e
        (0.90, (240, 160, 75)),  # #f0a04b
        (1.00, (253, 216, 112)), # #fdd870
    ]

    for y in range(height):
        t = y / height
        # Find the two stops we're between
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                local_t = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                r = int(stops[i][1][0] + (stops[i + 1][1][0] - stops[i][1][0]) * local_t)
                g = int(stops[i][1][1] + (stops[i + 1][1][1] - stops[i][1][1]) * local_t)
                b = int(stops[i][1][2] + (stops[i + 1][1][2] - stops[i][1][2]) * local_t)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
                break

    return img


def add_stars(img: Image.Image) -> None:
    """Add decorative stars to the upper portion."""
    draw = ImageDraw.Draw(img)
    import random
    random.seed(42)  # Deterministic stars
    for _ in range(50):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height // 3)
        brightness = random.randint(150, 255)
        size = random.choice([1, 1, 1, 2])
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def render_svg_to_image(svg_path: Path, width: int) -> Image.Image:
    """Render SVG to a PIL Image at the given width."""
    png_data = cairosvg.svg2png(url=str(svg_path), output_width=width)
    from io import BytesIO
    return Image.open(BytesIO(png_data))


def get_days_to_vappu() -> int | None:
    """Return days until Vappu, or None if it's currently Vappu."""
    now = datetime.now(FINNISH_TZ)
    year = now.year

    vappu_start = datetime(year, 4, 30, 0, 0, tzinfo=FINNISH_TZ)
    vappu_end = datetime(year, 5, 1, 23, 59, tzinfo=FINNISH_TZ)

    if vappu_start <= now <= vappu_end:
        return None  # It's Vappu!

    if now > vappu_end:
        vappu_start = datetime(year + 1, 4, 30, 0, 0, tzinfo=FINNISH_TZ)

    delta = vappu_start - now
    return delta.days + (1 if delta.seconds > 0 else 0)


def draw_glassmorphism_card(draw: ImageDraw.Draw, bbox: tuple, radius: int = 20) -> None:
    """Draw a frosted glass style rounded rectangle."""
    draw.rounded_rectangle(bbox, radius=radius, fill=(255, 255, 255, 20), outline=(255, 255, 255, 40), width=2)


def generate() -> None:
    img = create_gradient(WIDTH, HEIGHT)
    add_stars(img)

    # Convert to RGBA for compositing
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Load fonts
    font_dir = SCRIPT_DIR / "fonts"
    font_serif = ImageFont.truetype(str(font_dir / "DMSerifDisplay-Regular.ttf"), 52)
    font_large = ImageFont.truetype(str(font_dir / "Outfit-ExtraBold.ttf"), 220)
    font_label = ImageFont.truetype(str(font_dir / "Outfit-ExtraBold.ttf"), 40)
    font_vappu = ImageFont.truetype(str(font_dir / "DMSerifDisplay-Regular.ttf"), 80)

    # Set variation axis for Outfit (variable font) - weight 800 = ExtraBold
    try:
        font_large.set_variation_by_axes([800])
        font_label.set_variation_by_axes([600])
    except Exception:
        pass  # Not all Pillow versions support variable fonts

    # Render ylioppilaslakki SVG
    lakki_width = 100
    lakki_img = render_svg_to_image(SCRIPT_DIR / "yolakki.svg", lakki_width)
    lakki_x = (WIDTH - lakki_img.width) // 2
    lakki_y = 40
    img.paste(lakki_img, (lakki_x, lakki_y), lakki_img)

    # Title
    title = "Vappulaskuri"
    title_bbox = draw.textbbox((0, 0), title, font=font_serif)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_w) // 2
    title_y = lakki_y + lakki_img.height + 15
    # Text shadow
    draw.text((title_x + 2, title_y + 2), title, font=font_serif, fill=(0, 0, 0, 80))
    draw.text((title_x, title_y), title, font=font_serif, fill=(255, 255, 255, 240))

    days = get_days_to_vappu()

    if days is None:
        # It's Vappu!
        vappu_text = "Nyt on vappu!!!"
        vbbox = draw.textbbox((0, 0), vappu_text, font=font_vappu)
        vw = vbbox[2] - vbbox[0]
        vx = (WIDTH - vw) // 2
        vy = 320
        # Glow effect
        for offset in range(8, 0, -2):
            alpha = 30
            draw.text((vx, vy), vappu_text, font=font_vappu, fill=(253, 216, 112, alpha))
        draw.text((vx, vy), vappu_text, font=font_vappu, fill=(253, 216, 112, 255))
    else:
        # Countdown card
        days_str = str(days)
        label = "päivää vappuun" if days != 1 else "päivä vappuun"

        # Measure text using anchor="lt" (left-top) for accurate sizes
        days_bbox = font_large.getbbox(days_str)
        days_w = days_bbox[2] - days_bbox[0]
        days_h = days_bbox[3] - days_bbox[1]

        label_bbox = font_label.getbbox(label)
        label_w = label_bbox[2] - label_bbox[0]
        label_h = label_bbox[3] - label_bbox[1]

        padding_top = 40
        padding_bottom = 40
        gap = 20  # space between number and label

        # Card spans most of the image width
        card_content_w = max(int(WIDTH * 0.75), max(days_w, label_w) + 120)
        card_content_h = padding_top + days_h + gap + label_h + padding_bottom
        card_x = (WIDTH - card_content_w) // 2
        card_y = title_y + 80

        # Glassmorphism card
        draw_glassmorphism_card(draw, (card_x, card_y, card_x + card_content_w, card_y + card_content_h), radius=24)

        # Days number - use anchor="mt" (middle-top) for centering
        days_x = WIDTH // 2
        days_y = card_y + padding_top
        draw.text((days_x + 2, days_y + 2), days_str, font=font_large, anchor="mt", fill=(0, 0, 0, 50))
        draw.text((days_x, days_y), days_str, font=font_large, anchor="mt", fill=(255, 255, 255, 255))

        # Label - positioned below the number
        label_x = WIDTH // 2
        label_y = days_y + days_h + gap
        draw.text((label_x, label_y), label, font=font_label, anchor="mt", fill=(255, 255, 255, 180))

    # Composite overlay onto background
    img = Image.alpha_composite(img, overlay)

    # Save as RGB PNG
    img = img.convert("RGB")
    output_path = SCRIPT_DIR / "og-image.png"
    img.save(str(output_path), "PNG", optimize=True)
    print(f"Generated {output_path} ({img.width}x{img.height})")


if __name__ == "__main__":
    generate()
