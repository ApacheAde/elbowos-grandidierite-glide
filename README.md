# Grandidierite Glide

Full-colour Python 3 neon canal-slalom arcade for [ElbowOS](https://x.com/ElbowOS).

Steer a crystal skiff down a frozen teal canal. Thread the glowing gate gaps, snatch colour orbs, and dodge spinning red ice shards. Not a clone of the existing pinball, volley, tide-hopper, or brick-breaker packs.

## Play

```bash
pip install -r requirements.txt
python3 grandidierite_glide.py --play
```

A / Left and D / Right steer. R restarts. Esc quits.

## Record a 9:16 reel

```bash
python3 grandidierite_glide.py --record
```

Headless autoplay writes a 1080x1920, 15-second, 30fps H.264 MP4 (`SDL_VIDEODRIVER=dummy`, libx264 yuv420p, CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1sGTnHLsJpCvt92qcfblRXI1RtZEQRtkE/view?usp=drivesdk
- Repo: https://github.com/ApacheAde/elbowos-grandidierite-glide
