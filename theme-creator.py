import re
from PIL import Image


def rgb_to_hex(r: int, g: int, b: int) -> str:
    if not ((r >= 0 and r < 256) and (g >= 0 and g < 256) and (b >= 0 and b < 256)):
        raise ValueError("Invalid RBG values. Must be 0 <= x < 256")
    return f'#{r:0>2x}{g:0>2x}{b:0>2x}'


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.upper()
    if not re.match(r"[#][0-9A-F]{6}", hex_color):
        raise ValueError(
            "Invalid hex color format. Must be #XXXXXX format where X = 0-9 or A-F")
    hex_color = hex_color.strip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    if not ((r >= 0 and r < 256) and (g >= 0 and g < 256) and (b >= 0 and b < 256)):
        raise ValueError("Invalid RBG values. Must be 0 <= x < 256")
    M = max(r, g, b)
    m = min(r, g, b)
    C = M - m
    if C == 0:
        Hp = 0
    elif M == r:
        Hp = ((g - b) / C) % 6
    elif M == g:
        Hp = ((b - r) / C) + 2
    elif M == b:
        Hp = ((r - g) / C) + 4
    else:
        raise ValueError("An unknown ValueError occurred.")
    H = 60 * Hp
    L = 0.5 * (M + m) / 255
    if L == 1 or L == 0:
        S = 0
    else:
        S = abs(C / (1 - (abs(2 * L - 1) - 1))) / 255
    return (H, S, L)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    if not ((s >= 0 and s <= 1) and (l >= 0 and l <= 1)):
        raise ValueError("Values must be valid HSL values.")
    h = h % 360
    C = (1 - abs(2 * l - 1)) * s
    Hp = h / 60
    X = C * (1 - abs((Hp % 2) - 1))
    m = l - C / 2
    if 0 <= Hp < 1:
        rp, gp, bp = C, X, 0
    elif 1 <= Hp < 2:
        rp, gp, bp = X, C, 0
    elif 2 <= Hp < 3:
        rp, gp, bp = 0, C, X
    elif 3 <= Hp < 4:
        rp, gp, bp = 0, X, C
    elif 4 <= Hp < 5:
        rp, gp, bp = X, 0, C
    elif 5 <= Hp < 6:
        rp, gp, bp = C, 0, X
    else:
        raise ValueError("Could not generate RGB color. Unknown error")
    r, g, b = round((rp + m) * 255), round((gp + m)
                                           * 255), round((bp + m) * 255)
    return (r, g, b)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = hsl_to_rgb(h, s, l)
    return rgb_to_hex(r, g, b)


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    return rgb_to_hsl(*hex_to_rgb(hex_color))


def lighten(color: str, by: float) -> str:
    h, s, l = hex_to_hsl(color)
    l += by
    if l > 1:
        l = 1
    elif l < 0:
        l = 0
    return hsl_to_hex(h, s, l)


def create_highlighted_range(dark_color: str, total_colors: int,
                             max_lightness: float) -> list[str]:
    result = []
    for i in range(total_colors):
        lightened = lighten(dark_color, i * max_lightness / (total_colors - 1))
        result.append(lightened)
    return result


def lerp(val1: float, val2: float, pcnt: float) -> float:
    return val1 + (val2 - val1) * pcnt


def create_hsl_lerp_range(color1: str, color2: str, total_colors: int) -> list[str]:
    result = []
    color1_hsl = hex_to_hsl(color1)
    color2_hsl = hex_to_hsl(color2)
    for i in range(total_colors):
        h = lerp(color1_hsl[0], color2_hsl[0], i / (total_colors - 1))
        s = lerp(color1_hsl[1], color2_hsl[1], i / (total_colors - 1))
        l = lerp(color1_hsl[2], color2_hsl[2], i / (total_colors - 1))
        hsl = hsl_to_hex(h, s, l)
        result.append(hsl)
    return result


def create_rgb_lerp_range(color1: str, color2: str, total_colors: int) -> list[str]:
    result = []
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    for i in range(total_colors):
        r = round(lerp(color1_rgb[0], color2_rgb[0], i / (total_colors - 1)))
        g = round(lerp(color1_rgb[1], color2_rgb[1], i / (total_colors - 1)))
        b = round(lerp(color1_rgb[2], color2_rgb[2], i / (total_colors - 1)))
        rgb = rgb_to_hex(r, g, b)
        result.append(rgb)
    return result


def show_palettes(*palettes: list[str], blob_size: int = 100) -> None:
    max_len_pal = max([len(palette) for palette in palettes])
    imsize = (blob_size * len(palettes), blob_size * max_len_pal)
    pic = Image.new("RGB", imsize, color="#ffffff")
    for i, palette in enumerate(palettes):
        for j, color in enumerate(palette):
            blob = Image.new("RGB", (blob_size, blob_size), color=color)
            pic.paste(blob, (blob_size * i, blob_size * j))
    pic.show()
    return


def generate_ansi_palette(*colors: str) -> list[str]:
    result = []
    thresholds = {
        "black": [(0, 0, 0), (360, 0.2, 0.2)],
        "red": [(0, 0, 0), (360, 0.2, 0.2)],
        "green": [(0, 0, 0), (360, 0.2, 0.2)],
    }
    return result


class ThemeError(Exception):
    pass


def generate_theme_palette(basic_ui: list[str], variable: list[str],
                           language: list[str], constant: list[str],
                           ui_additional: dict[str, str],
                           ansi: list[str] | None = None, min_colors=3,
                           max_lightness=0.9) -> dict:
    if len(basic_ui) == 0:
        raise ThemeError("Need at least one color to generate palette.")
    elif len(basic_ui) == 1:
        _, _, l = hex_to_hsl(basic_ui[0])
        basic_ui = create_highlighted_range(
            basic_ui[0], min_colors, max_lightness)
    elif len(basic_ui) == 2:
        _, _, l = hex_to_hsl(basic_ui[0])
        basic_ui = create_rgb_lerp_range(
            basic_ui[0], basic_ui[1], min_colors)

    theme = {
        "ui_basic": basic_ui,
        "variable": variable,
        "language": language,
        "constant": constant,
        "ui_messages": ui_additional["messages"],
        "ansi": ui_additional["ansi"]
    }
    return theme


def modify_vscode_settings(theme: dict[str, str]) -> None:
    return


def main() -> None:
    gray_palette = create_rgb_lerp_range("#12100d", "#c9c2b5", 6)
    blue_palette = create_rgb_lerp_range("#1f3a70", "#e5e7fc", 6)
    red_palette = create_rgb_lerp_range("#7b2f2d", "#ff4f00", 6)
    copper_palette = create_highlighted_range("#c9b292", 3, -0.2)
    col4_palette = ["#5b8267", "#6bbd85",
                    "#cd7e1f", "#edb940", "#18ade4", "#baddf0"]
    col5_palette = ["#ba160c", "#fc3b1b", *copper_palette, "#eaece9"]
    show_palettes(gray_palette, blue_palette,
                  red_palette, col4_palette, col5_palette)
    return


if __name__ == "__main__":
    main()
