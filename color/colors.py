import re


def rgb_to_hex(r: int, g: int, b: int) -> str:
    if not ((0 <= r < 256) and (0 <= g < 256) and (0 <= b < 256)):
        raise ValueError("Invalid RBG values. Must be 0 <= x < 256")
    return f'#{r:0>2x}{g:0>2x}{b:0>2x}'


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.upper()
    if not re.match(r"[#][0-9A-F]{6}", hex_color):
        raise ValueError(
            "Invalid hex color. Must be #XXXXXX format where X = 0-9,A-F")
    hex_color = hex_color.strip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    if not ((0 <= r < 256) and (0 <= g < 256) and (0 <= b < 256)):
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
