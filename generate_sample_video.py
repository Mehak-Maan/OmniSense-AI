import os
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

ROOT = Path("d:/Projects/CMIT/Multimodal-RAG-video")
SAMPLE_DIR = ROOT / "sample_videos"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = ROOT / "temp_video_build"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

scenes_data = [
    {
        "title": "Multimodal RAG Overview",
        "subtitle": "Unified Intelligence across Video, Audio and Text",
        "points": [
            "1. Ingests video keyframes, audio speech, and PDF documents.",
            "2. Synchronizes visual scenes with spoken transcript timestamps.",
            "3. Enables semantic search and context-grounded AI answers."
        ],
        "voice": "Welcome to the Multimodal RAG overview. This system integrates video frames, speech audio, and documents so you can ask questions across all your media.",
        "bg_color_top": (18, 18, 38),
        "bg_color_bottom": (35, 30, 80),
        "accent_color": (99, 102, 241) # Indigo
    },
    {
        "title": "OpenCV Video Keyframing",
        "subtitle": "Temporal Scene Detection and Visual Analysis",
        "points": [
            "1. Samples high-resolution frames across the video timeline.",
            "2. Vision AI describes subjects, actions, and slide diagrams.",
            "3. Generates clickable video bookmarks and jump-to timestamps."
        ],
        "voice": "In step two, OpenCV extracts video keyframes at key timestamps. Vision models inspect the visual content to identify slides, graphics, and scene actions.",
        "bg_color_top": (15, 32, 39),
        "bg_color_bottom": (32, 58, 67),
        "accent_color": (16, 185, 129) # Emerald
    },
    {
        "title": "Groq Whisper Audio Transcription",
        "subtitle": "Converting Spoken Dialogue into Searchable Data",
        "points": [
            "1. Extracts audio tracks using FFmpeg pcm stream extraction.",
            "2. Groq Whisper generates high-speed, accurate text transcripts.",
            "3. Embeds spoken words into the multimodal vector index."
        ],
        "voice": "In step three, the audio track is extracted and transcribed using Groq Whisper. Every spoken sentence is indexed with its exact time location.",
        "bg_color_top": (44, 19, 56),
        "bg_color_bottom": (82, 34, 100),
        "accent_color": (236, 72, 153) # Pink
    },
    {
        "title": "Groq LLM Reasoning & Retrieval",
        "subtitle": "Instant Context-Grounded Answers with Timestamps",
        "points": [
            "1. TF-IDF vector retrieval ranks the top matching chunks.",
            "2. Llama 3 model synthesizes answers with source citations.",
            "3. Returns interactive video jump-links and confidence scores."
        ],
        "voice": "Finally, the Groq language model queries the vector index to generate concise answers with direct timestamps so you can jump straight to the answer in the video.",
        "bg_color_top": (20, 30, 48),
        "bg_color_bottom": (36, 59, 85),
        "accent_color": (14, 165, 233) # Sky blue
    }
]

def make_gradient(width, height, top_c, bot_c):
    base = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        ratio = y / height
        r = int(top_c[0] * (1 - ratio) + bot_c[0] * ratio)
        g = int(top_c[1] * (1 - ratio) + bot_c[1] * ratio)
        b = int(top_c[2] * (1 - ratio) + bot_c[2] * ratio)
        base[y, :] = (r, g, b)
    return base

def generate_voice_file(text: str, out_wav: Path):
    escaped = text.replace('"', '""')
    ps_cmd = (
        f'Add-Type -AssemblyName System.Speech; '
        f'$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        f'$synth.Rate = 0; '
        f'$synth.SetOutputToWaveFile("{out_wav.resolve()}"); '
        f'$synth.Speak("{escaped}"); '
        f'$synth.Dispose()'
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True)

def get_audio_duration(wav_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        str(wav_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(res.stdout.strip())

def create_slide_image(scene: dict, scene_idx: int, width=1280, height=720):
    grad = make_gradient(width, height, scene["bg_color_top"], scene["bg_color_bottom"])
    img = Image.fromarray(grad)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 46)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 24)
        font_tag = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = font_sub = font_body = font_tag = ImageFont.load_default()

    # Draw top pill badge
    badge_text = f"SCENE 0{scene_idx + 1} • MULTIMODAL RAG TEST VIDEO"
    draw.rounded_rectangle([60, 45, 480, 80], radius=8, fill=(scene["accent_color"][0]//2, scene["accent_color"][1]//2, scene["accent_color"][2]//2))
    draw.text((80, 52), badge_text, fill=(255, 255, 255), font=font_tag)

    # Title & Subtitle
    draw.text((60, 110), scene["title"], fill=(255, 255, 255), font=font_title)
    draw.text((60, 175), scene["subtitle"], fill=(200, 210, 230), font=font_sub)

    # Accent divider line
    draw.rectangle([60, 225, 1220, 228], fill=scene["accent_color"])

    # Content Box
    draw.rounded_rectangle([60, 260, 1220, 620], radius=16, fill=(0, 0, 0, 70), outline=scene["accent_color"], width=2)

    y_pos = 300
    for pt in scene["points"]:
        # Bullet indicator
        draw.ellipse([90, y_pos + 6, 104, y_pos + 20], fill=scene["accent_color"])
        draw.text((120, y_pos), pt, fill=(240, 240, 245), font=font_body)
        y_pos += 85

    # Footer banner
    footer_text = "Upload this video to Multimodal RAG Demo & ask questions about scenes, keyframes, or audio"
    draw.text((60, 660), footer_text, fill=(150, 160, 180), font=font_tag)

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def build_full_video():
    print("Step 1: Generating audio and slides...")
    scene_segments = []
    fps = 24
    width, height = 1280, 720

    for idx, sc in enumerate(scenes_data):
        wav_path = TEMP_DIR / f"scene_{idx}.wav"
        generate_voice_file(sc["voice"], wav_path)
        dur = get_audio_duration(wav_path) + 1.2 # extra pause
        slide_bgr = create_slide_image(sc, idx, width, height)
        
        # Render silent video clip for this scene
        scene_mp4 = TEMP_DIR / f"scene_{idx}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(scene_mp4), fourcc, fps, (width, height))
        total_frames = int(dur * fps)
        for _ in range(total_frames):
            out.write(slide_bgr)
        out.release()

        # Merge scene audio and video
        scene_synced_mp4 = TEMP_DIR / f"scene_synced_{idx}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(scene_mp4),
            "-i", str(wav_path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(scene_synced_mp4)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scene_segments.append(scene_synced_mp4)
        print(f"  Scene {idx+1} ready ({dur:.1f}s)")

    # Concatenate all scenes into final video
    concat_file = TEMP_DIR / "concat_list.txt"
    with open(concat_file, "w") as f:
        for seg in scene_segments:
            f.write(f"file '{seg.name}'\n")

    output_video = SAMPLE_DIR / "multimodal_ai_tutorial.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_video)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"\nSUCCESS! Test video created at: {output_video}")

if __name__ == "__main__":
    build_full_video()
