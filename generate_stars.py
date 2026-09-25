#!/usr/bin/env python3
"""
Generates the animated star-field SVGs for the profile README.

This mirrors the effect from my website (1vke.github.io/static/js/stars.js):
three star layers of increasing size that drift at different speeds
(parallax), except here the stars also gently fade in and out.

Why SVG? GitHub strips <script> and most CSS from READMEs, but SVG
animations (SMIL) still run when the SVG is displayed as an image.

Size trick #1: each layer is a <pattern> tile, so the seamless drift loop
is free — the pattern tiles infinitely and no star markup is duplicated.
Size trick #2: stars fade in "twinkle groups" sharing one <animate> each
(random membership + random phase/duration keeps it looking organic).

Trade-off: the tile is half the banner wide, so the left and right halves
repeat. Also, SMIL inside <pattern> content is not animated consistently
across browsers (Safari is the risky one) — see git history for the
non-pattern fallback if this ever breaks.
"""

W, H = 880, 260          # banner viewport
TW, TH = 440, 520        # pattern tile: half banner wide, field-height tall
SEED = 42069             # same seed as the website, lol
TITLE = "Hello, I'm Lucas 👋"

# (star count per tile, drift duration in seconds)
# Mirrors the website's layers: 700/50s, 200/100s, 100/150s, scaled down
# for a banner. Counts are per 440px-wide tile (two tiles cover the width).
LAYERS = [
    (45, 50),
    (20, 100),
    (8, 150),
]

TWINKLE_GROUPS = 6  # fade groups per layer; more = more organic, more markup


# LCG stands for "Linear Congruential Generator". ✨ The more you know ✨
def lcg(seed):
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2147483648
        yield state / 2147483648


def make_svg(star_fill, text_fill):
    gen = lcg(SEED)
    rnd = lambda: next(gen)
    patterns = []

    for count, drift in LAYERS:
        # Split this layer's stars into twinkle groups. Each group gets
        # ONE shared fade animation; stars are assigned randomly so the
        # groups aren't spatially clumped.
        groups = [[] for _ in range(TWINKLE_GROUPS)]
        for _ in range(count):
            groups[int(rnd() * TWINKLE_GROUPS)].append(
                f'<circle cx="{rnd() * TW:.0f}" cy="{rnd() * TH:.0f}" r="{0.7 + rnd() * 1.4:.1f}"/>'
            )

        group_markup = ""
        for stars in groups:
            if not stars:
                continue
            dur = 2 + rnd() * 4
            begin = -rnd() * dur
            o_min = 0.05 + rnd() * 0.15
            o_max = 0.4 + rnd() * 0.35
            group_markup += (
                f'<g fill="{star_fill}" opacity="{o_min:.2f}">'
                f'<animate attributeName="opacity" values="{o_min:.2f};{o_max:.2f};{o_min:.2f}" '
                f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
                + "".join(stars) + '</g>'
            )

        patterns.append(group_markup)

    defs = "".join(
        f'<pattern id="p{i}" width="{TW}" height="{TH}" patternUnits="userSpaceOnUse">' + p + '</pattern>'
        for i, p in enumerate(patterns)
    )

    # One rect per layer, painted with that layer's pattern. The rect is
    # tall enough that translating it up by one tile-height (the pattern
    # period) loops seamlessly while always covering the viewport.
    rects = "".join(
        f'<rect x="0" y="-{TH}" width="{W}" height="{3 * TH}" fill="url(#p{i})">'
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 -{TH}" '
        f'dur="{LAYERS[i][1]}s" repeatCount="indefinite"/></rect>'
        for i in range(len(LAYERS))
    )

    # The heading rides on top of the star field. It sits outside the
    # drifting layers, so the stars move (and twinkle) behind it.
    heading = (
        f'<text x="{W / 2}" y="{H / 2}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" '
        f'font-size="44" font-weight="700" fill="{text_fill}">{TITLE}</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{TITLE} — stars fading in and out">\n'
        f'<defs>{defs}</defs>\n{rects}\n{heading}\n</svg>\n'
    )


if __name__ == "__main__":
    with open("stars-light.svg", "w") as f:
        f.write(make_svg("#000", "#222"))
    with open("stars-dark.svg", "w") as f:
        f.write(make_svg("#fff", "#eee"))
    print("wrote stars-light.svg and stars-dark.svg")
