"""Piezas compartidas por los generadores de SVG del perfil.

Los SVG se ven dentro de un <img> en GitHub: no pueden cargar nada externo,
así que las fuentes, los logos y los íconos van embebidos en base64.
Solo usa la biblioteca estándar de Python.
"""

import base64
import json
import pathlib
from functools import lru_cache
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "src"

# Paleta de la marca: verde gecko, cian neón y magenta de los logos.
C = {
    "bg0": "#070b10",
    "bg1": "#0d141d",
    "panel": "#111923",
    "line": "#1f2a37",
    "text": "#e6edf3",
    "soft": "#c3cfdb",
    "muted": "#8293a7",
    "green": "#4ade80",
    "cyan": "#00d1ff",
    "magenta": "#ff3ea5",
    "gold": "#f5c542",
    "android": "#3ddc84",
}

SANS = "'Space Grotesk', 'Segoe UI', Ubuntu, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, monospace"
# JetBrains Mono mide 600/1000 em por carácter: el ancho del texto es exacto.
MONO_ADVANCE = 0.6

FONTS = {
    "sg500": ("Space Grotesk", 500, "space-grotesk-latin-500-normal.woff2"),
    "sg700": ("Space Grotesk", 700, "space-grotesk-latin-700-normal.woff2"),
    "jb400": ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal.woff2"),
    "jb700": ("JetBrains Mono", 700, "jetbrains-mono-latin-700-normal.woff2"),
}

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def t(text):
    return escape(str(text))


def b64(path):
    return base64.b64encode(pathlib.Path(path).read_bytes()).decode()


def font_css(*keys):
    rules = []
    for key in keys:
        family, weight, file = FONTS[key]
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64(SRC / 'fonts' / file)}) format('woff2')}}"
        )
    return "".join(rules)


def image_uri(name):
    return f"data:image/jpeg;base64,{b64(SRC / 'img' / name)}"


@lru_cache(maxsize=None)
def icons():
    return json.loads((SRC / "icons.json").read_text())


def mono_width(text, size):
    return len(text) * MONO_ADVANCE * size


def _lum(hex_color):
    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def readable(hex_color, floor=0.16):
    """Aclara los colores de marca que se pierden sobre fondo oscuro."""
    hex_color = "#" + hex_color.lstrip("#")
    if _lum(hex_color) < 0.02:
        return C["text"]
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    while _lum(f"#{r:02x}{g:02x}{b:02x}") < floor:
        r, g, b = (round(c + (255 - c) * 0.12) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def icon(slug, x, y, size, color=None):
    data = icons()[slug]
    fill = color or readable(data["hex"])
    return (
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24">'
        f'<path fill="{fill}" d="{data["path"]}"/></svg>'
    )


def chip(x, y, text, color, size=12, height=26, pad=12):
    width = mono_width(text, size) + pad * 2
    svg = (
        f'<g transform="translate({x:.1f} {y:.1f})">'
        f'<rect width="{width:.1f}" height="{height}" rx="{height / 2}" fill="{color}" fill-opacity=".08" '
        f'stroke="{color}" stroke-opacity=".45"/>'
        f'<text x="{pad}" y="{height / 2 + size * 0.36:.1f}" font-family="{MONO}" font-size="{size}" '
        f'fill="{C["soft"]}">{t(text)}</text></g>'
    )
    return svg, width


def svg_doc(width, height, title, body, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{t(title)}">'
        f"<title>{t(title)}</title><style>{css}{REDUCED_MOTION}</style><defs>{defs}</defs>{body}</svg>\n"
    )


def write(path, content):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}  {len(content) / 1024:.0f} KB")
