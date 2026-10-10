"""
BUSINESS ENGLISH PRO PODCAST - 16:9 FULL HD (1920x1080) VIDEO GENERATOR
Theme: Executive Penthouse Studio & Wall Street Broadcast Booth
Visuals: Illuminated "ON AIR" Lightbox + Brass Executive Mics + 24-Channel dB Peak Meter + Single-Line Highlighted Subtitles
"""
import os, sys, json, math, subprocess, random, requests, re, asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
import edge_tts

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

load_dotenv()

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
SUBFRAMES_PER_SEC = 2

EXECUTIVE_GOLD = (245, 158, 11)
PLATINUM = (226, 232, 240)
NAVY_ACCENT = (30, 58, 138)
ON_AIR_RED = (239, 68, 68)
WHITE = (255, 255, 255)
DARK_BG = (10, 16, 32)
CARD_BG = (18, 28, 52)
CARD_BORDER = (45, 68, 110)
MUTED_TEXT = (160, 178, 205)

EMMA_VOICE = "en-US-AvaNeural"
ANDREW_VOICE = "en-US-AndrewNeural"
VOICE_RATE = "-15%"

TOPICS = [
    {
        "topic": "How to Ask for Urgent Deadlines Politely in Workplace Emails",
        "category": "EMAIL DIPLOMACY & DEADLINES",
        "phrase": "COULD YOU PLEASE PRIORITIZE THIS BY EOD?",
        "keyword": "PRIORITIZE",
        "sub": "SOUND PROFESSIONAL NOT AGGRESSIVE"
    },
    {
        "topic": "Diplomatic Disagreements: How to Disagree Respectfully in Meetings",
        "category": "MEETING COMMUNICATION",
        "phrase": "I SEE YOUR PERSPECTIVE BUT HAVE A SLIGHTLY DIFFERENT TAKE",
        "keyword": "PERSPECTIVE",
        "sub": "CONSTRUCTIVE WORKPLACE DIALOGUE"
    },
    {
        "topic": "Salary Negotiation and Career Advancement Phrasing",
        "category": "CAREER ADVANCEMENT",
        "phrase": "BASED ON MY RECENT DELIVERABLES AND MARKET STANDARDS",
        "keyword": "DELIVERABLES",
        "sub": "CONFIDENT VALUE-DRIVEN CONVERSATIONS"
    }
]

def load_font(size, bold=True):
    fonts_to_try = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/trebucbd.ttf" if bold else "C:/Windows/Fonts/trebuc.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in fonts_to_try:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: continue
    return ImageFont.load_default()

def clean_text(text):
    text = re.sub(r'\b(mm+|um+|uh+|ah+)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_script_ai(topic_item, target_turns=6):
    prompt = f"""Write {target_turns} turns of a slow, clear English podcast between Emma and Andrew.
Topic: {topic_item['topic']}
Category: {topic_item['category']}
Key Executive Phrasing: {topic_item['phrase']}

RULES:
- Dialogue alternating between Host1 (Emma) and Host2 (Andrew)
- Each turn MUST be 2-3 short, clear sentences (18-28 words)
- Focus on practical workplace formulas: replacing blunt demands with polite, diplomatic corporate language
- Wrap exactly 1 key learning word per turn in **asterisks**
- Return as clean JSON array only:
[{{"speaker":"Host1","text":"..."}},{{"speaker":"Host2","text":"..."}}]"""

    key = os.getenv("POLLINATIONS_API_KEY")
    if key:
        try:
            resp = requests.post("https://gen.pollinations.ai/v1/chat/completions", json={
                "model": "gemini-fast",
                "messages": [
                    {"role": "system", "content": "You write professional, natural business English podcast dialogue. Wrap 1 key word per turn in **asterisks**."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8
            }, headers={"Authorization": f"Bearer {key}"}, timeout=60)
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"].strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw: raw = raw.split("```")[1].split("```")[0].strip()
                script = json.loads(raw)
                if isinstance(script, list) and len(script) > 0:
                    for i, turn in enumerate(script):
                        turn["speaker"] = "Host1" if i % 2 == 0 else "Host2"
                        turn["text"] = clean_text(turn["text"])
                        if "**" not in turn["text"]:
                            words = turn["text"].split()
                            if len(words) > 2:
                                idx = len(words) // 2
                                words[idx] = f"**{words[idx]}**"
                                turn["text"] = " ".join(words)
                    return script[:target_turns]
        except Exception as e:
            print(f"[script] AI note: {e}, using curated fallback.")

    return [
        {"speaker": "Host1", "text": f"Welcome back everyone! Today we are discussing how to sound like a senior executive in your **workplace** emails."},
        {"speaker": "Host2", "text": f"Never write 'I need this right now'. Instead, say: Could you please **prioritize** this by end of day?"},
        {"speaker": "Host1", "text": f"Using polite modal verbs like could or would keeps your communication professional and **diplomatic**."},
        {"speaker": "Host2", "text": f"It ensures high respect from your colleagues and builds long term **career** credibility!"}
    ][:target_turns]

async def generate_audio_files(turns, run_dir):
    audio_dir = run_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_list = []
    for i, turn in enumerate(turns):
        mp3_p = audio_dir / f"turn_{i:03d}.mp3"
        spoken = re.sub(r'\*\*(.*?)\*\*', r'\1', turn["text"])
        voice = EMMA_VOICE if turn["speaker"] == "Host1" else ANDREW_VOICE
        comm = edge_tts.Communicate(spoken, voice, rate=VOICE_RATE)
        await comm.save(str(mp3_p))

        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_p)],
                capture_output=True, text=True, check=True
            )
            duration = float(r.stdout.strip())
        except:
            duration = 5.0
        audio_list.append({"path": str(mp3_p), "duration": duration, "speaker": turn["speaker"]})
    return audio_list

def draw_executive_mic(draw, center_x, center_y, is_active, host_label):
    # Polished heavy brass/black base
    ring_c = EXECUTIVE_GOLD if is_active else (60, 75, 105)
    draw.ellipse([(center_x - 65, center_y + 115), (center_x + 65, center_y + 135)], fill=(18, 26, 42), outline=ring_c, width=3)
    # Brass stem
    draw.rectangle([(center_x - 7, center_y - 10), (center_x + 7, center_y + 115)], fill=(90, 80, 50) if is_active else (50, 60, 85))

    # Mic Body
    mic_c = (22, 34, 55) if not is_active else (38, 54, 88)
    draw.rounded_rectangle([(center_x - 30, center_y - 95), (center_x + 30, center_y - 20)], radius=16, fill=mic_c, outline=EXECUTIVE_GOLD if is_active else CARD_BORDER, width=3)

    # Brass bands
    draw.rectangle([(center_x - 30, center_y - 65), (center_x + 30, center_y - 58)], fill=EXECUTIVE_GOLD)
    for gy in range(center_y - 85, center_y - 30, 10):
        draw.line([(center_x - 22, gy), (center_x + 22, gy)], fill=EXECUTIVE_GOLD if is_active else (55, 70, 95), width=2)

    # Host Label
    f_p = load_font(22, bold=True)
    box_c = (20, 32, 54) if not is_active else (45, 36, 18)
    draw.rounded_rectangle([(center_x - 85, center_y + 145), (center_x + 85, center_y + 180)], radius=8, fill=box_c, outline=EXECUTIVE_GOLD, width=2)
    tag = f"🎙️ {host_label}" + (" (SPEAKER)" if is_active else "")
    draw.text((center_x, center_y + 162), tag, fill=EXECUTIVE_GOLD if is_active else MUTED_TEXT, font=f_p, anchor="mm")

def draw_on_air_box(draw, center_x, center_y, is_live):
    # Illuminated ON AIR Acrylic Lightbox
    box_w = 260
    box_h = 58
    bg_c = (180, 20, 20) if is_live else (45, 15, 18)
    border_c = (255, 80, 80) if is_live else (90, 30, 35)

    draw.rounded_rectangle([(center_x - box_w//2, center_y - box_h//2),
                            (center_x + box_w//2, center_y + box_h//2)],
                           radius=10, fill=bg_c, outline=border_c, width=3)

    f_onair = load_font(30, bold=True)
    txt_c = WHITE if is_live else (180, 120, 125)
    draw.text((center_x, center_y), "🔴 ON AIR", fill=txt_c, font=f_onair, anchor="mm")

def draw_peak_program_meter(draw, center_x, center_y, width, height, sub_idx, is_speaking):
    num_bars = 24
    bar_w = 9
    gap = (width - (num_bars * bar_w)) // (num_bars - 1)

    draw.rounded_rectangle([(center_x - width//2 - 18, center_y - height//2 - 12),
                            (center_x + width//2 + 18, center_y + height//2 + 12)],
                           radius=16, fill=(12, 18, 36), outline=EXECUTIVE_GOLD, width=2)

    f_hud = load_font(18, bold=True)
    draw.text((center_x, center_y - height//2 - 1), "• STUDIO BROADCAST PEAK PROGRAM METER (dB) •", fill=PLATINUM, font=f_hud, anchor="mm")

    start_x = center_x - width//2
    for b in range(num_bars):
        if is_speaking:
            phase = sub_idx * 0.92 + b * 0.45
            wave = abs(math.sin(phase)) * 0.75 + abs(math.cos(phase * 1.35)) * 0.25
            bar_h = int(12 + wave * (height - 28))
        else:
            bar_h = 8

        bx = start_x + b * (bar_w + gap)
        by = center_y + height//2 - 8 - bar_h

        # Multi-color PPM ladder: Green below 60%, Yellow 60-85%, Red peak > 85%
        ratio = bar_h / float(height - 28)
        if ratio > 0.85:
            fill_c = ON_AIR_RED
        elif ratio > 0.55:
            fill_c = EXECUTIVE_GOLD
        else:
            fill_c = (34, 197, 94) # Broadcast Green

        draw.rounded_rectangle([(bx, by), (bx + bar_w, center_y + height//2 - 8)], radius=3, fill=fill_c)

def render_podcast_subframe(topic_item, turn, turn_idx, sub_idx, total_subframes, elapsed, total_dur, out_path):
    canvas = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), DARK_BG)
    draw = ImageDraw.Draw(canvas)

    # Executive Penthouse Studio Backdrop
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        r = int(10 + ratio * 14)
        g = int(16 + ratio * 18)
        b = int(32 + ratio * 28)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b, 255))

    # City skyscraper bokeh / window grid in background
    for wx in range(160, VIDEO_WIDTH, 200):
        draw.line([(wx, 120), (wx, 620)], fill=(22, 32, 54), width=1)
    for wy in range(160, 620, 90):
        draw.line([(100, wy), (1820, wy)], fill=(22, 32, 54), width=1)

    # Top Header Deck
    # Left: Channel badge
    draw.rounded_rectangle([(60, 36), (560, 106)], radius=16, fill=CARD_BG, outline=EXECUTIVE_GOLD, width=2)
    f_brand = load_font(28, bold=True)
    draw.text((310, 71), "💼 BUSINESS ENGLISH PRO", fill=PLATINUM, font=f_brand, anchor="mm")

    # Center: Category Pill
    draw.rounded_rectangle([(590, 36), (1450, 106)], radius=16, fill=(18, 30, 56), outline=PLATINUM, width=2)
    f_scen = load_font(26, bold=True)
    draw.text((1020, 71), f"🏛️ FOCUS: {topic_item['category']}", fill=EXECUTIVE_GOLD, font=f_scen, anchor="mm")

    # Right: Penthouse Studio Tag
    draw.rounded_rectangle([(1480, 36), (1860, 106)], radius=16, fill=(24, 34, 60), outline=EXECUTIVE_GOLD, width=2)
    f_air = load_font(26, bold=True)
    draw.text((1670, 71), "EXECUTIVE DESK", fill=PLATINUM, font=f_air, anchor="mm")

    # Visual Studio Centerpiece: ON AIR Lightbox + Dual Brass Mics + Peak PPM Meter
    is_emma = (turn["speaker"] == "Host1")
    is_andrew = not is_emma

    # Center Top: Illuminated "ON AIR" Lightbox
    draw_on_air_box(draw, center_x=960, center_y=190, is_live=True)

    # Left Mic: Emma
    draw_executive_mic(draw, center_x=320, center_y=380, is_active=is_emma, host_label="EMMA")

    # Center Equalizer: Peak Program dB Meter
    draw_peak_program_meter(draw, center_x=960, center_y=350, width=560, height=140, sub_idx=sub_idx, is_speaking=True)

    # Center Executive Formula Pill
    draw.rounded_rectangle([(600, 460), (1320, 540)], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    f_top = load_font(22, bold=True)
    draw.text((960, 500), f"Executive Formula: \"{topic_item['phrase']}\"", fill=EXECUTIVE_GOLD, font=f_top, anchor="mm")

    # Right Mic: Andrew
    draw_executive_mic(draw, center_x=1600, center_y=380, is_active=is_andrew, host_label="ANDREW")

    # LOWER THIRD: SLEEK SINGLE-LINE SUBTITLE DISPLAY WITH WORD-BY-WORD HIGHLIGHTING
    draw.rounded_rectangle([(100, 680), (1820, 930)], radius=24, fill=(14, 22, 44, 240), outline=EXECUTIVE_GOLD, width=3)

    # Speaker Tag Pill
    active_name = "EMMA (Host)" if is_emma else "ANDREW (Host)"
    draw.rounded_rectangle([(140, 650), (450, 705)], radius=12, fill=EXECUTIVE_GOLD)
    f_spk = load_font(26, bold=True)
    draw.text((295, 677), f"🎙️ {active_name}", fill=(10, 16, 28), font=f_spk, anchor="mm")

    # Sentence & Spoken Word Highlighting
    raw_text = turn["text"]
    words_clean = [re.sub(r'[\*\*\.]', '', w).strip() for w in raw_text.split() if w.strip()]
    if not words_clean:
        words_clean = ["Listen", "carefully"]

    active_word_idx = min(len(words_clean) - 1, int((sub_idx / max(1, total_subframes)) * len(words_clean)))

    f_sub = load_font(42, bold=True)
    rendered_words = raw_text.split()

    line_words = []
    lines = []
    max_w = 1600
    curr_w = 0

    for w_i, w in enumerate(rendered_words):
        clean_w = re.sub(r'\*\*(.*?)\*\*', r'\1', w)
        wb = draw.textbbox((0, 0), clean_w + " ", font=f_sub)
        w_len = wb[2] - wb[0]
        if curr_w + w_len > max_w and line_words:
            lines.append(line_words)
            line_words = [(w_i, w, clean_w, w_len)]
            curr_w = w_len
        else:
            line_words.append((w_i, w, clean_w, w_len))
            curr_w += w_len
    if line_words:
        lines.append(line_words)

    y_start = 740 if len(lines) == 1 else 725
    line_h = 55
    for l_idx, line in enumerate(lines[:2]):
        total_line_w = sum(item[3] for item in line)
        start_x = 960 - total_line_w // 2
        curr_x = start_x
        y_pos = y_start + l_idx * line_h

        for (w_i, raw_w, clean_w, w_len) in line:
            is_active_word = (w_i == active_word_idx)
            is_key_word = ("**" in raw_w)

            if is_active_word:
                # Gold active karaoke pill
                draw.rounded_rectangle([(curr_x - 4, y_pos - 6), (curr_x + w_len - 2, y_pos + 46)], radius=8, fill=EXECUTIVE_GOLD)
                draw.text((curr_x, y_pos), clean_w, fill=(10, 16, 28), font=f_sub)
            elif is_key_word:
                draw.text((curr_x, y_pos), clean_w, fill=PLATINUM, font=f_sub)
            else:
                draw.text((curr_x, y_pos), clean_w, fill=WHITE, font=f_sub)
            curr_x += w_len

    # Tip Ribbon inside the Lower Third
    f_tip = load_font(22, bold=False)
    draw.text((960, 885), "💡 Corporate Formula: Using polite modals ('could', 'would') creates instant executive diplomacy.", fill=MUTED_TEXT, font=f_tip, anchor="mm")

    # Bottom Progress Deck
    draw.line([(0, 1020), (VIDEO_WIDTH, 1020)], fill=(32, 45, 75), width=3)
    ratio = min(1.0, elapsed / max(1.0, total_dur))
    draw.line([(0, 1020), (int(VIDEO_WIDTH * ratio), 1020)], fill=EXECUTIVE_GOLD, width=6)

    f_bot = load_font(24, bold=False)
    draw.text((70, 1050), "Business English Pro • Executive Communication • Corporate Fluency", fill=MUTED_TEXT, font=f_bot, anchor="lm")
    time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d} / {int(total_dur // 60):02d}:{int(total_dur % 60):02d}"
    draw.text((1850, 1050), time_str, fill=EXECUTIVE_GOLD, font=f_bot, anchor="rm")

    canvas.convert("RGB").save(out_path, quality=90)

def assemble_video(topic_item, turns, audio_list, run_dir):
    frames_dir = run_dir / "frames"
    clips_dir = run_dir / "clips"
    frames_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    total_dur = sum(a["duration"] for a in audio_list)
    elapsed = 0.0
    clips = []

    for i, (turn, audio) in enumerate(zip(turns, audio_list)):
        dur = audio["duration"]
        subframes_count = max(8, int(dur * SUBFRAMES_PER_SEC))

        turn_frames_dir = frames_dir / f"turn_{i:03d}"
        turn_frames_dir.mkdir(parents=True, exist_ok=True)

        for s_idx in range(subframes_count):
            frame_p = turn_frames_dir / f"frame_{s_idx:04d}.png"
            sub_elapsed = elapsed + (s_idx / subframes_count) * dur
            render_podcast_subframe(
                topic_item, turn, i, s_idx, subframes_count,
                sub_elapsed, total_dur, str(frame_p)
            )

        clip_p = clips_dir / f"clip_{i:03d}.mp4"
        input_pattern = str(turn_frames_dir / "frame_%04d.png")

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(SUBFRAMES_PER_SEC),
            "-i", input_pattern,
            "-i", audio["path"],
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-preset", "veryfast",
            str(clip_p)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        clips.append(clip_p)
        elapsed += dur

    concat_txt = run_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve().as_posix()}'\n")

    final_video = run_dir / "business_english_podcast_final.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(final_video)], check=True, capture_output=True)
    return final_video, total_dur

async def run_business_generation(topic_idx=0, turns_count=4):
    topic_item = TOPICS[topic_idx % len(TOPICS)]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Business Podcast] Generating 16:9 Executive Penthouse: '{topic_item['topic']}' ({turns_count} turns)...")
    turns = generate_script_ai(topic_item, target_turns=turns_count)
    audio_list = await generate_audio_files(turns, run_dir)
    video_p, dur = assemble_video(topic_item, turns, audio_list, run_dir)

    meta = {
        "title": f"Business English Pro: {topic_item['topic']} 🎙️ Slow English Podcast",
        "description": f"Level up your corporate English! Master executive communication: '{topic_item['phrase']}'. Follow for daily workplace English lessons! 💼📊",
        "phrase": topic_item["phrase"],
        "duration_seconds": dur
    }
    with open(run_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[Business Podcast] Video ready: {video_p}")
    return video_p, meta

if __name__ == "__main__":
    asyncio.run(run_business_generation(topic_idx=0, turns_count=2))
