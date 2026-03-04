# Vappulaskuri

A countdown website to Vappu (Finnish May Day celebration, April 30 - May 1).

## Project Structure

- `index.html` — Single-page site with inline CSS/JS, no build system
- `yolakki.svg` — Ylioppilaslakki (Finnish student cap) vector graphic with transparent background and white glow filter
- `yolakki.png` — Original raster version (white background, not used)
- `havis.png` — Havis Amanda with student cap (used for og:image)
- `.github/workflows/main.yml` — Deploys to FTP on push to master
- `.github/renovate.json` — Renovate config with automerge

## Design

- **Aesthetic**: Nordic spring festival / twilight-to-dawn gradient sky
- **Background**: Linear gradient from midnight blue through purple/pink to golden sunrise
- **Fonts**: DM Serif Display (headings) + Outfit (countdown numbers/labels) via Google Fonts
- **Countdown**: Glassmorphism cards with frosted glass effect, hover lift animation
- **Ylioppilaslakki**: Must be white crown + black band/brim (traditional colors). Uses SVG with white glow filter so dark parts are visible against the dark background
- **Vappu mode**: When date is April 30 - May 1, shows "Nyt on vappu!!!" with pulsing glow and confetti animation
- **Stars**: Twinkling star effect in the upper portion of the sky

## Deployment

- FTP deploy via `SamKirkland/FTP-Deploy-Action` on push to master
- Server credentials in GitHub secrets: `FTP_HOST`, `FTP_USER`, `FTP_PASS`
- `.github` folder is excluded from FTP upload
- Target directory: `public_html/`
- Google Analytics: G-8S1MBDVCX2

## Countdown Logic

- Vappu starts at vappuaatto (April 30) midnight
- Vappu ends May 1 at 23:59
- After May 1, countdown targets next year's Vappu
- Finnish labels with correct singular/plural forms (päivä/päivää, tunti/tuntia, etc.)
- No external countdown library — self-contained JS with `setInterval`
