import csv
import io
import textwrap
import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from pathlib import Path

SIZE = (256, 256)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "badges.csv"
OUTPUT_DIR = BASE_DIR / "badges"
ASSETS_DIR = BASE_DIR / "images"

OUTPUT_DIR.mkdir(exist_ok=True)

def generate_readme(rows):
    readme_path = OUTPUT_DIR / "README.md"

    def md_badge(row):
        title = row["titre"]
        desc = row["description"]
        file = row["fichier"]

        return f"![{title} : {desc}]({file})"

    lines = []
    lines.append("# 🎖️ Badges générés\n")

    # ligne compacte (tout sur une ligne)
    line = " ".join(md_badge(r) for r in rows)
    lines.append(line + "\n")

    readme_path.write_text("\n".join(lines), encoding="utf-8")

def make_grayscale(img):
    gray = ImageOps.grayscale(img)

    rgba = Image.merge(
        "RGBA",
        (gray, gray, gray, img.split()[3])
    )

    enhancer = ImageEnhance.Brightness(rgba)
    return enhancer.enhance(0.4)

# Use a real font that supports accents
def load_font(size):
    # macOS common font (good UTF-8 support)
    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

    if Path(font_path).exists():
        return ImageFont.truetype(font_path, size)

    # fallback (less ideal)
    return ImageFont.load_default()


def load_icon(image_name: str):
    icon_path = ASSETS_DIR / image_name

    if not icon_path.exists():
        return None

    if icon_path.suffix.lower() == ".svg":
        png_bytes = cairosvg.svg2png(
            url=str(icon_path),
            output_width=96,
            output_height=96
        )
        icon = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    else:
        icon = Image.open(icon_path).convert("RGBA")

    #icon = icon.resize((128, 128), Image.Resampling.LANCZOS)
    return icon


def draw_wrapped_text(draw, text, font, max_width, x, y, fill):
    lines = []

    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=28))

    line_height = font.size + 4

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]

        draw.text(
            (x - w / 2, y + i * line_height),
            line,
            font=font,
            fill=fill
        )

    return y + len(lines) * line_height


def create_badge(title, filename, description, image_name):
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_title = load_font(22)
    font_desc = load_font(16)

    color = (
        255,
        255,
        200
    )

    # background
    padding = 12

    draw.rounded_rectangle(
        [
            padding,
            padding,
            SIZE[0] - padding,
            SIZE[1] - padding
        ],
        radius=20,
        fill=(70, 70, 60)
    )

    # --- TITLE ---
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = bbox[2] - bbox[0]

    draw.text(
        ((SIZE[0] - title_w) / 2, 15),
        title,
        fill=color,
        font=font_title
    )

    # --- ICON ---
    icon = load_icon(image_name)
    if icon:
        img.paste(icon, ((SIZE[0] - icon.width) // 2, 60), icon)

    # --- DESCRIPTION ---
    draw_wrapped_text(
        draw,
        description,
        font_desc,
        SIZE[0],
        SIZE[0] / 2,
        180,
        (220, 220, 220)
    )

    base_path = OUTPUT_DIR / filename

    # save normal
    img.save(base_path, format="PNG")

    # save grayscale version
    gray_img = make_grayscale(img)
    gray_path = base_path.with_name(
        base_path.stem + "_" + base_path.suffix
    )

    gray_img.save(gray_path, format="PNG")


def main():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)
            create_badge(
                row["titre"],
                row["fichier"],
                row["description"],
                row["image"]
            )

    generate_readme(rows)

    print(f"Badges générés dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()