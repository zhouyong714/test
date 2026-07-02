from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 3600, 2200
OUT = Path("figure1_neuro_targets.png")


def load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


FONT_REG = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]
FONT_BOLD = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsunb.ttf",
    r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
]


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def darken(hex_color: str, factor: float = 0.8) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]
    return (int(r * factor), int(g * factor), int(b * factor), 255)


def bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    return draw.textbbox((0, 0), text, font=font)


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    b = bbox(draw, text, font)
    return b[2] - b[0], b[3] - b[1]


def draw_centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, font, fill):
    w, h = measure(draw, text, font)
    x, y = xy
    draw.text((x - w / 2, y - h / 2), text, font=font, fill=fill)


def round_rect(draw, xy, fill, outline, width=3, radius=24):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, xy, fill, outline=None, width=0, radius=None):
    x1, y1, x2, y2 = xy
    if radius is None:
        radius = int((y2 - y1) / 2)
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow_line(draw, start, end, color, width=4, head=18):
    x1, y1 = start
    x2, y2 = end
    draw.line([start, end], fill=color, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    left = (x2 - head * math.cos(ang) + head * 0.45 * math.sin(ang), y2 - head * math.sin(ang) - head * 0.45 * math.cos(ang))
    right = (x2 - head * math.cos(ang) - head * 0.45 * math.sin(ang), y2 - head * math.sin(ang) + head * 0.45 * math.cos(ang))
    draw.polygon([end, left, right], fill=color)


def draw_box(draw, box, title, drug, evidence, accent, title_size=30, drug_size=24, evidence_size=22):
    x1, y1, x2, y2 = box
    shadow = (x1 + 8, y1 + 10, x2 + 8, y2 + 10)
    round_rect(draw, shadow, fill=rgba("#000000", 24), outline=rgba("#000000", 0), width=0, radius=26)
    round_rect(draw, box, fill=rgba("#FFFFFF", 245), outline=rgba(accent), width=4, radius=26)
    draw.rectangle((x1, y1, x1 + 16, y2), fill=rgba(accent))
    title_font = load_font(FONT_BOLD, title_size)
    drug_font = load_font(FONT_REG, drug_size)
    evidence_font = load_font(FONT_BOLD, evidence_size)
    inner_x = x1 + 34
    top_y = y1 + 22
    draw.text((inner_x, top_y), title, font=title_font, fill=(25, 25, 25, 255))
    drug_y = y1 + 72
    draw.text((inner_x, drug_y), drug, font=drug_font, fill=(55, 55, 55, 255))
    ev_text = f"证据：{evidence}"
    ev_w, ev_h = measure(draw, ev_text, evidence_font)
    pad_x = 20
    pad_y = 10
    chip_w = ev_w + pad_x * 2
    chip_h = ev_h + pad_y * 2
    chip_x2 = x2 - 28
    chip_x1 = chip_x2 - chip_w
    chip_y2 = y2 - 20
    chip_y1 = chip_y2 - chip_h
    pill(draw, (chip_x1, chip_y1, chip_x2, chip_y2), fill=rgba(accent, 235), outline=rgba(accent), width=2, radius=chip_h // 2)
    draw.text((chip_x1 + pad_x, chip_y1 + pad_y - 1), ev_text, font=evidence_font, fill=(255, 255, 255, 255))


def draw_module_tag(draw, x, y, text, accent):
    tag_font = load_font(FONT_BOLD, 28)
    text_w, text_h = measure(draw, text, tag_font)
    pad_x, pad_y = 24, 14
    box = (x, y, x + text_w + pad_x * 2, y + text_h + pad_y * 2)
    shadow = (box[0] + 6, box[1] + 7, box[2] + 6, box[3] + 7)
    round_rect(draw, shadow, fill=rgba("#000000", 20), outline=rgba("#000000", 0), width=0, radius=24)
    pill(draw, box, fill=rgba(accent), outline=rgba(accent), width=0, radius=24)
    draw.text((x + pad_x, y + pad_y - 1), text, font=tag_font, fill=(255, 255, 255, 255))
    return box


def draw_capsule(draw, center, size, text, fill, outline, font_size=24):
    cx, cy = center
    w, h = size
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    pill(draw, box, fill=rgba(fill), outline=rgba(outline), width=3, radius=int(h / 2))
    font = load_font(FONT_BOLD, font_size)
    tw, th = measure(draw, text, font)
    draw.text((cx - tw / 2, cy - th / 2 - 1), text, font=font, fill=(255, 255, 255, 255))


def draw_cell_scene(draw):
    # main postsynaptic compartment
    cell = (1140, 720, 2510, 1780)
    round_rect(draw, (cell[0] + 10, cell[1] + 12, cell[2] + 10, cell[3] + 12), fill=rgba("#000000", 18), outline=rgba("#000000", 0), width=0, radius=44)
    round_rect(draw, cell, fill=rgba("#F8FAFC", 255), outline=rgba("#CBD5E1", 255), width=4, radius=44)

    # membrane line
    membrane_y = 1035
    draw.line([(cell[0] + 40, membrane_y), (cell[2] - 40, membrane_y)], fill=rgba("#64748B"), width=8)
    draw.line([(cell[0] + 40, membrane_y + 10), (cell[2] - 40, membrane_y + 10)], fill=rgba("#E2E8F0"), width=2)

    # presynaptic bouton
    bouton = (890, 780, 1410, 1210)
    draw.ellipse((bouton[0] + 6, bouton[1] + 8, bouton[2] + 6, bouton[3] + 8), fill=rgba("#000000", 18))
    draw.ellipse(bouton, fill=rgba("#FFF3E9"), outline=rgba("#E67E22"), width=4)
    # cleft
    cleft = (1395, 920, 1545, 1020)
    draw.rounded_rectangle(cleft, radius=30, fill=rgba("#FFFFFF", 240), outline=rgba("#F1F5F9"), width=2)

    # vesicles and ACh dots
    vesicles = [(1010, 890), (1085, 850), (1135, 930), (1210, 875), (1260, 950), (1130, 1030), (1005, 990)]
    for vx, vy in vesicles:
        draw.ellipse((vx - 20, vy - 20, vx + 20, vy + 20), fill=rgba("#FDE68A"), outline=rgba("#F59E0B"), width=2)
        draw.ellipse((vx - 8, vy - 8, vx + 8, vy + 8), fill=rgba("#FFFFFF"), outline=None)
    for ax, ay in [(1460, 945), (1490, 930), (1515, 960), (1435, 975), (1480, 995)]:
        draw.ellipse((ax - 7, ay - 7, ax + 7, ay + 7), fill=rgba("#FDBA74"), outline=None)

    # cell interior highlight
    draw.rounded_rectangle((1190, 1090, 2455, 1710), radius=38, fill=rgba("#FFFFFF", 160), outline=None)

    # calcium store / ER
    er = (1710, 1330, 2290, 1605)
    draw.rounded_rectangle((er[0] + 6, er[1] + 8, er[2] + 6, er[3] + 8), radius=120, fill=rgba("#000000", 12), outline=None)
    draw.rounded_rectangle(er, radius=120, fill=rgba("#F3E8FF", 255), outline=rgba("#A855F7", 255), width=4)
    # ER folds
    folds = [
        [(1760, 1430), (1810, 1385), (1860, 1450), (1910, 1400), (1970, 1460), (2030, 1398)],
        [(1760, 1510), (1820, 1470), (1880, 1528), (1945, 1472), (2005, 1530), (2085, 1482)],
    ]
    for pts in folds:
        draw.line(pts, fill=rgba("#C084FC"), width=5)

    # labels for scene
    label_font = load_font(FONT_BOLD, 30)
    small_font = load_font(FONT_REG, 24)
    draw.text((935, 736), "神经元 / 突触", font=label_font, fill=(60, 60, 60, 255))
    draw.text((1815, 1618), "细胞内钙库", font=label_font, fill=(97, 63, 144, 255))
    draw.text((1450, 1000), "AChE", font=load_font(FONT_BOLD, 24), fill=(139, 79, 20, 255))

    # membrane / store markers
    draw_capsule(draw, (1600, 1030), (150, 46), "nAChR", "#E67E22", "#C45F10", 24)
    draw_capsule(draw, (1775, 1090), (182, 46), "RDL", "#2B7BBB", "#1E5D93", 24)
    draw_capsule(draw, (1938, 1090), (174, 46), "GluCl", "#2B7BBB", "#1E5D93", 24)
    draw_capsule(draw, (2255, 980), (160, 46), "TAR1", "#2AA198", "#1D8178", 24)
    draw_capsule(draw, (2395, 1200), (158, 46), "Na_v", "#2E8B57", "#226847", 24)
    draw_capsule(draw, (2085, 1460), (150, 46), "RyR", "#5B5EAA", "#47498A", 24)

    # small calcium arrow
    draw.line([(2125, 1460), (2185, 1460)], fill=rgba("#A855F7"), width=5)
    arrow_line(draw, (2185, 1460), (2235, 1460), rgba("#A855F7"), width=5, head=12)

    # return anchor points for connectors
    return {
        "AChE": (1450, 945),
        "nAChR": (1600, 1030),
        "RDL": (1775, 1090),
        "GluCl": (1938, 1090),
        "TAR1": (2255, 980),
        "Na_v": (2395, 1200),
        "RyR": (2085, 1460),
    }


def main():
    img = Image.new("RGBA", (W, H), rgba("#FFFFFF"))
    draw = ImageDraw.Draw(img)

    # Top label and title
    tag = draw_module_tag(draw, 90, 55, "Figure 1", "#1F2937")
    title_font = load_font(FONT_BOLD, 60)
    subtitle_font = load_font(FONT_REG, 30)
    draw_centered(draw, (W / 2, 92), "小菜蛾神经系统药理靶标总图", title_font, (20, 20, 20, 255))
    draw_centered(draw, (W / 2, 155), "神经元 / 突触 + 细胞内钙库", subtitle_font, (90, 90, 90, 255))

    # module tags
    chol_tag = draw_module_tag(draw, 95, 220, "胆碱能兴奋性通路", "#E67E22")
    inh_tag = draw_module_tag(draw, 95, 820, "抑制性氯离子通路", "#2B7BBB")
    gpcr_tag = draw_module_tag(draw, 2640, 220, "新兴 GPCR", "#2AA198")
    exc_tag = draw_module_tag(draw, 2550, 820, "膜兴奋性 / 钙释放", "#2E8B57")

    # callout boxes
    left_boxes = [
        ((95, 270, 655, 425), "AChE", "药剂：有机磷类 / 氨基甲酸酯类", "中", "#E67E22", 30),
        ((95, 450, 655, 620), "nAChR", "药剂：新烟碱类 / 多杀菌素类", "高", "#E67E22", 30),
        ((95, 870, 655, 1035), "RDL / GABA receptor", "药剂：苯基吡唑类 / 间-二酰胺类", "高", "#2B7BBB", 28),
        ((95, 1050, 655, 1190), "GluCl", "药剂：阿维菌素类", "高", "#2B7BBB", 30),
    ]
    right_boxes = [
        ((2850, 270, 3520, 425), "TAR1 / Octopamine receptor", "药剂：甲脒类（参照）", "中-高", "#2AA198", 26),
        ((2850, 870, 3520, 1020), "Na_v", "药剂：拟除虫菊酯类 / SCBI", "高", "#2E8B57", 30),
        ((2850, 1050, 3520, 1215), "RyR", "药剂：双酰胺类", "极高", "#5B5EAA", 30),
    ]

    for box, title, drug, evidence, accent, title_size in left_boxes + right_boxes:
        draw_box(draw, box, title, drug, evidence, accent, title_size=title_size)

    anchors = draw_cell_scene(draw)

    # connectors, drawn over the space between callouts and targets
    connector_color = rgba("#64748B", 220)
    for box, title, *_rest in left_boxes + right_boxes:
        if title == "AChE":
            target = anchors["AChE"]
            start = (box[2], (box[1] + box[3]) / 2)
        elif title == "nAChR":
            target = anchors["nAChR"]
            start = (box[2], (box[1] + box[3]) / 2)
        elif title == "RDL / GABA receptor":
            target = anchors["RDL"]
            start = (box[2], (box[1] + box[3]) / 2)
        elif title == "GluCl":
            target = anchors["GluCl"]
            start = (box[2], (box[1] + box[3]) / 2)
        elif title == "TAR1 / Octopamine receptor":
            target = anchors["TAR1"]
            start = (box[0], (box[1] + box[3]) / 2)
        elif title == "Na_v":
            target = anchors["Na_v"]
            start = (box[0], (box[1] + box[3]) / 2)
        elif title == "RyR":
            target = anchors["RyR"]
            start = (box[0], (box[1] + box[3]) / 2)
        else:
            continue
        arrow_line(draw, start, target, connector_color, width=4, head=16)

    # callout dots on anchors
    for name, pt in anchors.items():
        color = {
            "AChE": "#E67E22",
            "nAChR": "#E67E22",
            "RDL": "#2B7BBB",
            "GluCl": "#2B7BBB",
            "TAR1": "#2AA198",
            "Na_v": "#2E8B57",
            "RyR": "#5B5EAA",
        }[name]
        x, y = pt
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=rgba(color), outline=rgba("#FFFFFF"), width=2)

    # small footer note
    footer_font = load_font(FONT_REG, 22)
    footer = "药剂类别与证据等级按本文表1口径整理"
    draw.text((W - 760, H - 58), footer, font=footer_font, fill=(110, 110, 110, 255))

    img.convert("RGB").save(OUT, quality=95)
    print(f"saved {OUT.resolve()}")


if __name__ == "__main__":
    main()
