#!/usr/bin/env python3
"""
Generates the animated star-field SVGs for the profile README.

This mirrors the effect from my website (1vke.github.io/static/js/stars.js):
three star layers of increasing size that drift at different speeds
(parallax), except here every star also gently fades in and out.

Why SVG? GitHub strips <script> and most CSS from READMEs, but SVG
animations (SMIL) still run when the SVG is displayed as an image.
"""

W, H = 880, 260          # banner viewport
FIELD = 2 * H            # star field spans 2x the viewport (like the site's 200dvh)
SEED = 42069             # same seed as the website, lol

# (radius, star count, drift duration in seconds)
# Mirrors the website's layers: 1px/700/50s, 2px/200/100s, 3px/100/150s
# (counts are scaled down since this is a banner, not a full viewport)
LAYERS = [
    (0.8, 90, 50),
    (1.3, 40, 100),
    (2.0, 15, 150),
]


# LCG stands for "Linear Congruential Generator". ✨ The more you know ✨
def lcg(seed):
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2147483648
        yield state / 2147483648


def star(rnd):
    """One twinkling star as a <circle> element."""
    x = rnd() * W
    y = rnd() * FIELD
    r = 0.7 + rnd() * 1.4

    dur = 1.8 + rnd() * 3.4        # twinkle cycle
    begin = -rnd() * dur           # negative begin = phase offset
    o_min = 0.05 + rnd() * 0.15
    o_max = 0.30 + rnd() * 0.25    # peaks around 0x7a alpha (~0.48), like the site

    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="FILL" opacity="{o_min:.2f}">\n'
        f'  <animate attributeName="opacity" values="{o_min:.2f};{o_max:.2f};{o_min:.2f}" '
        f'keyTimes="0;0.5;1" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" '
        f'dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
        f'</circle>'
    )


def make_svg(fill):
    gen = lcg(SEED)
    rnd = lambda: next(gen)
    layers = []
    for _, count, duration in LAYERS:
        stars = "\n".join(star(rnd) for _ in range(count)).replace("FILL", fill)
        layers.append(
            f'<g>\n'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 0" to="0 -{FIELD}" dur="{duration}s" repeatCount="indefinite"/>\n'
            f'<g>\n{stars}\n</g>\n'
            f'<g transform="translate(0 {FIELD})">\n{stars}\n</g>\n'
            f'</g>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Stars drifting and fading in and out">\n'
        + "\n".join(layers) + "\n</svg>\n"
    )


if __name__ == "__main__":
    with open("stars-light.svg", "w") as f:
        f.write(make_svg("#000000"))
    with open("stars-dark.svg", "w") as f:
        f.write(make_svg("#ffffff"))
    print("wrote stars-light.svg and stars-dark.svg")
