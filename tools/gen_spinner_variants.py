#!/usr/bin/env python3
"""Generate gitar-spin variants for badge rendering tests.

Ink bbox, measured with getBBox in a browser rather than estimated: x[2.00, 13.94],
y[2.51, 13.47], so the centre is (7.97, 7.99), i.e. the ink is already centred in the
16x16 box and rotating about (8, 8) is the right origin.

What does clip: the corner-to-centre radius is 8.13 against a half-box of 8, and the
jitter adds up to 0.99 more. So the ink needs to be about 14% smaller to spin inside
the box. Scaling about the centre is the fix. #4 padded the viewBox instead, which
keeps the same overflow while shrinking the glyph inside a bigger transparent margin.

Usage: python3 tools/gen_spinner_variants.py
Writes assets/lab/*.svg and prints the variant table.
"""

import pathlib

NOTCH = "m6.809 6.09-.657 2.187h1.172l.66-2.187zm0 0"
BODY = (
  "M6.707 2.613c-1.89-.36-3.039.219-3.758 1.403C2.355 4.988 2 6.512 2 8.02a9.4 9.4 0 0 0 "
  ".414 2.793h4.14l.305-.993H4.992c-.226 0-.402-.082-.52-.254H4.47a.68.68 0 0 1-.078-.57l."
  "156-.527.973-3.223a.94.94 0 0 1 .335-.484.9.9 0 0 1 .57-.215h2.72c.23 0 .41.086.52.265a."
  "68.68 0 0 1 .073.586q-.214.721-.441 1.438-.189.634-.383 1.273l2.629-1.086c.047-.023.098-"
  ".035.148-.023.055.008.098.04.133.074a.24.24 0 0 1 .063.262l-.309 1.02a.21.21 0 0 1-.144."
  "164L8.422 9.754s-.207.683-.277.933q-.14.474-.286.954a.1.1 0 0 0-.011.03l-.02.048a.94.94 0"
  " 0 1-.355.437.87.87 0 0 1-.535.192H3.184c.796.953 2.222 1.363 3.539.984 3.222-.922 7.222-"
  "2.98 7.222-5.312 0-2.329-4.082-4.801-7.238-5.407m0 0"
)

FILL = "#9966CC"
INK_CENTER = (7.97, 7.99)  # measured, not estimated

JITTER_STOPS = [(0, 0), (0.8, -0.5), (-0.7, 0.7), (0.5, 0.4), (0, 0), (0, 0)]


def jitter(amp=1.0):
  """Wobble, scaled by amp. The wobble is what forces the ink to shrink: the ink has to
  fit its own rotation circle (radius 8.108) plus the wobble inside a half-box of 8."""
  vals = "; ".join(f"{round(x * amp, 3)} {round(y * amp, 3)}" for x, y in JITTER_STOPS)
  return (
    '<animateTransform attributeName="transform" calcMode="spline" dur="3.2s"'
    ' keySplines="0.2 0 0.2 1; 0.2 0 0.2 1; 0.2 0 0.2 1; 0.25 0 0.6 1; 0 0 1 1"'
    ' keyTimes="0;0.12;0.28;0.46;0.58;1" repeatCount="indefinite" type="translate"'
    f' values="{vals}"/>'
  )


def spin(cx, cy):
  return (
    '<animateTransform attributeName="transform" calcMode="spline" dur="3.2s"'
    ' keySplines="0.08 0 0.22 1; 0 0 1 1" keyTimes="0;0.60;1" repeatCount="indefinite"'
    f' type="rotate" values="0 {cx} {cy}; 1440 {cx} {cy}; 1440 {cx} {cy}"/>'
  )


def svg(size, view_box, spin_center=(8, 8), recenter_scale=None, jitter_amp=1.0):
  """Build one variant.

  recenter_scale: if set, wrap the ink in a static transform that moves its true
  centre to the middle of a 16x16 box and scales it, so a full rotation plus the
  jitter stays inside the viewBox.
  """
  ink = f'<g fill="{FILL}" fill-rule="evenodd">{spin(*spin_center)}<path d="{NOTCH}"/><path d="{BODY}"/></g>'
  if recenter_scale is not None:
    tx, ty = INK_CENTER
    ink = f'<g transform="translate(8 8) scale({recenter_scale}) translate({-tx} {-ty})">{ink}</g>'
  inner = (jitter(jitter_amp) if jitter_amp else "") + ink
  return (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
    f' viewBox="{view_box}"><g>{inner}</g></svg>'
  )


# label -> (file, svg, what it isolates)
VARIANTS = {
  "a-16-orig": (
    svg(16, "0 0 16 16"),
    "baseline, what main serves after the revert",
  ),
  "b-13-padded": (
    svg(13, "-1.195 -1.155 18.5 18.5"),
    "the reverted #4 asset, kept so we can see the bad render side by side",
  ),
  "c-13-plain": (
    svg(13, "0 0 16 16"),
    "just smaller, no viewBox games - does 13px alone look wrong",
  ),
  "d-16-centered": (
    svg(16, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.92),
    "spin about the ink centre and scale 0.92 - no clipping, intrinsic size stays 16",
  ),
  "e-13-centered": (
    svg(13, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.92),
    "same fix rendered at 13",
  ),
  # Round 3. Correct geometry fix: keep viewBox 0 0 16 16 and the (8, 8) rotation
  # origin, just scale the ink so a full spin plus the jitter stays inside the box.
  # 8 / 8.13 = 0.98 covers the spin, 7.01 / 8.13 = 0.86 also covers the jitter.
  "i-11-scaled": (
    svg(11, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.86),
    "11px, ink scaled 0.86 - spin and jitter both fit",
  ),
  "j-11-plain": (
    svg(11, "0 0 16 16"),
    "11px, unscaled - control, clips by ~1 unit at the extremes",
  ),
  "k-12-scaled": (
    svg(12, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.86),
    "same fix at 12px",
  ),
  "l-11-nojitter": (
    svg(11, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.98, jitter_amp=0),
    "11px, no jitter, so the ink only has to fit the spin - biggest glyph of the three",
  ),
  # The shipping candidate: intrinsic 16 so markup can cap it at any size <= 16, ink
  # scaled so a full spin plus jitter never leaves the box.
  "n-16-scaled": (
    svg(16, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.86),
    "intrinsic 16, ink scaled 0.86 - size it from the markup",
  ),
  "o-16-jit50": (
    svg(16, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.925, jitter_amp=0.5),
    "half wobble, ink 0.925 - largest that still clears at 50% jitter",
  ),
  "p-16-jit25": (
    svg(16, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.956, jitter_amp=0.25),
    "quarter wobble, ink 0.956",
  ),
  "q-16-nojit": (
    svg(16, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.986, jitter_amp=0),
    "no wobble, ink 0.986 - biggest glyph that never clips",
  ),
  "h-14-centered": (
    svg(14, "0 0 16 16", spin_center=INK_CENTER, recenter_scale=0.92),
    "same fix at 14, closest to the text cap height",
  ),
  "f-16-nospin": (
    svg(16, "0 0 16 16", spin_center=(8, 8), jitter_amp=0).replace(spin(8, 8), ""),
    "static glyph, no animation - control for whether animation is the problem",
  ),
  "g-13-tight": (
    svg(13, "2 2.4 11.95 11.95", spin_center=INK_CENTER),
    "viewBox cropped to the ink so the glyph fills the box - clips while spinning",
  ),
}


def main():
  out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "lab"
  out.mkdir(parents=True, exist_ok=True)
  for name, (body, note) in VARIANTS.items():
    (out / f"{name}.svg").write_text(body + "\n")
    print(f"{name:<16} {len(body):>5}b  {note}")


if __name__ == "__main__":
  main()
