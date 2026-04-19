from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "Hridya-Farm-Company-Profile.pdf"
KERUPUK_ASSET = ASSETS / "kerupuk_telur_asin_generated.png"
RESAMPLE = getattr(Image, "Resampling", Image).LANCZOS

PAGE_W = 1240
PAGE_H = 1754
MARGIN = 78

GREEN = "#1d5441"
GREEN_DARK = "#102e23"
GREEN_SOFT = "#dfe9e3"
GOLD = "#bb8740"
GOLD_SOFT = "#efe2cb"
IVORY = "#f5f0e7"
WHITE = "#ffffff"
TEXT = "#243229"
MUTED = "#617267"
LINE = "#d7cebf"

CONTACT_EMAIL = "hridyafarm@gmail.com"
CONTACT_PHONE = "+6285721667024"
CONTACT_ADDRESS = (
    "Jl. Puskesmas No.29, RT.04/RW.01, Karangdep, Karanggedang, "
    "Kec. Sruweng, Kabupaten Kebumen, Jawa Tengah 54362"
)


@dataclass
class Product:
    name: str
    note: str
    image_name: str


PRODUCTS = [
    Product("Telur Tawar", "Telur bebek segar untuk retail harian, bahan baku kuliner, dan pengadaan rutin.", "telur_tawar_1772059646282.png"),
    Product("Telur Asin", "Varian inti dengan karakter masir, stabil untuk distribusi dan pasar oleh-oleh.", "telur_asin_1772059670436.png"),
    Product("Telur Panggang", "Olahan panggang bertekstur lebih legit dengan shelf life lebih panjang.", "telur_panggang_1772059835846.png"),
    Product("Telur Asap", "Produk bernilai tambah dengan profil rasa smokey untuk diferensiasi pasar.", "telur_asap_1772059875989.png"),
    Product("Kerupuk Telur Asin", "Produk turunan siap ekspansi untuk kategori snack, hampers, dan kanal reseller.", "kerupuk_telur_asin_generated.png"),
]


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    if serif:
        path = "/System/Library/Fonts/NewYork.ttf"
        index = 0
    else:
        path = "/System/Library/Fonts/HelveticaNeue.ttc"
        index = 1 if bold else 0
    return ImageFont.truetype(path, size=size, index=index)


def rgba(color: str, alpha: int) -> tuple[int, int, int, int]:
    return (*ImageColor.getrgb(color), alpha)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str | None = None, radius: int = 28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2 if outline else 1)


def fit_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = image.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    resized = image.resize((new_w, new_h), RESAMPLE)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def load_image(name: str, size: tuple[int, int]) -> Image.Image:
    with Image.open(ASSETS / name) as img:
        return fit_crop(img.convert("RGB"), size)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font_obj: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 8,
) -> int:
    x, y = xy
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        width = draw.textbbox((0, 0), candidate, font=font_obj)[2]
        if width <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    sample = draw.textbbox((0, 0), "Ag", font=font_obj)
    line_height = sample[3] - sample[1]
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += line_height + line_gap
    return y


def measure_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    max_width: int,
    line_gap: int = 8,
) -> int:
    lines = 0
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        width = draw.textbbox((0, 0), candidate, font=font_obj)[2]
        if width <= max_width:
            current = candidate
        else:
            if current:
                lines += 1
            current = word
    if current:
        lines += 1
    sample = draw.textbbox((0, 0), "Ag", font=font_obj)
    line_height = sample[3] - sample[1]
    return lines * line_height + max(lines - 1, 0) * line_gap


def fit_font_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    *,
    bold: bool = False,
    serif: bool = False,
    line_gap: int = 8,
) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(start_size, min_size - 1, -1):
        candidate = font(size, bold=bold, serif=serif)
        height = measure_wrapped_text(draw, text, candidate, max_width, line_gap=line_gap)
        if height <= max_height:
            return candidate, size
    return font(min_size, bold=bold, serif=serif), min_size


def draw_kicker(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, fill: str = GOLD_SOFT, text_fill: str = GREEN) -> None:
    text = text.upper()
    bbox = draw.textbbox((0, 0), text, font=font(16, bold=True))
    width = bbox[2] - bbox[0] + 42
    rounded_panel(draw, (x, y, x + width, y + 38), fill=fill, radius=19)
    draw.text((x + 21, y + 9), text, font=font(16, bold=True), fill=text_fill)


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str, y: int) -> int:
    draw.text((MARGIN, y), title, font=font(52, bold=True, serif=True), fill=GREEN_DARK)
    return draw_wrapped_text(draw, subtitle, (MARGIN, y + 76), font(22), MUTED, PAGE_W - 2 * MARGIN, line_gap=7)


def draw_metric(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, value: str) -> None:
    x1, y1, x2, y2 = box
    rounded_panel(draw, box, fill=WHITE, outline=LINE, radius=28)
    draw.text((x1 + 28, y1 + 24), label.upper(), font=font(17, bold=True), fill=GREEN)
    available_height = y2 - (y1 + 62) - 22
    value_font, fitted_size = fit_font_size(
        draw,
        value,
        x2 - x1 - 56,
        available_height,
        27,
        18,
        bold=True,
        serif=False,
        line_gap=3,
    )
    line_gap = 3 if fitted_size >= 22 else 2
    draw_wrapped_text(draw, value, (x1 + 28, y1 + 62), value_font, GREEN_DARK, x2 - x1 - 56, line_gap=line_gap)


def add_footer(draw: ImageDraw.ImageDraw, page_no: int) -> None:
    line_y = PAGE_H - 66
    draw.line((MARGIN, line_y, PAGE_W - MARGIN, line_y), fill=LINE, width=2)
    draw.text((MARGIN, line_y + 16), "Hridya Farm | Company Profile", font=font(17, bold=True), fill=MUTED)
    page_label = f"{page_no:02d}"
    bbox = draw.textbbox((0, 0), page_label, font=font(17, bold=True))
    draw.text((PAGE_W - MARGIN - (bbox[2] - bbox[0]), line_y + 16), page_label, font=font(17, bold=True), fill=MUTED)


def ensure_kerupuk_asset() -> None:
    if KERUPUK_ASSET.exists():
        return
    canvas = Image.new("RGB", (900, 900), "#efe5d4")
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((70, 110, 830, 860), fill="#ddd1bc")
    draw.ellipse((95, 90, 805, 800), fill="#faf5eb")

    chips = [
        (210, 240, 330, 410),
        (330, 180, 500, 350),
        (500, 235, 670, 420),
        (240, 405, 410, 585),
        (430, 400, 600, 575),
        (575, 455, 725, 615),
        (320, 560, 500, 725),
        (520, 595, 700, 765),
    ]
    colors = ["#e5c27b", "#ebc879", "#f1d390", "#deb76e", "#efcf85", "#e7bd71", "#f2d28d", "#dcae5d"]
    for (x1, y1, x2, y2), color in zip(chips, colors):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=36, fill=color, outline="#c1924a", width=4)
        draw.arc((x1 + 15, y1 + 18, x2 - 18, y2 - 20), 15, 160, fill="#f9e6b7", width=4)
        draw.arc((x1 + 20, y1 + 28, x2 - 24, y2 - 26), 190, 340, fill="#b88339", width=3)

    yolk = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
    ydraw = ImageDraw.Draw(yolk)
    ydraw.ellipse((14, 14, 206, 206), fill=rgba("#fff7dd", 230))
    ydraw.ellipse((48, 48, 172, 172), fill=rgba("#ef9e1d", 255))
    ydraw.ellipse((68, 68, 145, 145), fill=rgba("#f7c24d", 255))
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(yolk, (595, 105))

    label = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(label)
    rounded_panel(ldraw, (105, 710, 525, 818), fill=rgba("#13372b", 235), radius=30)
    ldraw.text((138, 735), "Kerupuk Telur Asin", font=font(34, bold=True, serif=True), fill=WHITE)
    ldraw.text((138, 778), "Visual produk tambahan", font=font(18, bold=True), fill="#d7e7dd")
    canvas = Image.alpha_composite(canvas, label).convert("RGB")
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=0.2))
    canvas.save(KERUPUK_ASSET)


def page_cover() -> Image.Image:
    bg = load_image("hero_ducks_1772059570675.png", (PAGE_W, PAGE_H)).filter(ImageFilter.GaussianBlur(radius=1.4))
    overlay = Image.new("RGBA", (PAGE_W, PAGE_H), rgba("#10261d", 150))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_overlay.polygon([(0, 1270), (PAGE_W, 1090), (PAGE_W, PAGE_H), (0, PAGE_H)], fill=rgba("#efe5d5", 240))
    page = Image.alpha_composite(bg.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(page)

    draw_kicker(draw, "Investor & Distributor Edition", MARGIN, 95, fill=rgba("#efe5d5", 235), text_fill=GREEN_DARK)
    draw.text((MARGIN, 180), "HRIDYA FARM", font=font(32, bold=True), fill=WHITE)
    draw.text((MARGIN, 242), "Company Profile", font=font(90, bold=True, serif=True), fill=WHITE)
    draw_wrapped_text(
        draw,
        "Profil perusahaan untuk kebutuhan pengembangan pasar, distribusi, dan penjajakan kemitraan pasokan telur bebek premium serta produk turunannya.",
        (MARGIN, 390),
        font(28),
        "#f3efe7",
        720,
        line_gap=9,
    )

    draw_metric(draw, (220, 540, 600, 694), "Kapasitas", "3.000 butir per hari")
    draw_metric(draw, (640, 540, 1020, 694), "Portofolio", "5 kategori produk")

    summary_top = 790
    summary_bottom = 1270
    rounded_panel(draw, (MARGIN, summary_top, 1148, summary_bottom), fill=rgba("#fffaf1", 242), radius=38)
    draw_kicker(draw, "Executive Summary", MARGIN + 40, summary_top + 42)
    draw.text((MARGIN + 40, summary_top + 98), "Ringkasan Bisnis", font=font(38, bold=True, serif=True), fill=GREEN_DARK)
    text_y = draw_wrapped_text(
        draw,
        "Hridya Farm beroperasi sebagai peternakan dan distributor telur bebek dengan fokus pada kualitas produk, kepastian pasokan, dan pengembangan nilai tambah. Portofolio saat ini mencakup telur tawar, telur asin, telur panggang, telur asap, serta pengembangan lini snack berbasis telur asin.",
        (MARGIN + 40, summary_top + 166),
        font(23),
        TEXT,
        610,
        line_gap=8,
    )
    draw_wrapped_text(
        draw,
        "Posisi bisnis diarahkan untuk melayani kebutuhan rumah tangga, horeca, reseller, agen, dan calon distributor regional yang membutuhkan pasokan konsisten dari sumber produksi langsung.",
        (MARGIN + 40, text_y + 12),
        font(23),
        TEXT,
        610,
        line_gap=8,
    )
    image_box = load_image("media__1772059382490.png", (238, 302)).convert("RGBA")
    image_x = 852
    image_y = summary_top + 72
    rounded_panel(draw, (image_x - 24, image_y - 24, image_x + 262, image_y + 326), fill=WHITE, outline="#d2b783", radius=34)
    page.alpha_composite(image_box, (image_x, image_y))

    draw_kicker(draw, "Kontak Utama", MARGIN, 1362, fill=rgba("#174436", 230), text_fill="#deebe5")
    draw.text((MARGIN, 1428), CONTACT_PHONE, font=font(27, bold=True), fill=GREEN_DARK)
    draw.text((MARGIN, 1473), CONTACT_EMAIL, font=font(23), fill=TEXT)
    addr_bottom = draw_wrapped_text(
        draw,
        CONTACT_ADDRESS,
        (MARGIN, 1512),
        font(19),
        TEXT,
        740,
        line_gap=5,
    )
    draw.text((MARGIN, min(max(addr_bottom + 12, 1582), 1620)), "Disusun untuk keperluan presentasi bisnis, distribusi, dan penjajakan kerja sama.", font=font(18), fill=MUTED)
    return page.convert("RGB")


def page_profile() -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), IVORY)
    draw = ImageDraw.Draw(page)
    y = draw_title(
        draw,
        "Profil Perusahaan",
        "Hridya Farm memposisikan diri sebagai produsen sekaligus distributor telur bebek dengan pendekatan operasional yang mengutamakan kualitas bahan baku dan konsistensi suplai.",
        92,
    )

    panel_top = y + 34
    panel_bottom = 1038
    rounded_panel(draw, (MARGIN, panel_top, PAGE_W - MARGIN, panel_bottom), fill=WHITE, outline=LINE, radius=34)
    draw_kicker(draw, "Corporate Overview", 110, y + 82, fill=GREEN_SOFT)

    left_box = (110, y + 150, 430, y + 662)
    rounded_panel(draw, left_box, fill="#fbf8f1", outline=LINE, radius=30)
    draw.text((138, y + 188), "Ringkasan Peran", font=font(28, bold=True, serif=True), fill=GREEN_DARK)
    summary_bottom = draw_wrapped_text(
        draw,
        "Hridya Farm bergerak sebagai produsen dan distributor telur bebek dengan model usaha yang menghubungkan pasokan, pengolahan, dan distribusi dalam satu alur bisnis.",
        (138, y + 246),
        font(18),
        TEXT,
        264,
        line_gap=6,
    )
    divider_top = summary_bottom + 22
    draw.line((138, divider_top, 402, divider_top), fill=LINE, width=2)
    draw.text((138, divider_top + 22), "Model Usaha", font=font(17, bold=True), fill=GREEN)
    model_bottom = draw_wrapped_text(
        draw,
        "Produksi dan distribusi langsung",
        (138, divider_top + 54),
        font(18, bold=True),
        GREEN_DARK,
        264,
        line_gap=4,
    )
    draw.text((138, model_bottom + 22), "Fokus Utama", font=font(17, bold=True), fill=GREEN)
    draw_wrapped_text(
        draw,
        "Mutu produk dan kesinambungan pasok",
        (138, model_bottom + 54),
        font(18, bold=True),
        GREEN_DARK,
        264,
        line_gap=4,
    )

    text_x = 490
    text_w = 560
    draw.text((text_x, y + 150), "Posisi dan Arah Bisnis", font=font(38, bold=True, serif=True), fill=GREEN_DARK)
    next_y = draw_wrapped_text(
        draw,
        "Hridya Farm tumbuh dari basis peternakan telur bebek menjadi entitas yang menggabungkan produksi, pengolahan, dan distribusi. Model bisnis ini memberi kontrol lebih baik terhadap mutu produk dan ketepatan pengiriman.",
        (text_x, y + 224),
        font(22),
        TEXT,
        text_w,
        line_gap=8,
    )
    next_y = draw_wrapped_text(
        draw,
        "Pendekatan tersebut membuat perusahaan relevan untuk pasar retail sekaligus untuk pembeli institusional yang membutuhkan pemasok langsung dengan kualitas terjaga. Fokus pengembangan diarahkan pada penguatan distribusi, produk bernilai tambah, dan ekspansi relasi dagang regional.",
        (text_x, next_y + 12),
        font(22),
        TEXT,
        text_w,
        line_gap=8,
    )

    metric_top = max(next_y + 30, y + 570)
    draw_metric(draw, (490, metric_top, 760, metric_top + 182), "Cakupan", "Retail, horeca, agen, grosir")
    draw_metric(draw, (790, metric_top, 1088, metric_top + 182), "Arah", "Distribusi dan ekspansi produk")

    value_top = 1068
    draw_kicker(draw, "Value Proposition", MARGIN, value_top, fill=GREEN_SOFT)
    draw.text((MARGIN, value_top + 62), "Keunggulan Operasional", font=font(36, bold=True, serif=True), fill=GREEN_DARK)
    bullets = [
        "Sumber pasokan berasal dari kegiatan peternakan dan pengelolaan produk secara langsung.",
        "Animal welfare dan lingkungan kandang yang lebih natural membantu menjaga mutu rasa dan kondisi telur.",
        "Standar higienitas diterapkan untuk mendukung keamanan produk serta konsistensi kualitas.",
        "Portofolio produk inti dan produk turunan memberi ruang bagi pertumbuhan margin dan diversifikasi kanal jual.",
    ]
    by = value_top + 134
    for item in bullets:
        text_height = measure_wrapped_text(draw, item, font(22), PAGE_W - 2 * MARGIN - 90, line_gap=7)
        box_bottom = by + max(text_height + 24, 66)
        rounded_panel(draw, (MARGIN, by - 12, PAGE_W - MARGIN, box_bottom), fill="#fbf8f1", outline=LINE, radius=24)
        draw.ellipse((MARGIN + 24, by + 12, MARGIN + 42, by + 30), fill=GOLD)
        by = draw_wrapped_text(draw, item, (MARGIN + 58, by), font(22), TEXT, PAGE_W - 2 * MARGIN - 90, line_gap=7) + 22

    note_top = by + 8
    note_height = 196
    note_bottom = note_top + note_height
    rounded_panel(draw, (MARGIN, note_top, PAGE_W - MARGIN, note_bottom), fill=GOLD_SOFT, radius=30)
    title_y = note_top + 34
    draw.text((MARGIN + 32, title_y), "Catatan untuk Mitra", font=font(29, bold=True), fill=GREEN)
    divider_y = title_y + 58
    draw.line((MARGIN + 32, divider_y, PAGE_W - MARGIN - 32, divider_y), fill="#d8c8aa", width=2)
    draw_wrapped_text(
        draw,
        "Struktur bisnis Hridya Farm sesuai untuk model kemitraan pasokan, reseller, distributor area, dan peluang pengembangan produk turunan berbasis telur asin.",
        (MARGIN + 32, divider_y + 28),
        font(22),
        GREEN_DARK,
        PAGE_W - 2 * MARGIN - 64,
        line_gap=8,
    )
    add_footer(draw, 2)
    return page


def page_products() -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), "#f8f4ec")
    draw = ImageDraw.Draw(page)
    y = draw_title(
        draw,
        "Portofolio Produk",
        "Portofolio disusun untuk menyeimbangkan kebutuhan pasar inti, produk bernilai tambah, dan potensi perluasan kanal distribusi.",
        92,
    )
    draw_kicker(draw, "Product Portfolio", MARGIN, y + 28)

    card_w = 332
    card_h = 470
    grid = [
        (MARGIN, 310),
        (MARGIN + 374, 310),
        (MARGIN + 748, 310),
        (MARGIN + 187, 835),
        (MARGIN + 561, 835),
    ]
    for product, (x, y0) in zip(PRODUCTS, grid):
        rounded_panel(draw, (x, y0, x + card_w, y0 + card_h), fill=WHITE, outline=LINE, radius=30)
        image = load_image(product.image_name, (card_w - 28, 220))
        page.paste(image, (x + 14, y0 + 14))
        name_bottom = draw_wrapped_text(draw, product.name, (x + 22, y0 + 256), font(25, bold=True, serif=True), GREEN_DARK, card_w - 44, line_gap=4)
        draw_wrapped_text(draw, product.note, (x + 22, name_bottom + 16), font(19), TEXT, card_w - 44, line_gap=6)

    add_footer(draw, 3)
    return page


def page_operations() -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), IVORY)
    draw = ImageDraw.Draw(page)
    y = draw_title(
        draw,
        "Operasional & Kapasitas",
        "Dokumen ini menyoroti aspek operasional yang relevan untuk calon distributor dan mitra pengadaan: kapasitas, kualitas, dan kesiapan pengiriman.",
        92,
    )

    rounded_panel(draw, (MARGIN, y + 38, 724, 1020), fill=WHITE, outline=LINE, radius=34)
    rounded_panel(draw, (760, y + 38, PAGE_W - MARGIN, 1020), fill=WHITE, outline=LINE, radius=34)
    draw_kicker(draw, "Supply Readiness", 110, y + 86, fill=GREEN_SOFT)
    draw.text((110, y + 148), "Kapasitas dan Ketahanan Pasok", font=font(34, bold=True, serif=True), fill=GREEN_DARK)
    points = [
        "Kemampuan pasokan mencapai hingga 3.000 butir per hari untuk kebutuhan reguler.",
        "Model operasi mendukung permintaan rumah tangga hingga pembelian dalam skala partai.",
        "Produk mentah dan olahan memungkinkan penyesuaian portofolio sesuai karakter pasar tujuan.",
    ]
    py = y + 228
    for point in points:
        point_height = measure_wrapped_text(draw, point, font(22), 478, line_gap=7)
        box_bottom = py + max(point_height + 24, 68)
        rounded_panel(draw, (110, py - 12, 694, box_bottom), fill="#fbf8f1", outline=LINE, radius=22)
        draw.rounded_rectangle((134, py + 11, 158, py + 35), radius=8, fill=GREEN)
        py = draw_wrapped_text(draw, point, (182, py), font(22), TEXT, 478, line_gap=7) + 20

    system_y = py + 18
    draw.text((110, system_y), "Sistem Produksi", font=font(34, bold=True, serif=True), fill=GREEN_DARK)
    draw_wrapped_text(
        draw,
        "Produksi menggabungkan pemeliharaan ternak, pemilihan telur, serta proses pengolahan tradisional untuk telur asin, panggang, dan asap. Kombinasi ini memberi kontrol lebih baik atas rasa, kualitas bahan baku, dan diferensiasi produk.",
        (110, system_y + 58),
        font(22),
        TEXT,
        560,
        line_gap=8,
    )

    right_x = 792
    right_w = 300
    draw_kicker(draw, "Quality Factors", right_x, y + 86, fill=GREEN_SOFT)
    fy = draw_wrapped_text(
        draw,
        "Faktor Pendukung Kualitas",
        (right_x, y + 148),
        font(31, bold=True, serif=True),
        GREEN_DARK,
        right_w,
        line_gap=4,
    )
    factors = [
        "Animal welfare untuk menjaga kondisi ternak dan kualitas hasil telur.",
        "Pakan alami dan kebersihan kandang untuk mendukung karakter rasa dan aroma produk.",
        "Sanitasi rutin untuk memperkecil risiko kontaminasi pada area produksi.",
        "Olahan bernilai tambah memberi opsi margin lebih tinggi di tingkat distribusi.",
    ]
    fy += 26
    for factor in factors:
        fy = draw_wrapped_text(draw, f"• {factor}", (right_x, fy), font(22), TEXT, right_w, line_gap=7) + 22

    rounded_panel(draw, (MARGIN, 1110, PAGE_W - MARGIN, 1604), fill=GREEN_DARK, radius=36)
    media = load_image("media__1772059382490.png", (340, 340))
    page.paste(media, (110, 1188))
    draw.rounded_rectangle((104, 1182, 458, 1536), radius=34, outline="#caa56c", width=3)
    draw_kicker(draw, "Strategic Fit", 520, 1186, fill=rgba("#214b3c", 255), text_fill="#dce9e2")
    draw.text((520, 1246), "Kesesuaian untuk Distributor", font=font(40, bold=True, serif=True), fill=WHITE)
    draw_wrapped_text(
        draw,
        "Dengan kombinasi kapasitas pasokan, variasi produk, dan pendekatan produksi langsung, Hridya Farm memiliki fondasi yang tepat untuk kerja sama distribusi area, pengadaan horeca, serta pengembangan private-label atau bundling produk.",
        (520, 1320),
        font(23),
        "#edf4ef",
        590,
        line_gap=9,
    )
    add_footer(draw, 4)
    return page


def page_partnership() -> Image.Image:
    page = Image.new("RGB", (PAGE_W, PAGE_H), "#f8f4ec")
    draw = ImageDraw.Draw(page)
    y = draw_title(
        draw,
        "Peluang Kemitraan",
        "Halaman ini merangkum bentuk kerja sama yang paling relevan untuk investor/distributor serta alasan mengapa lini bisnis Hridya Farm menarik untuk diperluas.",
        92,
    )

    draw_kicker(draw, "Partnership Opportunity", MARGIN, y + 28)
    rounded_panel(draw, (MARGIN, 310, 560, 1000), fill=WHITE, outline=LINE, radius=34)
    rounded_panel(draw, (600, 310, PAGE_W - MARGIN, 1000), fill=WHITE, outline=LINE, radius=34)
    rounded_panel(draw, (MARGIN, 1060, PAGE_W - MARGIN, 1578), fill=WHITE, outline=LINE, radius=34)

    draw.text((110, 366), "Model Kerja Sama", font=font(34, bold=True, serif=True), fill=GREEN_DARK)
    partnership_models = [
        "Distribusi area untuk kanal retail dan grosir lokal.",
        "Pasokan reguler ke rumah makan, restoran, toko oleh-oleh, dan bakery.",
        "Reseller produk olahan bernilai tambah seperti telur asin, telur asap, dan kerupuk telur asin.",
        "Pengembangan produk turunan dan bundling untuk pasar hampers atau snack premium.",
    ]
    py = 446
    for item in partnership_models:
        item_height = measure_wrapped_text(draw, item, font(23), 332, line_gap=7)
        box_bottom = py + max(item_height + 22, 66)
        rounded_panel(draw, (110, py - 12, 530, box_bottom), fill="#fbf8f1", outline=LINE, radius=22)
        draw.ellipse((132, py + 12, 150, py + 30), fill=GOLD)
        py = draw_wrapped_text(draw, item, (170, py), font(23), TEXT, 332, line_gap=7) + 26

    draw.text((630, 366), "Alasan Investasi Distribusi", font=font(34, bold=True, serif=True), fill=GREEN_DARK)
    reasons = [
        "Kapasitas pasok dan kontrol produksi berada di satu ekosistem bisnis.",
        "Produk utama sudah jelas, sementara produk turunan membuka peluang margin tambahan.",
        "Narasi kualitas dan sumber pasokan langsung mendukung positioning pasar premium dan menengah.",
        "Model distribusi dapat diperluas secara bertahap tanpa mengubah inti operasional perusahaan.",
    ]
    ry = 446
    for reason in reasons:
        ry = draw_wrapped_text(draw, f"• {reason}", (630, ry), font(23), TEXT, 500, line_gap=8) + 24

    draw_kicker(draw, "Closing Note", 110, 1104, fill=GOLD_SOFT)
    draw.text((110, 1166), "Penutup dan Arah Kerja Sama", font=font(34, bold=True, serif=True), fill=GREEN_DARK)
    close_y = draw_wrapped_text(
        draw,
        "Hridya Farm berada pada posisi yang relevan untuk kerja sama distribusi maupun pengadaan karena memiliki basis pasokan yang jelas, portofolio produk yang dapat diperluas, serta pendekatan operasional yang mendukung kesinambungan kualitas.",
        (110, 1238),
        font(23),
        TEXT,
        710,
        line_gap=8,
    )
    draw_wrapped_text(
        draw,
        "Apabila terdapat ketertarikan untuk menjajaki kemitraan lebih lanjut, Hridya Farm siap melanjutkan pada pembahasan ruang lingkup kerja sama, kebutuhan pasokan, cakupan distribusi, serta tahapan implementasi yang paling sesuai bagi kedua belah pihak.",
        (110, close_y + 10),
        font(23),
        TEXT,
        710,
        line_gap=8,
    )

    draw_kicker(draw, "Kontak", 865, 1230, fill=GREEN_SOFT)
    draw.text((865, 1288), CONTACT_PHONE, font=font(20, bold=True), fill=GREEN_DARK)
    draw.text((865, 1322), CONTACT_EMAIL, font=font(17), fill=TEXT)
    address_end = draw_wrapped_text(
        draw,
        CONTACT_ADDRESS,
        (865, 1354),
        font(15),
        TEXT,
        250,
        line_gap=4,
    )
    promo_font, _ = fit_font_size(draw, "Siap untuk pembahasan distribusi, pengadaan, dan pengembangan kerja sama.", 250, 112, 17, 14, bold=True, serif=False, line_gap=4)
    promo_y = max(address_end + 18, 1480)
    promo_y = draw_wrapped_text(draw, "Siap untuk pembahasan", (865, promo_y), promo_font, GREEN, 250, line_gap=4)
    promo_y = draw_wrapped_text(draw, "distribusi, pengadaan,", (865, promo_y + 4), promo_font, GREEN, 250, line_gap=4)
    draw_wrapped_text(draw, "dan pengembangan kerja sama.", (865, promo_y + 4), promo_font, GREEN, 250, line_gap=4)

    add_footer(draw, 5)
    return page


def generate_pages() -> Iterable[Image.Image]:
    ensure_kerupuk_asset()
    yield page_cover()
    yield page_profile()
    yield page_products()
    yield page_operations()
    yield page_partnership()


def main() -> None:
    pages = list(generate_pages())
    pages[0].save(OUTPUT, "PDF", resolution=200.0, save_all=True, append_images=pages[1:])
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
