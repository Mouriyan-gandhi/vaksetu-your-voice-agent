"""
TTS Interactive Test Console
=============================
Solo test for Mouriyan: Type text → hear speech.

Usage:
    python -m tts.test_tts
"""

import sys
import os

# Add parent dir to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts.tts import SarvamTTS
from tts.config import LANGUAGES, VOICES, SAMPLE_TEXTS


def print_banner():
    """Print a cool banner."""
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║    🎤  SARVAM TTS TEST CONSOLE  🎤          ║")
    print("║    Multilingual Text-to-Speech Engine        ║")
    print("║    by Mouriyan                               ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def interactive_mode(engine: SarvamTTS):
    """Run the interactive test loop."""
    print("📌 Commands: 'quit' to exit, 'voices' to list voices, 'langs' to list languages\n")

    while True:
        # Select language
        lang_options = "/".join(["hindi", "kannada", "english"])
        language = input(f"🌍 Language [{lang_options}]: ").strip().lower()
        
        if language in ("quit", "exit", "q"):
            print("👋 Goodbye!")
            break
        if language == "voices":
            engine.list_voices()
            continue
        if language == "langs":
            engine.list_languages()
            continue
        
        if not language:
            language = "hindi"
        if language not in LANGUAGES:
            print(f"❌ Unknown language '{language}'. Try: {', '.join(LANGUAGES.keys())}")
            continue

        # Select voice
        voice_options = "/".join(VOICES.keys())
        speaker = input(f"🎙️  Voice [{voice_options}]: ").strip().lower()
        if not speaker:
            speaker = "anushka"
        if speaker not in VOICES:
            print(f"❌ Unknown voice '{speaker}'. Try: {', '.join(VOICES.keys())}")
            continue

        # Get text (or use sample)
        text = input(f"📝 Text (or press Enter for sample): ").strip()
        if not text:
            text = SAMPLE_TEXTS.get(language, "Hello, this is a test.")
            print(f"   Using sample: \"{text}\"")

        # Synthesize and play
        print()
        try:
            engine.speak(text, language=language, speaker=speaker)
            
            # Also save to file
            safe_lang = language.replace(" ", "_")
            output_path = f"output/test_{safe_lang}_{speaker}.wav"
            engine.save_audio(text, language=language, speaker=speaker, filepath=output_path)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        print("─" * 50)
        print()


def quick_test(engine: SarvamTTS):
    """Run a quick automated test across all 3 main languages."""
    print("⚡ Running quick test across Hindi, Kannada, English...\n")

    test_cases = [
        ("hindi", "anushka", SAMPLE_TEXTS["hindi"]),
        ("kannada", "anushka", SAMPLE_TEXTS["kannada"]),
        ("english", "anushka", SAMPLE_TEXTS["english"]),
    ]

    for lang, voice, text in test_cases:
        print(f"{'─' * 50}")
        print(f"  Language: {lang} | Voice: {voice}")
        print(f"  Text: \"{text[:60]}{'...' if len(text) > 60 else ''}\"")
        print()
        try:
            output_path = f"output/quick_test_{lang}_{voice}.wav"
            engine.save_audio(text, language=lang, speaker=voice, filepath=output_path)
            print(f"  ✅ Saved to {output_path}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        print()

    print("⚡ Quick test complete!")


def main():
    print_banner()

    try:
        engine = SarvamTTS()
        print("✅ API key loaded successfully!\n")
    except ValueError as e:
        print(str(e))
        print("\n💡 To fix this:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Sarvam API key from dashboard.sarvam.ai")
        sys.exit(1)

    # Ask for mode
    print("Select mode:")
    print("  1. 🎮 Interactive (type text, hear speech)")
    print("  2. ⚡ Quick Test (auto-test all 3 languages)")
    print()
    choice = input("Choice [1/2]: ").strip()

    if choice == "2":
        quick_test(engine)
    else:
        interactive_mode(engine)


if __name__ == "__main__":
    main()
