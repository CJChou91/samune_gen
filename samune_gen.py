import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ======= 對聯式標題的函式（前面給過的簡化版） =======
def text_size(draw, s, font, stroke_width=0):
    bbox = draw.textbbox((0,0), s, font=font, stroke_width=stroke_width)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]

def measure_vertical_block(draw, text, font, char_spacing, stroke_width=0):
    max_w = 0
    total_h = 0
    for ch in text:
        w,h = text_size(draw, ch, font, stroke_width)
        max_w = max(max_w, w)
        total_h += h + char_spacing
    if len(text) > 0:
        total_h -= char_spacing
    return max_w, total_h

def draw_vertical_text(im, text, x, y_center, font, char_spacing,
                       fill, stroke_fill, stroke_width):
    draw = ImageDraw.Draw(im)
    col_w, col_h = measure_vertical_block(draw, text, font, char_spacing, stroke_width)
    y = int(y_center - col_h/2)
    for ch in text:
        w,h = text_size(draw, ch, font, stroke_width)
        x_draw = int(x + (col_w - w)/2)
        draw.text((x_draw, y), ch, font=font, fill=fill,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
        y += h + char_spacing

def add_duilian_and_resize(image_path, main_title, sub_title, output_path,
                           font_path, target_size=(854,480)):
    im = Image.open(image_path).convert("RGBA")
    W,H = im.size
    draw = ImageDraw.Draw(im)

    # 字體大小簡化：直接取圖高的 1/12
    font_size = max(24, H//12)
    font = ImageFont.truetype(font_path, font_size)
    char_spacing = int(font_size * 0.12)
    y_center = H // 2

    col_w_L, col_h_L = measure_vertical_block(draw, main_title, font, char_spacing)
    col_w_R, col_h_R = measure_vertical_block(draw, sub_title, font, char_spacing)

    # 左右欄位位置
    x_left_col = 40
    x_right_col = W - 40 - col_w_R

    draw_vertical_text(im, main_title, x_left_col, y_center, font, char_spacing,
                       (255,255,0,180), (0,0,0,230), 4)
    draw_vertical_text(im, sub_title, x_right_col, y_center, font, char_spacing,
                       (255,255,0,180), (0,0,0,230), 4)

    # 縮放到 480p
    out = im.resize(target_size, Image.LANCZOS).convert("RGB")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, quality=95)
    print(f"Saved -> {output_path}")

# ======= 主程式 (args) =======
def main():
    parser = argparse.ArgumentParser(description="加上對聯式標題並縮放到480p")
    parser.add_argument("--image", required=True, help="輸入圖片路徑")
    parser.add_argument("--main", required=True, help="主標題（左側）")
    parser.add_argument("--sub", required=True, help="副標題（右側）")
    parser.add_argument("--output", help="輸出圖片路徑", default="output.png")
    parser.add_argument("--font", help="字體檔案路徑 (TTF/OTF)", default=r"Font\Dela_Gothic_One\DelaGothicOne-Regular.ttf")
    parser.add_argument("--size", type=str, default="854x480",
                        help="輸出解析度，格式如 854x480 或 640x480")

    args = parser.parse_args()

    # 解析 size
    try:
        w,h = map(int, args.size.lower().split("x"))
        target_size = (w,h)
    except:
        print("解析 --size 參數錯誤，請用類似 854x480 格式")
        sys.exit(1)

    add_duilian_and_resize(args.image, args.main, args.sub,
                           args.output, args.font, target_size)

if __name__ == "__main__":
    main()
