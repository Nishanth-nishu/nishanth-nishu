"""Generate three animated owl SVGs for the profile README (stdlib only).

    assets/owl-hero.svg   - owl coding at a laptop, headphones, coffee, commits floating up
    assets/owl-fly.svg    - owl flying across a night strip, wings flapping
    assets/owl-sleep.svg  - owl sleeping under the moon, wakes up, looks around, dozes off

Run from the repo root:  python scripts/gen_owls.py
"""
import html
import os

G = "#00ff41"; DK = "#06140a"; MID = "#0f6b2c"; LM = "#d6ff7a"; TX = "#9dffb5"; RED = "#ff2e63"

DEFS = f'''<defs>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="halo"><stop offset="0" stop-color="{G}" stop-opacity="0.45"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
<radialGradient id="bgglow"><stop offset="0" stop-color="{G}" stop-opacity="0.22"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
<radialGradient id="iris" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#eaffc0"/><stop offset="0.55" stop-color="{G}"/><stop offset="1" stop-color="#009a2a"/></radialGradient>
<radialGradient id="moon"><stop offset="0" stop-color="#eaffd0" stop-opacity="0.9"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.3"/></pattern>
</defs>'''


def frame(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
            f'{DEFS}<clipPath id="fr"><rect width="{w}" height="{h}" rx="14"/></clipPath>'
            f'<g clip-path="url(#fr)"><rect width="{w}" height="{h}" fill="#000"/>{body}'
            f'<rect width="{w}" height="{h}" fill="url(#scan)"/>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="none" stroke="{G}" stroke-opacity="0.45"/></g></svg>')


def stars(w, h, n, seed):
    import random
    r = random.Random(seed)
    out = ""
    for _ in range(n):
        x, y = r.randint(10, w - 10), r.randint(8, h - 40)
        d = r.uniform(1.8, 4.2); b = r.uniform(0, 3)
        out += (f'<circle cx="{x}" cy="{y}" r="{r.choice([1, 1.3, 1.7])}" fill="#d9ffe3">'
                f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>')
    return out


def eye(cx, cy=92, r=33, lid=None, look=True):
    """Big neon eye. `lid` = (values, keyTimes, dur) for a custom eyelid scaleY cycle (sleep/wake)."""
    if lid:
        v, kt, dur = lid
        blink = f'<animateTransform attributeName="transform" type="scale" values="{v}" keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/>'
    else:
        blink = '<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 0.06;1 1;1 1" keyTimes="0;0.9;0.94;0.98;1" dur="5s" repeatCount="indefinite"/>'
    look_anim = ('<animateTransform attributeName="transform" type="translate" values="0 0;-9 3;-9 3;9 -2;9 -2;0 0" '
                 'keyTimes="0;0.15;0.4;0.6;0.85;1" dur="6s" repeatCount="indefinite"/>') if look else ''
    return f'''<g transform="translate({cx},{cy})">
 <circle r="{r+9}" fill="url(#halo)"><animate attributeName="r" values="{r+7};{r+13};{r+7}" dur="2.4s" repeatCount="indefinite"/></circle>
 <g>{blink}
  <circle r="{r}" fill="#021005" stroke="{G}" stroke-width="3"/>
  <circle r="{r-5}" fill="url(#iris)"/>
  <circle r="{r-3}" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="5 9" opacity="0.7"><animateTransform attributeName="transform" type="rotate" values="0;360" dur="9s" repeatCount="indefinite"/></circle>
  <circle r="{r-12}" fill="none" stroke="#00c030" stroke-width="2" stroke-dasharray="14 10" opacity="0.8"><animateTransform attributeName="transform" type="rotate" values="360;0" dur="6s" repeatCount="indefinite"/></circle>
  <g>{look_anim}<circle r="12" fill="#020a03"/><circle cx="-4" cy="-5" r="4" fill="#fff"/><circle cx="5" cy="4" r="1.8" fill="#d6ffe0"/></g>
 </g>
</g>'''


def head(lid=None, headphones=True, look=True, tilt=True):
    tilt_anim = ('<animateTransform attributeName="transform" type="rotate" values="0 0 130;-4 0 130;-4 0 130;3 0 130;3 0 130;0 0 130" '
                 'keyTimes="0;0.2;0.4;0.6;0.8;1" dur="9s" repeatCount="indefinite"/>') if tilt else ''
    hp = f'''
  <path d="M-78 84 C-92 -6 92 -6 78 84" fill="none" stroke="#000" stroke-width="12" stroke-linecap="round"/>
  <path d="M-78 84 C-92 -6 92 -6 78 84" fill="none" stroke="{G}" stroke-width="8" stroke-linecap="round" opacity="0.9"/>
  <path d="M-78 84 C-92 -6 92 -6 78 84" fill="none" stroke="{DK}" stroke-width="4" stroke-linecap="round"/>
  <rect x="-96" y="72" width="26" height="52" rx="9" fill="{DK}" stroke="{G}" stroke-width="3"/>
  <rect x="70" y="72" width="26" height="52" rx="9" fill="{DK}" stroke="{G}" stroke-width="3"/>
  <rect x="-90" y="80" width="14" height="36" rx="6" fill="{G}" opacity="0.4"><animate attributeName="opacity" values="0.25;0.9;0.25" dur="0.7s" repeatCount="indefinite"/></rect>
  <rect x="76" y="80" width="14" height="36" rx="6" fill="{G}" opacity="0.4"><animate attributeName="opacity" values="0.9;0.25;0.9" dur="0.7s" repeatCount="indefinite"/></rect>''' if headphones else ''
    return f'''<g>{tilt_anim}
  <path d="M-74 66 L-70 18 L-36 46 Q0 36 36 46 L70 18 L74 66 Q84 104 52 132 Q0 152 -52 132 Q-84 104 -74 66Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-70 18 L-52 38 M70 18 L52 38" stroke="{G}" stroke-width="2.5"/>
  <path d="M0 70 C-20 48 -70 56 -66 96 C-62 128 -20 134 0 118 C20 134 62 128 66 96 C70 56 20 48 0 70Z" fill="#031007" stroke="{MID}" stroke-width="2"/>
  {eye(-34, lid=lid, look=look)}{eye(34, lid=lid, look=look)}
  <path d="M-9 114 L9 114 L0 134Z" fill="{LM}" stroke="{G}" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M-62 56 L-12 70" stroke="{G}" stroke-width="3" stroke-linecap="round"/>
  <path d="M62 56 L12 70" stroke="{G}" stroke-width="3" stroke-linecap="round"/>{hp}
 </g>'''


# ===================================================================== HERO
def hero():
    cx = 450
    msgs = [("git commit -m 'feat: agents'", -330, 0), ("✔ tests passed", 190, 2.6),
            ("merge main → prod", -300, 5.2), ("fix: ship it", 230, 7.8), ("deploy ✓", -120, 3.9), ("PR #42 merged", 120, 6.5)]
    float_txt = "".join(
        f'<text x="{cx+dx}" y="270" opacity="0" fill="{TX}" font-size="13" font-family="Consolas,monospace">{html.escape(t)}'
        f'<animate attributeName="y" values="270;30" dur="9s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.95;0" dur="9s" begin="{b}s" repeatCount="indefinite"/></text>'
        for t, dx, b in msgs)
    feath = ""
    for row, y in enumerate((150, 166, 182)):
        for x in range(-36, 37, 18):
            d = row * 0.3 + (x + 36) / 18 * 0.15
            feath += (f'<path d="M{x-7} {y} l7 6 l7 -6" fill="none" stroke="{G}" stroke-width="1.6" opacity="0.35">'
                      f'<animate attributeName="opacity" values="0.15;0.8;0.15" dur="2.6s" begin="{d:.2f}s" repeatCount="indefinite"/></path>')
    owl = f'''<g filter="url(#glow)">
 <animateTransform attributeName="transform" type="translate" values="{cx} 6;{cx} 2;{cx} 6" dur="3.4s" repeatCount="indefinite"/>
 <path d="M-64 128 Q-92 200 -66 262 L66 262 Q92 200 64 128 Q0 156 -64 128Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
 {feath}
 <g>
  <path d="M0 140 V196" stroke="{G}" stroke-width="2.5"/>
  <path d="M0 160 C0 172 22 168 22 182" fill="none" stroke="{RED}" stroke-width="2.5"/>
  <path d="M0 140 V196" stroke="#fff" stroke-width="2.5" stroke-dasharray="4 60"><animate attributeName="stroke-dashoffset" values="64;0" dur="2s" repeatCount="indefinite"/></path>
  <circle cx="0" cy="142" r="5" fill="{DK}" stroke="{G}" stroke-width="2.5"/>
  <circle cx="0" cy="160" r="5" fill="{G}"><animate attributeName="r" values="4;7;4" dur="1.6s" repeatCount="indefinite"/></circle>
  <circle cx="22" cy="182" r="5" fill="{RED}"><animate attributeName="r" values="4;7;4" dur="1.6s" begin="0.5s" repeatCount="indefinite"/></circle>
  <circle cx="0" cy="196" r="5" fill="{DK}" stroke="{G}" stroke-width="2.5"/>
 </g>
 {head()}
 <rect x="-98" y="196" width="196" height="46" rx="7" fill="#04110a" stroke="{G}" stroke-width="3"/>
 <g fill="none" stroke="{G}" stroke-width="3" stroke-linecap="round">
  <path d="M-12 232 V206 M-12 216 C-12 224 12 220 12 210"/>
  <g fill="{DK}"><circle cx="-12" cy="206" r="4.5"/><circle cx="-12" cy="232" r="4.5"/><circle cx="12" cy="210" r="4.5"/></g>
  <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite"/>
 </g>
 <path d="M-112 242 H112 L104 254 H-104Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
 <g><animateTransform attributeName="transform" type="translate" values="0 0;0 5;0 0" dur="0.36s" repeatCount="indefinite"/>
  <path d="M-62 134 Q-104 176 -64 212 Q-40 214 -46 176 Q-48 150 -62 134Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M-72 160 q10 8 20 0 M-70 176 q10 8 18 0" fill="none" stroke="{G}" stroke-width="1.6" opacity="0.6"/></g>
 <g><animateTransform attributeName="transform" type="translate" values="0 5;0 0;0 5" dur="0.36s" repeatCount="indefinite"/>
  <path d="M62 134 Q104 176 64 212 Q40 214 46 176 Q48 150 62 134Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M72 160 q-10 8 -20 0 M70 176 q-10 8 -18 0" fill="none" stroke="{G}" stroke-width="1.6" opacity="0.6"/></g>
 <g transform="translate(138,0)">
  <rect x="-16" y="224" width="32" height="30" rx="5" fill="{DK}" stroke="{G}" stroke-width="3"/>
  <path d="M16 232 q16 0 16 12 q0 10 -16 8" fill="none" stroke="{G}" stroke-width="3"/>
  <rect x="-12" y="228" width="24" height="5" fill="#7a4a21"/>
  <g fill="none" stroke="{TX}" stroke-width="2.5" stroke-linecap="round">
   <path d="M-7 218 q-6 -8 0 -14 q6 -6 0 -14" opacity="0"><animate attributeName="opacity" values="0;0.9;0" dur="2.4s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 6;0 -10" dur="2.4s" repeatCount="indefinite"/></path>
   <path d="M5 218 q-6 -8 0 -14 q6 -6 0 -14" opacity="0"><animate attributeName="opacity" values="0;0.9;0" dur="2.4s" begin="0.8s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 6;0 -10" dur="2.4s" begin="0.8s" repeatCount="indefinite"/></path>
  </g>
 </g>
</g>'''
    body = (f'<ellipse cx="{cx}" cy="150" rx="260" ry="170" fill="url(#bgglow)"><animate attributeName="opacity" values="0.6;1;0.6" dur="3s" repeatCount="indefinite"/></ellipse>'
            f'<rect x="{cx-210}" y="254" width="420" height="10" rx="2" fill="{DK}" stroke="{G}" stroke-width="2"/>'
            f'<g>{float_txt}</g>{owl}')
    return frame(900, 290, body, "Neon owl with headphones coding on a laptop with commits floating up")


# ===================================================================== FLY
def fly():
    w, h = 900, 200
    path = "M-120 112 C120 62 260 150 450 104 S760 62 1020 112"
    # one flying owl (front view, wings flapping) + fading trail owls

    def flyer(op, scale):
        wl_up = "M-14 4 Q-60 -44 -112 -30 Q-84 6 -14 22Z"
        wl_dn = "M-14 4 Q-60 30 -108 52 Q-80 16 -14 22Z"
        wr_up = "M14 4 Q60 -44 112 -30 Q84 6 14 22Z"
        wr_dn = "M14 4 Q60 30 108 52 Q80 16 14 22Z"
        dur = "0.5s"
        return f'''<g opacity="{op}" transform="scale({scale})">
  <path d="{wl_up}" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"><animate attributeName="d" values="{wl_up};{wl_dn};{wl_up}" dur="{dur}" repeatCount="indefinite"/></path>
  <path d="{wr_up}" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"><animate attributeName="d" values="{wr_up};{wr_dn};{wr_up}" dur="{dur}" repeatCount="indefinite"/></path>
  <ellipse cx="0" cy="20" rx="22" ry="34" fill="{DK}" stroke="{G}" stroke-width="3"/>
  <path d="M-10 26 l5 5 l5 -5 M0 26 l5 5 l5 -5 M-5 38 l5 5 l5 -5" fill="none" stroke="{G}" stroke-width="1.5" opacity="0.6"/>
  <g transform="translate(0,-18) scale(0.26) translate(0,-90)">{head(headphones=True, look=False, tilt=False)}</g>
  <path d="M-8 50 l-4 12 M-2 52 l-1 12 M8 50 l4 12 M2 52 l1 12" stroke="{LM}" stroke-width="2.2" stroke-linecap="round"/>
 </g>'''
    trail = ""
    for i, (op, sc) in enumerate([(0.12, 0.8), (0.2, 0.88), (0.32, 0.94)]):
        trail += (f'<g><animateMotion dur="11s" begin="-{(3-i)*0.18:.2f}s" repeatCount="indefinite" path="{path}" rotate="0"/>'
                  f'{flyer(op, sc)}</g>')
    main = (f'<g filter="url(#glow)"><animateMotion dur="11s" repeatCount="indefinite" path="{path}" rotate="0"/>{flyer(1, 1.0)}</g>')
    # sparkle dust left behind
    dust = "".join(
        f'<circle r="2" fill="{G}"><animateMotion dur="11s" begin="-{k*0.25:.2f}s" repeatCount="indefinite" path="{path}"/>'
        f'<animate attributeName="opacity" values="0;0.8;0" dur="1.1s" begin="{k*0.2:.1f}s" repeatCount="indefinite"/></circle>' for k in range(1, 7))
    moon = (f'<circle cx="810" cy="38" r="40" fill="url(#moon)"><animate attributeName="r" values="36;42;36" dur="5s" repeatCount="indefinite"/></circle>'
            f'<circle cx="810" cy="38" r="15" fill="#eaffd0"/><circle cx="803" cy="33" r="3" fill="#c9eeb4"/>')
    body = stars(w, h, 36, 5) + moon + f'<g opacity="0.9">{dust}</g>{trail}{main}'
    return frame(w, h, body, "An owl with headphones flying across a night sky")


# ===================================================================== SLEEP
def sleep():
    w, h = 900, 250
    cx = 450
    # eyelid cycle (12s): asleep -> wake up -> look around -> doze off
    lid = ("1 0.04;1 0.04;1 1;1 1;1 0.06;1 1;1 1;1 0.04;1 0.04",
           "0;0.30;0.36;0.60;0.64;0.68;0.80;0.88;1", "12s")
    zs = "".join(
        f'<text x="{cx+95+k*14}" y="{70-k*6}" fill="{TX}" font-size="{20+k*6}" font-family="Consolas,monospace" opacity="0">Z'
        f'<animate attributeName="y" values="{110-k*6};{20-k*6}" dur="4s" begin="{k*1.2}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.9;0" dur="4s" begin="{k*1.2}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x" values="{cx+95+k*14};{cx+125+k*14}" dur="4s" begin="{k*1.2}s" repeatCount="indefinite"/></text>'
        for k in range(3))
    # Zs only while asleep -> hide while awake by overlaying with group opacity animation
    zgroup = (f'<g>{zs}<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.28;0.34;0.9;1" dur="12s" repeatCount="indefinite"/></g>')
    # "!" popup when waking
    bang = (f'<text x="{cx+80}" y="40" fill="{RED}" font-size="34" font-weight="700" font-family="Consolas,monospace" opacity="0">!'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.30;0.34;0.42;1" dur="12s" repeatCount="indefinite"/></text>')
    moon = (f'<circle cx="150" cy="70" r="70" fill="url(#moon)"><animate attributeName="r" values="64;74;64" dur="6s" repeatCount="indefinite"/></circle>'
            f'<circle cx="150" cy="70" r="28" fill="#eaffd0"/><circle cx="141" cy="62" r="5" fill="#c9eeb4"/><circle cx="160" cy="80" r="3.5" fill="#c9eeb4"/>')
    branch = (f'<path d="M120 232 Q450 214 780 232" stroke="#2a1a10" stroke-width="12" fill="none" stroke-linecap="round"/>'
              f'<path d="M120 232 Q450 214 780 232" stroke="{MID}" stroke-width="2" fill="none" stroke-linecap="round"/>'
              f'<path d="M700 230 q24 -26 54 -30" stroke="{MID}" stroke-width="4" fill="none" stroke-linecap="round"/>'
              f'<ellipse cx="760" cy="198" rx="12" ry="5" fill="{G}" opacity="0.7" transform="rotate(-25 760 198)"/>')
    owl = f'''<g filter="url(#glow)" transform="translate({cx},40) scale(0.62)">
 <animateTransform attributeName="transform" type="translate" values="{cx} 44;{cx} 40;{cx} 44" additive="replace" dur="3s" repeatCount="indefinite"/>
 <g transform="scale(0.62)">
 <path d="M-64 128 Q-92 200 -66 262 L66 262 Q92 200 64 128 Q0 156 -64 128Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
 <path d="M-62 150 q10 8 20 0 M-20 150 q10 8 20 0 M22 150 q10 8 20 0 M-42 176 q10 8 20 0 M0 176 q10 8 20 0" fill="none" stroke="{G}" stroke-width="2" opacity="0.5"/>
 <path d="M-64 150 Q-92 200 -60 240 Q-48 200 -52 160Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
 <path d="M64 150 Q92 200 60 240 Q48 200 52 160Z" fill="{DK}" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
 <g fill="{LM}"><path d="M-26 262 l-8 14 M-16 262 l-2 16 M-6 262 l5 14" stroke="{LM}" stroke-width="4" stroke-linecap="round"/><path d="M26 262 l8 14 M16 262 l2 16 M6 262 l-5 14" stroke="{LM}" stroke-width="4" stroke-linecap="round"/></g>
 {head(lid=lid, headphones=False, look=True, tilt=False)}
 </g>
</g>'''
    # restructure transform: scale applied inside group so the float animation (translate) is not overridden
    owl = owl.replace(f'<g filter="url(#glow)" transform="translate({cx},40) scale(0.62)">', '<g filter="url(#glow)">')
    owl = owl.replace(' <g transform="scale(0.62)">', ' <g transform="scale(0.62)">', 1)
    body = (stars(w, h, 40, 9) + moon + branch + f'<ellipse cx="{cx}" cy="140" rx="200" ry="120" fill="url(#bgglow)"/>'
            + owl + zgroup + bang)
    return frame(w, h, body, "A neon owl sleeping on a branch under the moon, waking up and looking around")


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out, exist_ok=True)
    for name, fn in (("owl-hero.svg", hero), ("owl-fly.svg", fly), ("owl-sleep.svg", sleep)):
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
