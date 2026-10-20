import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

class AudioProcessor:
    def __init__(self):
        self.groq_client = None
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
            except Exception as e:
                print(f"Failed to initialize Groq client for audio: {e}")

    def audio_to_text(self, audio_file_path: str) -> str:
        """
        High-accuracy speech-to-text using Groq Whisper-large-v3-turbo.
        Falls back to SpeechRecognition if Groq is unavailable.
        """
        # 1. State-of-the-art Groq Whisper (Fastest & Most Accurate)
        if self.groq_client and os.path.exists(audio_file_path):
            try:
                with open(audio_file_path, "rb") as file:
                    filename = os.path.basename(audio_file_path)
                    transcription = self.groq_client.audio.transcriptions.create(
                        file=(filename, file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text"
                    )
                    transcribed_text = str(transcription).strip()
                    if transcribed_text:
                        return transcribed_text
            except Exception as e:
                print(f"Groq Whisper transcription error: {e}, falling back...")

        # 2. Fallback to SpeechRecognition (Google)
        try:
            import speech_recognition as sr
            from pydub import AudioSegment

            recognizer = sr.Recognizer()
            audio = AudioSegment.from_file(audio_file_path)
            wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio.export(wav_file.name, format="wav")

            with sr.AudioFile(wav_file.name) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    return text
                except sr.UnknownValueError:
                    return "Could not understand audio clearly."
                except sr.RequestError as re:
                    return f"Speech recognition request error: {re}"
        except Exception as fallback_error:
            return f"Error processing audio file: {fallback_error}"

    def text_to_speech(self, text: str):
        """Convert text to speech using gTTS and save as a .mp3 file."""
        if not text or text.strip() == "":
            return None
        try:
            from gtts import gTTS
            # Shorten if extremely long to avoid timeout
            clean_text = text[:600] if len(text) > 600 else text
            tts = gTTS(clean_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts.save(temp_audio.name)
                return temp_audio.name
        except Exception as e:
            print(f"TTS Error: {e}")
            return None