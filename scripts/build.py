#!/usr/bin/env python3
import argparse
import json
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent

SANS = '-apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif'
MONO = 'ui-monospace, SFMono-Regular, Menlo, monospace'

SHIELDS_STATIC = "https://img.shields.io/static/v1?label=&message={text}&color={color}&style=for-the-badge"
SHIELDS_STARS = "https://img.shields.io/github/stars/{repo}?style=for-the-badge"

STATUS_BADGES = {
    "coming-soon": {"url": SHIELDS_STATIC, "text": "即将上架 · Coming soon", "color": "6e7781", "linked": False},
    "in-development": {"url": SHIELDS_STATIC, "text": "开发中 · In development", "color": "6e7781", "linked": False},
    "private": {"url": SHIELDS_STATIC, "text": "私有项目 · Private", "color": "6e7781", "linked": False},
    "open-source": {"url": SHIELDS_STARS, "text": "", "color": "", "linked": True},
    "live": {"url": SHIELDS_STATIC, "text": "立即使用 · Try it", "color": "2da44e", "linked": True},
}

THEME_CSS = """
.bg{fill:#f6f8fa}
.border{stroke:#d0d7de}
.fg{fill:#1f2328}
.muted{fill:#656d76}
.rule{fill:#d0d7de}
@media (prefers-color-scheme: dark){
.bg{fill:#161b22}
.border{stroke:#30363d}
.fg{fill:#e6edf3}
.muted{fill:#8b949e}
.rule{fill:#30363d}
}
"""

REDUCED_MOTION_CSS = """
@media (prefers-reduced-motion: reduce){
*{animation:none !important}
.sweep{display:none}
}
"""


def esc(text):
    return escape(text, quote=True)


def text_width(text, size):
    # CJK glyphs are about one em wide; Latin averages closer to 0.6 em.
    return sum(size if ord(ch) > 0x2E80 else size * 0.6 for ch in text)


def fit(text, size, limit, where):
    width = text_width(text, size)
    if width > limit:
        raise SystemExit(f"text too wide in {where}: {text!r} needs {width:.0f}px, limit {limit}px")
    return esc(text)


def svg(width, height, body, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">\n'
        f"<style>\ntext{{font-family:{SANS}}}\n.mono{{font-family:{MONO}}}\n"
        f"{THEME_CSS}{extra_css}{REDUCED_MOTION_CSS}</style>\n"
        f"{body}</svg>\n"
    )


def build_header(profile, projects):
    name = fit(profile["name_en"], 64, 800, "header name")
    zh = fit(profile["tagline_zh"], 26, 800, "header tagline_zh")
    en = fit(profile["tagline_en"], 18, 800, "header tagline_en")
    bar = "".join(
        f'<rect x="{48 + i * 80}" y="116" width="80" height="4" fill="{p["accent"]}"/>'
        for i, p in enumerate(projects)
    )
    css = """
.in{animation:rise 1.6s ease-out both}
.d1{animation-delay:.2s}
.d2{animation-delay:.7s}
.d3{animation-delay:1.1s}
.bar{animation:grow 2.2s ease-out .4s both;transform-origin:48px 118px}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
"""
    body = (
        '<rect class="bg border" x="0.5" y="0.5" width="899" height="239" rx="12"/>\n'
        f'<text class="fg in d1" x="48" y="96" font-size="64" font-weight="700">{name}</text>\n'
        f'<g class="bar">{bar}</g>\n'
        f'<text class="fg in d2" x="48" y="166" font-size="26" font-weight="600">{zh}</text>\n'
        f'<text class="muted in d3" x="48" y="200" font-size="18">{en}</text>\n'
    )
    return svg(900, 240, body, css)


def build_card(project):
    where = f"card {project['id']}"
    index = esc(project["index"])
    title = fit(project["title"], 30, 680, where + " title")
    subtitle = fit(project["subtitle"], 15, 680, where + " subtitle")
    liner = fit(project["one_liner_zh"], 20, 680, where + " one_liner_zh")
    accent = project["accent"]
    css = f"""
.sweep{{animation:sweep 8s ease-in-out infinite}}
@keyframes sweep{{0%{{transform:translateX(-300px)}}65%,100%{{transform:translateX(1000px)}}}}
"""
    body = (
        "<defs>\n"
        f'<linearGradient id="glow-{esc(project["id"])}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{accent}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{accent}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>\n'
        f'<clipPath id="clip-{esc(project["id"])}"><rect x="0" y="0" width="900" height="160" rx="12"/></clipPath>\n'
        "</defs>\n"
        '<rect class="bg border" x="0.5" y="0.5" width="899" height="159" rx="12"/>\n'
        f'<g clip-path="url(#clip-{esc(project["id"])})">'
        f'<g class="sweep"><rect x="0" y="0" width="240" height="160" fill="url(#glow-{esc(project["id"])})"/>'
        f'<rect x="60" y="157" width="120" height="3" fill="{accent}"/></g></g>\n'
        f'<text class="mono" x="40" y="104" font-size="72" font-weight="700" fill="{accent}">{index}</text>\n'
        '<rect class="rule" x="160" y="32" width="1" height="96"/>\n'
        f'<text class="fg" x="192" y="68" font-size="30" font-weight="700">{title}</text>\n'
        f'<text class="muted mono" x="192" y="94" font-size="15">{subtitle}</text>\n'
        f'<text class="fg" x="192" y="132" font-size="20">{liner}</text>\n'
    )
    return svg(900, 160, body, css)


def build_divider():
    css = """
.dot{animation:pulse 4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}
"""
    body = (
        '<rect class="rule" x="0" y="23" width="900" height="1"/>\n'
        '<circle class="dot muted" cx="450" cy="23.5" r="3.5"/>\n'
    )
    return svg(900, 48, body, css)


def build_footer(profile):
    thanks = fit("感谢阅读 · Thanks for stopping by", 22, 800, "footer thanks")
    contact = fit(f"Email  {profile['email']}    WeChat  {profile['wechat']}", 16, 800, "footer contact")
    css = """
.in{animation:rise 1.6s ease-out both}
.d2{animation-delay:.5s}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
"""
    body = (
        '<rect class="bg border" x="0.5" y="0.5" width="899" height="119" rx="12"/>\n'
        f'<text class="fg in" x="450" y="52" font-size="22" font-weight="600" text-anchor="middle">{thanks}</text>\n'
        f'<text class="muted mono in d2" x="450" y="86" font-size="16" text-anchor="middle" xml:space="preserve">{contact}</text>\n'
    )
    return svg(900, 120, body, css)


def badge_markdown(project):
    entry = STATUS_BADGES[project["status"]]
    link = project["link"]
    repo = urlparse(link).path.strip("/") if link else ""
    cta = " · ".join(t for t in (project.get("cta_zh"), project.get("cta_en")) if t)
    text = cta or entry["text"]
    url = entry["url"].format(text=quote(text, safe=""), color=entry["color"], repo=repo)
    image = f"![{text or project['status']}]({url})"
    if entry["linked"]:
        return f"[{image}]({link})"
    return image


def build_readme(data):
    profile = data["profile"]
    projects = data["projects"]
    followers = "https://img.shields.io/github/followers/xianengqi?style=for-the-badge&label=Followers"
    count = f"https://img.shields.io/static/v1?label=Projects&message={len(projects)}&color=6e7781&style=for-the-badge"
    out = [
        f'<img src="assets/header.svg" width="100%" alt="{esc(profile["name_en"])}">',
        "",
        f'**{profile["intro_zh"]}**<br>',
        f'**{profile["intro_en"]}**',
        "",
        f"![Followers]({followers}) ![Projects]({count})",
        "",
    ]
    for p in projects:
        card = f'<img src="assets/card-{p["id"]}.svg" width="100%" alt="{esc(p["index"] + " " + p["title"])}">'
        heading = p["title"]
        if STATUS_BADGES[p["status"]]["linked"]:
            card = f'<a href="{esc(p["link"])}">{card}</a>'
            heading = f'[{heading}]({p["link"]})'
        out += [
            '<img src="assets/divider.svg" width="100%" alt="">',
            "",
            f'## {heading}',
            "",
            card,
            "",
            f'<b>{p["one_liner_zh"]}</b>{p["detail_zh"]}<br>',
            f'<b>{p["one_liner_en"]}</b> {p["detail_en"]}',
            "",
            badge_markdown(p),
            "",
        ]
    out += [
        '<img src="assets/divider.svg" width="100%" alt="">',
        "",
        f'<img src="assets/footer.svg" width="100%" alt="{esc(profile["email"])}">',
        "",
    ]
    return "\n".join(out)


def generate():
    data = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
    files = {
        "assets/header.svg": build_header(data["profile"], data["projects"]),
        "assets/divider.svg": build_divider(),
        "assets/footer.svg": build_footer(data["profile"]),
        "README.md": build_readme(data),
    }
    for p in data["projects"]:
        files[f"assets/card-{p['id']}.svg"] = build_card(p)
    return files


def main():
    parser = argparse.ArgumentParser(description="Generate README.md and assets/*.svg from projects.json")
    parser.add_argument("--check", action="store_true", help="compare generated output with disk, write nothing")
    args = parser.parse_args()

    files = generate()

    if args.check:
        stale = []
        for rel, content in files.items():
            path = ROOT / rel
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(rel)
        for path in sorted((ROOT / "assets").glob("*.svg")):
            rel = path.relative_to(ROOT).as_posix()
            if rel not in files:
                stale.append(rel + " (not generated)")
        if stale:
            print("out of date:", file=sys.stderr)
            for rel in stale:
                print(f"  {rel}", file=sys.stderr)
            return 1
        print("up to date")
        return 0

    (ROOT / "assets").mkdir(exist_ok=True)
    for rel, content in files.items():
        (ROOT / rel).write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
