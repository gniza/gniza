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


W_MOBILE = 420  # largura das versões para celular (*-m.svg)


def mname(name, mobile):
    """'hero.svg' -> 'hero-m.svg' na versão para celular."""
    return name.replace(".svg", "-m.svg") if mobile else name


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
HERO_SUB_M = ("desenvolvedor web · front-end", "vibe coding com Claude")  # versão celular
PERGUNTA = "> me conta sobre o Gabriel"
RESPOSTAS = [
    ("●", "Desenvolvedor web apaixonado por front-end"),
    ("●", "Cria sites e cardápios online para negócios locais"),
    ("●", "Pedidos pelo WhatsApp, mobile-first e visual caprichado"),
    ("●", "Programa em parceria com o Claude Code"),
]
STATUS = "✔ Disponível para novos projetos"


def hero(mobile=False):
    T = 18.0
    if mobile:
        W, fs, CW, wrap_n = W_MOBILE, 14.5, 8.8, 32
        box, welcome, name_xy, name_fs = (24, 76, W_MOBILE - 48, 236), (44, 110, 14), (42, 172, 46), 46
        subs, sub_fs, help_line = [(44, 210, HERO_SUB_M[0]), (44, 232, HERO_SUB_M[1])], 14, None
        spark_xyz, mascot = (352, 126, .34), (292, 250, 5)
        y0, dy, x0 = 350, 26, 32
    else:
        W, fs, CW, wrap_n = 1200, 17, 10.3, None
        box, welcome, name_xy, name_fs = (40, 82, 1120, 216), (72, 122, 16), (70, 198, 70), 70
        subs, sub_fs, help_line = [(72, 240, HERO_SUB)], 17, (72, 274)
        spark_xyz, mascot = (1062, 168, .72), (860, 170, 9)
        y0, dy, x0 = 350, 32, 50

    # linhas da conversa (no celular as respostas longas quebram em duas)
    resp_lines = []
    for b, txt in RESPOSTAS:
        parts = textwrap.wrap(txt, wrap_n) if wrap_n else [txt]
        resp_lines.append([(b if j == 0 else " ", p) for j, p in enumerate(parts)])
    n_resp = sum(len(r) for r in resp_lines)
    H = y0 + dy * (n_resp + 2) + (40 if mobile else 54)

    o = frame(W, H) + stars(W, H, 18 if mobile else 30) + window_chrome(W, "gniza — claude" if mobile else "gniza — claude — ~/github/gniza")
    bx, by, bw, bh = box
    o += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" fill="{PANEL}" stroke="{OR}" stroke-opacity=".75" stroke-width="1.5"/>'
    o += f'<text x="{welcome[0]}" y="{welcome[1]}" {MONO} font-size="{welcome[2]}" fill="{OR}">✻ Bem-vindo ao Claude Code</text>'
    o += (f'<text x="{name_xy[0]}" y="{name_xy[1]}" {SERIF} font-size="{name_fs}" fill="{CREAM}" letter-spacing="-1">{esc(HERO_NAME)}'
          f'{reveal(.2, .8)}</text>')
    for x, y, t in subs:
        o += f'<text x="{x}" y="{y}" {MONO} font-size="{sub_fs}" fill="{MUTED}">{esc(t)}</text>'
    if help_line:
        o += f'<text x="{help_line[0]}" y="{help_line[1]}" {MONO} font-size="14" fill="{DIM}">/help para ajuda · /status para ver a configuração</text>'
    o += f'<g filter="url(#glow)">{spark(*spark_xyz)}</g>'
    mx, my, mu = mascot
    o += (f'<g transform="translate({mx},{my})">{bob(clawd(mu), mu - 1)}'
          f'<ellipse cx="{7*mu}" cy="{9.3*mu:.0f}" rx="{5.8*mu:.0f}" ry="{mu*.55:.1f}" fill="#000" opacity=".35">'
          f'<animate attributeName="rx" values="{5.8*mu:.0f};{4.7*mu:.0f};{5.8*mu:.0f}" dur=".9s" repeatCount="indefinite"/></ellipse></g>')

    # pergunta digitada
    n = len(PERGUNTA)
    w = n * CW + 6
    s0, d = .6, 1.6
    times, vals = [0], [0]
    for k in range(1, n + 1):
        times.append(s0 + (k - 1) * d / n)
        vals.append(round(w * k / n, 1))
    times += [16.6, T]
    vals += [0, 0]
    kt = ";".join(f"{t/T:.4f}" for t in times[:-1]) + ";1"
    o += (f'<clipPath id="q"><rect x="{x0}" y="{y0-22}" height="30" width="{w:.0f}">'
          f'<animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
          f'keyTimes="{kt}" values="{";".join(map(str, vals))}"/></rect></clipPath>')
    o += (f'<text x="{x0}" y="{y0}" {MONO} font-size="{fs}" fill="{CREAM}" clip-path="url(#q)">'
          f'<tspan fill="{DIM}">&gt;</tspan>{esc(PERGUNTA[1:])}</text>')

    def window(a, b, base=1):
        k = f"0;{a/T:.4f};{(a+.3)/T:.4f};{b/T:.4f};{(b+.3)/T:.4f};1"
        return (f'opacity="{base}"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" '
                f'keyTimes="{k}" values="0;0;1;1;0;0"/>')

    # spinner "pensando"
    ys = y0 + dy
    spin = ""
    for k, gch in enumerate("·✢✳✶✻✽"):
        a, b = k / 6, (k + 1) / 6
        ka = f'values="1;0;0" keyTimes="0;{b:.4f};1"' if k == 0 else f'values="0;1;0;0" keyTimes="0;{a:.4f};{b:.4f};1"'
        spin += (f'<text x="{x0}" y="{ys}" {MONO} font-size="{fs}" fill="{OR}" opacity="0">{gch}'
                 f'<animate attributeName="opacity" calcMode="discrete" dur=".9s" repeatCount="indefinite" {ka}/></text>')
    o += (f'<linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" x2="160" y1="0" y2="0">'
          f'<stop offset="0" stop-color="{OR}"/><stop offset=".5" stop-color="{MANILLA}"/><stop offset="1" stop-color="{OR}"/>'
          f'<animateTransform attributeName="gradientTransform" type="translate" from="-80 0" to="200 0" dur="1.2s" repeatCount="indefinite"/></linearGradient>')
    o += (f'<g {window(2.4, 3.9, 0)}{spin}'
          f'<text x="{x0 + 2*CW:.0f}" y="{ys}" {MONO} font-size="{fs}" fill="url(#sh)">Pensando…</text></g>')

    # respostas
    t, y = 4.2, ys
    for lines in resp_lines:
        g = ""
        for b, txt in lines:
            g += (f'<text x="{x0}" y="{y}" {MONO} font-size="{fs}" fill="{CREAM}" xml:space="preserve">'
                  f'<tspan fill="{OR}">{b}</tspan> {esc(txt)}</text>')
            y += dy
        o += f'<g {window(t, 16.4)}{g}</g>'
        t += .7
    o += (f'<g {window(t + .3, 16.4)}<text x="{x0}" y="{y}" {MONO} font-size="{fs}" fill="{GREEN}">'
          f'{esc(STATUS)}</text></g>')
    y += dy + 6
    o += (f'<g {window(t + 1, 16.4)}<text x="{x0}" y="{y}" {MONO} font-size="{fs}" fill="{OR}">&gt;</text>'
          f'<rect x="{x0 + 18}" y="{y-15}" width="{fs*.6:.0f}" height="{fs+3:.0f}" fill="{OR}">'
          f'<animate attributeName="opacity" dur="1s" repeatCount="indefinite" values="1;1;0;0" keyTimes="0;.5;.5;1"/></rect></g>')
    save(mname("hero.svg", mobile), svg(W, H, o, border_gradient("bd") + GLOW))


# ======================================================= 2. títulos de seção
TITULOS = {
    "sobre": "Sobre mim",
    "stack": "Ferramentas",
    "projetos": "Projetos em destaque",
    "contrib": "Contribuições",
    "nizashop": "Minha loja",
    "contato": "Vamos conversar?",
}


def titles(mobile=False):
    W, H = (W_MOBILE, 70) if mobile else (900, 70)
    for key, txt in TITULOS.items():
        o = spark(30, 36, .32, 14, 10)
        o += f'<text x="70" y="47" {SERIF} font-size="34" fill="{OR}">{esc(txt)}</text>'
        x0 = 70 + len(txt) * 17 + 24
        if x0 < W - 30:
            o += (f'<line x1="{x0}" y1="38" x2="{x0}" y2="38" stroke="url(#ln)" stroke-width="2" stroke-linecap="round">'
                  f'<animate attributeName="x2" values="{x0};{W-10};{W-10}" keyTimes="0;.4;1" dur="4s" repeatCount="indefinite"/></line>')
        defs = (f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{OR}"/>'
                f'<stop offset="1" stop-color="{OR}" stop-opacity="0"/></linearGradient>')
        save(mname(f"titulo-{key}.svg", mobile), svg(W, H, o, defs))


# ======================================================= 3. CLAUDE.md
# CONTEÚDO  (tipo, texto)  tipos: h1, h2, quote, li, blank
CLAUDE_MD = [
    ("h1", "# Gabriel Niza"),
    ("blank", ""),
    ("quote", "> Desenvolvedor web que transforma ideias em sites rápidos e bonitos."),
    ("blank", ""),
    ("h2", "## Sobre"),
    ("li", "Fundador e CEO da NizaShop, loja na Shopee"),
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


def claude_md(mobile=False):
    if mobile:
        W, fs, cw, lh, top, gut, tx, wrap_n = W_MOBILE, 15, 9.05, 24, 106, 44, 54, 34
    else:
        W, fs, cw, lh, top, gut, tx, wrap_n = 1200, 18, 10.85, 28, 112, 78, 98, None
    # linhas visuais: (número ou None, tipo, texto)
    rows = []
    for i, (kind, txt) in enumerate(CLAUDE_MD):
        if wrap_n and kind in ("li", "quote") and len(txt) > wrap_n:
            body = txt[1:].strip() if kind == "quote" else txt
            parts = textwrap.wrap(body, wrap_n - 2)
            rows.append((i + 1, kind, ("> " + parts[0]) if kind == "quote" else parts[0]))
            rows += [(None, kind + "+", p) for p in parts[1:]]
        else:
            rows.append((i + 1, kind, txt))
    H = top + len(rows) * lh + 40
    o = frame(W, H) + window_chrome(W, "~/github/gniza")
    o += f'<rect x="10" y="58" width="{W-20}" height="36" fill="{PANEL}"/>'
    o += f'<rect x="10" y="58" width="170" height="36" fill="{BG}"/><rect x="10" y="58" width="170" height="2" fill="{OR}"/>'
    o += f'<text x="34" y="81" {MONO} font-size="14" fill="{CREAM}"><tspan fill="{OR}">✻</tspan> CLAUDE.md</text>'
    o += f'<text x="208" y="81" {MONO} font-size="14" fill="{DIM}">README.md</text>'
    if not mobile:
        o += f'<text x="340" y="81" {MONO} font-size="14" fill="{DIM}">index.html</text>'
    o += f'<line x1="{gut}" y1="100" x2="{gut}" y2="{H-24}" stroke="{BORDER}"/>'
    for r, (num, kind, txt) in enumerate(rows):
        y = top + r * lh + 12
        if num:
            o += f'<text x="{gut - 20}" y="{y}" text-anchor="end" {MONO} font-size="{fs - 3}" fill="{DIM}">{num}</text>'
        if kind == "blank":
            continue
        if kind == "h1":
            line = f'<tspan fill="{DIM}">#</tspan><tspan fill="{OR}" font-weight="700">{esc(txt[1:])}</tspan>'
        elif kind == "h2":
            line = f'<tspan fill="{DIM}">##</tspan><tspan fill="{KRAFT}" font-weight="700">{esc(txt[2:])}</tspan>'
        elif kind == "quote":
            line = f'<tspan fill="{DIM}">&gt;</tspan><tspan fill="{MUTED}" font-style="italic">{esc(txt[1:])}</tspan>'
        elif kind == "quote+":
            line = f'<tspan fill="{MUTED}" font-style="italic">  {esc(txt)}</tspan>'
        elif kind == "li+":
            line = f'<tspan fill="{CREAM}">  {esc(txt)}</tspan>'
        else:
            line = f'<tspan fill="{OR}">-</tspan> <tspan fill="{CREAM}">{esc(txt)}</tspan>'
        o += f'<text x="{tx}" y="{y}" {MONO} font-size="{fs}" xml:space="preserve">{line}{reveal(.3 + r * .16, .35)}</text>'
    last = top + (len(rows) - 1) * lh + 12
    cx = tx + (len(rows[-1][2]) + 2) * cw
    o += (f'<rect x="{cx:.0f}" y="{last-fs+2}" width="3" height="{fs+3}" fill="{OR}" opacity="0">'
          f'<animate attributeName="opacity" begin="{.3 + len(rows)*.16:.1f}s" dur="1s" repeatCount="indefinite" '
          f'values="1;1;0;0" keyTimes="0;.5;.5;1"/></rect>')
    if not mobile:
        o += f'<g transform="translate({W-190},{H-118})">{bob(clawd(9), 5, 1.4)}</g>'
    save(mname("claude-md.svg", mobile), svg(W, H, o, border_gradient("bd", 10)))


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
# cards médios: (nome, subtítulo, cor, logo em scripts/logos/, selo, cor do selo)
SECUNDARIAS = [
    ("Gemini", "assistente de IA", "#8e7cf0", "googlegemini", "SECUNDÁRIA", MUTED),
    ("ChatGPT", "assistente de IA", "#10a37f", "openai", "SECUNDÁRIA", MUTED),
]
DESIGN_MARKETING = [
    ("TryBloom", "design de marca com IA", "#9d4edd", "trybloom", "DESIGN", "#c08cf0"),
    ("Shopee", "Vendedor na Shopee", "#ee4d2d", "shopee", "VENDEDOR", "#ff7a5c"),
]


def tool_icon(icon, col):
    """Logo oficial animado, centrado em (0,0), ~50px."""
    if icon == "googlegemini":
        return (f'<g><animateTransform attributeName="transform" type="rotate" values="0;0;90;90" '
                f'keyTimes="0;.55;.8;1" dur="5s" repeatCount="indefinite" calcMode="spline" '
                f'keySplines="0 0 1 1;.5 0 .3 1;0 0 1 1"/>'
                f'<g><animateTransform attributeName="transform" type="scale" values="1;1.12;1" dur="2.5s" repeatCount="indefinite"/>'
                f'<path transform="scale(1.9) translate(-12,-12)" fill="url(#gem)" d="{logo_path(icon)}"/></g></g>')
    if icon == "openai":
        return (f'<rect x="-25" y="-25" width="50" height="50" rx="13" fill="{col}"/>'
                f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>'
                f'<path transform="scale(1.45) translate(-12,-12)" fill="#ffffff" d="{logo_path(icon)}"/></g>')
    if icon == "trybloom":
        # ícone oficial (360x360): fundo branco, contorno da flor e miolo roxos
        src = (LOGOS / "trybloom.svg").read_text()
        rect = re.search(r"<rect[^>]*/>", src).group(0)
        outer, inner = re.findall(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]+)"', src)[:2]
        return (f'<g transform="translate(-25,-25) scale({50/360:.4f})">{rect}'
                f'<g><animateTransform attributeName="transform" type="rotate" from="0 180 180" to="360 180 180" dur="14s" repeatCount="indefinite"/>'
                f'<path d="{outer[0]}" fill="{outer[1]}"/></g>'
                f'<g transform="translate(180,180)"><g><animateTransform attributeName="transform" type="scale" values="1;1.1;1" '
                f'dur="2.4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>'
                f'<path transform="translate(-180,-180)" d="{inner[0]}" fill="{inner[1]}"/></g></g></g>')
    if icon == "shopee":
        # sacola oficial em branco sobre o laranja da marca, dando pulinhos
        return (f'<rect x="-25" y="-25" width="50" height="50" rx="13" fill="{col}"/>'
                f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0;0 0" '
                f'keyTimes="0;.2;.4;1" dur="1.8s" repeatCount="indefinite"/>'
                f'<path transform="scale(1.4) translate(-12,-12)" fill="#ffffff" d="{logo_path(icon)}"/></g>')
    raise ValueError(icon)


def tool_card(sw, sh, name, sub, col, icon, badge, badge_col, compact=False):
    """Card médio de ferramenta. compact=True (celular) põe o selo no canto superior direito."""
    o = (f'<rect width="{sw:.0f}" height="{sh}" rx="16" fill="{PANEL}" stroke="{col}" stroke-opacity=".55" stroke-width="1.5"/>'
         f'<rect width="{sw:.0f}" height="{sh}" rx="16" fill="{col}" opacity=".06"/>')
    bw = len(badge) * 8.4 + 30
    by = 12 if compact else sh / 2 - 14
    bh = 24 if compact else 28
    o += (f'<g transform="translate(52,{sh/2})">{tool_icon(icon, col)}</g>'
          f'<text x="96" y="{sh/2 - 4}" {SERIF} font-size="{27 if compact else 30}" fill="{CREAM}">{esc(name)}</text>'
          f'<text x="98" y="{sh/2 + 22}" {MONO} font-size="14" fill="{MUTED}">{esc(sub)}</text>'
          f'<rect x="{sw - bw - (14 if compact else 26):.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh}" rx="{bh/2:.0f}" fill="{PANEL}" stroke="{badge_col}" stroke-opacity=".7"/>'
          f'<text x="{sw - bw/2 - (14 if compact else 26):.0f}" y="{by + bh/2 + 4:.0f}" text-anchor="middle" {MONO} font-size="{11 if compact else 12}" font-weight="700" '
          f'fill="{badge_col}" letter-spacing="1.2">{esc(badge)}</text>')
    return o


def stack(mobile=False):
    if mobile:
        W, cols, ch, gx, gy = W_MOBILE, 2, 54, 14, 14
        fx, fy, fw, fh = 16, 76, W_MOBILE - 32, 330
    else:
        W, cols, ch, gx, gy = 1200, 6, 64, 20, 22
        fx, fy, fw, fh = 45, 84, 1110, 244
    cw = (fw - (cols - 1) * gx) / cols if mobile else 168
    o = window_chrome(W, "/stack")

    # ---------- card principal ----------
    o += (f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="none" stroke="{OR}" stroke-width="10" '
          f'filter="url(#soft)" opacity=".35"><animate attributeName="opacity" values=".15;.5;.15" dur="3s" repeatCount="indefinite"/></rect>')
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="{PANEL}"/>'
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="url(#rg)"/>'
    o += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="20" fill="none" stroke="url(#bd2)" stroke-width="2.5"/>'
    if mobile:
        o += f'<g filter="url(#glow)">{spark(fx + 96, fy + 78, .55, 18)}</g>'
        mx, my, mu = fx + fw - 150, fy + 44, 7
        o += (f'<g transform="translate({mx},{my})">{bob(clawd(mu), 6)}'
              f'<ellipse cx="{7*mu}" cy="{9.4*mu:.0f}" rx="{5.8*mu:.0f}" ry="4" fill="#000" opacity=".35"/></g>')
        cx = fx + fw / 2
        o += (f'<rect x="{cx - 116}" y="{fy + 150}" width="232" height="28" rx="14" fill="{OR}" fill-opacity=".15" stroke="{OR}" stroke-opacity=".7"/>'
              f'<text x="{cx}" y="{fy + 169}" text-anchor="middle" {MONO} font-size="13" font-weight="700" fill="{OR}" letter-spacing="1.5">'
              f'★ FERRAMENTA PRINCIPAL<animate attributeName="opacity" values="1;.55;1" dur="2s" repeatCount="indefinite"/></text>')
        o += f'<text x="{cx}" y="{fy + 226}" text-anchor="middle" {SERIF} font-size="46" fill="{CREAM}" letter-spacing="-1">{esc(PRINCIPAL)}</text>'
        o += f'<text x="{cx}" y="{fy + 254}" text-anchor="middle" {MONO} font-size="13.5" fill="{MUTED}">{esc(PRINCIPAL_SUB)}</text>'
        cmd_fs, cmd_cw = 13.5, 8.2
        w = len(PRINCIPAL_CMD) * cmd_cw + 6
        tx = cx - (w + 72) / 2
        cy, my2 = fy + 286, fy + 306
        bar_x, bar_w = fx + 112, fw - 190
    else:
        o += f'<g filter="url(#glow)">{spark(fx + 112, fy + fh / 2, 1.05, 18)}</g>'
        tx = fx + 222
        o += (f'<rect x="{tx}" y="{fy + 24}" width="232" height="28" rx="14" fill="{OR}" fill-opacity=".15" stroke="{OR}" stroke-opacity=".7"/>'
              f'<text x="{tx + 116}" y="{fy + 43}" text-anchor="middle" {MONO} font-size="13" font-weight="700" fill="{OR}" letter-spacing="1.5">'
              f'★ FERRAMENTA PRINCIPAL<animate attributeName="opacity" values="1;.55;1" dur="2s" repeatCount="indefinite"/></text>')
        o += f'<text x="{tx - 2}" y="{fy + 104}" {SERIF} font-size="58" fill="{CREAM}" letter-spacing="-1">{esc(PRINCIPAL)}</text>'
        o += f'<text x="{tx}" y="{fy + 138}" {MONO} font-size="17" fill="{MUTED}">{esc(PRINCIPAL_SUB)}</text>'
        cmd_fs, cmd_cw = 16, 9.7
        w = len(PRINCIPAL_CMD) * cmd_cw + 6
        cy, my2 = fy + 180, fy + 206
        bar_x, bar_w = tx + 100, 300
    # comando digitado em loop
    T, n = 8.0, len(PRINCIPAL_CMD)
    times, vals = [0], [0]
    for k in range(1, n + 1):
        times.append(.4 + (k - 1) * 2.2 / n)
        vals.append(round(w * k / n, 1))
    times += [7.4, T]
    vals += [0, 0]
    kt = ";".join(f"{t/T:.4f}" for t in times[:-1]) + ";1"
    o += (f'<clipPath id="cmd"><rect x="{tx:.0f}" y="{cy - 20}" height="28" width="{w:.0f}">'
          f'<animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
          f'keyTimes="{kt}" values="{";".join(map(str, vals))}"/></rect></clipPath>')
    o += (f'<text x="{tx:.0f}" y="{cy}" {MONO} font-size="{cmd_fs}" fill="{CREAM}" clip-path="url(#cmd)" xml:space="preserve">'
          f'<tspan fill="{OR}">&gt;</tspan>{esc(PRINCIPAL_CMD[1:])}</text>')
    o += (f'<text x="{tx + w + 12:.0f}" y="{cy}" {MONO} font-size="{cmd_fs}" fill="{GREEN}">✔ feito'
          f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;{3/T:.3f};{3.2/T:.3f};{7.3/T:.3f};{7.4/T:.3f};1" values="0;0;1;1;0;0"/></text>')
    # medidor de uso
    lx = fx + 24 if mobile else tx
    o += f'<text x="{lx:.0f}" y="{my2 + 11}" {MONO} font-size="13" fill="{DIM}">uso diário</text>'
    o += f'<rect x="{bar_x:.0f}" y="{my2}" width="{bar_w}" height="12" rx="6" fill="{BG}" stroke="{BORDER}"/>'
    o += (f'<rect x="{bar_x:.0f}" y="{my2}" width="{bar_w}" height="12" rx="6" fill="url(#bar)">'
          f'<animate attributeName="width" values="0;{bar_w};{bar_w}" keyTimes="0;.35;1" dur="{T}s" repeatCount="indefinite"/></rect>')
    o += f'<text x="{bar_x + bar_w + 14:.0f}" y="{my2 + 11}" {MONO} font-size="13" font-weight="700" fill="{OR}">100%</text>'
    if not mobile:
        mx = fx + fw - 210
        o += (f'<g transform="translate({mx},{fy + 66})">{bob(clawd(10), 9)}'
              f'<ellipse cx="70" cy="96" rx="58" ry="5" fill="#000" opacity=".35">'
              f'<animate attributeName="rx" values="58;46;58" dur=".9s" repeatCount="indefinite"/></ellipse></g>')
        for k, (dx, dy, fs) in enumerate(((-26, 40, 18), (166, 30, 14), (150, 140, 12), (-10, 150, 13))):
            o += (f'<text x="{mx + dx}" y="{fy + dy}" {MONO} font-size="{fs}" fill="{OR}">✻'
                  f'<animate attributeName="opacity" values="0;1;0" dur="2.2s" begin="{-k*.55:.2f}s" repeatCount="indefinite"/></text>')

    # ---------- secundárias e design & marketing ----------
    sh, sg = (84, 14) if mobile else (96, 20)
    sw = fw if mobile else (fw - sg) / 2
    ly = fy + fh + 44
    for label, cards in (("└ ferramentas secundárias", SECUNDARIAS), ("└ design & marketing", DESIGN_MARKETING)):
        o += f'<text x="{fx}" y="{ly}" {MONO} font-size="14" fill="{DIM}">{esc(label)}</text>'
        for i, card_data in enumerate(cards):
            if mobile:
                x, y = fx, ly + 20 + i * (sh + sg)
            else:
                x, y = fx + i * (sw + sg), ly + 20
            o += f'<g transform="translate({x:.0f},{y})">{bob(tool_card(sw, sh, *card_data, compact=mobile), 3, 2.6 + i * .5)}</g>'
        ly += 20 + (len(cards) * (sh + sg) - sg if mobile else sh) + 44

    # ---------- demais ferramentas ----------
    o += f'<text x="{fx}" y="{ly}" {MONO} font-size="14" fill="{DIM}">└ outras ferramentas</text>'
    top = ly + 22
    rows = math.ceil(len(STACK) / cols)
    T2 = len(STACK) * .35 + 1.5
    for i, (name, col) in enumerate(STACK):
        r, c = divmod(i, cols)
        in_row = min(cols, len(STACK) - r * cols)
        x0 = fx if mobile else (W - (in_row * cw + (in_row - 1) * gx)) / 2
        x = x0 + c * (cw + gx)
        y = top + r * (ch + gy)
        a = i * .35 / T2
        chip = (f'<rect width="{cw:.0f}" height="{ch}" rx="14" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.5">'
                f'<animate attributeName="stroke" dur="{T2:.1f}s" repeatCount="indefinite" '
                f'keyTimes="0;{a:.3f};{a+.04:.3f};{a+.12:.3f};1" values="{BORDER};{BORDER};{OR};{BORDER};{BORDER}"/></rect>'
                f'<circle cx="26" cy="{ch/2}" r="6" fill="{col}"/>'
                f'<text x="44" y="{ch/2+6}" {MONO} font-size="16" font-weight="600" fill="{CREAM}">{esc(name)}</text>')
        o += f'<g transform="translate({x:.0f},{y})">{bob(chip, 4, 2 + (i % 4) * .4)}</g>'
    H = top + rows * (ch + gy) + 20
    o = frame(W, H) + stars(W, H, 18) + o
    defs = (border_gradient("bd", 12) + border_gradient("bd2", 5) + GLOW
            + '<filter id="soft" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>'
            + f'<radialGradient id="rg" cx="{.25 if mobile else .12}" cy="{.25 if mobile else .5}" r=".6"><stop offset="0" stop-color="{OR}" stop-opacity=".22"/>'
              f'<stop offset="1" stop-color="{OR}" stop-opacity="0"/></radialGradient>'
            + '<linearGradient id="gem" gradientUnits="userSpaceOnUse" x1="3" y1="3" x2="21" y2="21">'
              '<stop offset="0" stop-color="#439ddf"/><stop offset=".3" stop-color="#4f87ed"/>'
              '<stop offset=".6" stop-color="#9476c5"/><stop offset=".85" stop-color="#bc688e"/>'
              '<stop offset="1" stop-color="#d6645d"/></linearGradient>'
            + f'<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{OR_D}"/><stop offset="1" stop-color="{MANILLA}"/></linearGradient>')
    save(mname("stack.svg", mobile), svg(W, H, o, defs))


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


def projects(mobile=False):
    """No celular os cards (2 por linha) mostram só o essencial, em letras grandes."""
    W, H = (300, 170) if mobile else (600, 210)
    for i, (name, lang, col, desc) in enumerate(PROJETOS):
        o = (f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
             f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="18" fill="none" stroke="url(#bd)" stroke-width="2" '
             f'stroke-dasharray="{90 if mobile else 180} {2*(W+H)}"><animate attributeName="stroke-dashoffset" from="0" to="-{2*(W+H)-8}" dur="6s" '
             f'begin="{-i*1.1:.1f}s" repeatCount="indefinite"/></rect>')
        if mobile:
            fs = min(25, 262 / (len(name) * .62))
            o += (f'<circle cx="28" cy="38" r="6" fill="{OR}"><animate attributeName="opacity" values="1;.3;1" '
                  f'dur="1.6s" begin="{-i*.3:.1f}s" repeatCount="indefinite"/></circle>'
                  f'<text x="42" y="44" {MONO} font-size="17" fill="{DIM}">Read</text>'
                  f'<text x="22" y="88" {MONO} font-size="{fs:.1f}" font-weight="700" fill="{CREAM}">{esc(name)}</text>'
                  f'<line x1="20" y1="112" x2="{W-20}" y2="112" stroke="{BORDER}"/>'
                  f'<circle cx="30" cy="141" r="8" fill="{col}"/>'
                  f'<text x="46" y="148" {MONO} font-size="{19 if len(lang) > 4 else 20}" fill="{CREAM}">{lang}</text>'
                  f'<text x="{W-18}" y="148" text-anchor="end" {MONO} font-size="20" fill="{OR}">abrir ↗</text>')
        else:
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
        save(mname(f"projeto-{name}.svg", mobile), svg(W, H, o, border_gradient("bd", 6)))


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


# ======================================================= 8. NizaShop
NIZA_DIR = OUT.parent / "nizashop" / "assets"
AMEIXA, PITAYA, PESSEGO, LAVANDA, LILAS, NOITE = "#2B1646", "#E11D6A", "#FFC7AE", "#EFE9F8", "#B8A4E3", "#1B1128"
SANS = "font-family=\"Inter,'Segoe UI',Roboto,Helvetica,Arial,sans-serif\""
SHOPEE = "#ee4d2d"
# CONTEÚDO
NIZA_CEO = "Fundador & CEO · Gabriel Niza"
NIZA_PILARES = [
    ("estrela", "Curadoria", "produtos escolhidos a dedo"),
    ("etiqueta", "Preço justo", "ofertas e cupons toda semana"),
    ("raio", "Envio rápido", "pedido separado no mesmo dia"),
    ("coracao", "Feito com carinho", "embalagem caprichada"),
]
NIZA_PALETA = [("Ameixa", AMEIXA), ("Pitaya", PITAYA), ("Pêssego", PESSEGO), ("Lavanda", LAVANDA), ("Lilás", LILAS), ("Noite", NOITE)]


def b64(path):
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def niza_parts():
    src = (NIZA_DIR / "logos" / "NizaShop-02-sobre-ameixa.svg").read_text()
    n_path = re.search(r'<path d="(M18 46[^"]+)"', src).group(1)
    words = re.findall(r'<path transform="(translate\([^)]+\))" d="([^"]+)"', src)
    return n_path, words  # words: [(transform, d) "Niza", (transform, d) "shop"]


def niza_logo(intro=1.0, light=True):
    """Logo completo (viewBox 643x198) com animação de entrada e detalhes em loop."""
    n_path, words = niza_parts()
    box, ink = (LAVANDA, AMEIXA) if light else (AMEIXA, "#ffffff")
    t = intro
    sym = (f'<rect width="64" height="64" rx="18" fill="{box}"/>'
           f'<path d="{n_path}" pathLength="1" fill="{ink}" stroke="{ink}" stroke-width="2" stroke-linejoin="round" '
           f'stroke-dasharray="1" stroke-dashoffset="0">'
           f'<animate attributeName="stroke-dashoffset" values="1;1;0" keyTimes="0;{t/(t+1):.3f};1" dur="{t+1:.2f}s" fill="freeze"/>'
           f'<animate attributeName="fill-opacity" values="0;0;1" keyTimes="0;{(t+.8)/(t+1.3):.3f};1" dur="{t+1.3:.2f}s" fill="freeze"/></path>'
           f'<g transform="translate(42.5,17)"><g>'
           f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -5;0 0;0 -2;0 0" '
           f'keyTimes="0;.6;.72;.84;.92;1" dur="2.6s" begin="{t+1.2:.1f}s" repeatCount="indefinite"/>'
           f'<circle r="4.2" fill="{PITAYA}"/><circle r="4.2" fill="none" stroke="{PITAYA}" stroke-width="1.2">'
           f'<animate attributeName="r" values="4.2;9" dur="2.6s" begin="{t+1.2:.1f}s" repeatCount="indefinite"/>'
           f'<animate attributeName="opacity" values=".8;0" dur="2.6s" begin="{t+1.2:.1f}s" repeatCount="indefinite"/></circle></g></g>')
    o = (f'<g transform="translate(99,99)"><g>'
         f'<animateTransform attributeName="transform" type="scale" values="0;0;1.12;1" keyTimes="0;{t*.4/(t+.6):.3f};{(t*.4+.45)/(t+.6):.3f};1" dur="{t+.6:.2f}s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.3 0 .4 1;.4 0 .6 1"/>'
         f'<g transform="translate(-75,-75) scale(2.34375)">{sym}</g></g></g>')
    for i, (tr, d) in enumerate(words):
        st = t + .25 + i * .3
        o += (f'<g opacity="1"><animate attributeName="opacity" values="0;0;1" keyTimes="0;{st/(st+.5):.3f};1" dur="{st+.5:.2f}s" fill="freeze"/>'
              f'<animateTransform attributeName="transform" type="translate" values="-24 0;-24 0;0 0" keyTimes="0;{st/(st+.5):.3f};1" dur="{st+.5:.2f}s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;.2 0 .2 1"/>'
              f'<path transform="{tr}" fill="#ffffff" d="{d}"/>'
              f'<path transform="{tr}" fill="url(#shine)" d="{d}"/></g>')
    return o


SHINE = ('<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="160" y2="0">'
         '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#f6c9ff" stop-opacity=".9"/>'
         '<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
         '<animateTransform attributeName="gradientTransform" type="translate" values="-200 0;-200 0;700 0" keyTimes="0;.55;1" dur="4.5s" repeatCount="indefinite"/></linearGradient>')


def niza_glows(w, h, n=3):
    cols = [LILAS, PITAYA, PESSEGO]
    o = ""
    for i in range(n):
        cx, cy = w * (.2 + .3 * i), h * (.3 + .25 * (i % 2))
        o += (f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w*.22:.0f}" ry="{h*.35:.0f}" fill="{cols[i % 3]}" opacity=".22" filter="url(#nblur)">'
              f'<animate attributeName="cx" values="{cx:.0f};{cx + w*.12:.0f};{cx:.0f}" dur="{12 + i*3}s" repeatCount="indefinite"/>'
              f'<animate attributeName="cy" values="{cy:.0f};{cy + h*.15:.0f};{cy:.0f}" dur="{9 + i*2}s" repeatCount="indefinite"/></ellipse>')
    return o


def sparkles(w, h, n):
    o = ""
    for _ in range(n):
        x, y, r = random.randint(20, w - 20), random.randint(20, h - 20), random.uniform(3, 7)
        d = f"M0 {-r} Q0 0 {r} 0 Q0 0 0 {r} Q0 0 {-r} 0 Q0 0 0 {-r}Z"
        o += (f'<path transform="translate({x},{y})" d="{d}" fill="#fff" opacity="0">'
              f'<animate attributeName="opacity" values="0;.9;0" dur="{random.uniform(2, 4):.1f}s" '
              f'begin="{-random.uniform(0, 4):.1f}s" repeatCount="indefinite"/></path>')
    return o


def light_sweep(w, h, dur=6):
    return (f'<rect x="-300" y="-50" width="160" height="{h+100}" fill="url(#beam)" transform="skewX(-20)">'
            f'<animate attributeName="x" values="-300;-300;{w+300}" keyTimes="0;.5;1" dur="{dur}s" repeatCount="indefinite"/></rect>')


BEAM = ('<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
NBLUR = '<filter id="nblur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>'


def shopee_icon(size=50):
    k = size / 50
    return (f'<g transform="scale({k:.3f})"><rect x="-25" y="-25" width="50" height="50" rx="13" fill="{SHOPEE}"/>'
            f'<path transform="scale(1.4) translate(-12,-12)" fill="#fff" d="{logo_path("shopee")}"/></g>')


def nizashop_hero(mobile=False):
    W, H = (W_MOBILE, 400) if mobile else (1200, 420)
    o = (f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="26"/></clipPath><g clip-path="url(#cl)">'
         f'<image href="{b64(NIZA_DIR / "fundos" / "faixa-hero.jpg")}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
         f'{niza_glows(W, H)}{sparkles(W, H, 16 if mobile else 26)}{light_sweep(W, H)}</g>')
    if mobile:
        o += f'<g transform="translate({(W - 643*.58)/2:.0f},96) scale(.58)">{niza_logo(.6)}</g>'
        pw, py = 360, 290
    else:
        o += f'<g transform="translate(290,72) scale(.96)">{niza_logo(.6)}</g>'
        pw, py = 380, 312
    o += (f'<g opacity="1">{reveal(2.2, .6)}<rect x="{W/2-pw/2}" y="{py}" width="{pw}" height="44" rx="22" fill="{LILAS}"/>'
          f'<text x="{W/2}" y="{py+29}" text-anchor="middle" {SANS} font-size="18" font-weight="700" fill="{AMEIXA}">{esc(NIZA_CEO)}</text></g>')
    o += f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="26" fill="none" stroke="url(#nb)" stroke-width="2"/>'
    defs = SHINE + BEAM + NBLUR + niza_border()
    (NIZA_DIR / mname("abertura.svg", mobile)).write_text(svg(W, H, o, defs), encoding="utf-8")


def niza_border(gid="nb"):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PITAYA}"/>'
            f'<stop offset=".5" stop-color="{LILAS}"/><stop offset="1" stop-color="{PESSEGO}"/>'
            f'<animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="7s" repeatCount="indefinite"/></linearGradient>')


def niza_icon(kind, c):
    if kind == "estrela":
        pts = " ".join(f"{math.cos(math.pi/2 + k*math.pi/5)*(18 if k % 2 == 0 else 8):.1f},{-math.sin(math.pi/2 + k*math.pi/5)*(18 if k % 2 == 0 else 8):.1f}" for k in range(10))
        return f'<polygon points="{pts}" fill="{c}"/>'
    if kind == "etiqueta":
        return (f'<path d="M-16 -4 L-4 -16 H14 V2 L2 14 Z" fill="{c}" transform="rotate(0)"/>'
                f'<circle cx="7" cy="-9" r="3" fill="{AMEIXA}"/>')
    if kind == "raio":
        return f'<polygon points="4,-18 -12,3 -1,3 -5,18 12,-4 1,-4" fill="{c}"/>'
    return f'<path d="M0 14 C-22 0 -14 -18 0 -8 C14 -18 22 0 0 14Z" fill="{c}"/>'


def nizashop_pilares(mobile=False):
    """Computador: 4 cards lado a lado. Celular: 4 cards horizontais empilhados."""
    if mobile:
        W, cw, ch, g = W_MOBILE, W_MOBILE - 32, 104, 14
        H = 4 * ch + 3 * g + 40
    else:
        W, cw, ch, g = 1200, 270, 190, 20
        H = ch + 40
    x0 = 16 if mobile else (W - (4 * cw + 3 * g)) / 2
    o = ""
    for i, (ic, t, sub) in enumerate(NIZA_PILARES):
        a = i * .25
        icon = (f'<circle r="30" fill="{LAVANDA}" opacity=".1"/>'
                f'<g><animateTransform attributeName="transform" type="scale" values="1;1.15;1" dur="2s" begin="{-a:.2f}s" repeatCount="indefinite"/>'
                f'{niza_icon(ic, PITAYA if i % 2 == 0 else PESSEGO)}</g>')
        card = (f'<rect width="{cw}" height="{ch}" rx="22" fill="{AMEIXA}"/>'
                f'<rect width="{cw}" height="{ch}" rx="22" fill="url(#pg{i})"/>'
                f'<rect width="{cw}" height="{ch}" rx="22" fill="none" stroke="{LILAS}" stroke-opacity=".35"/>')
        if mobile:
            card += (f'<g transform="translate(52,{ch/2})">{icon}</g>'
                     f'<text x="100" y="{ch/2 - 4}" {SANS} font-size="23" font-weight="800" fill="#fff">{esc(t)}</text>'
                     f'<text x="100" y="{ch/2 + 22}" {SANS} font-size="15.5" fill="{LILAS}">{esc(sub)}</text>')
            x, y = x0, 20 + i * (ch + g)
        else:
            card += (f'<g transform="translate(52,58)">{icon}</g>'
                     f'<text x="26" y="128" {SANS} font-size="24" font-weight="800" fill="#fff">{esc(t)}</text>'
                     f'<text x="26" y="158" {SANS} font-size="15" fill="{LILAS}">{esc(sub)}</text>')
            x, y = x0 + i * (cw + g), 20
        o += f'<g transform="translate({x:.0f},{y})">{bob(card, 5, 2.4 + i * .3)}</g>'
    defs = "".join(f'<radialGradient id="pg{i}" cx=".2" cy=".2" r=".9"><stop offset="0" stop-color="{c}" stop-opacity=".35"/>'
                   f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
                   for i, c in enumerate([LILAS, PITAYA, LILAS, PESSEGO]))
    (NIZA_DIR / mname("pilares.svg", mobile)).write_text(svg(W, H, o, defs), encoding="utf-8")


def nizashop_paleta(mobile=False):
    n, g = len(NIZA_PALETA), 16
    cols = 3 if mobile else n
    W = W_MOBILE if mobile else 1200
    cw = (W - 40 - (cols - 1) * g) / cols
    rows = math.ceil(n / cols)
    H = 40 + rows * 150 + (rows - 1) * g
    o = ""
    for i, (nome, c) in enumerate(NIZA_PALETA):
        r, k = divmod(i, cols)
        x, y = 20 + k * (cw + g), 20 + r * (150 + g)
        dark = c in (AMEIXA, NOITE, PITAYA)
        tc = "#fff" if dark else AMEIXA
        o += (f'<g transform="translate({x:.0f},{y})"><g opacity="1">{reveal(.2 + i * .15, .4)}'
              f'<rect width="{cw:.0f}" height="150" rx="20" fill="{c}" stroke="{LILAS}" stroke-opacity=".4">'
              f'<animate attributeName="height" values="150;150;140;150" keyTimes="0;.7;.85;1" dur="4s" begin="{i*.3:.1f}s" repeatCount="indefinite"/></rect>'
              f'<text x="16" y="104" {SANS} font-size="{17 if mobile else 20}" font-weight="800" fill="{tc}">{esc(nome)}</text>'
              f'<text x="16" y="130" {MONO} font-size="{12.5 if mobile else 14}" fill="{tc}" opacity=".8">{c}</text></g></g>')
    (NIZA_DIR / mname("paleta.svg", mobile)).write_text(svg(W, H, o), encoding="utf-8")


# CONTEÚDO: ferramentas usadas para criar a loja (logo em scripts/logos/)
NIZA_FEITA_COM = [("Claude", "claude"), ("Gemini", "googlegemini"), ("TryBloom", "trybloom")]
GEM = ('<linearGradient id="gem" gradientUnits="userSpaceOnUse" x1="3" y1="3" x2="21" y2="21">'
       '<stop offset="0" stop-color="#439ddf"/><stop offset=".3" stop-color="#4f87ed"/>'
       '<stop offset=".6" stop-color="#9476c5"/><stop offset=".85" stop-color="#bc688e"/>'
       '<stop offset="1" stop-color="#d6645d"/></linearGradient>')


def mini_logo(icon, size=32):
    """Logo oficial pequeno e animado, centrado em (0,0)."""
    if icon == "claude":
        k = size / 24
        return (f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="12s" repeatCount="indefinite"/>'
                f'<path transform="scale({k:.3f}) translate(-12,-12)" fill="{OR}" d="{logo_path("claude")}"/></g>')
    return f'<g transform="scale({size/50:.3f})">{tool_icon(icon, "#fff")}</g>'


def nizashop_card(mobile=False):
    """Card de destaque no perfil (assets/nizashop-destaque.svg e -m.svg)."""
    W, H = (W_MOBILE, 560) if mobile else (1200, 370)
    o = (f'<clipPath id="cl"><rect width="{W}" height="{H}" rx="22"/></clipPath><g clip-path="url(#cl)">'
         f'<image href="{b64(NIZA_DIR / "fundos" / "faixa-card.jpg")}" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
         f'{niza_glows(W, H)}{sparkles(W, H, 20)}{light_sweep(W, H, 7)}</g>')
    btn = (f'<rect width="196" height="46" rx="23" fill="{LILAS}"/>'
           f'<text x="98" y="29" text-anchor="middle" {SANS} font-size="18" font-weight="800" fill="{AMEIXA}">conhecer a loja →</text>')
    pill = (f'<rect width="232" height="40" rx="20" fill="{PITAYA}"/>'
            f'<text x="116" y="26" text-anchor="middle" {SANS} font-size="17" font-weight="800" fill="#fff" letter-spacing=".5">FUNDADOR &amp; CEO</text>')
    vend = f'<g>{shopee_icon(30)}</g><text x="26" y="6" {SANS} font-size="17" font-weight="700" fill="#fff">Vendedor na Shopee</text>'
    if mobile:
        o += f'<g transform="translate({(W - 643*.58)/2:.0f},30) scale(.58)">{niza_logo(.4)}</g>'
        o += f'<g transform="translate({(W - 232)/2:.0f},164)">{pill}</g>'
        o += f'<g transform="translate({W/2 - 98:.0f},236)">{vend}</g>'
        fy = 270
        o += (f'<rect x="20" y="{fy}" width="{W-40}" height="190" rx="20" fill="{NOITE}" fill-opacity=".55" stroke="{LILAS}" stroke-opacity=".3"/>'
              f'<text x="{W/2}" y="{fy+34}" text-anchor="middle" {SANS} font-size="16" font-weight="600" fill="{LILAS}">loja criada com</text>')
        for i, (nome, icon) in enumerate(NIZA_FEITA_COM):
            cw_ = W - 88
            chip = (f'<rect x="0" y="-22" width="{cw_}" height="44" rx="22" fill="#ffffff" fill-opacity=".08" stroke="#ffffff" stroke-opacity=".18"/>'
                    f'<g transform="translate(28,0)">{mini_logo(icon, 28)}</g>'
                    f'<text x="54" y="7" {SANS} font-size="19" font-weight="700" fill="#fff">{esc(nome)}</text>')
            o += f'<g transform="translate(44,{fy + 62 + i*46})"><g opacity="1">{reveal(1.2 + i*.35, .5)}{chip}</g></g>'
        o += f'<g transform="translate({(W - 196)/2:.0f},{H - 76})">{bob(btn, 3, 1.6)}</g>'
    else:
        o += f'<g transform="translate(44,36) scale(.62)">{niza_logo(.4)}</g>'
        o += f'<g transform="translate(64,196)">{pill}</g>'
        o += f'<g transform="translate({W-250},196)">{bob(btn, 3, 1.6)}</g>'
        o += f'<g transform="translate({W-152},96)">{bob(shopee_icon(64), 8, 1.4)}</g>'
        fy = 266
        o += (f'<rect x="44" y="{fy}" width="{W-88}" height="72" rx="20" fill="{NOITE}" fill-opacity=".55" stroke="{LILAS}" stroke-opacity=".3"/>'
              f'<text x="74" y="{fy+43}" {SANS} font-size="17" font-weight="600" fill="{LILAS}">loja criada com</text>')
        x = 236
        for i, (nome, icon) in enumerate(NIZA_FEITA_COM):
            chip = (f'<rect x="-8" y="-24" width="{len(nome)*11.5 + 68:.0f}" height="48" rx="24" fill="#ffffff" fill-opacity=".08" stroke="#ffffff" stroke-opacity=".18"/>'
                    f'<g transform="translate(20,0)">{mini_logo(icon, 30)}</g>'
                    f'<text x="46" y="7" {SANS} font-size="19" font-weight="700" fill="#fff">{esc(nome)}</text>')
            o += f'<g transform="translate({x},{fy+36})"><g opacity="1">{reveal(1.2 + i*.35, .5)}{chip}</g></g>'
            x += len(nome) * 11.5 + 88
        o += f'<g transform="translate({W - 258},{fy + 36})">{vend}</g>'
    o += f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="22" fill="none" stroke="url(#nb)" stroke-width="2.5"/>'
    save(mname("nizashop-destaque.svg", mobile), svg(W, H, o, SHINE + BEAM + NBLUR + GEM + niza_border()))


def data_uri(path, size=None, fmt="JPEG", quality=72, crop=None):
    """Imagem redimensionada embutida como data URI (para usar dentro dos SVGs)."""
    import base64, io
    from PIL import Image
    im = Image.open(path)
    if crop:
        w0, h0 = im.size
        im = im.crop(tuple(int(v * d) for v, d in zip(crop, (w0, h0, w0, h0))))
    if size:
        im = im.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG":
        im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        im.save(buf, fmt, optimize=True)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


# CONTEÚDO do painel bento
BENTO_CAMPANHAS = [("10.10", "#b8a4e3"), ("11.11", "#7d9bff"), ("12.12", "#e0a3c4"), ("Black Friday", "#ffffff"), ("Natal", "#6ee7b7")]
BENTO_AVISOS = [
    ("pedido", "Novo pedido recebido", PITAYA),
    ("coracao", "Pedido embalado com carinho", PESSEGO),
    ("entrega", "Saiu para entrega", LILAS),
    ("estrela", "Nova avaliação ★★★★★", "#ffd166"),
]


def bento_tile(x, y, w, h, label, inner, i, glow=LILAS):
    return (f'<g transform="translate({x},{y})"><g opacity="1">{reveal(.15 + i * .18, .5)}'
            f'<rect width="{w}" height="{h}" rx="24" fill="{AMEIXA}"/>'
            f'<rect width="{w}" height="{h}" rx="24" fill="url(#tg{i})"/>'
            f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="24" fill="none" stroke="{LILAS}" stroke-opacity=".28" stroke-width="1.5"/>'
            f'<text x="24" y="38" {SANS} font-size="12.5" font-weight="800" fill="{LILAS}" letter-spacing="1.6">{esc(label)}</text>'
            f'{inner}</g></g>')


def bento_phone(w, h):
    pw, ph = 214, 440
    px, py = (w - pw) / 2, 58
    sx, sy, sw, sh = px + 9, py + 9, pw - 18, ph - 18
    n_path, _ = niza_parts()
    o = (f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="36" fill="#0c0912" stroke="#3b2d52" stroke-width="3"/>'
         f'<clipPath id="scr"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="28"/></clipPath><g clip-path="url(#scr)">'
         f'<image href="{data_uri(NIZA_DIR / "fundos" / "plano-de-fundo-05-ameixa-com-brilho.jpg", (int(sw), int(sh)), crop=(.27, 0, .73, .46))}" '
         f'x="{sx}" y="{sy}" width="{sw}" height="{sh}" preserveAspectRatio="xMidYMid slice"/>')
    # cabeçalho da loja
    hx, hy = sx + 14, sy + 38
    o += (f'<g transform="translate({hx},{hy}) scale(.56)"><rect width="64" height="64" rx="18" fill="{LAVANDA}"/>'
          f'<path d="{n_path}" fill="{AMEIXA}" stroke="{AMEIXA}" stroke-width="2" stroke-linejoin="round"/>'
          f'<circle cx="42.5" cy="17" r="4.2" fill="{PITAYA}"/></g>'
          f'<text x="{hx+46}" y="{hy+17}" {SANS} font-size="15" font-weight="800" fill="#fff">Niza<tspan font-weight="400">shop</tspan></text>'
          f'<text x="{hx+46}" y="{hy+33}" {SANS} font-size="10.5" fill="{LILAS}">loja na Shopee</text>')
    o += (f'<g transform="translate({sx+sw-62},{hy+8})"><rect width="50" height="22" rx="11" fill="{PITAYA}">'
          f'<animate attributeName="opacity" values="1;.65;1" dur="1.6s" repeatCount="indefinite"/></rect>'
          f'<text x="25" y="15" text-anchor="middle" {SANS} font-size="10.5" font-weight="800" fill="#fff">Seguir</text></g>')
    o += f'<g transform="translate({sx+sw/2},{sy+10})"><rect x="-30" y="-1" width="60" height="16" rx="8" fill="#0c0912"/></g>'
    # banners rolando em "swipes"
    banners = sorted((NIZA_DIR / "banners").glob("*.jpg"))
    bw = sw - 24
    bh = bw / 2
    gap = 12
    step = bh + gap
    top = hy + 52
    defs_imgs = ""
    col = ""
    for k in range(len(banners) * 2):
        f = banners[k % len(banners)]
        if k < len(banners):
            defs_imgs += f'<image id="pb{k}" href="{data_uri(f, (int(bw*2), int(bh*2)))}" width="{bw:.1f}" height="{bh:.1f}" clip-path="url(#pbc)"/>'
        col += f'<use href="#pb{k % len(banners)}" x="{sx+12}" y="{top + k*step:.1f}"/>'
    n = len(banners)
    T = n * 2.0
    kt, vals = [], []
    for k in range(n):
        kt += [k * 2.0 / T, (k * 2.0 + 1.4) / T]
        vals += [f"0 {-k*step:.1f}", f"0 {-k*step:.1f}"]
    kt.append(1)
    vals.append(f"0 {-n*step:.1f}")
    splines = ";".join(["0 0 1 1", ".6 0 .2 1"] * n)
    o += (f'<clipPath id="feed"><rect x="{sx}" y="{top-4}" width="{sw}" height="{sy+sh-top+4}"/></clipPath>'
          f'<g clip-path="url(#feed)"><g><animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" '
          f'calcMode="spline" keyTimes="{";".join(f"{t:.4f}" for t in kt)}" values="{";".join(vals)}" keySplines="{splines}"/>{col}</g></g>')
    o += '</g>'
    defs = f'<clipPath id="pbc"><rect width="{bw:.1f}" height="{bh:.1f}" rx="10"/></clipPath>{defs_imgs}'
    return o, defs


def bento_calendario(w, h):
    T = len(BENTO_CAMPANHAS) * 2.4
    cx, cy = w / 2, 150
    o = (f'<rect x="28" y="62" width="{w-56}" height="150" rx="18" fill="{NOITE}" fill-opacity=".7"/>'
         f'<line x1="28" y1="{cy-13}" x2="{w-28}" y2="{cy-13}" stroke="{AMEIXA}" stroke-width="3"/>')
    dots = ""
    for i, (txt, c) in enumerate(BENTO_CAMPANHAS):
        a, b = i / len(BENTO_CAMPANHAS), (i + 1) / len(BENTO_CAMPANHAS)
        e = .25 / T
        if i == 0:
            kt, vals = f"0;{b-e:.4f};{b:.4f};{1-e:.4f};1", "1 1;1 1;1 0;1 0;1 1"
        else:
            kt, vals = f"0;{a:.4f};{a+e:.4f};{b-e:.4f};{b:.4f};1", "1 0;1 0;1 1;1 1;1 0;1 0"
        fs = min(92 if len(txt) <= 5 else 62, (w - 80) / (len(txt) * .56))
        base = "" if i == 0 else ' transform="scale(1,0)"'
        o += (f'<g transform="translate({cx},{cy-13})"><g{base}><animateTransform attributeName="transform" type="scale" '
              f'dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/>'
              f'<text y="{fs*.36:.0f}" text-anchor="middle" {SANS} font-size="{fs:.0f}" font-weight="900" fill="{c}" letter-spacing="-2">{esc(txt)}</text></g></g>')
        dots += (f'<circle cx="{cx - 48 + i*24}" cy="236" r="5" fill="{c}" opacity=".3">'
                 f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                 f'keyTimes="0;{a:.4f};{b:.4f}" values=".3;1;.3"/></circle>')
    return o + dots


def bento_vendedor(w, h):
    """Vitrine de produtos que se acendem em sequência + selo 'Vendedor na Shopee'."""
    o = f'<g transform="translate({w-44},40)">{bob(shopee_icon(34), 3, 1.6)}</g>'
    cols, gap, x0, y0 = 3, 10, 24, 60
    cw = (w - 2 * x0 - (cols - 1) * gap) / cols
    ch = 60
    T = 6 * .6 + 1.2
    for k in range(6):
        r, c = divmod(k, cols)
        x, y = x0 + c * (cw + gap), y0 + r * (ch + gap)
        a = k * .6 / T
        o += (f'<g transform="translate({x:.1f},{y})">'
              f'<rect width="{cw:.1f}" height="{ch}" rx="12" fill="#ffffff" fill-opacity=".07" stroke="#ffffff" stroke-opacity=".14">'
              f'<animate attributeName="stroke" dur="{T:.1f}s" repeatCount="indefinite" keyTimes="0;{a:.3f};{a+.05:.3f};{a+.2:.3f};1" '
              f'values="#ffffff;#ffffff;{SHOPEE};#ffffff;#ffffff"/>'
              f'<animate attributeName="stroke-opacity" dur="{T:.1f}s" repeatCount="indefinite" keyTimes="0;{a:.3f};{a+.05:.3f};{a+.2:.3f};1" '
              f'values=".14;.14;1;.14;.14"/></rect>'
              f'<rect x="8" y="8" width="{ch-16}" height="{ch-16}" rx="8" fill="{[LILAS, PESSEGO, PITAYA][k % 3]}" fill-opacity=".55"/>'
              f'<rect x="{ch}" y="16" width="{cw-ch-10:.1f}" height="7" rx="3.5" fill="#ffffff" fill-opacity=".45"/>'
              f'<rect x="{ch}" y="31" width="{(cw-ch-10)*.6:.1f}" height="7" rx="3.5" fill="{SHOPEE}" fill-opacity=".8"/></g>')
    o += (f'<rect x="{x0}" y="{h-50}" width="{w-2*x0}" height="30" rx="15" fill="#fff" fill-opacity=".08" stroke="{LILAS}" stroke-opacity=".3"/>'
          f'<circle cx="{x0+18}" cy="{h-35}" r="5" fill="#6ee7b7"><animate attributeName="opacity" values="1;.3;1" dur="1.2s" repeatCount="indefinite"/></circle>'
          f'<text x="{x0+32}" y="{h-30}" {SANS} font-size="13.5" font-weight="700" fill="#fff">Vendedor na Shopee</text>')
    return o


def bento_cupom(w, h):
    tw, th = w - 52, 118
    x0, y0 = 26, 70
    cut = tw * .36
    ticket = (f'<rect width="{tw}" height="{th}" rx="16" fill="{LAVANDA}"/>'
              f'<rect width="{cut:.0f}" height="{th}" rx="16" fill="{PITAYA}"/><rect x="{cut-16:.0f}" width="16" height="{th}" fill="{PITAYA}"/>'
              f'<circle cx="{cut:.0f}" cy="0" r="11" fill="{AMEIXA}"/><circle cx="{cut:.0f}" cy="{th}" r="11" fill="{AMEIXA}"/>'
              f'<line x1="{cut:.0f}" y1="16" x2="{cut:.0f}" y2="{th-16}" stroke="{AMEIXA}" stroke-width="2.5" stroke-dasharray="5 6">'
              f'<animate attributeName="stroke-dashoffset" from="0" to="-22" dur="1.2s" repeatCount="indefinite"/></line>'
              f'<text x="{cut/2:.0f}" y="{th/2+22}" text-anchor="middle" {SANS} font-size="62" font-weight="900" fill="#fff">%</text>'
              f'<text x="{cut + 16:.0f}" y="{th/2-6}" {SANS} font-size="19" font-weight="900" fill="{AMEIXA}">Cupons</text>'
              f'<text x="{cut + 16:.0f}" y="{th/2+16}" {SANS} font-size="19" font-weight="900" fill="{AMEIXA}">da loja</text>'
              f'<rect x="0" y="0" width="{tw}" height="{th}" rx="16" fill="url(#cshine)"/>')
    o = (f'<g transform="translate({x0 + tw/2},{y0 + th/2})"><g>'
         f'<animateTransform attributeName="transform" type="rotate" values="-4;3;-4" dur="4s" repeatCount="indefinite" '
         f'calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>'
         f'<g transform="translate({-tw/2},{-th/2})">{bob(ticket, 4, 2.2)}</g></g></g>')
    o += f'<text x="26" y="{h-26}" {SANS} font-size="13.5" fill="{LILAS}">pegue o seu antes de comprar</text>'
    for k, (dx, dy, fs) in enumerate(((w - 46, 46, 18), (w - 70, 64, 12), (w - 34, 78, 13))):
        o += (f'<text x="{dx}" y="{dy}" {SANS} font-size="{fs}" font-weight="900" fill="{PESSEGO}">%'
              f'<animate attributeName="opacity" values="0;1;0" dur="2.4s" begin="{-k*.8:.1f}s" repeatCount="indefinite"/></text>')
    return o


def bento_avisos(w, h):
    T, n = 8.0, len(BENTO_AVISOS)
    slot = 58
    o = f'<clipPath id="nt"><rect x="0" y="52" width="{w}" height="{h-60}"/></clipPath><g clip-path="url(#nt)">'
    for i, (ic, txt, c) in enumerate(BENTO_AVISOS):
        if ic == "pedido":
            glyph = '<path d="M-5 0H5M0 -5V5" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>'
        elif ic == "coracao":
            glyph = f'<g transform="scale(.5)">{niza_icon("coracao", AMEIXA)}</g>'
        elif ic == "entrega":
            glyph = f'<path d="M-6 0H5M1 -5L6 0L1 5" fill="none" stroke="{AMEIXA}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            glyph = f'<g transform="scale(.45)">{niza_icon("estrela", AMEIXA)}</g>'
        toast = (f'<rect width="{w-48}" height="48" rx="16" fill="#ffffff" fill-opacity=".09" stroke="#ffffff" stroke-opacity=".16"/>'
                 f'<g transform="translate(26,24)"><circle r="15" fill="{c}"/>{glyph}</g>'
                 f'<text x="54" y="21" {SANS} font-size="14.5" font-weight="700" fill="#fff">{esc(txt)}</text>'
                 f'<text x="54" y="38" {SANS} font-size="11.5" fill="{LILAS}">NizaShop · agora</text>')
        y0 = 62
        vals = [f"24 {y0-30}", f"24 {y0}", f"24 {y0}", f"24 {y0+slot}", f"24 {y0+slot}", f"24 {y0+2*slot}", f"24 {y0+2*slot}", f"24 {y0+3*slot}", f"24 {y0+3*slot}"]
        kts = [0, .4, 2, 2.4, 4, 4.4, 6, 6.4, T]
        ops = "0;1;1;1;1;1;1;0;0"
        kt = ";".join(f"{t/T:.4f}" for t in kts)
        begin = -((T - i * 2) % T)
        base_y = y0 + ((n - 1 - i) % n) * slot
        o += (f'<g transform="translate(24,{base_y})"><animateTransform attributeName="transform" type="translate" dur="{T}s" begin="{begin}s" '
              f'repeatCount="indefinite" keyTimes="{kt}" values="{";".join(vals)}" calcMode="spline" '
              f'keySplines="{";".join([".3 0 .2 1", "0 0 1 1"] * 4)}"/>'
              f'<animate attributeName="opacity" dur="{T}s" begin="{begin}s" repeatCount="indefinite" keyTimes="{kt}" values="{ops}"/>'
              f'{toast}</g>')
    return o + '</g>'


def nizashop_bento(mobile=False):
    """Painel bento animado da loja (assets/nizashop-bento.svg e -m.svg)."""
    P, G = 20, 16
    if mobile:
        W = W_MOBILE
        tw = W - 2 * P
        tiles = [("LOJA NA SHOPEE", 500, "phone"), ("CALENDÁRIO DE CAMPANHAS", 262, "cal"),
                 ("VENDEDOR NA SHOPEE", 262, "vend"), ("CUPONS", 230, "cup"), ("NOTIFICAÇÕES", 262, "av")]
        H = P * 2 + sum(t[1] for t in tiles) + G * (len(tiles) - 1)
        y = P
        o = f'<rect width="{W}" height="{H}" rx="28" fill="{NOITE}"/>{niza_glows(W, H)}'
        phone_defs = ""
        for i, (label, th, kind) in enumerate(tiles):
            if kind == "phone":
                inner, phone_defs = bento_phone(tw, th)
            else:
                inner = {"cal": bento_calendario, "vend": bento_vendedor, "cup": bento_cupom, "av": bento_avisos}[kind](tw, th)
            o += bento_tile(P, y, tw, th, label, inner, i)
            y += th + G
    else:
        W, H = 1200, 560
        pw = 300
        rx0 = P + pw + G
        rw = W - P - rx0
        th = (H - 2 * P - G) / 2
        cal_w, sel_w = 480, 300
        phone, phone_defs = bento_phone(pw, H - 2 * P)
        o = (f'<rect width="{W}" height="{H}" rx="28" fill="{NOITE}"/>{niza_glows(W, H)}'
             + bento_tile(P, P, pw, H - 2 * P, "LOJA NA SHOPEE", phone, 0)
             + bento_tile(rx0, P, cal_w, th, "CALENDÁRIO DE CAMPANHAS", bento_calendario(cal_w, th), 1)
             + bento_tile(rx0 + cal_w + G, P, rw - cal_w - G, th, "VENDEDOR NA SHOPEE", bento_vendedor(rw - cal_w - G, th), 2)
             + bento_tile(rx0, P + th + G, sel_w, th, "CUPONS", bento_cupom(sel_w, th), 3)
             + bento_tile(rx0 + sel_w + G, P + th + G, rw - sel_w - G, th, "NOTIFICAÇÕES", bento_avisos(rw - sel_w - G, th), 4))
    o += f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="28" fill="none" stroke="url(#nb)" stroke-width="2.5"/>'
    tgs = "".join(f'<radialGradient id="tg{i}" cx="{cx}" cy="{cy}" r=".9"><stop offset="0" stop-color="{c}" stop-opacity=".28"/>'
                  f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
                  for i, (c, cx, cy) in enumerate([(LILAS, .5, .9), (PITAYA, .1, .1), (SHOPEE, .9, .1), (PESSEGO, .5, .5), (LILAS, .9, .9)]))
    defs = (tgs + phone_defs + NBLUR + niza_border()
            + '<linearGradient id="cshine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="120" y2="0">'
              '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".45"/>'
              '<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
              '<animateTransform attributeName="gradientTransform" type="translate" values="-160 0;-160 0;420 0" keyTimes="0;.6;1" dur="3.5s" repeatCount="indefinite"/></linearGradient>')
    save(mname("nizashop-bento.svg", mobile), svg(W, H, o, defs))


def tl(pairs, T):
    """Linha do tempo [(segundo, valor), ...] -> (keyTimes, values) para animações SMIL."""
    kt = ";".join(f"{min(t / T, 1):.4f}" for t, _ in pairs)
    return kt, ";".join(str(v) for _, v in pairs)


def anim(attr, pairs, T, kind=None, extra=""):
    kt, vals = tl(pairs, T)
    if kind:
        return (f'<animateTransform attributeName="transform" type="{kind}" dur="{T}s" repeatCount="indefinite" '
                f'keyTimes="{kt}" values="{vals}" {extra}/>')
    return f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}" {extra}/>'


# CONTEÚDO do pitch deck
DECK = {
    "titulo": "NizaShop · Apresentação institucional",
    "capa": ("Comprar bem, ", "com carinho."),
    "missao": [("Levar produtos ", "escolhidos a dedo,"), ("com preço justo e entrega rápida,", ""), ("para quem compra na Shopee.", "")],
    # versão celular (linhas mais curtas)
    "missao_m": [("Levar produtos", ""), ("", "escolhidos a dedo,"), ("com preço justo", ""), ("e entrega rápida,", ""),
                 ("para quem compra", ""), ("na Shopee.", "")],
    "titulo_m": "NizaShop · Institucional",
    "valor": [
        ("estrela", "Curadoria", ("seleção cuidadosa de cada", "produto do catálogo")),
        ("etiqueta", "Preço justo", ("ofertas, cupons e campanhas", "durante todo o ano")),
        ("coracao", "Experiência", ("embalagem própria e", "atendimento atencioso")),
    ],
    "ciclo_texto": ("A IA ajuda na curadoria e no", "atendimento; os pedidos geram", "avaliações e o retorno melhora a loja."),
    "ciclo": ["Curadoria", "Vitrine", "Pedidos", "Avaliações", "Melhorias"],
    "fases": [
        ("Identidade e lançamento", "marca, logo e kit de embalagem", "concluída"),
        ("Campanhas sazonais", "10.10, 11.11, 12.12 e Natal", "em andamento"),
        ("Escala com IA", "catálogo e atendimento com IA", ""),
        ("Novos canais", "expandir além da Shopee", ""),
    ],
}
PAPER, INK2, LINE = "#faf8fd", "#6b5a84", "#e9e2f4"


def niza_static(word_fill=AMEIXA, box=AMEIXA, ink="#ffffff"):
    """Logo completo estático (viewBox 643x198)."""
    n_path, words = niza_parts()
    o = (f'<g transform="translate(24,24) scale(2.34375)"><rect width="64" height="64" rx="18" fill="{box}"/>'
         f'<path d="{n_path}" fill="{ink}" stroke="{ink}" stroke-width="2" stroke-linejoin="round"/>'
         f'<circle cx="42.5" cy="17" r="4.2" fill="{PITAYA}"/></g>')
    return o + "".join(f'<path transform="{tr}" fill="{word_fill}" d="{d}"/>' for tr, d in words)


def nizashop_deck(mobile=False):
    """Apresentação institucional que passa sozinha (assets/nizashop-deck.svg e -m.svg)."""
    S, N = 4.5, 5
    T = S * N
    W, H = (W_MOBILE, 700) if mobile else (1200, 470)
    LX = 24 if mobile else 72          # margem esquerda do conteúdo
    TOPBAR = 52 if mobile else 56

    def span(i):
        return i * S, (i + 1) * S

    def slide_win(i):
        s0, e = span(i)
        if i == 0:
            op = [(0, 0), (.45, 1), (e - .35, 1), (e, 0), (T, 0)]
            tr = [(0, "30 0"), (.45, "0 0"), (e - .35, "0 0"), (e, "-30 0"), (T, "-30 0")]
        elif e >= T:
            op = [(0, 0), (s0, 0), (s0 + .45, 1), (T - .35, 1), (T, 0)]
            tr = [(0, "30 0"), (s0, "30 0"), (s0 + .45, "0 0"), (T - .35, "0 0"), (T, "-30 0")]
        else:
            op = [(0, 0), (s0, 0), (s0 + .45, 1), (e - .35, 1), (e, 0), (T, 0)]
            tr = [(0, "30 0"), (s0, "30 0"), (s0 + .45, "0 0"), (e - .35, "0 0"), (e, "-30 0"), (T, "-30 0")]
        sp = 'calcMode="spline" keySplines="' + ";".join([".2 0 .2 1"] * (len(tr) - 1)) + '"'
        return anim("opacity", op, T), anim(None, tr, T, "translate", sp)

    def appear(i, d, dur=.45, rise=0):
        """Elemento que aparece d segundos depois do início do slide i (e some quando o slide acaba)."""
        s0, e = span(i)
        st = s0 + d
        if e >= T:
            op = [(0, 0), (st, 0), (st + dur, 1), (T, 1)]
        else:
            op = [(0, 0), (st, 0), (st + dur, 1), (e, 1), (min(e + .01, T), 0), (T, 0)]
        out = anim("opacity", op, T)
        if rise:
            pts = [(t, f"0 {rise if v == 0 else 0}") for t, v in op]
            out += anim(None, pts, T, "translate")
        return out

    def label(txt):
        y = 92 if mobile else 104
        return f'<text x="{LX}" y="{y}" {SANS} font-size="13" font-weight="800" fill="{PITAYA}" letter-spacing="2.2">{esc(txt)}</text>'

    def italic(txt):
        return f'<tspan {SERIF} font-style="italic" font-weight="400" fill="{PITAYA}">{esc(txt)}</tspan>'

    n_path, _ = niza_parts()
    symbol = (f'<rect width="64" height="64" rx="18" fill="{AMEIXA}"/>'
              f'<path d="{n_path}" fill="#fff" stroke="#fff" stroke-width="2" stroke-linejoin="round"/>'
              f'<circle cx="42.5" cy="17" r="4.2" fill="{PITAYA}"/>')
    slides = []

    # ---------- 1. capa ----------
    c = label("APRESENTAÇÃO INSTITUCIONAL")
    if mobile:
        c += f'<g transform="translate(14,106) scale(.5)">{niza_static()}</g>'
        c += f'<text x="{LX}" y="262" {SANS} font-size="32" font-weight="900" fill="{AMEIXA}" letter-spacing="-1">{esc(DECK["capa"][0].strip())}</text>'
        c += f'<text x="{LX}" y="302" {SERIF} font-size="36" font-style="italic" fill="{PITAYA}">{esc(DECK["capa"][1])}</text>'
        pill_y, deco_xy, deco_k = 326, (W / 2, 520), .72
    else:
        c += f'<g transform="translate(62,124) scale(.62)">{niza_static()}</g>'
        c += (f'<text x="{LX}" y="312" {SANS} font-size="40" font-weight="900" fill="{AMEIXA}" letter-spacing="-1">{esc(DECK["capa"][0])}'
              f'{italic(DECK["capa"][1])}</text>')
        pill_y, deco_xy, deco_k = 342, (940, 252), 1
    c += (f'<g opacity="1">{appear(0, .6)}<rect x="{LX}" y="{pill_y}" width="318" height="42" rx="21" fill="{AMEIXA}"/>'
          f'<circle cx="{LX + 24}" cy="{pill_y + 21}" r="5" fill="{PITAYA}"/>'
          f'<text x="{LX + 40}" y="{pill_y + 27}" {SANS} font-size="16" font-weight="700" fill="#fff">Gabriel Niza · Fundador &amp; CEO</text></g>')
    deco = (f'<circle r="150" fill="{LAVANDA}"/>'
            f'<circle r="118" fill="none" stroke="{LILAS}" stroke-width="2" stroke-dasharray="4 10">'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="30s" repeatCount="indefinite"/></circle>'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite"/>'
            f'<circle cx="118" cy="0" r="7" fill="{PITAYA}"/></g>'
            + bob(f'<g transform="translate(-72,-72) scale(2.25)">{symbol}</g>', 8, 3))
    c += f'<g transform="translate({deco_xy[0]:.0f},{deco_xy[1]}) scale({deco_k})">{deco}</g>'
    slides.append(c)

    # ---------- 2. missão ----------
    c = label("01 — MISSÃO")
    if mobile:
        c += f'<text x="6" y="236" {SERIF} font-size="170" fill="{LILAS}" opacity=".3">“</text>'
        y = 170
        for k, (txt, it) in enumerate(DECK["missao_m"]):
            body = italic(it) if it else esc(txt)
            c += (f'<g opacity="1">{appear(1, .3 + k * .18, rise=12)}<text x="{LX}" y="{y}" {SANS} font-size="29" '
                  f'font-weight="800" fill="{AMEIXA}" letter-spacing="-.5">{body}</text></g>')
            y += 44
        ay = y + 14
        c += (f'<g opacity="1">{appear(1, 1.6)}<line x1="{LX}" y1="{ay}" x2="{LX + 40}" y2="{ay}" stroke="{PITAYA}" stroke-width="3"/>'
              f'<text x="{LX + 54}" y="{ay + 6}" {SANS} font-size="15" font-weight="600" fill="{INK2}">Gabriel Niza, Fundador &amp; CEO</text></g>')
    else:
        c += f'<text x="64" y="262" {SERIF} font-size="210" fill="{LILAS}" opacity=".45">“</text>'
        for k, (txt, it) in enumerate(DECK["missao"]):
            extra = italic(it) if it else ""
            c += (f'<g opacity="1">{appear(1, .35 + k * .3, rise=14)}<text x="170" y="{196 + k*56}" {SANS} font-size="38" '
                  f'font-weight="800" fill="{AMEIXA}" letter-spacing="-1">{esc(txt)}{extra}</text></g>')
        c += (f'<g opacity="1">{appear(1, 1.5)}<line x1="172" y1="352" x2="212" y2="352" stroke="{PITAYA}" stroke-width="3"/>'
              f'<text x="226" y="358" {SANS} font-size="16" font-weight="600" fill="{INK2}">Gabriel Niza, Fundador &amp; CEO</text></g>')
    slides.append(c)

    # ---------- 3. proposta de valor ----------
    c = label("02 — PROPOSTA DE VALOR")
    c += (f'<text x="{LX}" y="{138 if mobile else 150}" {SANS} font-size="{28 if mobile else 32}" font-weight="900" fill="{AMEIXA}" '
          f'letter-spacing="-1">Por que a {italic("NizaShop")}</text>')
    for k, (ic, tit, (l1, l2)) in enumerate(DECK["valor"]):
        accent = [PITAYA, LILAS, PESSEGO][k]
        if mobile:
            cw, chh = W - 2 * LX, 124
            card = (f'<rect width="{cw}" height="{chh}" rx="20" fill="#ffffff" stroke="{LINE}" stroke-width="1.5"/>'
                    f'<rect width="4" height="{chh}" rx="2" fill="{accent}"/>'
                    f'<g transform="translate(50,{chh/2})"><circle r="26" fill="{LAVANDA}"/>{niza_icon(ic, PITAYA)}</g>'
                    f'<text x="94" y="46" {SANS} font-size="21" font-weight="800" fill="{AMEIXA}">{esc(tit)}</text>'
                    f'<text x="94" y="74" {SANS} font-size="15" fill="{INK2}">{esc(l1)}</text>'
                    f'<text x="94" y="96" {SANS} font-size="15" fill="{INK2}">{esc(l2)}</text>')
            x, y = LX, 162 + k * (chh + 14)
        else:
            cw = 328
            card = (f'<rect width="{cw}" height="196" rx="22" fill="#ffffff" stroke="{LINE}" stroke-width="1.5"/>'
                    f'<rect width="{cw}" height="4" rx="2" fill="{accent}"/>'
                    f'<g transform="translate(52,60)"><circle r="28" fill="{LAVANDA}"/>{niza_icon(ic, PITAYA)}</g>'
                    f'<text x="28" y="124" {SANS} font-size="23" font-weight="800" fill="{AMEIXA}">{esc(tit)}</text>'
                    f'<text x="28" y="152" {SANS} font-size="15" fill="{INK2}">{esc(l1)}</text>'
                    f'<text x="28" y="174" {SANS} font-size="15" fill="{INK2}">{esc(l2)}</text>')
            x, y = LX + k * (cw + 36), 186
        c += f'<g transform="translate({x},{y})"><g opacity="1">{appear(2, .3 + k * .25, rise=18)}{card}</g></g>'
    slides.append(c)

    # ---------- 4. ciclo de crescimento ----------
    c = label("03 — CRESCIMENTO COM IA")
    if mobile:
        c += f'<text x="{LX}" y="134" {SANS} font-size="30" font-weight="900" fill="{AMEIXA}" letter-spacing="-1">Um ciclo que</text>'
        c += f'<text x="{LX}" y="174" {SERIF} font-size="34" font-style="italic" fill="{PITAYA}">se retroalimenta.</text>'
        fx, fy, R, pfs, pk, core_r, logo_s = W / 2, 352, 112, 13, 8, 50, 22
        for k, line in enumerate(DECK["ciclo_texto"]):
            c += f'<text x="{LX}" y="{530 + k*24}" {SANS} font-size="15.5" fill="{INK2}">{esc(line)}</text>'
    else:
        c += f'<text x="{LX}" y="166" {SANS} font-size="38" font-weight="900" fill="{AMEIXA}" letter-spacing="-1">Um ciclo que</text>'
        c += f'<text x="{LX}" y="214" {SERIF} font-size="42" font-style="italic" fill="{PITAYA}">se retroalimenta.</text>'
        fx, fy, R, pfs, pk, core_r, logo_s = 850, 262, 138, 14, 9, 62, 26
        for k, line in enumerate(DECK["ciclo_texto"]):
            c += f'<text x="{LX}" y="{270 + k*28}" {SANS} font-size="18" fill="{INK2}">{esc(line)}</text>'
    ring = (f'<circle r="{R}" fill="none" stroke="{LINE}" stroke-width="2"/>'
            f'<circle r="{R}" fill="none" stroke="{LILAS}" stroke-width="2.5" stroke-dasharray="10 14">'
            f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="14s" repeatCount="indefinite"/></circle>'
            f'<circle r="7" fill="{PITAYA}"><animateMotion dur="5s" repeatCount="indefinite" '
            f'path="M0 {-R} A{R} {R} 0 1 1 -0.01 {-R}Z"/></circle>')
    nodes = DECK["ciclo"]
    for k, nome in enumerate(nodes):
        ang = -math.pi / 2 + k * 2 * math.pi / len(nodes)
        nx, ny = math.cos(ang) * R, math.sin(ang) * R
        mid = ang + math.pi / len(nodes)
        ax, ay = math.cos(mid) * R, math.sin(mid) * R
        ring += f'<path transform="translate({ax:.1f},{ay:.1f}) rotate({math.degrees(mid) + 90:.1f})" d="M-5 -4 L1 0 L-5 4" fill="none" stroke="{LILAS}" stroke-width="2.5" stroke-linecap="round"/>'
        pw = len(nome) * pk + 28
        a0, a1 = k / len(nodes), (k + 1) / len(nodes)
        if k == 0:
            hi = f'keyTimes="0;{a1:.3f}" values="{PITAYA};#ffffff"'
            hit = f'keyTimes="0;{a1:.3f}" values="#ffffff;{AMEIXA}"'
        else:
            hi = f'keyTimes="0;{a0:.3f};{a1:.3f}" values="#ffffff;{PITAYA};#ffffff"'
            hit = f'keyTimes="0;{a0:.3f};{a1:.3f}" values="{AMEIXA};#ffffff;{AMEIXA}"'
        ring += (f'<g transform="translate({nx:.1f},{ny:.1f})"><g opacity="1">{appear(3, .3 + k * .15)}'
                 f'<rect x="{-pw/2:.0f}" y="-17" width="{pw:.0f}" height="34" rx="17" fill="#ffffff" stroke="{LILAS}" stroke-width="1.5">'
                 f'<animate attributeName="fill" dur="5s" repeatCount="indefinite" calcMode="discrete" {hi}/></rect>'
                 f'<text y="5" text-anchor="middle" {SANS} font-size="{pfs}" font-weight="700" fill="{AMEIXA}">{esc(nome)}'
                 f'<animate attributeName="fill" dur="5s" repeatCount="indefinite" calcMode="discrete" {hit}/></text></g></g>')
    core = (f'<circle r="{core_r}" fill="{AMEIXA}"/><circle r="{core_r}" fill="none" stroke="{PITAYA}" stroke-width="2" opacity=".6">'
            f'<animate attributeName="r" values="{core_r};{core_r + 16}" dur="2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".6;0" dur="2s" repeatCount="indefinite"/></circle>'
            f'<g transform="translate({-logo_s*.65:.0f},-12)">{mini_logo("claude", logo_s)}</g>'
            f'<g transform="translate({logo_s*.65:.0f},-12)">{mini_logo("googlegemini", logo_s)}</g>'
            f'<text y="{core_r*.5:.0f}" text-anchor="middle" {SANS} font-size="{16 if mobile else 18}" font-weight="900" fill="#fff" letter-spacing="2">IA</text>')
    c += f'<g transform="translate({fx:.0f},{fy})">{ring}{core}</g>'
    slides.append(c)

    # ---------- 5. próximos passos + assinatura ----------
    c = label("04 — PRÓXIMOS PASSOS")
    fases = DECK["fases"]
    s0, _ = span(4)

    def marker(tag):
        if tag == "concluída":
            return (f'<circle r="15" fill="{PITAYA}"/><path d="M-6 0 L-2 5 L7 -5" fill="none" stroke="#fff" stroke-width="3" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>')
        if tag:
            return (f'<circle r="15" fill="#fff" stroke="{PITAYA}" stroke-width="4"/><circle r="5" fill="{PITAYA}"/>'
                    f'<circle r="15" fill="none" stroke="{PITAYA}" stroke-width="2"><animate attributeName="r" values="15;28" dur="1.6s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values=".7;0" dur="1.6s" repeatCount="indefinite"/></circle>')
        return f'<circle r="13" fill="#fff" stroke="{LILAS}" stroke-width="3"/>'

    def texts(k, tit, sub, tag, anchor, tx, y_fase, y_tit, y_sub, y_tag):
        out = (f'<text x="{tx}" y="{y_fase}" text-anchor="{anchor}" {SANS} font-size="12.5" font-weight="800" fill="{LILAS}" letter-spacing="1.5">FASE {k+1}</text>'
               f'<text x="{tx}" y="{y_tit}" text-anchor="{anchor}" {SANS} font-size="18" font-weight="800" fill="{AMEIXA}">{esc(tit)}</text>'
               f'<text x="{tx}" y="{y_sub}" text-anchor="{anchor}" {SANS} font-size="14" fill="{INK2}">{esc(sub)}</text>')
        if tag:
            tw = len(tag) * 7.6 + 24
            bx = {"start": tx, "middle": tx - tw / 2, "end": tx - tw}[anchor]
            col = "#2f9e6e" if tag == "concluída" else PITAYA
            out += (f'<rect x="{bx:.0f}" y="{y_tag}" width="{tw:.0f}" height="24" rx="12" fill="{col}" fill-opacity=".12"/>'
                    f'<text x="{bx + tw/2:.0f}" y="{y_tag + 16}" text-anchor="middle" {SANS} font-size="12" font-weight="800" fill="{col}">{esc(tag)}</text>')
        return out

    if mobile:
        lx, ys = 44, [128, 236, 344, 452]
        c += f'<line x1="{lx}" y1="{ys[0]}" x2="{lx}" y2="{ys[-1]}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
        prog_end = (ys[1] + ys[2]) / 2 - 20
        c += (f'<line x1="{lx}" y1="{ys[0]}" x2="{lx}" y2="{prog_end:.0f}" stroke="{PITAYA}" stroke-width="4" stroke-linecap="round">'
              f'{anim("y2", [(0, ys[0]), (s0 + .3, ys[0]), (s0 + 1.6, round(prog_end)), (T, round(prog_end))], T)}</line>')
        for k, (tit, sub, tag) in enumerate(fases):
            c += (f'<g transform="translate({lx},{ys[k]})"><g opacity="1">{appear(4, .2 + k * .25)}{marker(tag)}'
                  f'{texts(k, tit, sub, tag, "start", 34, -10, 13, 34, 44)}</g></g>')
        c += f'<g opacity="1">{appear(4, 1.6)}<text x="{LX}" y="584" {SERIF} font-size="28" font-style="italic" fill="{AMEIXA}">Obrigado.</text></g>'
        sig_w, sig_base, sig_line, sig_cap = 200, 588, 606, 624
    else:
        lx0, lx1, ly = 110, 1090, 176
        xs = [lx0 + k * (lx1 - lx0) / (len(fases) - 1) for k in range(len(fases))]
        c += f'<line x1="{lx0}" y1="{ly}" x2="{lx1}" y2="{ly}" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
        prog_end = (xs[1] + xs[2]) / 2 - 60
        c += (f'<line x1="{lx0}" y1="{ly}" x2="{prog_end:.0f}" y2="{ly}" stroke="{PITAYA}" stroke-width="4" stroke-linecap="round">'
              f'{anim("x2", [(0, lx0), (s0 + .3, lx0), (s0 + 1.6, round(prog_end)), (T, round(prog_end))], T)}</line>')
        for k, (tit, sub, tag) in enumerate(fases):
            anchor = "start" if k == 0 else ("end" if k == len(fases) - 1 else "middle")
            tx = -12 if k == 0 else (12 if k == len(fases) - 1 else 0)
            c += (f'<g transform="translate({xs[k]:.0f},{ly})"><g opacity="1">{appear(4, .2 + k * .25)}{marker(tag)}'
                  f'{texts(k, tit, sub, tag, anchor, tx, 46, 72, 96, 110)}</g></g>')
        c += f'<g opacity="1">{appear(4, 1.6)}<text x="{LX}" y="398" {SERIF} font-size="34" font-style="italic" fill="{AMEIXA}">Obrigado.</text></g>'
        sig_w, sig_base, sig_line, sig_cap = 330, 382, 415, 433
    sig_src = (LOGOS / "assinatura.svg").read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', sig_src).group(1).split()]
    sig_d = re.search(r'<path d="([^"]+)"', sig_src).group(1)
    k = sig_w / vb[2]
    sx = W - LX - sig_w
    c += (f'<clipPath id="sig"><rect x="{sx - 10}" y="{sig_base - 82}" height="{sig_w * .4 + 50:.0f}" width="{sig_w + 20}">'
          f'{anim("width", [(0, 0), (s0 + 1.2, 0), (s0 + 2.8, sig_w + 20), (T, sig_w + 20)], T)}</rect></clipPath>'
          f'<g clip-path="url(#sig)"><path transform="translate({sx - vb[0]*k:.1f},{sig_base}) scale({k:.4f})" d="{sig_d}" '
          f'fill="{AMEIXA}" stroke="{AMEIXA}" stroke-width="10" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0">'
          f'{anim("stroke-dashoffset", [(0, 1), (s0 + 1.2, 1), (s0 + 2.6, 0), (T, 0)], T)}'
          f'{anim("fill-opacity", [(0, 0), (s0 + 2.0, 0), (s0 + 2.9, 1), (T, 1)], T)}</path></g>'
          f'<line x1="{sx}" y1="{sig_line}" x2="{W - LX}" y2="{sig_line}" stroke="{LINE}" stroke-width="1.5"/>'
          f'<text x="{W - LX}" y="{sig_cap}" text-anchor="end" {SANS} font-size="13" font-weight="600" fill="{INK2}">Fundador &amp; CEO, NizaShop</text>')
    slides.append(c)

    # ---------- moldura, barra superior, contador e progresso ----------
    o = (f'<rect width="{W}" height="{H}" rx="22" fill="{PAPER}"/>'
         f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
         f'<circle cx="{W-80}" cy="{H-40}" r="220" fill="{LAVANDA}" opacity=".5"/>')
    sym_k, title_x, title = (.36, 50, DECK["titulo_m"]) if mobile else (.39, 66, DECK["titulo"])
    o += (f'<g transform="translate({16 if mobile else 28},{14 if mobile else 16}) scale({sym_k})">{symbol}</g>'
          f'<text x="{title_x}" y="{32 if mobile else 35}" {SANS} font-size="{13 if mobile else 14}" font-weight="700" fill="{AMEIXA}">{esc(title)}</text>'
          f'<line x1="0" y1="{TOPBAR}" x2="{W}" y2="{TOPBAR}" stroke="{LINE}" stroke-width="1.5"/>')
    for i in range(N):
        s0, e = span(i)
        if i == 0:
            op = f'keyTimes="0;{e/T:.4f}" values="1;0"'
        else:
            op = f'keyTimes="0;{s0/T:.4f};{min(e/T, 1):.4f}" values="0;1;0"' if e < T else f'keyTimes="0;{s0/T:.4f}" values="0;1"'
        o += (f'<text x="{W - (16 if mobile else 28)}" y="{32 if mobile else 35}" text-anchor="end" {MONO} font-size="{13 if mobile else 14}" fill="{INK2}" opacity="{1 if i == 0 else 0}">'
              f'<tspan fill="{AMEIXA}" font-weight="700">{i+1:02d}</tspan> / {N:02d}'
              f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" {op}/></text>')
    seg_g, mx = 8, (16 if mobile else 28)
    sw = (W - 2 * mx - (N - 1) * seg_g) / N
    py = H - 24
    for i in range(N):
        s0, e = span(i)
        x = mx + i * (sw + seg_g)
        pts = [(0, 0), (s0, 0), (e, round(sw, 1))] + ([] if e >= T else [(T, round(sw, 1))])
        o += (f'<rect x="{x:.1f}" y="{py}" width="{sw:.1f}" height="4" rx="2" fill="{LINE}"/>'
              f'<rect x="{x:.1f}" y="{py}" width="{sw if i == 0 else 0:.1f}" height="4" rx="2" fill="{PITAYA}">{anim("width", pts, T)}</rect>')
    o += f'<clipPath id="area"><rect x="0" y="{TOPBAR + 1}" width="{W}" height="{H - TOPBAR - 34}"/></clipPath><g clip-path="url(#area)">'
    for i, c in enumerate(slides):
        op, tr = slide_win(i)
        o += f'<g opacity="{1 if i == 0 else 0}">{op}<g>{tr}{c}</g></g>'
    o += '</g>'
    save(mname("nizashop-deck.svg", mobile), svg(W, H, o, GEM))


def nizashop():
    for m in (False, True):
        nizashop_hero(m); nizashop_pilares(m); nizashop_paleta(m); nizashop_card(m); nizashop_deck(m); nizashop_bento(m)


if __name__ == "__main__":
    for m in (False, True):  # versão computador e versão celular (*-m.svg)
        hero(m); titles(m); claude_md(m); stack(m); projects(m)
    walk(); footer(); nizashop()
    print("SVGs gerados em", OUT)
