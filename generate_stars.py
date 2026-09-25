#!/usr/bin/env python3
"""
Generates the animated star-field SVGs for the profile README.

This mirrors the effect from my website (1vke.github.io/static/js/stars.js):
three star layers of increasing size that drift at different speeds
(parallax), except here the stars also gently fade in and out.

Why SVG? GitHub strips <script> and most CSS from READMEs, but SVG
animations (SMIL) still run when the SVG is displayed as an image.

Size trick: instead of one fade animation per star, stars are split into
a few "twinkle groups" that share a single <animate> each (random
membership + random phase/duration per group keeps it looking organic).
Each layer is emitted twice — offset by one field-height — so the
vertical drift loops seamlessly, just like the site's 200dvh duplicate.
"""

W, H = 880, 260          # banner viewport
FIELD = 2 * H            # star field spans 2x the viewport
SEED = 42069             # same seed as the website, lol
TITLE = "Hello, I'm Lucas 👋"

# (star count, drift duration in seconds)
# Mirrors the website's layers: 700/50s, 200/100s, 100/150s,
# scaled down since this is a banner, not a full viewport.
LAYERS = [
    (90, 50),
    (40, 100),
    (15, 150),
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
    layers = []

    for count, drift in LAYERS:
        # Split this layer's stars into twinkle groups. Each group gets
        # ONE shared fade animation; stars are assigned randomly so the
        # groups aren't spatially clumped.
        groups = [[] for _ in range(TWINKLE_GROUPS)]
        for _ in range(count):
            groups[int(rnd() * TWINKLE_GROUPS)].append(
                f'<circle cx="{rnd() * W:.0f}" cy="{rnd() * FIELD:.0f}" r="{0.7 + rnd() * 1.4:.1f}"/>'
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

        layers.append(
            f'<g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="0 -{FIELD}" dur="{drift}s" repeatCount="indefinite"/>'
            + group_markup
            + f'<g transform="translate(0 {FIELD})">' + group_markup + '</g>'
            f'</g>'
        )

    # The heading rides on top of the star field. It sits outside the
    # drifting <g> layers, so the stars move (and twinkle) behind it.
    heading = (
        f'<text x="{W / 2}" y="{H / 2}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" '
        f'font-size="44" font-weight="700" fill="{text_fill}">{TITLE}</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{TITLE} — stars fading in and out">\n'
        + "\n".join(layers) + "\n"
        + heading + "\n</svg>\n"
    )


if __name__ == "__main__":
    with open("stars-light.svg", "w") as f:
        f.write(make_svg("#000", "#222"))
    with open("stars-dark.svg", "w") as f:
        f.write(make_svg("#fff", "#eee"))
    print("wrote stars-light.svg and stars-dark.svg")
