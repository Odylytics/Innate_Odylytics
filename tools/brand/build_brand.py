"""Generates the brand SVG fragments (main lockup, symbol, gesture stroke) from web/public/brand/*.svg. Does not redraw the logo."""
import re, sys
from pathlib import Path
B = Path(__file__).parents[2] / "web/public/brand"
mark, word = (B / "mark.svg").read_text(), (B / "wordmark.svg").read_text()
stroke_m = re.search(r'<path id="Gesture stroke" d="([^"]+)"', mark).group(1)
dot_m = re.search(r'<path id="Dot" d="([^"]+)"', mark).group(1)
letters = re.search(r'<path id="innate letters" d="([^"]+)"', word).group(1)
idot = re.search(r'<path id="i dot" d="([^"]+)"', word).group(1)

def symbol(c, dot, h=None):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40.56 40.5" fill="none" overflow="visible"{f" height=\"{h}\"" if h else ""}>'
         f'<path d="{stroke_m}" stroke="{c}" stroke-width="6.6" stroke-linecap="round" stroke-linejoin="round"/><path d="{dot_m}" fill="{dot}"/></svg>')
    return s

def lockup(c, dot, h):
    """Primary lockup: symbol + wordmark on one baseline."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 228.17 43.73" fill="none" height="{h}" overflow="visible">'
            f'<g transform="translate(0 3.23)"><path d="{stroke_m}" stroke="{c}" stroke-width="6.6" stroke-linecap="round" stroke-linejoin="round"/><path d="{dot_m}" fill="{dot}"/></g>'
            f'<g transform="translate(54.56 0)"><path d="{letters}" stroke="{c}" stroke-width="6.49324" stroke-linecap="round" stroke-linejoin="round"/><path d="{idot}" fill="{dot}"/></g></svg>')

def gesture(c, op):
    """Supergraphic: the gesture stroke scaled up and cropped by the frame."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40.56 40.5" fill="none" overflow="visible">'
            f'<path d="{stroke_m}" stroke="{c}" stroke-opacity="{op}" stroke-width="6.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

INK, JADE, MINT = "#071A1C", "#11B88F", "#63E6BE"
FRAG = {
    "@LOCK_INK_26@": '<img src="@ASSETS@/lockup-ink.png" style="height:26px;display:block" alt="innate">', "@LOCK_INK_30@": '<img src="@ASSETS@/lockup-ink.png" style="height:30px;display:block" alt="innate">',
    "@LOCK_DARK_34@": '<img src="@ASSETS@/lockup-dark.png" style="height:34px;display:block" alt="innate">', "@LOCK_DARK_26@": '<img src="@ASSETS@/lockup-dark.png" style="height:26px;display:block" alt="innate">',
    "@SYM_DARK_44@": symbol("#fff", MINT, 44), "@SYM_INK_26@": symbol(INK, JADE, 26),
    "@GESTURE@": gesture(JADE, 0.2),
}
if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    t = Path(src).read_text()
    assets = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parents[1] / "assets"
    for k, v in FRAG.items(): t = t.replace(k, v)
    t = t.replace("@ASSETS@", "file://" + str(assets)).replace("@QR@", (assets / "qr-innate.svg").read_text()).replace("@MECH@", (assets / "mechanism-guide.svg").read_text())
    Path(dst).write_text(t)
