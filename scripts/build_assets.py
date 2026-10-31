#!/usr/bin/env python3
"""Genera los SVG estáticos del perfil en assets/.

Uso:  python3 scripts/build_assets.py

Para cambiar un texto (una tarjeta de proyecto, el setup, el stack) edita los
datos de este archivo y vuelve a ejecutarlo. Las estadísticas de GitHub no
salen de aquí: las genera scripts/github_stats.py desde la Action del perfil.
"""

from svgkit import C, MONO, MONO_ADVANCE, ROOT, SANS, chip, font_css, icon, icons, image_uri, mono_width, readable, svg_doc, t, write

OUT = ROOT / "assets"

# ---------------------------------------------------------------- datos

TYPING = [
    "Desarrollador con ojo de diseñador",
    "Rust · Tauri · Python · GTK · QML",
    "Arch Linux + dotfiles al extremo",
    "Transformando la lógica en estética",
]

DEGREES = [
    ("Lic. en Gestión y Desarrollo de Tecnología", C["green"]),
    ("Maestría en Diseño Multimedia", C["cyan"]),
]

PROJECTS = [
    {
        "slug": "gekkoapp",
        "accent": C["cyan"],
        "label": "PROYECTO INSIGNIA",
        "star": True,
        "title": "GekkoApp",
        "tagline": ["Control Center para Arch Linux,", "Garuda y Solus"],
        "desc": [
            "Instala, actualiza y desinstala todo tu entorno",
            "con un clic: releases verificados con SHA-256,",
            "auto-actualización y tema Material You.",
        ],
        "chips": ["Rust", "Tauri v2", "Arch · Solus"],
    },
    {
        "slug": "nitro-gekko",
        "accent": C["magenta"],
        "label": "CONTROL DE HARDWARE",
        "title": "Nitro Gekko",
        "tagline": ["Panel de control del Acer Nitro", "AN17-51 para GNOME"],
        "desc": [
            "Perfiles térmicos, ventiladores, límite de",
            "potencia, salud de batería y teclado RGB de",
            "4 zonas, sin editar /sys a mano.",
        ],
        "chips": ["Python", "GTK4 · libadwaita", "GNOME Shell"],
    },
    {
        "slug": "gekko-bauh",
        "accent": C["gold"],
        "label": "TIENDA DE APLICACIONES",
        "title": "bauh Gekko Edition",
        "title_size": 25,
        "tagline": ["Gestor gráfico de software para", "Arch Linux, Flatpak y Solus"],
        "desc": [
            "pacman, AUR y Chaotic AUR en una sola interfaz.",
            "Fork independiente de bauh, con identidad",
            "propia y releases verificados.",
        ],
        "chips": ["Python", "PyQt5", "AUR · Flatpak · eopkg"],
    },
    {
        "slug": "gekko-adb",
        "accent": C["android"],
        "label": "SUITE ANDROID",
        "title": "Gekko ADB Studio",
        "tagline": ["Control total de tu Android", "desde Linux, nativo en GTK"],
        "desc": [
            "Espejo con scrcpy, debloat por marca, gaming",
            "con teclado y mando reales, APKs y ADB por",
            "Wi-Fi en un clic. Tema Matugen dinámico.",
        ],
        "chips": ["Python", "GTK 4 / 3", "ADB · scrcpy"],
    },
]

# (etiqueta, slug de simple-icons o glifo propio, color opcional)
STACK = [
    ("desarrollo", [
        ("Rust", "rust", "#dea584"), ("C++", "cplusplus", None), ("C#", "!csharp", None),
        ("Java", "openjdk", "#ed8b00"), ("Python", "python", None), ("TypeScript", "typescript", None),
        ("PHP", "php", None), ("Ruby", "ruby", None), ("Swift", "swift", None),
        ("Kotlin", "kotlin", None), ("HTML5", "html5", None), ("CSS", "css", None),
        ("Bash", "gnubash", None), ("Qt / QML", "qt", None), ("Tauri", "tauri", None),
        ("GTK", "gtk", None), ("MySQL", "mysql", None), ("JSON", "json", None),
    ]),
    ("diseño multimedia", [
        ("Photoshop", "!Ps:#31a8ff", None), ("Illustrator", "!Ai:#ff9a00", None),
        ("After Effects", "!Ae:#9999ff", None), ("GIMP", "gimp", None), ("Krita", "krita", None),
        ("Blender", "blender", None), ("Affinity", "!Af:#4fb3ff", None), ("Kdenlive", "kdenlive", None),
    ]),
    ("sistemas y entornos", [
        ("Arch Linux", "archlinux", None), ("Linux", "linux", None), ("Windows", "!windows", None),
        ("Docker", "docker", None), ("Git", "git", None), ("GNOME", "gnome", None),
        ("Hyprland", "hyprland", None), ("Niri", "niri", None),
    ]),
]

SETUP = [
    ("OS", "Arch Linux x86_64 · Windows (secundario)"),
    ("Host", "Acer Nitro AN17-51"),
    ("CPU", "Intel Core i7-13620H"),
    ("GPU", "NVIDIA GeForce RTX 4050 Laptop"),
    ("Stack", "Rust · Tauri · Python · GTK · QML"),
    ("Diseño", "Blender · Krita · GIMP · Adobe"),
    ("Lema", "Transformando la lógica en estética"),
]

ARCH_LOGO = r"""                   -`
                  .o+`
                 `ooo/
                `+oooo:
               `+oooooo:
               -+oooooo+:
             `/:-:++oooo+:
            `/++++/+++++++:
           `/++++++++++++++:
          `/+++ooooooooooooo/`
         ./ooosssso++osssssso+`
        .oossssso-````/ossssss+`
       -osssssso.      :ssssssso.
      :osssssss/        osssso+++.
     /ossssssss/        +ssssooo/-
   `/ossssso+/:-        -:/+osssso+-
  `+sso+:-`                 `.-/+oso:
 `++:.                           `-/+/
 .`                                 `/"""

MOTTO = "Transformando la lógica en estética, un commit a la vez."

CONTACT = [
    ("gmail", "Gmail", "anyaspy5426@gmail.com"),
    ("discord", "Discord", "thegekko5"),
]


# ---------------------------------------------------------------- piezas

def glow_orbs(orbs):
    """Manchas de luz difusas; cada una deriva despacio en bucle."""
    defs, body = [], []
    for i, (cx, cy, r, color, op) in enumerate(orbs):
        defs.append(
            f'<radialGradient id="orb{i}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        )
        body.append(f'<circle class="orb o{i % 3}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb{i})"/>')
    css = (
        ".orb{transform-box:fill-box;transform-origin:center}"
        ".o0{animation:drift 14s ease-in-out infinite alternate}"
        ".o1{animation:drift 18s ease-in-out -6s infinite alternate-reverse}"
        ".o2{animation:drift 22s ease-in-out -3s infinite alternate}"
        "@keyframes drift{from{transform:translate(-18px,-10px) scale(1)}to{transform:translate(22px,14px) scale(1.08)}}"
    )
    return "".join(defs), "".join(body), css


def typing_line(x, y, size, phrases, color):
    """Texto que se escribe y se borra en bucle (SMIL, funciona dentro de <img>)."""
    cw = size * MONO_ADVANCE
    type_s, hold_s, erase_s, gap_s = 0.055, 2.2, 0.022, 0.35
    points, spans, now = [], [], 0.0
    for phrase in phrases:
        start = now
        for n in range(len(phrase) + 1):
            points.append((now, n * cw))
            now += type_s
        now += hold_s
        for n in range(len(phrase), -1, -1):
            points.append((now, n * cw))
            now += erase_s
        now += gap_s
        spans.append((start, now))
    total = now
    key_times = ";".join(f"{p[0] / total:.5f}" for p in points)
    widths = ";".join(f"{p[1]:.1f}" for p in points)
    cursor_x = ";".join(f"{x + p[1]:.1f}" for p in points)
    first_w = len(phrases[0]) * cw

    texts = []
    for i, (phrase, (start, end)) in enumerate(zip(phrases, spans)):
        if i == 0:
            values, times = "visible;hidden", f"0;{end / total:.5f}"
        else:
            values, times = "hidden;visible;hidden", f"0;{start / total:.5f};{end / total:.5f}"
        texts.append(
            f'<text x="{x}" y="{y}" visibility="{"visible" if i == 0 else "hidden"}">{t(phrase)}'
            f'<animate attributeName="visibility" values="{values}" keyTimes="{times}" '
            f'dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/></text>'
        )
    defs = (
        f'<clipPath id="typeclip"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="{first_w:.1f}">'
        f'<animate attributeName="width" values="{widths}" keyTimes="{key_times}" dur="{total:.2f}s" '
        f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
    )
    body = (
        f'<g clip-path="url(#typeclip)" font-family="{MONO}" font-size="{size}" fill="{color}">{"".join(texts)}</g>'
        f'<rect class="blink" x="{x + first_w:.1f}" y="{y - size * 0.82:.1f}" width="{cw * 0.9:.1f}" height="{size * 1.05:.1f}" '
        f'fill="{color}" rx="2"><animate attributeName="x" values="{cursor_x}" keyTimes="{key_times}" '
        f'dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )
    css = ".blink{animation:blink 1.05s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    return defs, body, css


def star(x, y, r, color):
    import math
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{x + rad * math.cos(a):.1f},{y + rad * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}"/>'


# ---------------------------------------------------------------- SVGs

def header():
    w, h = 1200, 400
    orb_defs, orbs, orb_css = glow_orbs([
        (160, 40, 300, C["cyan"], 0.30),
        (1080, 420, 320, C["magenta"], 0.26),
        (930, 210, 230, C["green"], 0.30),
    ])
    type_defs, type_body, type_css = typing_line(98.4, 300, 22, TYPING, C["cyan"])

    chips, cx = [], 72
    for text, color in DEGREES:
        svg, cw = chip(cx, 330, text, color, size=13, height=30, pad=14)
        chips.append(svg)
        cx += cw + 12

    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg0"]}"/>'
        f'<stop offset=".65" stop-color="#0a1119"/><stop offset="1" stop-color="#0b0d14"/></linearGradient>'
        f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0V40" fill="none" stroke="#17222f" stroke-width="1"/></pattern>'
        f'<radialGradient id="gridfade" cx=".32" cy=".42" r=".75"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#000"/></radialGradient>'
        f'<mask id="gridmask"><rect width="{w}" height="{h}" fill="url(#gridfade)"/></mask>'
        f'<linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}"/>'
        f'<stop offset="1" stop-color="{C["cyan"]}"/></linearGradient>'
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}" stop-opacity="0"/>'
        f'<stop offset=".3" stop-color="{C["green"]}"/><stop offset=".6" stop-color="{C["cyan"]}"/>'
        f'<stop offset="1" stop-color="{C["magenta"]}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="mascotfade" cx=".55" cy=".48" r=".58"><stop offset=".45" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#000"/></radialGradient>'
        f'<linearGradient id="mascotfloor" x1="0" y1="0" x2="0" y2="1"><stop offset=".72" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#000"/></linearGradient>'
        f'<mask id="mascotmask" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#mascotfade)"/></mask>'
        f'<mask id="floormask" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#mascotfloor)"/></mask>'
        f'<filter id="blur" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="14"/></filter>'
        + orb_defs + type_defs
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        f'<rect width="{w}" height="{h}" fill="url(#grid)" mask="url(#gridmask)"/>'
        + orbs +
        f'<g class="blend" mask="url(#floormask)"><image class="mascot" href="{image_uri("mascot.jpg")}" x="676" y="58" '
        f'width="530" height="343" mask="url(#mascotmask)"/></g>'
        f'<text x="72" y="104" font-family="{MONO}" font-size="17">'
        f'<tspan fill="{C["green"]}">the-gekko@arch</tspan><tspan fill="{C["muted"]}">:</tspan>'
        f'<tspan fill="{C["cyan"]}">~</tspan><tspan fill="{C["muted"]}">$ </tspan>'
        f'<tspan fill="{C["text"]}">whoami</tspan></text>'
        f'<text x="66" y="194" font-family="{SANS}" font-weight="700" font-size="92" letter-spacing="-2" '
        f'fill="url(#title)" opacity=".55" filter="url(#blur)">The-Gekko</text>'
        f'<text x="66" y="194" font-family="{SANS}" font-weight="700" font-size="92" letter-spacing="-2" '
        f'fill="url(#title)">The-Gekko</text>'
        f'<text x="72" y="240" font-family="{SANS}" font-weight="500" font-size="28" letter-spacing="1" fill="{C["soft"]}">'
        f'<tspan fill="{C["magenta"]}" font-family="{MONO}">// </tspan>Soluciones Tech</text>'
        f'<text x="72" y="300" font-family="{MONO}" font-size="22" fill="{C["magenta"]}">&gt;</text>'
        + type_body + "".join(chips) +
        f'<rect y="{h - 2}" width="{w}" height="2" fill="url(#edge)"/>'
    )
    css = font_css("sg500", "sg700", "jb400") + orb_css + type_css + (
        ".blend{mix-blend-mode:lighten}.mascot{animation:float 6s ease-in-out infinite}"
        "@keyframes float{50%{transform:translateY(-8px)}}"
    )
    write(OUT / "header.svg", svg_doc(w, h, "The-Gekko · Soluciones Tech — desarrollador con ojo de diseñador", body, css, defs))


def divider():
    w, h = 1200, 14
    defs = (
        f'<linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}" stop-opacity="0"/>'
        f'<stop offset=".25" stop-color="{C["green"]}" stop-opacity=".7"/><stop offset=".5" stop-color="{C["cyan"]}"/>'
        f'<stop offset=".75" stop-color="{C["magenta"]}" stop-opacity=".7"/>'
        f'<stop offset="1" stop-color="{C["magenta"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    body = (
        f'<rect y="6" width="{w}" height="2" rx="1" fill="url(#line)"/>'
        f'<rect class="shine" y="5" width="180" height="4" rx="2" fill="url(#shine)"/>'
        f'<rect x="{w / 2 - 5}" y="2" width="10" height="10" rx="2" fill="{C["bg0"]}" stroke="{C["cyan"]}" '
        f'stroke-width="1.5" transform="rotate(45 {w / 2} 7)"/>'
    )
    css = (
        ".shine{animation:sweep 5s ease-in-out infinite}"
        f"@keyframes sweep{{from{{transform:translateX(-200px)}}to{{transform:translateX({w + 20}px)}}}}"
    )
    write(OUT / "divider.svg", svg_doc(w, h, "separador", body, css, defs))


def project_card(p):
    w, h = 500, 290
    accent = p["accent"]
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101822"/>'
        f'<stop offset="1" stop-color="#0a0f15"/></linearGradient>'
        f'<linearGradient id="stroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity=".9"/>'
        f'<stop offset=".5" stop-color="{C["line"]}"/><stop offset="1" stop-color="{accent}" stop-opacity=".35"/></linearGradient>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{accent}" stop-opacity=".45"/>'
        f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="corner" cx="1" cy="1" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".12"/>'
        f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="logo"><rect x="30" y="30" width="112" height="112" rx="20"/></clipPath>'
    )
    lx = 164
    label = ""
    if p.get("star"):
        label += star(lx + 6, 45.5, 7, accent)
        lx += 19
    label += (
        f'<text x="{lx}" y="50" font-family="{MONO}" font-weight="700" font-size="11.5" letter-spacing="1.6" '
        f'fill="{accent}">{t(p["label"])}</text>'
    )
    tagline = "".join(
        f'<text x="164" y="{114 + i * 20}" font-family="{SANS}" font-weight="500" font-size="14.5" fill="{C["soft"]}">{t(line)}</text>'
        for i, line in enumerate(p["tagline"])
    )
    desc = "".join(
        f'<text x="30" y="{176 + i * 21}" font-family="{SANS}" font-weight="500" font-size="14.5" fill="{C["muted"]}">{t(line)}</text>'
        for i, line in enumerate(p["desc"])
    )
    chips, cx = [], 30
    for text in p["chips"]:
        svg, cw = chip(cx, h - 56, text, accent)
        chips.append(svg)
        cx += cw + 8
    arrow = (
        f'<g transform="translate({w - 46} 26)" stroke="{C["muted"]}" stroke-width="1.6" fill="none" stroke-linecap="round">'
        f'<circle cx="14" cy="14" r="14" stroke="{C["line"]}"/>'
        f'<path d="M10 18 18 10M12 10h6v6"/></g>'
    )
    body = (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="20" fill="url(#bg)" stroke="url(#stroke)" stroke-width="1.5"/>'
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="20" fill="url(#corner)"/>'
        f'<circle class="pulse" cx="86" cy="86" r="92" fill="url(#glow)"/>'
        f'<image href="{image_uri(p["slug"] + ".jpg")}" x="30" y="30" width="112" height="112" clip-path="url(#logo)"/>'
        f'<rect x="30" y="30" width="112" height="112" rx="20" fill="none" stroke="{accent}" stroke-opacity=".5"/>'
        + label +
        f'<text x="163" y="88" font-family="{SANS}" font-weight="700" font-size="{p.get("title_size", 28)}" '
        f'fill="{C["text"]}">{t(p["title"])}</text>'
        + tagline + desc + "".join(chips) + arrow
    )
    css = font_css("sg500", "sg700", "jb400", "jb700") + (
        ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 4s ease-in-out infinite}"
        "@keyframes pulse{50%{opacity:.55;transform:scale(1.08)}}"
    )
    write(OUT / "cards" / f'{p["slug"]}.svg', svg_doc(w, h, f'{p["title"]} — {" ".join(p["tagline"])}', body, css, defs))


def custom_glyph(spec, x, y, size):
    """Íconos que simple-icons ya no publica (Adobe, Affinity, C#, Windows)."""
    if spec == "!windows":
        color, s, g = "#3aa0ff", size / 2 - 1.5, 3
        return "".join(
            f'<rect x="{x + dx * (s + g):.1f}" y="{y + dy * (s + g):.1f}" width="{s:.1f}" height="{s:.1f}" rx="1.5" fill="{color}"/>'
            for dx in (0, 1) for dy in (0, 1)
        )
    if spec == "!csharp":
        color, cx, cy, r = "#b77fd6", x + size / 2, y + size / 2, size / 2
        import math
        pts = " ".join(f"{cx + r * math.cos(math.pi / 6 + i * math.pi / 3):.1f},{cy + r * math.sin(math.pi / 6 + i * math.pi / 3):.1f}" for i in range(6))
        return (
            f'<polygon points="{pts}" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-width="2"/>'
            f'<text x="{cx}" y="{cy + 4.6}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="13" fill="{color}">C#</text>'
        )
    letters, color = spec[1:].split(":")
    return (
        f'<rect x="{x + 1}" y="{y + 1}" width="{size - 2}" height="{size - 2}" rx="6" fill="{color}" fill-opacity=".12" '
        f'stroke="{color}" stroke-width="2"/>'
        f'<text x="{x + size / 2}" y="{y + size / 2 + 5.4}" text-anchor="middle" font-family="{SANS}" font-weight="700" '
        f'font-size="15" fill="{color}">{letters}</text>'
    )


def stack():
    w, tile, step, per_row = 960, 64, 88, 9
    body, y, n = [], 50, 0
    for section, items in STACK:
        body.append(
            f'<text x="44" y="{y}" font-family="{MONO}" font-weight="700" font-size="13" fill="{C["green"]}">// {t(section)}</text>'
            f'<line x1="{44 + mono_width("// " + section, 13) + 14:.1f}" y1="{y - 4.5}" x2="{w - 44}" y2="{y - 4.5}" '
            f'stroke="{C["line"]}"/>'
        )
        y += 22
        rows = [items[i:i + per_row] for i in range(0, len(items), per_row)]
        for row in rows:
            x0 = (w - (len(row) * step - (step - tile))) / 2
            for i, (label, spec, color) in enumerate(row):
                x = x0 + i * step
                inner = 32
                ix, iy = x + (tile - inner) / 2, y + (tile - inner) / 2
                glyph = custom_glyph(spec, ix, iy, inner) if spec.startswith("!") else icon(spec, ix, iy, inner, color)
                body.append(
                    f'<g class="tile" style="animation-delay:{n * 0.04:.2f}s">'
                    f'<rect x="{x:.1f}" y="{y}" width="{tile}" height="{tile}" rx="16" fill="#161f2b" stroke="{C["line"]}"/>'
                    f'{glyph}<text x="{x + tile / 2:.1f}" y="{y + tile + 19}" text-anchor="middle" font-family="{MONO}" '
                    f'font-size="11" fill="{C["muted"]}">{t(label)}</text></g>'
                )
                n += 1
            y += tile + 40
        y += 22
    h = y - 12
    body.insert(0, (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="20" fill="url(#bg)" stroke="{C["line"]}" stroke-width="1.5"/>'
    ))
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101822"/>'
        f'<stop offset="1" stop-color="#0a0f15"/></linearGradient>'
    )
    css = font_css("sg700", "jb400", "jb700") + (
        ".tile{animation:rise .6s cubic-bezier(.2,.7,.2,1) backwards}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
    )
    labels = ", ".join(label for _, items in STACK for label, _, _ in items)
    write(OUT / "stack.svg", svg_doc(w, h, f"Stack tecnológico: {labels}", "".join(body), css, defs))


def setup():
    w, h = 960, 470
    art = ARCH_LOGO.split("\n")
    art_size, art_lh, top = 12.5, 15.5, 120
    defs = (
        f'<clipPath id="win"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16"/></clipPath>'
        f'<linearGradient id="arch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["cyan"]}"/>'
        f'<stop offset="1" stop-color="#1793d1"/></linearGradient>'
    )
    art_svg = "".join(
        f'<text x="44" y="{top + i * art_lh:.1f}" xml:space="preserve">{t(line)}</text>' for i, line in enumerate(art)
    )
    ix, lh, size = 380, 27, 15
    info = [
        f'<text x="{ix}" y="{top + 4}" font-weight="700"><tspan fill="{C["green"]}">the-gekko</tspan>'
        f'<tspan fill="{C["muted"]}">@</tspan><tspan fill="{C["cyan"]}">soluciones-tech</tspan></text>',
        f'<text x="{ix}" y="{top + 4 + lh}" fill="{C["muted"]}">{"-" * 25}</text>',
    ]
    for i, (key, value) in enumerate(SETUP):
        y = top + 4 + lh * (i + 2)
        info.append(
            f'<text x="{ix}" y="{y}"><tspan fill="{C["cyan"]}" font-weight="700">{t(key)}</tspan>'
            f'<tspan fill="{C["muted"]}">: </tspan><tspan fill="{C["text"]}">{t(value)}</tspan></text>'
        )
    palette = ["#1f2a37", "#ff5f6d", C["green"], C["gold"], "#3aa0ff", C["magenta"], C["cyan"], C["text"]]
    by = top + 4 + lh * (len(SETUP) + 2) + 2
    blocks = "".join(
        f'<rect x="{ix + i * 30}" y="{by}" width="30" height="16" fill="{c}"/>' for i, c in enumerate(palette)
    )
    prompt = (
        f'<tspan fill="{C["green"]}">the-gekko@arch</tspan><tspan fill="{C["muted"]}">:</tspan>'
        f'<tspan fill="{C["cyan"]}">~</tspan><tspan fill="{C["muted"]}">$ </tspan>'
    )
    last_y = h - 32
    body = (
        f'<g clip-path="url(#win)"><rect width="{w}" height="{h}" fill="#0a0f15"/>'
        f'<rect width="{w}" height="40" fill="{C["panel"]}"/><rect y="40" width="{w}" height="1" fill="{C["line"]}"/></g>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="none" stroke="{C["line"]}" stroke-width="1.5"/>'
        f'<circle cx="26" cy="20" r="6" fill="#ff5f56"/><circle cx="46" cy="20" r="6" fill="#ffbd2e"/>'
        f'<circle cx="66" cy="20" r="6" fill="#27c93f"/>'
        f'<text x="{w / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{C["muted"]}">the-gekko@arch: ~</text>'
        f'<text x="32" y="80" font-family="{MONO}" font-size="{size}">{prompt}<tspan fill="{C["text"]}">fastfetch</tspan></text>'
        f'<g font-family="{MONO}" font-weight="700" font-size="{art_size}" fill="url(#arch)">{art_svg}</g>'
        f'<g font-family="{MONO}" font-size="{size}">{"".join(info)}</g>{blocks}'
        f'<text x="32" y="{last_y}" font-family="{MONO}" font-size="{size}">{prompt}</text>'
        f'<rect class="blink" x="{32 + mono_width("the-gekko@arch:~$ ", size):.1f}" y="{last_y - 13}" width="9" height="17" '
        f'fill="{C["cyan"]}" rx="1.5"/>'
    )
    css = font_css("jb400", "jb700") + "text{font-variant-ligatures:none}.blink{animation:blink 1.05s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    summary = "; ".join(f"{k}: {v}" for k, v in SETUP)
    write(OUT / "setup.svg", svg_doc(w, h, f"Mi setup — {summary}", body, css, defs))


def footer():
    w, h = 1200, 170
    orb_defs, orbs, orb_css = glow_orbs([
        (240, 170, 260, C["green"], 0.22),
        (960, 0, 260, C["magenta"], 0.20),
        (600, 120, 220, C["cyan"], 0.18),
    ])
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1119"/>'
        f'<stop offset="1" stop-color="{C["bg0"]}"/></linearGradient>'
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}" stop-opacity="0"/>'
        f'<stop offset=".3" stop-color="{C["green"]}"/><stop offset=".6" stop-color="{C["cyan"]}"/>'
        f'<stop offset="1" stop-color="{C["magenta"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="motto" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C["green"]}"/>'
        f'<stop offset=".5" stop-color="{C["cyan"]}"/><stop offset="1" stop-color="{C["magenta"]}"/></linearGradient>'
        + orb_defs
    )
    body = (
        f'<rect width="{w}" height="{h}" rx="22" fill="url(#bg)"/>'
        f'<g clip-path="url(#round)">{orbs}</g>'
        f'<rect x="80" y="0" width="{w - 160}" height="2" fill="url(#edge)"/>'
        f'<text x="{w / 2}" y="82" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="30" '
        f'fill="url(#motto)">{t(MOTTO)}</text>'
        f'<text x="{w / 2}" y="122" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{C["muted"]}">'
        f'The-Gekko · Soluciones Tech · hecho con Rust, café y Arch Linux</text>'
    )
    defs += f'<clipPath id="round"><rect width="{w}" height="{h}" rx="22"/></clipPath>'
    css = font_css("sg700", "jb400") + orb_css
    write(OUT / "footer.svg", svg_doc(w, h, MOTTO, body, css, defs))


def contact_button(slug, label, value):
    size, h = 15, 58
    w = round(64 + max(mono_width(value, size), mono_width(label.upper(), 10.5)) + 26)
    color = readable(icons()[slug]["hex"])
    defs = (
        f'<linearGradient id="stroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{color}"/>'
        f'<stop offset="1" stop-color="{C["line"]}"/></linearGradient>'
    )
    body = (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{(h - 1.5) / 2}" fill="{C["panel"]}" '
        f'stroke="url(#stroke)" stroke-width="1.5"/>'
        f'<circle cx="31" cy="{h / 2}" r="18" fill="{color}" fill-opacity=".14"/>'
        + icon(slug, 20, h / 2 - 11, 22, color) +
        f'<text x="62" y="24" font-family="{MONO}" font-weight="700" font-size="10.5" letter-spacing="1.4" fill="{color}">'
        f'{t(label.upper())}</text>'
        f'<text x="62" y="43" font-family="{MONO}" font-size="{size}" fill="{C["text"]}">{t(value)}</text>'
    )
    write(OUT / f"contact-{slug}.svg", svg_doc(w, h, f"{label}: {value}", body, font_css("jb400", "jb700"), defs))


def main():
    print("Generando SVG en assets/:")
    header()
    divider()
    for p in PROJECTS:
        project_card(p)
    stack()
    setup()
    footer()
    for c in CONTACT:
        contact_button(*c)


if __name__ == "__main__":
    main()
