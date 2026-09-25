#!/usr/bin/env python3
"""
Generates the animated star-field SVGs for the profile README.

This mimics the effect from my website:
three star layers of increasing size that drift at different speeds
(parallax), except here every star also gently fades in and out.

Why SVG? GitHub strips <script> and most CSS from READMEs, but SVG
animations (SMIL) still run when the SVG is displayed as an image.
"""

W, H = 880, 260		# banner viewport
FIELD = 2 * H		# star field
SEED = 42069
TITLE = "Hello, I'm Lucas 👋"

# (radius, star count, drift duration in seconds)
# (counts are scaled down since this is a banner, not a full viewport)
LAYERS = [
    (0.8, 90, 50),
    (1.3, 40, 100),
    (2.0, 15, 150),
]

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

    dur = 1.8 + rnd() * 3.4			# twinkle cycle
    begin = -rnd() * dur			# negative begin = phase offset
    o_min = 0.05 + rnd() * 0.15
    o_max = 0.30 + rnd() * 0.25

    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="FILL" opacity="{o_min:.2f}">\n'
        f'  <animate attributeName="opacity" values="{o_min:.2f};{o_max:.2f};{o_min:.2f}" '
        f'keyTimes="0;0.5;1" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1" '
        f'dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
        f'</circle>'
    )

def make_svg(fill, text_fill):
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
        f.write(make_svg("#000000", "#222222"))
    with open("stars-dark.svg", "w") as f:
        f.write(make_svg("#ffffff", "#eeeeee"))
    print("wrote stars-light.svg and stars-dark.svg")
