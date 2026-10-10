"""
Business & Workplace English Pro - Video Generator (9:16 Vertical Reel)
Executive workplace communication, email formulas, meeting phrases, and diplomatic professional phrasing.
"""
import os, sys, json, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
import edge_tts

load_dotenv()

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

BG_DARK = (15, 23, 42)           # Executive slate
NAVY_CARD = (30, 41, 59)
GOLD_ACCENT = (245, 158, 11)     # Amber / Gold
BLUE_ACCENT = (59, 130, 246)
GREEN_SUCCESS = (16, 185, 129)
WHITE = (255, 255, 255)

VOICE_CORP = "en-US-AvaNeural"

PHRASES = [
    {
        "category": "WORKPLACE EMAILS & DEADLINES",
        "blunt": "I need this done right now.",
        "pro": "Could you please prioritize this by end of day?",
        "formula": "Formula: Modal Verb (Could/Would) + Kindly/Please + Deadline (EOD/COB)",
        "context": "Use this phrase with colleagues to request urgent tasks without sounding bossy or rude!",
        "script": [
            "Want to sound like a senior executive in English emails?",
            "Never say: 'I need this done right now'! It sounds aggressive and demanding.",
            "Instead, say: 'Could you please prioritize this by end of day?' Save this for your career!"
        ]
    },
    {
        "category": "MEETING DISAGREEMENTS",
        "blunt": "You are completely wrong about this.",
        "pro": "I see your perspective, but I have a slightly different take.",
        "formula": "Formula: Acknowledge view ('I see your point') + Soft transition ('However/Different take')",
        "context": "Diplomatic disagreements keep workplace relationships positive and constructive!",
        "script": [
            "In business meetings, never say: 'You are completely wrong'!",
            "Diplomatic leaders say: 'I see your perspective, but I have a slightly different take.'",
            "This sounds professional and respectful! Follow Business English Pro for daily career hacks!"
        ]
    }
]

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def render_business_frame(item, step_idx, total_steps, out_path):
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(canvas)

    # Executive subtle gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(15 + ratio * 15)
        g = int(23 + ratio * 18)
        b = int(42 + ratio * 28)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Top Brand Header
    draw.rounded_rectangle([(70, 90), (WIDTH - 70, 180)], radius=22, fill=(24, 34, 60), outline=GOLD_ACCENT, width=3)
    f_hdr = load_font(32, bold=True)
    draw.text((WIDTH // 2, 135), "💼 BUSINESS & WORKPLACE ENGLISH PRO", fill=GOLD_ACCENT, font=f_hdr, anchor="mm")

    # Category Pill
    draw.rounded_rectangle([(70, 210), (WIDTH - 70, 280)], radius=16, fill=(30, 45, 80), outline=BLUE_ACCENT, width=2)
    f_cat = load_font(26, bold=True)
    draw.text((WIDTH // 2, 245), f"TOPIC: {item['category']}", fill=BLUE_ACCENT, font=f_cat, anchor="mm")

    # Hook Headline
    f_hook = load_font(50, bold=True)
    draw.text((WIDTH // 2, 345), "SOUND LIKE AN EXECUTIVE!", fill=WHITE, font=f_hook, anchor="mm")

    # 1. BLUNT / CASUAL CARD
    draw.rounded_rectangle([(70, 410), (WIDTH - 70, 660)], radius=26, fill=(40, 25, 35), outline=(239, 68, 68), width=3)
    f_tag = load_font(26, bold=True)
    draw.rounded_rectangle([(110, 435), (420, 485)], radius=12, fill=(239, 68, 68))
    draw.text((265, 460), "❌ TOO BLUNT / CASUAL", fill=WHITE, font=f_tag, anchor="mm")

    f_blunt = load_font(50, bold=True)
    draw.text((WIDTH // 2, 565), f'"{item["blunt"]}"', fill=(255, 180, 180), font=f_blunt, anchor="mm")

    # Arrow Down
    f_arr = load_font(44, bold=True)
    draw.text((WIDTH // 2, 720), "⬇️ EXECUTIVE UPGRADE ⬇️", fill=GOLD_ACCENT, font=f_arr, anchor="mm")

    # 2. PROFESSIONAL / DIPLOMATIC CARD
    draw.rounded_rectangle([(70, 780), (WIDTH - 70, 1080)], radius=26, fill=(18, 45, 40), outline=GREEN_SUCCESS, width=4)
    draw.rounded_rectangle([(110, 805), (460, 855)], radius=12, fill=GREEN_SUCCESS)
    draw.text((285, 830), "✅ POLITE & DIPLOMATIC", fill=WHITE, font=f_tag, anchor="mm")

    f_pro = load_font(52, bold=True)
    pwords = item["pro"].split()
    plines = []
    cp = []
    for pw in pwords:
        tb = draw.textbbox((0, 0), " ".join(cp + [pw]), font=f_pro)
        if tb[2] - tb[0] > (WIDTH - 240):
            plines.append(" ".join(cp))
            cp = [pw]
        else:
            cp = [pw]
    if cp: plines.append(" ".join(cp))
    for pl_idx, pl in enumerate(plines):
        draw.text((WIDTH // 2, 925 + pl_idx * 65), f'"{pl}"', fill=WHITE, font=f_pro, anchor="mm")

    # 3. EXECUTIVE FORMULA CARD
    draw.rounded_rectangle([(70, 1140), (WIDTH - 70, 1420)], radius=26, fill=NAVY_CARD, outline=GOLD_ACCENT, width=3)
    f_frm_lbl = load_font(30, bold=True)
    draw.text((110, 1185), "📐 THE PROFESSIONAL FORMULA:", fill=GOLD_ACCENT, font=f_frm_lbl, anchor="lm")

    f_frm_txt = load_font(36, bold=False)
    fwords = item["formula"].split()
    flines = []
    cf = []
    for fw in fwords:
        tb = draw.textbbox((0, 0), " ".join(cf + [fw]), font=f_frm_txt)
        if tb[2] - tb[0] > (WIDTH - 240):
            flines.append(" ".join(cf))
            cf = [fw]
        else:
            cf = [fw]
    if cf: flines.append(" ".join(cf))
    for fl_idx, fl in enumerate(flines):
        draw.text((110, 1250 + fl_idx * 50), fl, fill=WHITE, font=f_frm_txt, anchor="lm")

    # 4. CONTEXT / APPLICATION NOTE
    draw.rounded_rectangle([(70, 1470), (WIDTH - 70, 1710)], radius=24, fill=(22, 32, 58), outline=BLUE_ACCENT, width=2)
    f_ctx_lbl = load_font(28, bold=True)
    draw.text((110, 1515), "🎯 CAREER TIP:", fill=BLUE_ACCENT, font=f_ctx_lbl, anchor="lm")

    f_ctx_txt = load_font(34, bold=False)
    cwords = item["context"].split()
    clines = []
    cc = []
    for cw in cwords:
        tb = draw.textbbox((0, 0), " ".join(cc + [cw]), font=f_ctx_txt)
        if tb[2] - tb[0] > (WIDTH - 240):
            clines.append(" ".join(cc))
            cc = [cw]
        else:
            cc = [cw]
    if cc: clines.append(" ".join(cc))
    for cl_idx, cl in enumerate(clines):
        draw.text((110, 1575 + cl_idx * 48), cl, fill=(220, 230, 245), font=f_ctx_txt, anchor="lm")

    # Footer
    f_cta = load_font(32, bold=True)
    draw.text((WIDTH // 2, 1780), "👔 Save this phrase for your next email!", fill=GOLD_ACCENT, font=f_cta, anchor="mm")
    f_sub = load_font(26, bold=False)
    draw.text((WIDTH // 2, 1835), "Follow Business English Pro for career advancement!", fill=(148, 163, 184), font=f_sub, anchor="mm")

    canvas.convert("RGB").save(out_path, quality=95)

async def assemble_business_reel(item, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    audio_dir = run_dir / "audio"
    for d in [frames_dir, clips_dir, audio_dir]:
        d.mkdir(parents=True, exist_ok=True)

    clips = []
    total_steps = len(item["script"])

    for s_idx, text in enumerate(item["script"]):
        mp3_p = audio_dir / f"step_{s_idx}.mp3"
        await edge_tts.Communicate(text, VOICE_CORP, rate="-10%").save(str(mp3_p))

        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_p)],
            capture_output=True, text=True, check=True
        )
        dur = float(r.stdout.strip())

        frame_p = frames_dir / f"frame_{s_idx}.png"
        render_business_frame(item, s_idx, total_steps, str(frame_p))

        clip_p = clips_dir / f"clip_{s_idx}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(frame_p), "-i", str(mp3_p),
            "-vf", f"scale={WIDTH}:{HEIGHT},fps={FPS}",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-preset", "fast", "-t", f"{dur:.3f}", str(clip_p)
        ], check=True, capture_output=True)

        clips.append(clip_p)

    concat_txt = run_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    final_v = run_dir / "business_english_reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(final_v)], check=True, capture_output=True)
    return final_v

async def run_business_generation(idx=0):
    item = PHRASES[idx % len(PHRASES)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Business English] Generating Reel for: '{item['category']}'...")
    final_v = await assemble_business_reel(item, run_dir)

    meta = {
        "title": f"How to sound professional in English emails! 💼 Business English Pro",
        "description": f"Upgrade your workplace English communication! Don't say '{item['blunt']}', say '{item['pro']}'. Formula: {item['formula']}. Follow Business English Pro for daily career hacks! 👔📊",
        "category": item["category"]
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[Business English] Video ready: {final_v}")
    return final_v, meta
