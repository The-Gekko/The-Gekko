#!/usr/bin/env python3
"""Genera las tarjetas de estadísticas del perfil con la API GraphQL de GitHub.

Lo ejecuta la Action .github/workflows/profile.yml una vez al día y publica el
resultado en la rama `output`. Así el perfil no depende de servicios externos
que se caen o se quedan sin cuota.

Uso local:
    GITHUB_TOKEN=... python3 scripts/github_stats.py --user The-Gekko --out dist
    python3 scripts/github_stats.py --mock datos.json --out dist   # sin red
"""

import argparse
import datetime as dt
import json
import math
import os
import pathlib
import sys
import urllib.request

from svgkit import C, MONO, SANS, font_css, svg_doc, t, write

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""

# Lenguajes que inflan el gráfico sin decir nada del trabajo.
IGNORED_LANGUAGES = {"Makefile", "Dockerfile", "Roff", "M4", "Meson"}


def fetch(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "the-gekko-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        sys.exit(f"GraphQL respondió con errores: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days, today):
    """Racha actual y la más larga dentro del calendario (último año)."""
    days = sorted((d for d in days if d["date"] <= today.isoformat()), key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i > 0:  # hoy sin contribuciones todavía no rompe la racha
            break
    return current, longest


def summarize(user, today):
    repos = user["repositories"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days, today)

    langs = {}
    for repo in repos["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in IGNORED_LANGUAGES:
                continue
            entry = langs.setdefault(name, {"size": 0, "color": edge["node"]["color"] or C["muted"]})
            entry["size"] += edge["size"]

    return {
        "contributions": calendar["totalContributions"],
        "commits": user["contributionsCollection"]["totalCommitContributions"],
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos["nodes"]),
        "repos": repos["totalCount"],
        "followers": user["followers"]["totalCount"],
        "streak": current,
        "longest": longest,
        "languages": sorted(langs.items(), key=lambda kv: kv[1]["size"], reverse=True),
    }


def card_frame(w, h, accent, title, subtitle):
    defs = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101822"/>'
        f'<stop offset="1" stop-color="#0a0f15"/></linearGradient>'
        f'<linearGradient id="stroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity=".9"/>'
        f'<stop offset=".5" stop-color="{C["line"]}"/><stop offset="1" stop-color="{accent}" stop-opacity=".35"/></linearGradient>'
    )
    body = (
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="20" fill="url(#bg)" stroke="url(#stroke)" stroke-width="1.5"/>'
        f'<text x="30" y="48" font-family="{SANS}" font-weight="700" font-size="22" fill="{C["text"]}">{t(title)}</text>'
        f'<text x="30" y="70" font-family="{MONO}" font-size="11.5" fill="{C["muted"]}">{t(subtitle)}</text>'
    )
    return defs, body


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 10000 else f"{n:,}".replace(",", ".")


def stats_card(s, today):
    w, h = 500, 290
    defs, body = card_frame(w, h, C["cyan"], "GitHub en números", f"// actualizado el {today:%d/%m/%Y}")
    metrics = [
        ("Contribuciones (año)", s["contributions"], C["green"]),
        ("Commits (año)", s["commits"], C["cyan"]),
        ("Pull requests", s["prs"], C["magenta"]),
        ("Issues", s["issues"], C["gold"]),
        ("Estrellas", s["stars"], C["gold"]),
        ("Repos públicos", s["repos"], C["green"]),
    ]
    rows = []
    for i, (label, value, color) in enumerate(metrics):
        y = 112 + i * 29
        rows.append(
            f'<g class="row" style="animation-delay:{i * 0.08:.2f}s">'
            f'<rect x="30" y="{y - 11}" width="8" height="8" rx="2" fill="{color}"/>'
            f'<text x="48" y="{y - 3}" font-family="{SANS}" font-weight="500" font-size="14.5" fill="{C["soft"]}">{t(label)}</text>'
            f'<text x="290" y="{y - 3}" text-anchor="end" font-family="{MONO}" font-weight="700" font-size="15" '
            f'fill="{C["text"]}">{fmt(value)}</text></g>'
        )
    # Anillo de racha
    cx, cy, r = 392, 158, 58
    circ = 2 * math.pi * r
    ratio = min(1.0, s["streak"] / max(s["longest"], 1)) if s["streak"] else 0
    defs += (
        f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["green"]}"/>'
        f'<stop offset="1" stop-color="{C["cyan"]}"/></linearGradient>'
    )
    ring = (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["line"]}" stroke-width="9"/>'
        f'<circle class="ring" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ring)" stroke-width="9" '
        f'stroke-linecap="round" stroke-dasharray="{circ * ratio:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="34" '
        f'fill="{C["text"]}">{s["streak"]}</text>'
        f'<text x="{cx}" y="{cy + 28}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{C["muted"]}">'
        f'{"día" if s["streak"] == 1 else "días"}</text>'
        f'<text x="{cx}" y="{cy + r + 32}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="11" '
        f'letter-spacing="1.2" fill="{C["green"]}">RACHA ACTUAL</text>'
        f'<text x="{cx}" y="{cy + r + 50}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{C["muted"]}">'
        f'mejor: {s["longest"]} {"día" if s["longest"] == 1 else "días"}</text>'
    )
    css = font_css("sg500", "sg700", "jb400", "jb700") + (
        ".row{animation:in .5s ease-out backwards}@keyframes in{from{opacity:0;transform:translateX(-6px)}}"
        f".ring{{animation:fill 1.4s cubic-bezier(.3,.7,.2,1) backwards}}@keyframes fill{{from{{stroke-dasharray:0 {circ:.1f}}}}}"
    )
    summary = ", ".join(f"{label}: {value}" for label, value, _ in metrics)
    return svg_doc(w, h, f"Estadísticas de GitHub — {summary}, racha actual: {s['streak']} días", body + "".join(rows) + ring, css, defs)


def languages_card(s, today, top=8):
    w, h = 500, 290
    defs, body = card_frame(w, h, C["magenta"], "Lenguajes", "// por tamaño de código en repos públicos")
    langs = s["languages"]
    total = sum(v["size"] for _, v in langs) or 1
    shown = langs[:top]
    if len(langs) > top:
        shown = langs[:top - 1] + [("Otros", {"size": sum(v["size"] for _, v in langs[top - 1:]), "color": C["muted"]})]

    bar_x, bar_y, bar_w, bar_h = 30, 94, w - 60, 12
    defs += f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6"/></clipPath>'
    segs, x = [], bar_x
    for name, v in shown:
        seg_w = bar_w * v["size"] / total
        segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{seg_w + 0.5:.2f}" height="{bar_h}" fill="{v["color"]}"/>')
        x += seg_w
    bar = f'<g class="bar" clip-path="url(#bar)"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="{C["line"]}"/>{"".join(segs)}</g>'

    legend = []
    for i, (name, v) in enumerate(shown):
        col, row = i % 2, i // 2
        lx, ly = 30 + col * 225, 144 + row * 34
        pct = 100 * v["size"] / total
        legend.append(
            f'<g class="row" style="animation-delay:{i * 0.06:.2f}s">'
            f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{v["color"]}"/>'
            f'<text x="{lx + 20}" y="{ly}" font-family="{SANS}" font-weight="500" font-size="14.5" fill="{C["soft"]}">{t(name)}</text>'
            f'<text x="{lx + 200}" y="{ly}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{C["muted"]}">{pct:.1f}%</text></g>'
        )
    if not langs:
        legend.append(f'<text x="30" y="150" font-family="{MONO}" font-size="13" fill="{C["muted"]}">Sin datos todavía.</text>')
    css = font_css("sg500", "sg700", "jb400") + (
        ".row{animation:in .5s ease-out backwards}@keyframes in{from{opacity:0;transform:translateX(-6px)}}"
        ".bar{transform-box:fill-box;transform-origin:left;animation:grow 1.2s cubic-bezier(.3,.7,.2,1) backwards}"
        "@keyframes grow{from{transform:scaleX(0)}}"
    )
    summary = ", ".join(f"{n} {100 * v['size'] / total:.1f}%" for n, v in shown)
    return svg_doc(w, h, f"Lenguajes más usados — {summary}", body + bar + "".join(legend), css, defs)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "The-Gekko"))
    ap.add_argument("--out", default="dist")
    ap.add_argument("--mock", help="JSON con la respuesta de `user` para probar sin red")
    args = ap.parse_args()

    if args.mock:
        user = json.loads(pathlib.Path(args.mock).read_text())
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Falta GITHUB_TOKEN")
        user = fetch(args.user, token)
    if user is None:
        sys.exit(f"No existe el usuario {args.user}")

    today = dt.datetime.now(dt.timezone.utc).date()
    s = summarize(user, today)
    out = pathlib.Path(args.out)
    print(f"Estadísticas de {args.user}:")
    write(out / "stats.svg", stats_card(s, today))
    write(out / "languages.svg", languages_card(s, today))


if __name__ == "__main__":
    main()
