#!/usr/bin/env python3
"""Gera todos os SVGs animados do perfil (tema Claude).

Edite os textos nas seções marcadas com "CONTEÚDO" e rode:
    python3 scripts/gerar_assets.py
"""
import html
import math
import re
import random
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
LOGOS = Path(__file__).resolve().parent / "logos"  # ícones oficiais (Simple Icons, CC0)
OUT.mkdir(exist_ok=True)
random.seed(11)

# ---------------------------------------------------------------- paleta
BG = "#141413"        # fundo
PANEL = "#1f1e1b"     # cartões
PANEL2 = "#2a2824"    # barras de título
BORDER = "#3d3a35"
CREAM = "#f0eee6"
MUTED = "#a39e93"
DIM = "#6b665d"
OR = "#d97757"        # laranja Claude
OR_D = "#c15f3c"
KRAFT = "#d4a27f"
MANILLA = "#ebdbbc"
GREEN = "#8cc084"

MONO = "font-family=\"'JetBrains Mono','Fira Code',SFMono-Regular,Menlo,Consolas,monospace\""
SERIF = "font-family=\"'Tiempos Headline','Copernicus',Georgia,'Times New Roman',serif\""
esc = html.escape


def save(name, body):
    (OUT / name).write_text(body, encoding="utf-8")


def svg(w, h, inner, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><defs>{defs}</defs>{inner}</svg>')


def border_gradient(gid, dur=8):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{OR}"/><stop offset=".5" stop-color="{MANILLA}"/>'
            f'<stop offset="1" stop-color="{OR_D}"/>'
            f'<animateTransform attributeName="gradientTransform" type="rotate" '
            f'from="0 .5 .5" to="360 .5 .5" dur="{dur}s" repeatCount="indefinite"/></linearGradient>')


GLOW = ('<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge></filter>')


def logo_path(name):
    """Caminho (atributo d) de um logo oficial em scripts/logos/<name>.svg (viewBox 24x24)."""
    return re.search(r'<path d="([^"]+)"', (LOGOS / f"{name}.svg").read_text()).group(1)


def spark(cx, cy, scale=1.0, dur=24, width=None):
    """Logo oficial da Claude girando devagar e 'respirando'."""
    k = scale * 5.6
    return (f'<g transform="translate({cx},{cy})"><g>'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{dur}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="1;1.09;1" dur="2.6s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>'
            f'<path transform="scale({k:.3f}) translate(-12,-12)" fill="{OR}" d="{logo_path("claude")}"/>'
            f'</g></g></g>')


def clawd(u, walk=False, wave=True):
    """Mascote em pixel art (14u x 8u)."""
    def r(x, y, w, h, c=OR):
        return f'<rect x="{x*u:.1f}" y="{y*u:.1f}" width="{w*u:.1f}" height="{h*u:.1f}" fill="{c}"/>'
    g = r(2, 0, 10, 6)
    arm = r(0, 2, 2, 2)
    if wave:
        arm = (f'<g>{arm}<animateTransform attributeName="transform" type="rotate" '
               f'values="0 {2*u} {3*u};-16 {2*u} {3*u};0 {2*u} {3*u}" dur="1.6s" repeatCount="indefinite"/></g>')
    g += arm + r(12, 2, 2, 2)
    blink = (lambda attr, a, b: f'<animate attributeName="{attr}" values="{a};{a};{b};{a};{a}" '
             f'keyTimes="0;.92;.95;.98;1" dur="4s" repeatCount="indefinite"/>')
    for ex in (4, 9):
        g += (f'<rect x="{ex*u}" y="{2*u}" width="{u}" height="{2*u}" fill="{BG}">'
              f'{blink("height", 2*u, .3*u)}{blink("y", 2*u, 2.85*u)}</rect>')
    for i, lx in enumerate((3, 5, 8, 10)):
        leg = r(lx, 6, 1, 2)
        if walk:
            leg = (f'<g>{leg}<animateTransform attributeName="transform" type="translate" '
                   f'values="0 0;0 -{.9*u};0 0" dur=".5s" begin="{(i % 2)*.25}s" repeatCount="indefinite"/></g>')
        g += leg
    return g


def bob(inner, amp=8, dur=.9):
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -{amp};0 0" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" '
            f'keySplines=".4 0 .6 1;.4 0 .6 1"/>{inner}</g>')


def reveal(start, length=.5):
    """Aparece uma vez (fica visível mesmo onde não há animação)."""
    dur = start + length
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{start/dur:.4f};1" '
            f'dur="{dur:.2f}s" fill="freeze"/>')


def window_chrome(w, title, gid="bd"):
    return (f'<rect x="10" y="10" width="{w-20}" height="48" rx="18" fill="{PANEL2}"/>'
            f'<rect x="10" y="38" width="{w-20}" height="20" fill="{PANEL2}"/>'
            f'<circle cx="40" cy="34" r="7" fill="#ff5f56"/><circle cx="64" cy="34" r="7" fill="#ffbd2e"/>'
            f'<circle cx="88" cy="34" r="7" fill="#27c93f"/>'
            f'<text x="{w/2}" y="40" text-anchor="middle" {MONO} font-size="14" fill="{MUTED}">{esc(title)}</text>')


def frame(w, h, gid="bd"):
    return f'<rect x="10" y="10" width="{w-20}" height="{h-20}" rx="18" fill="{BG}" stroke="url(#{gid})" stroke-width="2.5"/>'


def stars(w, h, n, y0=60):
    return "".join(
        f'<circle cx="{random.randint(30, w-30)}" cy="{random.randint(y0, h-30)}" r="{random.choice([1, 1.5, 2])}" '
        f'fill="{OR}" opacity="0"><animate attributeName="opacity" values="0;.5;0" '
        f'dur="{random.uniform(2.5, 5):.1f}s" begin="{-random.uniform(0, 5):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(n))


# ======================================================= 1. terminal (hero)
# CONTEÚDO
HERO_NAME = "Gabriel Niza"
HERO_SUB = "desenvolvedor web · front-end · vibe coding com Claude"
PERGUNTA = "> me conta sobre o Gabriel"
RESPOSTAS = [
    ("●", "Desenvolvedor web apaixonado por front-end"),
    ("●", "Cria sites e cardápios online para negócios locais"),
    ("●", "Pedidos pelo WhatsApp, mobile-first e visual caprichado"),
    ("●", "Programa em parceria com o Claude Code"),
]
STATUS = "✔ Disponível para novos projetos"


def hero():
    W, H, T = 1200, 580, 18.0
    CW = 10.3  # largura de um caractere (17px mono)
    y0, dy = 350, 32
    o = frame(W, H) + stars(W, H, 30) + window_chrome(W, "gniza — claude — ~/github/gniza")

    # caixa de boas-vindas
    o += f'<rect x="40" y="82" width="{W-80}" height="216" rx="14" fill="{PANEL}" stroke="{OR}" stroke-opacity=".75" stroke-width="1.5"/>'
    o += f'<text x="72" y="122" {MONO} font-size="16" fill="{OR}">✻ Bem-vindo ao Claude Code</text>'
    o += (f'<text x="70" y="198" {SERIF} font-size="70" fill="{CREAM}" letter-spacing="-1">{esc(HERO_NAME)}'
          f'{reveal(.2, .8)}</text>')
    o += f'<text x="72" y="240" {MONO} font-size="17" fill="{MUTED}">{esc(HERO_SUB)}</text>'
    o += f'<text x="72" y="274" {MONO} font-size="14" fill="{DIM}">/help para ajuda · /status para ver a configuração</text>'
    o += f'<g filter="url(#glow)">{spark(1062, 168, .72)}</g>'
    o += (f'<g transform="translate(860,170)">{bob(clawd(9), 8)}'
          f'<ellipse cx="63" cy="84" rx="52" ry="5" fill="#000" opacity=".35">'
          f'<animate attributeName="rx" values="52;42;52" dur=".9s" repeatCount="indefinite"/></ellipse></g>')

    # pergunta digitada
    n = len(PERGUNTA)
    w = n * CW + 6
    s, d = .6, 1.6
    times, vals = [0], [0]
    for k in range(1, n + 1):
        times.append(s + (k - 1) * d / n)
        vals.append(round(w * k / n, 1))
    times += [16.6, T]
    vals += [0, 0]
    kt = ";".join(f"{t/T:.4f}" for t in times[:-1]) + ";1"
    o += (f'<clipPath id="q"><rect x="50" y="{y0-22}" height="30" width="{w:.0f}">'
          f'<animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
          f'keyTimes="{kt}" values="{";".join(map(str, vals))}"/></rect></clipPath>')
    o += (f'<text x="50" y="{y0}" {MONO} font-size="17" fill="{CREAM}" clip-path="url(#q)">'
          f'<tspan fill="{DIM}">&gt;</tspan>{esc(PERGUNTA[1:])}</text>')

    def window(a, b, base=1):
        k = f"0;{a/T:.4f};{(a+.3)/T:.4f};{b/T:.4f};{(b+.3)/T:.4f};1"
        return (f'opacity="{base}"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" '
                f'keyTimes="{k}" values="0;0;1;1;0;0"/>')

    # spinner "pensando"
    ys = y0 + dy
    glyphs = "·✢✳✶✻✽"
    spin = ""
    for k, gch in enumerate(glyphs):
        a, b = k / 6, (k + 1) / 6
        if k == 0:
            anim = f'values="1;0;0" keyTimes="0;{b:.4f};1"'
        else:
            anim = f'values="0;1;0;0" keyTimes="0;{a:.4f};{b:.4f};1"'
        spin += (f'<text x="50" y="{ys}" {MONO} font-size="17" fill="{OR}" opacity="0">{gch}'
                 f'<animate attributeName="opacity" calcMode="discrete" dur=".9s" repeatCount="indefinite" {anim}/></text>')
    o += (f'<linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" x2="160" y1="0" y2="0">'
          f'<stop offset="0" stop-color="{OR}"/><stop offset=".5" stop-color="{MANILLA}"/><stop offset="1" stop-color="{OR}"/>'
          f'<animateTransform attributeName="gradientTransform" type="translate" from="-80 0" to="200 0" dur="1.2s" repeatCount="indefinite"/></linearGradient>')
    o += (f'<g {window(2.4, 3.9, 0)}{spin}'
          f'<text x="72" y="{ys}" {MONO} font-size="17" fill="url(#sh)">Pensando…</text></g>')

    # respostas
    t = 4.2
    for i, (b, txt) in enumerate(RESPOSTAS):
        y = ys + i * dy
        o += (f'<g {window(t, 16.4)}<text x="50" y="{y}" {MONO} font-size="17" fill="{CREAM}">'
              f'<tspan fill="{OR}">{b}</tspan> {esc(txt)}</text></g>')
        t += .7
    y = ys + len(RESPOSTAS) * dy
    o += (f'<g {window(t + .3, 16.4)}<text x="50" y="{y}" {MONO} font-size="17" fill="{GREEN}">'
          f'{esc(STATUS)}</text></g>')
    # prompt final
    y += dy + 6
    o += (f'<g {window(t + 1, 16.4)}<text x="50" y="{y}" {MONO} font-size="17" fill="{OR}">&gt;</text>'
          f'<rect x="68" y="{y-15}" width="10" height="20" fill="{OR}">'
          f'<animate attributeName="opacity" dur="1s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;.5;.5;1"/></rect></g>')
    save("hero.svg", svg(W, H, o, border_gradient("bd") + GLOW))


# ======================================================= 2. títulos de seção
TITULOS = {
    "sobre": "Sobre mim",
    "stack": "Ferramentas",
    "projetos": "Projetos em destaque",
    "contrib": "Contribuições",
    "contato": "Vamos conversar?",
}


def titles():
    for key, txt in TITULOS.items():
        W, H = 900, 70
        o = spark(30, 36, .32, 14, 10)
        o += f'<text x="70" y="47" {SERIF} font-size="34" fill="{OR}">{esc(txt)}</text>'
        x0 = 70 + len(txt) * 17 + 24
        o += (f'<line x1="{x0}" y1="38" x2="{x0}" y2="38" stroke="url(#ln)" stroke-width="2" stroke-linecap="round">'
              f'<animate attributeName="x2" values="{x0};{W-10};{W-10}" keyTimes="0;.4;1" dur="4s" repeatCount="indefinite"/></line>')
        defs = (f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{OR}"/>'
                f'<stop offset="1" stop-color="{OR}" stop-opacity="0"/></linearGradient>')
        save(f"titulo-{key}.svg", svg(W, H, o, defs))


# ======================================================= 3. CLAUDE.md
# CONTEÚDO  (tipo, texto)  tipos: h1, h2, quote, li, blank
CLAUDE_MD = [
    ("h1", "# Gabriel Niza"),
    ("blank", ""),
    ("quote", "> Desenvolvedor web que transforma ideias em sites rápidos e bonitos."),
    ("blank", ""),
    ("h2", "## Sobre"),
    ("li", "Foco em front-end e experiência mobile"),
    ("li", "Crio sites e cardápios online para negócios locais"),
    ("li", "Aprendendo: Next.js, Supabase e animações em SVG"),
    ("blank", ""),
    ("h2", "## Regras do projeto"),
    ("li", "Sempre mobile-first"),
    ("li", "Pedido direto pelo WhatsApp"),
    ("li", "Carregar rápido e ficar bonito"),
    ("li", "Na dúvida, perguntar pro Claude ✻"),
]


def claude_md():
    W = 1200
    lh, top = 28, 112
    H = top + len(CLAUDE_MD) * lh + 40
    o = frame(W, H) + window_chrome(W, "~/github/gniza")
    # abas
    o += f'<rect x="10" y="58" width="{W-20}" height="36" fill="{PANEL}"/>'
    o += f'<rect x="10" y="58" width="170" height="36" fill="{BG}"/><rect x="10" y="58" width="170" height="2" fill="{OR}"/>'
    o += f'<text x="34" y="81" {MONO} font-size="14" fill="{CREAM}"><tspan fill="{OR}">✻</tspan> CLAUDE.md</text>'
    o += f'<text x="208" y="81" {MONO} font-size="14" fill="{DIM}">README.md</text>'
    o += f'<text x="340" y="81" {MONO} font-size="14" fill="{DIM}">index.html</text>'
    o += f'<line x1="78" y1="100" x2="78" y2="{H-24}" stroke="{BORDER}"/>'
    for i, (kind, txt) in enumerate(CLAUDE_MD):
        y = top + i * lh + 12
        o += f'<text x="58" y="{y}" text-anchor="end" {MONO} font-size="15" fill="{DIM}">{i+1}</text>'
        if kind == "blank":
            continue
        if kind == "h1":
            line = f'<tspan fill="{DIM}">#</tspan><tspan fill="{OR}" font-weight="700">{esc(txt[1:])}</tspan>'
        elif kind == "h2":
            line = f'<tspan fill="{DIM}">##</tspan><tspan fill="{KRAFT}" font-weight="700">{esc(txt[2:])}</tspan>'
        elif kind == "quote":
            line = f'<tspan fill="{DIM}">&gt;</tspan><tspan fill="{MUTED}" font-style="italic">{esc(txt[1:])}</tspan>'
        else:
            line = f'<tspan fill="{OR}">-</tspan> <tspan fill="{CREAM}">{esc(txt)}</tspan>'
        o += f'<text x="98" y="{y}" {MONO} font-size="18">{line}{reveal(.3 + i * .18, .35)}</text>'
    # cursor no fim
    last = top + (len(CLAUDE_MD) - 1) * lh + 12
    cx = 98 + (len(CLAUDE_MD[-1][1]) + 2) * 10.85
    o += (f'<rect x="{cx:.0f}" y="{last-16}" width="3" height="21" fill="{OR}" opacity="0">'
          f'<animate attributeName="opacity" begin="{.3 + len(CLAUDE_MD)*.18:.1f}s" dur="1s" repeatCount="indefinite" '
          f'values="1;1;0;0" keyTimes="0;.5;.5;1"/></rect>')
    # mascote espiando no canto
    o += f'<g transform="translate({W-190},{H-118})">{bob(clawd(9), 5, 1.4)}</g>'
    save("claude-md.svg", svg(W, H, o, border_gradient("bd", 10)))


# ======================================================= 4. ferramentas
# CONTEÚDO
STACK = [
    ("HTML5", "#e34f26"), ("CSS3", "#2965f1"), ("JavaScript", "#f7df1e"),
    ("TypeScript", "#3178c6"), ("React", "#61dafb"), ("Next.js", "#f0eee6"),
    ("Tailwind", "#38bdf8"), ("Supabase", "#3ecf8e"), ("Vercel", "#f0eee6"),
    ("Git", "#f05032"), ("Figma", "#a259ff"),
]
# ferramenta principal (card em destaque)
PRINCIPAL = "Claude Code"
PRINCIPAL_SUB = "meu parceiro de programação no terminal"
PRINCIPAL_CMD = '> claude "cria o site e deixa bonito"'
# ferramentas secundárias (nome, cor da borda, logo em scripts/logos/)
SECUNDARIAS = [
    ("Gemini", "#8e7cf0", "googlegemini"),
    ("ChatGPT", "#10a37f", "openai"),
]


def stack():
    W, cols, cw, ch, gx, gy = 1200, 6, 168, 64, 20, 22
    fx, fy, fw, fh = 45, 84, W - 90, 244
    o = window_chrome(W, "/stack")

    # ---------- card principal ----------
    o += (f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="none" stroke="{OR}" stroke-width="10" '
          f'filter="url(#soft)" opacity=".35"><animate attributeName="opacity" values=".15;.5;.15" dur="3s" repeatCount="indefinite"/></rect>')
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="{PANEL}"/>'
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="url(#rg)"/>'
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="none" stroke="url(#bd2)" stroke-width="2.5"/>'
    o += f'<g filter="url(#glow)">{spark(fx + 112, fy + fh / 2, 1.05, 18)}</g>'
    tx = fx + 222
    o += (f'<rect x="{tx}" y="{fy + 24}" width="232" height="28" rx="14" fill="{OR}" fill-opacity=".15" stroke="{OR}" stroke-opacity=".7"/>'
          f'<text x="{tx + 116}" y="{fy + 43}" text-anchor="middle" {MONO} font-size="13" font-weight="700" fill="{OR}" letter-spacing="1.5">'
          f'★ FERRAMENTA PRINCIPAL<animate attributeName="opacity" values="1;.55;1" dur="2s" repeatCount="indefinite"/></text>')
    o += f'<text x="{tx - 2}" y="{fy + 104}" {SERIF} font-size="58" fill="{CREAM}" letter-spacing="-1">{esc(PRINCIPAL)}</text>'
    o += f'<text x="{tx}" y="{fy + 138}" {MONO} font-size="17" fill="{MUTED}">{esc(PRINCIPAL_SUB)}</text>'
    # comando digitado em loop
    T, n = 8.0, len(PRINCIPAL_CMD)
    w = n * 9.7 + 6
    times, vals = [0], [0]
    for k in range(1, n + 1):
        times.append(.4 + (k - 1) * 2.2 / n)
        vals.append(round(w * k / n, 1))
    times += [7.4, T]
    vals += [0, 0]
    kt = ";".join(f"{t/T:.4f}" for t in times[:-1]) + ";1"
    cy = fy + 180
    o += (f'<clipPath id="cmd"><rect x="{tx}" y="{cy - 20}" height="28" width="{w:.0f}">'
          f'<animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
          f'keyTimes="{kt}" values="{";".join(map(str, vals))}"/></rect></clipPath>')
    o += (f'<text x="{tx}" y="{cy}" {MONO} font-size="16" fill="{CREAM}" clip-path="url(#cmd)" xml:space="preserve">'
          f'<tspan fill="{OR}">&gt;</tspan>{esc(PRINCIPAL_CMD[1:])}</text>')
    o += (f'<text x="{tx + w + 14:.0f}" y="{cy}" {MONO} font-size="16" fill="{GREEN}">✔ feito'
          f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;{3/T:.3f};{3.2/T:.3f};{7.3/T:.3f};{7.4/T:.3f};1" values="0;0;1;1;0;0"/></text>')
    # medidor de uso
    my = fy + 206
    o += f'<text x="{tx}" y="{my + 11}" {MONO} font-size="13" fill="{DIM}">uso diário</text>'
    o += f'<rect x="{tx + 100}" y="{my}" width="300" height="12" rx="6" fill="{BG}" stroke="{BORDER}"/>'
    o += (f'<rect x="{tx + 100}" y="{my}" width="300" height="12" rx="6" fill="url(#bar)">'
          f'<animate attributeName="width" values="0;300;300" keyTimes="0;.35;1" dur="{T}s" repeatCount="indefinite"/></rect>')
    o += f'<text x="{tx + 414}" y="{my + 11}" {MONO} font-size="13" font-weight="700" fill="{OR}">100%</text>'
    # mascote
    mx = fx + fw - 210
    o += (f'<g transform="translate({mx},{fy + 66})">{bob(clawd(10), 9)}'
          f'<ellipse cx="70" cy="96" rx="58" ry="5" fill="#000" opacity=".35">'
          f'<animate attributeName="rx" values="58;46;58" dur=".9s" repeatCount="indefinite"/></ellipse></g>')
    for k, (dx, dy, fs) in enumerate(((-26, 40, 18), (166, 30, 14), (150, 140, 12), (-10, 150, 13))):
        o += (f'<text x="{mx + dx}" y="{fy + dy}" {MONO} font-size="{fs}" fill="{OR}">✻'
              f'<animate attributeName="opacity" values="0;1;0" dur="2.2s" begin="{-k*.55:.2f}s" repeatCount="indefinite"/></text>')

    # ---------- secundárias ----------
    ly = fy + fh + 44
    o += f'<text x="{fx}" y="{ly}" {MONO} font-size="14" fill="{DIM}">└ ferramentas secundárias</text>'
    sh, sg = 96, 20
    sw = (fw - sg) / 2
    for i, (name, col, icon) in enumerate(SECUNDARIAS):
        x, y = fx + i * (sw + sg), ly + 20
        if icon == "googlegemini":
            ic = (f'<g><animateTransform attributeName="transform" type="rotate" values="0;0;90;90" '
                  f'keyTimes="0;.55;.8;1" dur="5s" repeatCount="indefinite" calcMode="spline" '
                  f'keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1"/>'
                  f'<g><animateTransform attributeName="transform" type="scale" values="1;1.12;1" dur="2.5s" repeatCount="indefinite"/>'
                  f'<path transform="scale(1.9) translate(-12,-12)" fill="url(#gem)" d="{logo_path(icon)}"/></g></g>')
        else:
            ic = (f'<rect x="-25" y="-25" width="50" height="50" rx="13" fill="{col}"/>'
                  f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>'
                  f'<path transform="scale(1.45) translate(-12,-12)" fill="#ffffff" d="{logo_path(icon)}"/></g>')
        card = (f'<rect width="{sw:.0f}" height="{sh}" rx="16" fill="{PANEL}" stroke="{col}" stroke-opacity=".55" stroke-width="1.5"/>'
                f'<rect width="{sw:.0f}" height="{sh}" rx="16" fill="{col}" opacity=".06"/>'
                f'<g transform="translate(52,{sh/2})">{ic}</g>'
                f'<text x="96" y="{sh/2 - 4}" {SERIF} font-size="30" fill="{CREAM}">{esc(name)}</text>'
                f'<text x="98" y="{sh/2 + 22}" {MONO} font-size="14" fill="{MUTED}">assistente de IA</text>'
                f'<rect x="{sw - 148:.0f}" y="{sh/2 - 14}" width="122" height="28" rx="14" fill="none" stroke="{MUTED}" stroke-opacity=".6"/>'
                f'<text x="{sw - 87:.0f}" y="{sh/2 + 5}" text-anchor="middle" {MONO} font-size="12" font-weight="700" fill="{MUTED}" letter-spacing="1.2">SECUNDÁRIA</text>')
        o += f'<g transform="translate({x:.0f},{y})">{bob(card, 3, 2.6 + i * .5)}</g>'

    # ---------- demais ferramentas ----------
    ly = ly + 20 + sh + 44
    o += f'<text x="{fx}" y="{ly}" {MONO} font-size="14" fill="{DIM}">└ outras ferramentas</text>'
    top = ly + 22
    rows = math.ceil(len(STACK) / cols)
    T2 = len(STACK) * .35 + 1.5
    for i, (name, col) in enumerate(STACK):
        r, c = divmod(i, cols)
        in_row = min(cols, len(STACK) - r * cols)
        x0 = (W - (in_row * cw + (in_row - 1) * gx)) / 2
        x = x0 + c * (cw + gx)
        y = top + r * (ch + gy)
        a = i * .35 / T2
        chip = (f'<rect width="{cw}" height="{ch}" rx="14" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5">'
                f'<animate attributeName="stroke" dur="{T2:.1f}s" repeatCount="indefinite" '
                f'keyTimes="0;{a:.3f};{a+.04:.3f};{a+.12:.3f};1" values="{BORDER};{BORDER};{OR};{BORDER};{BORDER}"/></rect>'
                f'<circle cx="26" cy="{ch/2}" r="6" fill="{col}"/>'
                f'<text x="44" y="{ch/2+6}" {MONO} font-size="16" font-weight="600" fill="{CREAM}">{esc(name)}</text>')
        o += f'<g transform="translate({x:.0f},{y})">{bob(chip, 4, 2 + (i % 4) * .4)}</g>'
    H = top + rows * (ch + gy) + 20
    o = frame(W, H) + stars(W, H, 18) + o
    defs = (border_gradient("bd", 12) + border_gradient("bd2", 5) + GLOW
            + '<filter id="soft" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>'
            + f'<radialGradient id="rg" cx=".12" cy=".5" r=".6"><stop offset="0" stop-color="{OR}" stop-opacity=".22"/>'
              f'<stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>'
            + '<linearGradient id="gem" gradientUnits="userSpaceOnUse" x1="3" y1="3" x2="21" y2="21">'
              '<stop offset="0" stop-color="#439ddf"/><stop offset=".3" stop-color="#4f87ed"/>'
              '<stop offset=".6" stop-color="#9476c5"/><stop offset=".85" stop-color="#bc688e"/>'
              '<stop offset="1" stop-color="#d6645d"/></linearGradient>'
            + f'<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{OR_D}"/><stop offset="1" stop-color="{MANILLA}"/></linearGradient>')
    save("stack.svg", svg(W, H, o, defs))


# ======================================================= 5. projetos
# CONTEÚDO (repo, linguagem, cor, descrição)
PROJETOS = [
    ("agrovic-site", "TypeScript", "#3178c6", "Pedidos pelo WhatsApp para casa de ração, farmácia e consultório veterinário."),
    ("costelao-pedidos", "TypeScript", "#3178c6", "Cardápio mobile-first do Restaurante O Costelão, com pedido pelo WhatsApp."),
    ("studiohairhousebarber", "TypeScript", "#3178c6", "Site moderno para o Studio Hair House Barber."),
    ("DomBoscoPage", "HTML", "#e34f26", "Página institucional Dom Bosco."),
    ("SitePontoPet", "CSS", "#2965f1", "Site do pet shop Ponto Pet."),
    ("AtakamaGastrobar", "CSS", "#2965f1", "Site do Atakama Gastrobar."),
]


def projects():
    W, H = 600, 210
    for i, (name, lang, col, desc) in enumerate(PROJETOS):
        o = (f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
             f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="none" stroke="url(#bd)" stroke-width="2" '
             f'stroke-dasharray="180 1400"><animate attributeName="stroke-dashoffset" from="0" to="-1580" dur="6s" '
             f'begin="{-i*1.1:.1f}s" repeatCount="indefinite"/></rect>')
        o += (f'<circle cx="38" cy="50" r="7" fill="{OR}"><animate attributeName="opacity" values="1;.3;1" '
              f'dur="1.6s" begin="{-i*.3:.1f}s" repeatCount="indefinite"/></circle>')
        o += f'<text x="58" y="57" {MONO} font-size="21" font-weight="700" fill="{CREAM}">{esc(name)}</text>'
        o += f'<text x="{W-30}" y="57" text-anchor="end" {MONO} font-size="13" fill="{DIM}">Read</text>'
        for j, line in enumerate(textwrap.wrap(desc, 52)[:2]):
            pre = "└ " if j == 0 else "  "
            o += f'<text x="34" y="{98 + j*26}" {MONO} font-size="15.5" fill="{MUTED}" xml:space="preserve"><tspan fill="{DIM}">{pre}</tspan>{esc(line)}</text>'
        o += f'<line x1="30" y1="150" x2="{W-30}" y2="150" stroke="{BORDER}"/>'
        o += f'<circle cx="40" cy="178" r="6" fill="{col}"/>'
        o += f'<text x="54" y="183" {MONO} font-size="14" fill="{CREAM}">{lang}</text>'
        o += (f'<text x="{W-30}" y="183" text-anchor="end" {MONO} font-size="14" fill="{OR}">abrir ↗'
              f'<animate attributeName="x" values="{W-30};{W-26};{W-30}" dur="1.8s" repeatCount="indefinite"/></text>')
        save(f"projeto-{name}.svg", svg(W, H, o, border_gradient("bd", 6)))


# ======================================================= 6. mascote andando
def walk():
    u = 4.5
    o = (f'<line x1="0" y1="72" x2="900" y2="72" stroke="{OR}" stroke-opacity=".4" stroke-width="2" '
         f'stroke-dasharray="3 9" stroke-linecap="round"><animate attributeName="stroke-dashoffset" '
         f'from="0" to="-24" dur=".8s" repeatCount="indefinite"/></line>')
    trail = "".join(
        f'<text x="{-14 - k*22}" y="{50 - (k % 2)*8}" {MONO} font-size="{12 - k*2}" fill="{OR}" opacity="{.7 - k*.2:.1f}">✻</text>'
        for k in range(3))
    o += (f'<g><animateTransform attributeName="transform" type="translate" from="-70 0" to="960 0" '
          f'dur="11s" repeatCount="indefinite"/>{trail}<g transform="translate(0,26)">'
          f'{bob(clawd(u, walk=True), 3, .5)}</g>'
          f'<text x="{7*u}" y="14" text-anchor="middle" {MONO} font-size="14" fill="{OR}">✻'
          f'<animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></text></g>')
    save("clawd-walk.svg", svg(900, 84, o))


# ======================================================= 7. rodapé
def footer():
    W, H = 1200, 190
    defs = (f'<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="{OR_D}"/>'
            f'<stop offset=".5" stop-color="{OR}"/><stop offset="1" stop-color="{KRAFT}"/></linearGradient>')
    def wave(y, a, dur, op):
        p1 = f"M0 {y} Q300 {y-a} 600 {y} T1200 {y} V{H} H0Z"
        p2 = f"M0 {y} Q300 {y+a} 600 {y} T1200 {y} V{H} H0Z"
        return (f'<path fill="url(#f)" opacity="{op}" d="{p1}"><animate attributeName="d" dur="{dur}s" '
                f'repeatCount="indefinite" values="{p1};{p2};{p1}"/></path>')
    bubbles = "".join(
        f'<text x="{random.randint(80, 1120)}" y="{H}" {MONO} font-size="{random.randint(10, 18)}" fill="{OR}" opacity="0">✻'
        f'<animate attributeName="y" values="{H-30};{20}" dur="{d:.1f}s" begin="{-b:.1f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;.8;0" dur="{d:.1f}s" begin="{-b:.1f}s" repeatCount="indefinite"/></text>'
        for d, b in ((random.uniform(4, 7), random.uniform(0, 7)) for _ in range(12)))
    o = bubbles
    o += f'<g transform="translate(537,58)">{bob(clawd(9), 6, 1.2)}</g>'
    o += wave(140, 30, 8, .35) + wave(158, 22, 6, .6) + wave(176, 10, 5, 1)
    save("footer.svg", svg(W, H, o, defs))


if __name__ == "__main__":
    hero(); titles(); claude_md(); stack(); projects(); walk(); footer()
    print("SVGs gerados em", OUT)
