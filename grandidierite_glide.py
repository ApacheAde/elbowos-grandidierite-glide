#!/usr/bin/env python3
"""Grandidierite Glide — neon canal-slalom arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/GRANDIDIERITE_GLIDE_ElbowOS.mp4")
CYAN, AMBER, MAG, LIME = (70, 255, 226), (255, 186, 64), (255, 64, 168), (168, 255, 90)
RED, WHITE, INK = (255, 58, 72), (244, 250, 255), (5, 10, 24)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        try:
            self.screen = pygame.display.set_mode((W, H), 0 if PLAY else pygame.HIDDEN)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        self.font = pygame.font.SysFont("dejavusans", 58, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = self.score = self.flash = self.spawn_acc = self.passed = 0
        self.lives, self.skiff_x, self.skiff_vx, self.scroll = 3, W / 2, 0.0, 0.0
        self.gates, self.orbs, self.shards, self.wake = [], [], [], []
        random.seed(11)

    def spawn(self):
        y, roll = -90, random.random()
        if roll < 0.55:
            gap = random.randint(250, 360)
            cx = random.randint(240, W - 240)
            hue = random.choice([AMBER, MAG, LIME, CYAN])
            self.gates.append({"y": y, "cx": cx, "gap": gap, "hue": hue, "alive": True})
            self.orbs.append({"x": cx, "y": y - 70, "c": hue, "r": 20})
        elif roll < 0.82:
            for i in range(5):
                self.orbs.append({
                    "x": 160 + i * 190 + random.randint(-20, 20),
                    "y": y, "c": random.choice([AMBER, MAG, LIME, CYAN]), "r": 18,
                })
        else:
            self.shards.append({
                "x": random.randint(140, W - 140), "y": y,
                "vx": random.choice([-2.4, 2.4]), "r": 30,
            })

    def update(self, steer):
        self.t += 1
        speed = 10 + min(9, self.t / 80)
        self.scroll += speed
        self.skiff_vx = self.skiff_vx * 0.84 + steer * 2.1
        self.skiff_x = max(100, min(W - 100, self.skiff_x + self.skiff_vx))
        self.wake.append((self.skiff_x, 1488, 1.0))
        self.wake = [(x, y + speed * 0.35, a - 0.045) for x, y, a in self.wake if a > 0.05][-36:]
        self.spawn_acc += 1
        if self.spawn_acc > max(16, 32 - self.t // 70):
            self.spawn_acc = 0
            self.spawn()
        sy = 1468
        for g in self.gates:
            g["y"] += speed
            if g["alive"] and sy - 24 < g["y"] < sy + 36:
                if abs(self.skiff_x - g["cx"]) < g["gap"] / 2 - 18:
                    self.score += 25
                    self.passed += 1
                    self.flash = 8
                else:
                    self.lives -= 1
                    self.flash = -8
                g["alive"] = False
        self.gates = [g for g in self.gates if g["y"] < H + 90]
        kept = []
        for o in self.orbs:
            o["y"] += speed
            if (o["x"] - self.skiff_x) ** 2 + (o["y"] - sy) ** 2 < 68 ** 2:
                self.score += 10
                self.flash = 6
            elif o["y"] < H + 30:
                kept.append(o)
        self.orbs = kept
        kept = []
        for s in self.shards:
            s["y"] += speed * 0.9
            s["x"] += s["vx"]
            if s["x"] < 100 or s["x"] > W - 100:
                s["vx"] *= -1
            if (s["x"] - self.skiff_x) ** 2 + (s["y"] - sy) ** 2 < (s["r"] + 34) ** 2:
                self.lives -= 1
                self.flash = -10
            elif s["y"] < H + 40:
                kept.append(s)
        self.shards = kept
        if self.lives <= 0:
            keep = self.score
            self.reset()
            self.score = keep
        if self.flash:
            self.flash += -1 if self.flash > 0 else 1

    def ai(self):
        sy, target, best = 1468, W / 2, None
        for g in self.gates:
            if g["alive"] and g["y"] < sy and (best is None or g["y"] > best["y"]):
                best = g
        if best:
            target = best["cx"]
        for s in self.shards:
            if 980 < s["y"] < sy + 30 and abs(s["x"] - self.skiff_x) < 150:
                target = 200 if s["x"] > self.skiff_x else W - 200
                break
        for o in self.orbs:
            if 1180 < o["y"] < sy and abs(o["x"] - target) < 90:
                target = o["x"]
                break
        if self.skiff_x < target - 16:
            return 1
        if self.skiff_x > target + 16:
            return -1
        return 0

    def draw(self, surf):
        pulse = 0.5 + 0.5 * math.sin(self.t * 0.12)
        for i in range(0, H, 10):
            k = i / H
            surf.fill((int(6 + 14 * k), int(22 + 48 * k + 8 * pulse), int(42 + 46 * k)), (0, i, W, 10))
        off = int(self.scroll) % 180
        for y in range(-180, H + 180, 180):
            yy = y + off
            pygame.draw.line(surf, (28, 90, 120), (90, yy), (W - 90, yy), 2)
            pygame.draw.arc(surf, (40, 140, 160), (200, yy - 20, 280, 50), 0.2, 2.6, 2)
        pygame.draw.rect(surf, (10, 36, 52), (0, 0, 64, H))
        pygame.draw.rect(surf, (10, 36, 52), (W - 64, 0, 64, H))
        for y in range(0, H, 80):
            pygame.draw.circle(surf, CYAN, (26, (y + int(self.scroll * 0.6)) % H), 7)
            pygame.draw.circle(surf, MAG, (W - 26, (y + 36 + int(self.scroll * 0.6)) % H), 7)
        for x, y, a in self.wake:
            pygame.draw.circle(surf, (int(70 * a), int(230 * a), int(220 * a)), (int(x), int(y)), int(14 * a) + 2)
        for g in self.gates:
            left, right = int(g["cx"] - g["gap"] / 2), int(g["cx"] + g["gap"] / 2)
            col = g["hue"] if g["alive"] else (50, 62, 74)
            pygame.draw.rect(surf, col, (64, int(g["y"]) - 16, max(0, left - 64), 32), border_radius=10)
            pygame.draw.rect(surf, col, (right, int(g["y"]) - 16, max(0, W - 64 - right), 32), border_radius=10)
            pygame.draw.circle(surf, WHITE, (left, int(g["y"])), 12)
            pygame.draw.circle(surf, WHITE, (right, int(g["y"])), 12)
        for o in self.orbs:
            pygame.draw.circle(surf, o["c"], (int(o["x"]), int(o["y"])), o["r"])
            pygame.draw.circle(surf, WHITE, (int(o["x"]), int(o["y"])), o["r"], 3)
        for s in self.shards:
            ang = self.t * 0.22 + s["x"] * 0.01
            pts = [(s["x"] + math.cos(ang + k * 1.57) * s["r"], s["y"] + math.sin(ang + k * 1.57) * s["r"]) for k in range(4)]
            pygame.draw.polygon(surf, RED, pts)
            pygame.draw.polygon(surf, WHITE, pts, 2)
        sx, sy = int(self.skiff_x), 1468
        hull = [(sx, sy - 54), (sx + 40, sy + 30), (sx, sy + 14), (sx - 40, sy + 30)]
        pygame.draw.polygon(surf, CYAN, hull)
        pygame.draw.polygon(surf, WHITE, hull, 3)
        pygame.draw.polygon(surf, AMBER, [(sx, sy - 28), (sx + 12, sy + 4), (sx - 12, sy + 4)])
        ring = (255, 255, 210) if self.flash > 0 else RED if self.flash < 0 else None
        if ring:
            pygame.draw.circle(surf, ring, (sx, sy), 78, 4)
        banner = pygame.Surface((W, 250), pygame.SRCALPHA)
        banner.fill((5, 12, 28, 150))
        surf.blit(banner, (0, 28))
        title = self.font.render("GRANDIDIERITE GLIDE", True, CYAN)
        surf.blit(title, title.get_rect(center=(W // 2, 92)))
        sub = self.tiny.render("neon canal slalom", True, AMBER)
        surf.blit(sub, sub.get_rect(center=(W // 2, 148)))
        surf.blit(self.small.render(f"SCORE  {self.score}", True, WHITE), (72, 188))
        surf.blit(self.small.render("LIVES  " + "●" * max(0, self.lives), True, MAG), (72, 234))
        foot = pygame.Surface((W, 110), pygame.SRCALPHA)
        foot.fill((5, 12, 28, 160))
        surf.blit(foot, (0, H - 120))
        tag = self.small.render("x.com/ElbowOS", True, LIME)
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 64)))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        surf = pygame.Surface((W, H))
        raw = getattr(pygame.image, "tobytes", pygame.image.tostring)
        try:
            for _ in range(FPS * SECS):
                self.update(self.ai())
                self.draw(surf)
                proc.stdin.write(raw(surf, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT, "score", self.score)

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            steer = 0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                steer -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                steer += 1
            if keys[pygame.K_ESCAPE]:
                running = False
            self.update(steer)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()
        pygame.quit()


if __name__ == "__main__":
    main()
