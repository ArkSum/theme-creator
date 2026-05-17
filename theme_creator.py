from PIL import Image
from pathlib import Path
from statistics import mean
from math import sqrt
from itertools import batched
from copy import copy

from theme.vscode import modify_vscode_settings
from theme.neovim import create_lua_groups
from color.colors import (hex_to_rgb, hex_to_hsl, hsl_to_hex,
                          rgb_to_hex, lighten, lightness)


def create_highlighted_range(start_color: str, total_colors: int,
                             end_lightness: float) -> list[str]:
    result = []
    for i in range(total_colors):
        lightness_range = end_lightness - lightness(start_color)
        lightened = lighten(start_color, i *  lightness_range / (total_colors - 1))
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


def rgb_lerp(color1: str, color2: str, total_colors: int) -> list[str]:
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


def show_palettes(*palettes: list[str], blob_size: int = 100,
                  max_col_size: int = 8) -> None:
    palette_list = list(palettes)
    i = 0
    while i < len(palette_list):
        j = 0
        if len(palette_list[i]) > max_col_size:
            palette = palette_list.pop(i)
            split_palette = batched(palette, max_col_size)
            for j, partial_palette in enumerate(split_palette):
                palette_list.insert(i + j, list(partial_palette))
        i += 1 + j

    max_len_pal = max([len(palette) for palette in palette_list])
    imsize = (blob_size * len(palette_list), blob_size * max_len_pal)
    pic = Image.new("RGB", imsize, color="#ffffff")
    for i, palette in enumerate(palette_list):
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
                       *colors: str) -> list[str] | None:
    candidates = []
    candidates_for_dist = []
    for color in colors:
        hsl = hex_to_hsl(color)
        if lb[0] > ub[0]:
            is_in_hsl_range = all((l <= c <= 360) or (0 <= c < u)
                                  for l, c, u in zip(lb, hsl, ub))
        else:
            is_in_hsl_range = all((l <= c < u)
                                  for l, c, u in zip(lb, hsl, ub))
        if is_in_hsl_range:
            if hsl[0] - lb[0] > 60:
                hue_scaled = (hsl[0] - 360) / 60
            else:
                hue_scaled = hsl[0] / 60
            candidates.append(hsl)
            candidates_for_dist.append((hue_scaled, hsl[1], hsl[2]))
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
    result = list(hsl_to_hex(*item) for item in candidates)
    return result


def generate_ansi_palette(*colors: str, overrides: dict | None = None
                          ) -> list[str]:
    result = []
    main_targets = {
        # ansi_name : [lower_bound, target, upper_bound]
        "black": [(0, 0, 0), (0, 0, 0), (360, 0.33, 0.33)],
        "red": [(330, 0.1, 0.33), (0, 1, 0.5), (30, 1, 0.9)],
        "green": [(90, 0.1, 0.33), (120, 1, 0.5), (150, 1, 0.9)],
        "yellow": [(30, 0.1, 0.33), (60, 1, 0.5), (90, 1, 0.9)],
        "blue": [(210, 0.1, 0.33), (240, 1, 0.5), (270, 1, 0.9)],
        "magenta": [(270, 0.1, 0.33), (300, 1, 0.5), (330, 1, 0.9)],
        "cyan": [(150, 0.1, 0.33), (180, 1, 0.5), (210, 1, 0.9)],
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
        match = sort_color_by_dist(lb, target, ub, *colors)
        if match is None:
            theme_input = hsl_to_hex(target[0], avg_sat, avg_light)
            theme_blend = hsl_lerp(theme_input, hsl_to_hex(*target), 3)[1]
            result.append(theme_blend)
        else:
            result.append(match[0])
    for index, (name, bright_target) in enumerate(bright_targets.items()):
        if overrides is not None and name in overrides.keys():
            result.append(overrides[name])
            continue
        lb, target, ub = bright_target 
        match = sort_color_by_dist(lb, target, ub, *colors)
        if match is None or (match[0] in result and len(match) == 1):
            base_color = result[index]
            lighter_color = lighten(base_color, 0.3)
            result.append(lighter_color)
        elif match[0] in result:
            result.append(match[1])
        else:
            result.append(match[0])
    for i in range(8):
        if hex_to_hsl(result[i])[2] > hex_to_hsl(result[i + 8])[2]:
            temp = result[i]
            result[i] = result[i + 8]
            result[i + 8] = temp
    return result


def generate_git_palette(*colors: str, overrides: dict | None = None
                         ) -> list[str]:
    result = []
    main_targets = {
        # ansi_name : [lower_bound, target, upper_bound]
        # Bright green/blue
        "added": [(90, 0.1, 0.33), (140, 0.7, 0.7), (210, 0.9, 0.9)],
        # Yellow
        "modified": [(30, 0.1, 0.33), (60, 1, 0.5), (90, 1, 0.9)],
        # Red
        "deleted": [(330, 0.1, 0.33), (0, 1, 0.7), (30, 1, 0.9)],
        # Gray
        "ignored": [(0, 0, 0.33), (0, 0, 0.5), (360, 0.33, 0.67)],
        # Mild green/blue
        "untracked": [(90, 0.1, 0.3), (160, 0.3, 0.4), (210, 0.4, 0.6)],
        # Dark Red
        "conflicting": [(330, 0.1, 0.33), (0, 1, 0.3), (30, 1, 0.9)],
    }
    hsl_colors = [hex_to_hsl(color) for color in colors]
    avg_sat = mean(hsl[1] for hsl in hsl_colors)
    avg_light = mean(hsl[2] for hsl in hsl_colors)
    for name, main_target in main_targets.items():
        if name == "untracked":
            pass
        if overrides is not None and name in overrides.keys():
            result.append(overrides[name])
            continue
        lb, target, ub = main_target
        match = sort_color_by_dist(lb, target, ub, *colors)
        if match is not None and len(match) > 1:
            i = 0
            while i < len(match) and match[i] in result:
                i += 1
            if i == len(match):
                match = None
            else:
                result.append(match[i])
                continue
        if match is None:
            theme_input = hsl_to_hex(target[0], avg_sat, avg_light)
            theme_blend = hsl_lerp(theme_input, hsl_to_hex(*target), 3)[1]
            result.append(theme_blend)
        else:
            result.append(match[0])
    return result


class ThemeError(Exception):
    pass


def generate_palette(*colors: str, min_colors: int = 3,
                     max_lightness: float = 0.9) -> list[str]:
    if len(colors) == 1:
        result = create_highlighted_range(colors[0], min_colors, max_lightness)
    elif len(colors) < min_colors:
        result = rgb_lerp(colors[0], colors[-1], min_colors)
    else:
        result = list(colors)
    return result


def generate_theme_palette(basic: list[str] | str, git: list[str] | str | None = None,
                           hilite: dict[str, list[str]] | None = None,
                           ansi: list[str] | None = None, min_colors=3,
                           max_lightness=0.9) -> dict:
    if isinstance(basic, str):
        basic = [basic]
        theme_basic = generate_palette(*basic, min_colors=min_colors, max_lightness=max_lightness)
    else:
        theme_basic = copy(basic)

    all_colors = basic
    if hilite is not None:
        hilite_colors = [color for palette in hilite.values()
                         for color in palette]
        all_colors.extend(hilite_colors)

    if ansi is None:
        theme_ansi = generate_ansi_palette(*all_colors)
    else:
        theme_ansi = ansi

    if hilite is None:
        theme_brackets = [
            theme_ansi[11], theme_ansi[13], theme_ansi[14],
            theme_ansi[11], theme_ansi[13], theme_ansi[14]
        ]
        theme_hilite = [
            theme_ansi[12],
            theme_ansi[12],
            theme_ansi[9],
            theme_ansi[11]
        ]
    else:
        theme_brackets = hilite["brackets"]
        theme_hilite = hilite["main"]

    if git is None:
        theme_git = generate_git_palette(*all_colors)
    else:
        theme_git = copy(git)
    mid_gray = theme_basic[int(len(theme_basic) / 2)]
    theme_scrollbar = [mid_gray + "40", mid_gray + "80"]

    theme = {
        "basic": theme_basic,
        "scrollbar": theme_scrollbar,
        "highlight": theme_hilite,
        "git": theme_git,
        "brackets": theme_brackets,
        "ansi": theme_ansi,
    }
    return theme


def demo_palettes() -> None:
    gray_palette = rgb_lerp("#12100d", "#c9c2b5", 6)
    blue_palette = rgb_lerp("#1f3a70", "#e5e7fc", 6)
    red_palette = rgb_lerp("#7b2f2d", "#ff4f00", 6)
    copper_palette = create_highlighted_range("#c9b292", 3, -0.2)
    other_colors = ["#5b8267", "#6bbd85", "#cd7e1f", "#edb940",
                    "#18ade4", "#baddf0", "#ba160c", "#fc3b1b", "#eaece9"]
    all_colors = [*gray_palette, *blue_palette, *red_palette, *other_colors]
    ansi_overrides = {
        'magenta': copper_palette[2],
        'bright_magenta': copper_palette[0],
    }
    ansi_colors = generate_ansi_palette(*all_colors,
                                        overrides=ansi_overrides)
    show_palettes(ansi_colors)
    return


def main() -> None:
    gray_palette = rgb_lerp("#12100d", "#c9c2b5", 4)
    gray_palette.append("#eaece9")
    blue_palette = rgb_lerp("#1f3a70", "#e5e7fc", 6)
    red_palette = rgb_lerp("#7b2f2d", "#ff4f00", 6)
    copper_palette = create_highlighted_range("#d3c3ab", 3, 0.6)
    other_colors = ["#5b8267", "#6bbd85", "#cd7e1f", "#edb940",
                    "#18ade4", "#baddf0", "#2369b1", "#ba160c", "#fc3b1b"]
    col4_palette = other_colors[:6]
    col5_palette = [*other_colors[6:], *copper_palette]
    all_colors = [*gray_palette, *blue_palette, *red_palette, *other_colors]
    ansi_overrides = {
        'magenta': copper_palette[2],
        'bright_magenta': copper_palette[0],
    }
    ansi_colors = generate_ansi_palette(*all_colors,
                                        overrides=ansi_overrides)
    git_colors = generate_git_palette(*all_colors)
    highlights = {
        "comment": [copper_palette[2]],
        "warning": [other_colors[3]],
        "error": [other_colors[7]],
        "brackets": [*copper_palette, *copper_palette],
        "main": [other_colors[1], other_colors[4], other_colors[3], other_colors[7]],
    }
    language = {  # Docstring:  #cd7e1f
        "Normal": gray_palette[3],  #c9c2b6
        "Comment": copper_palette[2],  #9f8662
        "Numeric": other_colors[5],  #baddf0
        "String": other_colors[1],  #6bbd85
        "Keyword": other_colors[8],  #fc3b1b
        "Constant": red_palette[3],  #cc512e
        "Function": blue_palette[-1],  #e5e7fc
        "Variable": blue_palette[3],  #97b8da
        "Parameter": other_colors[5],  #baddf0
        # "Decorator": blue_palette[4],  #c7d8e9
        "Types": other_colors[6],  #2369b1 + "bold"
        "Constant Name": other_colors[4],  #18ade4
        "Language Variable": blue_palette[2]
    }
    ui_colors = generate_theme_palette(gray_palette, git=git_colors,
                                       hilite=highlights, ansi=ansi_colors)
    all_palettes = list(palette for palette in ui_colors.values()
                        if palette is not None)
    print("{")
    for key, palette in ui_colors.items():
        print(f'\t{key}: {str(palette)},')
    print("}")
    show_palettes(*all_palettes)
    modify_vscode_settings(Path("./.vscode/settings.json"), ui_colors, language)
    return


if __name__ == "__main__":
    main()
