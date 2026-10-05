#!/usr/bin/env python3
"""Gera todos os SVGs animados do perfil (tema Claude).

Edite os textos nas seções marcadas com "CONTEÚDO" e rode:
    python3 scripts/gerar_assets.py
"""
import html
import math
import random
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
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


def spark(cx, cy, scale=1.0, dur=24, width=9):
    """Faísca de raios irregulares que gira e pulsa."""
    lens = [62, 44, 58, 40, 66, 46, 56, 42, 60, 48, 64, 40]
    rays = ""
    for k, L in enumerate(lens):
        a = 2 * math.pi * k / len(lens)
        x1, y1 = math.cos(a) * 14, math.sin(a) * 14
        x2, y2 = math.cos(a) * L, math.sin(a) * L
        d = 2.4 + (k % 3) * .4
        rays += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{OR}" '
                 f'stroke-width="{width}" stroke-linecap="round">'
                 f'<animate attributeName="x2" values="{x2:.1f};{x2*1.14:.1f};{x2:.1f}" dur="{d:.1f}s" begin="{-k*.2:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y2" values="{y2:.1f};{y2*1.14:.1f};{y2:.1f}" dur="{d:.1f}s" begin="{-k*.2:.1f}s" repeatCount="indefinite"/></line>')
    return (f'<g transform="translate({cx},{cy}) scale({scale})"><g>'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{dur}s" repeatCount="indefinite"/>'
            f'{rays}</g></g>')


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
    o += f'<g filter="url(#glow)">{spark(1070, 160, .85)}</g>'
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
    ("Git", "#f05032"), ("Figma", "#a259ff"), ("Claude Code", OR),
]


def stack():
    W, cols, cw, ch, gx, gy = 1200, 6, 168, 64, 20, 22
    rows = math.ceil(len(STACK) / cols)
    x0 = (W - (cols * cw + (cols - 1) * gx)) / 2
    top = 92
    H = top + rows * (ch + gy) + 26
    o = frame(W, H) + window_chrome(W, "/stack")
    T = len(STACK) * .35 + 1.5
    for i, (name, col) in enumerate(STACK):
        x = x0 + (i % cols) * (cw + gx)
        y = top + (i // cols) * (ch + gy)
        a = i * .35 / T
        icon = (f'<g transform="translate(26,{ch/2})">{spark(0, 0, .17, 10, 12)}</g>' if name == "Claude Code"
                else f'<circle cx="26" cy="{ch/2}" r="6" fill="{col}"/>')
        chip = (f'<rect width="{cw}" height="{ch}" rx="14" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5">'
                f'<animate attributeName="stroke" dur="{T:.1f}s" repeatCount="indefinite" '
                f'keyTimes="0;{a:.3f};{a+.04:.3f};{a+.12:.3f};1" values="{BORDER};{BORDER};{OR};{BORDER};{BORDER}"/></rect>'
                f'{icon}<text x="44" y="{ch/2+6}" {MONO} font-size="16" font-weight="600" fill="{CREAM}">{esc(name)}</text>')
        o += f'<g transform="translate({x:.0f},{y})">{bob(chip, 4, 2 + (i % 4) * .4)}</g>'
    save("stack.svg", svg(W, H, o, border_gradient("bd", 12)))


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
