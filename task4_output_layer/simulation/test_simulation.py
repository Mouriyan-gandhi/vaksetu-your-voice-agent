"""
Solo Test for Persona Simulation
=================================
Mouriyan can run this to watch the bots talk to each other.

Usage:
    python -m simulation.test_simulation
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.personas import PERSONAS, get_persona
from simulation.simulation import SimulationEngine
from colorama import Fore, Style

def main():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   🤖  BOT VS BOT SIMULATOR                  ║")
    print("║   Mouriyan's Voice Agent Testing Engine      ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # Persona Selection
    print("Select a Persona to test against the AI:")
    
    # Sort and display options
    persona_keys = list(PERSONAS.keys())
    for i, key in enumerate(persona_keys, 1):
        p_class = PERSONAS[key]
        print(f"  {i}. {p_class.__name__}")
        
    print()
    
    # Get user choice
    while True:
        try:
            choice = input(f"Choice (1-{len(persona_keys)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(persona_keys):
                selected_key = persona_keys[idx]
                break
            print("❌ Invalid number.")
        except ValueError:
            print("❌ Please enter a number.")
            
    # Number of turns
    while True:
         try:
             turns_str = input("\nHow many conversation turns? (default: 4): ").strip()
             turns = int(turns_str) if turns_str else 4
             if turns > 0:
                 break
             print("❌ Must be greater than 0.")
         except ValueError:
             print("❌ Please enter a valid number.")

    # Optional TTS
    use_tts = input("\nEnable audio TTS playback? (y/N): ").strip().lower() == 'y'

    print("\n" + "─"*50)
    print("🚀 Initializing Simulation...")
    print("─"*50)

    try:
        # Load persona and run
        customer = get_persona(selected_key)
        engine = SimulationEngine(use_tts=use_tts)
        
        # Give user time to read the initialization before starting
        import time
        time.sleep(1)
        
        engine.run(customer, num_turns=turns)
        
    except Exception as e:
        print(Fore.RED + f"\n❌ Simulation crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
