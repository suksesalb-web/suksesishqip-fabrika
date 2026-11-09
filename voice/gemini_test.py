"""Voice comparison test (not used by the posting pipeline): Anila (Edge) vs Gemini TTS voices, same text."""
import asyncio, base64, json, os, subprocess, sys, time
from pathlib import Path
import requests

OUT = Path("voice/samples-gemini")
OUT.mkdir(parents=True, exist_ok=True)
TEXT = ("E di çfarë më habit? <breath> Ai që duket më i pasur në lagje, shpesh ka më pak para se ti. "
        "Makina me këste. Telefoni me këste. Pushimet me kredi. <sigh> Dhe çdo muaj, rroga ikën para se të vijë. "
        "Çdo lek që shpenzon për t'u dukur, është një lek që nuk punon kurrë për ty. "
        "Të pasurit e vërtetë duken të thjeshtë. S'kanë nevojë të bindin askënd.")
STYLE = ("Shqip standarde, natyrshëm, si një shok që të tregon diçka të vërtetë në kafe: "
         "i qetë, bindës, me pauza të shkurtra, pa ton reklame")
STYLE_EN = ("Speak in standard Albanian, naturally, like a friend telling you something true over coffee: "
            "calm, convincing, short pauses, not like an advert")
VOICES = ["Sami", "Riko", "Despina", "Sulafat"]
MODELS = ["gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"]
KEY = os.environ["GEMINI_API_KEY"]


def call(model, body):
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                      headers={"x-goog-api-key": KEY, "Content-Type": "application/json"}, json=body, timeout=120)
    return r


def gemini(voice):
    bodies = [  # newest request shape first, then the older ones
        {"contents": [{"role": "user", "parts": [{"text": TEXT, "speech_metadata": {"style": STYLE_EN}}]}],
         "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"voice": voice}}}},
        {"contents": [{"role": "user", "parts": [{"text": f"{STYLE_EN}:\n{TEXT}"}]}],
         "generationConfig": {"responseModalities": ["AUDIO"],
                              "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}},
    ]
    errors = []
    for model in MODELS:
        for body in bodies:
            r = call(model, body)
            if r.status_code == 200:
                part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
                raw = base64.b64decode(part["data"])
                mime = part.get("mimeType", "")
                wav = OUT / f"gemini-{voice}.raw"
                wav.write_bytes(raw)
                src = ["-i", str(wav)] if raw[:4] == b"RIFF" else ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(wav)]
                subprocess.run(["ffmpeg", "-y", "-v", "error", *src, "-af", "loudnorm=I=-16", "-b:a", "128k",
                                str(OUT / f"gemini-{voice}.mp3")], check=True)
                wav.unlink()
                print(f"OK {voice} via {model} ({mime})")
                return
            errors.append(f"{model}: {r.status_code} {r.text[:300]}")
            if r.status_code == 429:
                time.sleep(20)
    print(f"FAILED {voice}:\n  " + "\n  ".join(errors))


async def anila():
    import edge_tts
    await edge_tts.Communicate(TEXT, "sq-AL-AnilaNeural", rate="+6%").save(str(OUT / "anila.mp3"))


asyncio.run(anila())
print("OK anila")
for v in VOICES:
    gemini(v)
    time.sleep(8)
