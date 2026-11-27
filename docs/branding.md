# The Lombo look

## Contents

- [The rule](#the-rule)
- [Colours and type](#colours-and-type)
- [The seal and the L](#the-seal-and-the-l)
- [LomboSaga's own mark](#lombosagas-own-mark)
- [What every app needs](#what-every-app-needs)
- [What to avoid](#what-to-avoid)

## The rule

**The Lombo L is in every icon.** Each app has its own seal, and a small mark of its own sits in
the open corner of the L. Each app also gets one wordmark trick (Tier's letters step down,
Shrink's get smaller from S to K, Shelf's F leans).

## Colours and type

| Use | Value |
|---|---|
| Background | `#0d0a08` |
| Surface | `#1a140f` |
| Borders | `#2c231a`, `#443528` |
| Text, muted | `#f4ede3`, `#b3a696` |
| Ember gradient | `#ffb347` to `#ff6a1a` to `#e23d0f` |

Headings and wordmarks: Cinzel (SIL Open Font License). Body text: Geist.

## The seal and the L

The seal is a ring with the gradient, an inner frame line, and the L. Banners use the same seal on
the left and the wordmark on the right.

## LomboSaga's own mark

An **open book with a ribbon** sits in the L's open corner. The wordmark trick: **the letters of SAGA grow**, one volume after another.

## What every app needs

- `assets/icon.svg`, plus `assets/icon-512.png` for the container registry and GitHub.
- `assets/banner.svg` and `banner.png`, shown at the top of the README (1200 x 300).
- `assets/social-preview.svg` and `social-preview.png` (1280 x 640), uploaded in the repository settings.

SVG text uses fonts the viewer may not have, so the PNG versions are exported with Cinzel installed
(see the `forge-branding` skill in the workspace) and used where exact lettering matters.

## What to avoid

- No Tolkien names, scripts, rings or symbols. The feel comes from engraved capitals, a map-style
  frame and the forge colours, not from borrowed imagery.
- No logos, names or colours of other products. "For Jellyfin" is fine in a description; never
  imply the Jellyfin project or any other product made the app.
