from PIL import Image
from statistics import mean
from math import sqrt

from color.colors import (hex_to_rgb, hex_to_hsl, hsl_to_hex,
                          rgb_to_hex, lighten)


def create_highlighted_range(dark_color: str, total_colors: int,
                             max_lightness: float) -> list[str]:
    result = []
    for i in range(total_colors):
        lightened = lighten(dark_color, i * max_lightness / (total_colors - 1))
        result.append(lightened)
    return result


def lerp(val1: float, val2: float, pcnt: float) -> float:
    return val1 + (val2 - val1) * pcnt


def hsl_lerp(color1: str, color2: str, total_colors: int) -> list[str]:
    result = []
    color1_hsl = hex_to_hsl(color1)
    color2_hsl = hex_to_hsl(color2)
    for i in range(total_colors):
        h = lerp(color1_hsl[0], color2_hsl[0], i / (total_colors - 1))
        s = lerp(color1_hsl[1], color2_hsl[1], i / (total_colors - 1))
        lt = lerp(color1_hsl[2], color2_hsl[2], i / (total_colors - 1))
        hsl = hsl_to_hex(h, s, lt)
        result.append(hsl)
    return result


def create_rgb_lerp_range(color1: str, color2: str,
                          total_colors: int) -> list[str]:
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


HSL = tuple[float, float, float]


def dist(val1: tuple[float, ...], val2: tuple[float, ...],
         weights: tuple[float, ...] | None = None) -> float:
    if weights is None:
        weights = (1,) * len(val1)
    diff_sq = [((x2 - x1) * w) ** 2 for x2, x1, w in zip(val2, val1, weights)]
    return sqrt(sum(diff_sq))


def sort_color_by_dist(lb: HSL, target: HSL, ub: HSL,
                       *colors: HSL) -> list[HSL] | None:
    candidates = []
    candidates_for_dist = []
    for hsl in colors:
        if lb[0] > ub[0]:
            is_in_hsl_range = all((l <= c and c <= 360) or (
                0 <= c and c < u) for l, c, u in zip(lb, hsl, ub))
        else:
            is_in_hsl_range = all((l <= c and c < u)
                                  for l, c, u in zip(lb, hsl, ub))
        if is_in_hsl_range:
            if (hsl[0] - lb[0]) > 60:
                hue_scaled = (hsl[0] - 360) / 60
            else:
                hue_scaled = hsl[0] / 60
            candidates.append(hsl)
            candidates_for_dist.append(hue_scaled, hsl[1], hsl[2])
    if len(candidates) == 0:
        return None
    if (ub[0] - lb[0]) == 360:
        dists = [dist(target[1:], cand[1:]) for cand in candidates_for_dist]
    else:
        # in order to emphasize hue while scaling, 0 ~= lb hue, 1 ~= ub hue
        target_hue_dist = ((target[0] - lb[0]) % 360) / 60
        target_for_dist = (target_hue_dist, target[1], target[2])
        dists = [dist(target_for_dist, cand, weights=(3, 3, 1))
                 for cand in candidates_for_dist]
    sorted_pair = sorted(zip(dists, candidates))
    dists, candidates = zip(*sorted_pair)
    return list(candidates)


def generate_ansi_palette(*colors: str, overrides: dict | None = None
                          ) -> list[str]:
    result = []
    main_targets = {
        # ansi_name : [lower_bound, target, upper_bound]
        "black": [(0, 0, 0), (0, 0, 0), (360, 0.33, 0.33)],
        "red": [(330, 0.2, 0.33), (0, 1, 0.5), (30, 1, 0.9)],
        "green": [(90, 0.2, 0.33), (120, 1, 0.5), (150, 1, 0.9)],
        "yellow": [(30, 0.2, 0.33), (60, 1, 0.5), (90, 1, 0.9)],
        "blue": [(210, 0.2, 0.33), (240, 1, 0.5), (270, 1, 0.9)],
        "magenta": [(270, 0.2, 0.33), (300, 1, 0.5), (330, 1, 0.9)],
        "cyan": [(150, 0.2, 0.33), (180, 1, 0.5), (210, 1, 0.9)],
        "white": [(0, 0, 0.67), (0, 0, 0.67), (360, 0.33, 1)],
    }
    bright_targets = {
        # ansi_name : [lower_bound, target, upper_bound]
        "bright_black": [(0, 0, 0), (0, 0, 0.33), (360, 0.33, 0.33)],
        "bright_red": [(330, 0.2, 0.33), (0, 1, 0.75), (30, 1, 0.9)],
        "bright_green": [(90, 0.2, 0.33), (120, 1, 0.75), (150, 1, 0.9)],
        "bright_yellow": [(30, 0.2, 0.33), (60, 1, 0.75), (90, 1, 0.9)],
        "bright_blue": [(210, 0.2, 0.33), (240, 1, 0.75), (270, 1, 0.9)],
        "bright_magenta": [(270, 0.2, 0.33), (300, 1, 0.75), (330, 1, 0.9)],
        "bright_cyan": [(150, 0.2, 0.33), (180, 1, 0.75), (210, 1, 0.9)],
        "bright_white": [(0, 0, 0.67), (0, 0, 1), (360, 0.33, 1)],
    }
    hsl_colors = [hex_to_hsl(color) for color in colors]
    avg_sat = mean(hsl[1] for hsl in hsl_colors)
    avg_light = mean(hsl[2] for hsl in hsl_colors)
    for name, main_target in main_targets.items():
        if overrides is not None and name in overrides.keys():
            result.append(overrides[name])
            continue
        lb, target, ub = main_target
        match = sort_color_by_dist(lb, target, ub, *hsl_colors)
        if match is None:
            theme_input = hsl_to_hex(target[0], avg_sat, avg_light)
            theme_blend = hsl_lerp(theme_input, hsl_to_hex(*target), 3)[1]
            result.append(theme_blend)
        else:
            result.append(hsl_to_hex(*match[0]))
    for index, (name, main_target) in enumerate(bright_targets.items()):
        if overrides is not None and name in overrides.keys():
            result.append(overrides[name])
            continue
        lb, target, ub = main_target
        match = sort_color_by_dist(lb, target, ub, *hsl_colors)
        if match is None or (hsl_to_hex(*match[0]) in result and len(match) == 1):
            base_color = result[index]
            lighter_color = lighten(base_color, 0.3)
            result.append(lighter_color)
        elif hsl_to_hex(*match[0]) in result:
            result.append(hsl_to_hex(*match[1]))
        else:
            result.append(hsl_to_hex(*match[0]))
    for i in range(8):
        if hex_to_hsl(result[i])[2] > hex_to_hsl(result[i + 8])[2]:
            temp = result[i]
            result[i] = result[i + 8]
            result[i + 8] = temp
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
