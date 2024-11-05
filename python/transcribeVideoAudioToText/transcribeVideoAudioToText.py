import os
import requests
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'resources', 'inputVideoAudioFiles')
OUTPUT_DIR = os.path.join(BASE_DIR, 'resources', 'outputTextTranscriptions')
TEMP_DIR = os.path.join(BASE_DIR, 'resources', 'tempChunks')

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

API_URL = "https://api.openai.com/v1/audio/transcriptions"
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("Error: Please set the OPENAI_API_KEY environment variable.")
    exit(1)

CHUNK_DURATION_SECONDS = 10 * 60  # 10 minutes in seconds

def split_audio_file(input_file):
    chunk_files = []
    command = [
        "ffmpeg", "-i", input_file, "-f", "segment",
        "-segment_time", str(CHUNK_DURATION_SECONDS),
        "-ar", "16000",  # Ensure sample rate is 16kHz
        "-ac", "1",       # Ensure mono audio
        os.path.join(TEMP_DIR, "chunk_%03d.wav")
    ]
    subprocess.run(command, check=True)
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith("chunk_") and filename.endswith(".wav"):
            chunk_files.append(os.path.join(TEMP_DIR, filename))
    return chunk_files

def transcribe_chunk(chunk_path):
    if os.path.getsize(chunk_path) == 0:
        print(f"Skipping empty chunk: {chunk_path}")
        return ""

    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(chunk_path, 'rb') as chunk:
        files = {"file": (chunk_path, chunk, "audio/wav")}
        data = {
            "model": "whisper-1",
            "language": "en"
        }

        try:
            response = requests.post(API_URL, headers=headers, files=files, data=data, timeout=300)
            response.raise_for_status()
            return response.json().get("text", "")
        except requests.exceptions.RequestException as e:
            print(f"Failed to process chunk {chunk_path}: {e}")
            if response.content:
                print("Error details:", response.content.decode())
            return ""

print(f"Starting transcription process in {INPUT_DIR}")
files_found = False

for filename in os.listdir(INPUT_DIR):
    file_path = os.path.join(INPUT_DIR, filename)
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension not in {'.mp3', '.wav', '.m4a'}:
        print(f"Skipping unsupported file type: {filename}")
        continue

    files_found = True
    print(f"Processing file: {filename}")

    try:
        chunk_files = split_audio_file(file_path)
    except subprocess.CalledProcessError as e:
        print(f"Error during file splitting with ffmpeg for {filename}: {e}")
        continue

    transcription_text = ""

    for i, chunk_file in enumerate(chunk_files, start=1):
        print(f"Transcribing chunk {i}/{len(chunk_files)} for file {filename}")
        chunk_text = transcribe_chunk(chunk_file)
        transcription_text += chunk_text + "\n"

    output_filename = f"{os.path.splitext(filename)[0]}.txt"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(transcription_text)

    print(f"Transcription for {filename} written to {output_path}")

# Clean up temporary chunk files
for temp_file in os.listdir(TEMP_DIR):
    os.remove(os.path.join(TEMP_DIR, temp_file))

if not files_found:
    print(f"No supported files found in {INPUT_DIR}. Place .mp3, .wav, or .m4a files there and try again.")

print("Transcription process completed.")
