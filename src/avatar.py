import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

LOGO_IMG = np.array(PIL.Image.open("static/logo.png"))
font_big: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype("static/Rubik-Bold.ttf", 124)
font_small: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype("static/Rubik-Bold.ttf", 74)


def print_text(
    img: PIL.Image.Image,
    pos: tuple[int, int],
    text: str,
    font: PIL.ImageFont.FreeTypeFont,
    max_width: int,
    max_height: int,
) -> PIL.Image.Image:
    font_size = font.size
    draw = PIL.ImageDraw.Draw(img)
    current_font = PIL.ImageFont.truetype(font.path, font_size)

    # Wrap text to fit within max_width and max_height
    wrapped_text = text
    trials = 1000
    while trials:
        trials -= 1
        lines = []
        words = wrapped_text.split()
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            _, _, w, _ = current_font.getbbox(test_line)
            if w > max_width:
                # If line width exceeds max_width, start a new line
                current_line.pop()  # remove word causing overflow
                lines.append(" ".join(current_line))
                current_line = [word]  # start new line with current word
        # Add any remaining words in the current line to lines
        if current_line:
            lines.append(" ".join(current_line))

        max_width_in_lines = 0

        for line in lines:
            _, _, w, _ = current_font.getbbox(line)
            max_width_in_lines = max(w, max_width_in_lines)

        # Calculate total height of the text block
        _, _, _, line_height = current_font.getbbox("A")
        text_height = line_height * len(lines)

        if (text_height <= max_height) and (max_width_in_lines <= max_width):
            # Draw the wrapped text
            y_text = pos[1] - text_height // 2
            for line in lines:
                _, _, text_width, _ = current_font.getbbox(line)
                x_text = pos[0] - text_width // 2
                draw.text((x_text, y_text), line, font=current_font, fill=(255, 255, 255))
                y_text += line_height
            break
        else:
            # Reduce font size if text block is too tall
            font_size -= 1
            current_font = PIL.ImageFont.truetype(font.path, font_size)

    return img


def generate_avatar(title: str, subtitle: str | None, color: tuple[int, int, int]) -> PIL.Image.Image:
    img = np.zeros((640, 640, 3), np.uint32) + np.array(color)

    h = LOGO_IMG.shape[0]
    w = LOGO_IMG.shape[1]
    y0 = 105 - h // 2
    x0 = (img.shape[1] - w) // 2
    roi = img[y0 : y0 + h, x0 : x0 + w, :]
    img[y0 : y0 + h, x0 : x0 + w, :] = roi * (255 - LOGO_IMG[:, :, :3]) // 255 + (LOGO_IMG[:, :, :3])

    img = img.clip(0, 255).astype(np.uint8)

    img = PIL.Image.fromarray(img)
    max_width = 600
    max_height = 300
    if subtitle is not None:
        img = print_text(img, (640 // 2, 640 // 2), title, font_big, max_width, max_height)
        img = print_text(img, (640 // 2, 640 // 2 + 200), subtitle, font_small, max_width, 74)
    else:
        img = print_text(img, (640 // 2, 640 // 2), title, font_big, max_width, max_height)

    return img
