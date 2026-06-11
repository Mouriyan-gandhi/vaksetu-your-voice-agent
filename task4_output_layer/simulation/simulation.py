"""
Bot-vs-Bot Simulation Engine
=============================
Runs automated conversations between the AI Brain (simulated for now)
and the selected Customer Persona.

Usage:
    from simulation import SimulationEngine, get_persona
    
    engine = SimulationEngine()
    customer = get_persona("frustrated")
    engine.run(customer, num_turns=5)
"""

import os
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

class SimulationEngine:
    """Manages the lifecycle of a Bot-vs-Bot conversation."""

    def __init__(self, use_tts: bool = False):
        self.use_tts = use_tts
        self.tts_engine = None
        
        if self.use_tts:
            try:
                import sys
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from tts.tts import SarvamTTS
                self.tts_engine = SarvamTTS()
                print(Fore.GREEN + "✅ TTS Engine integrated with Simulation!")
            except Exception as e:
                print(Fore.YELLOW + f"⚠️  Failed to load TTS Engine: {e}")
                print(Fore.YELLOW + "   Falling back to text-only mode.")
                self.use_tts = False

    def simulate_ai_brain(self, customer_input: str, turn_number: int, persona_type: str) -> str:
        """
        Mock AI Brain. 
        In production, this would call Shaurya's reasoning engine / LLM.
        """
        # A simple state machine to mock the AI's goal logic
        if turn_number == 0:
            if "frustrated" in persona_type.lower() or "evasive" in persona_type.lower():
                return "Namaste sir. Main ABC Bank se bol raha hoon. Aapka credit card payment pending hai."
            else:
                return "Namaste. Main aapki ASHA didi ka AI assistant hoon. Aapki health checkup call hai."
        
        lower_input = customer_input.lower()
        
        if "frustrated" in persona_type.lower():
            if "manager" in lower_input or "complaint" in lower_input:
                return "Sir, main samajh raha hoon aap pareshan hain. Main aapki line supervisor ko connect kar sakta hoon. Ya kya hum settlement option discuss karein?"
            elif "aisa" in lower_input or "nahi" in lower_input:
                 return "Sir, agar abhi payment nahi ho pa rahi, toh hum EMI freeze ya restructuring option dekh sakte hain. Kya main details batau?"
            return "Sir, aap gussa mat hoiye. Hum solution nikalne ke liye hi call kar rahe hain."
            
        elif "confused" in persona_type.lower():
            if "samajh nahi" in lower_input or "kaunsi" in lower_input or "phir se" in lower_input:
                return "Main phir se batata hoon, bilkul aaram se. Aapko bas subah uth kar ek gol wali goli leni hai. Baaki sab same rahega. Samajh aaya?"
            elif "dar" in lower_input or "side effect" in lower_input or "chakkar" in lower_input:
                 return "Aap daro mat mataji. Ye nayi dawai bilkul safe hai. Agar chakkar aaye toh mujhe call back karna, theek hai?"
            return "Haan haan, theek hai. Apna dhyaan rakhiyega. Dawai samay par lena zaroori hai."
            
        elif "evasive" in persona_type.lower():
            if "baad mein" in lower_input or "wife" in lower_input or "busy" in lower_input:
                return "Sir, ye zaroori call hai bank se. Aapse baat karna zaroori hai aage ki penalty fees rokne ke liye. Bas 2 minute lagenge."
            elif "credit card" in lower_input or "weather" in lower_input or "aur" in lower_input:
                return "Sir, nayi scheme toh main bata dunga, par pehle purana payment clear karna padega system mein. Kya aaj shyam tak ho jayega?"
            return "Aap bataiye payment kis din expected hai taaki main system mein update kar du aur daily calls band ho jayein."
            
        elif "cooperative" in persona_type.lower():
            if "aadhaar" in lower_input or "pan" in lower_input or "address" in lower_input:
                return "Tumba dhanyavaada. Details thagondiddini. Iga next, nimage yaarannu nominee aagi haakbeku?"
            elif "doubt" in lower_input or "benefit" in lower_input or "premium" in lower_input:
                 return "Khandita, premium tingalige 500 roopayi irutte. Benefits nalli aaspattri kharchu cover aagutte. Agree idhira?"
            return "Process complete aagide. Nimma samayakke dhanyavaada. Shubha dina!"

        return "Main samajh raha hoon. Aage baat karte hain."

    def run(self, persona, num_turns: int = 5, output_dir: str = "output"):
        """Run the Bot-vs-Bot conversation loop."""
        
        print("\n" + "="*60)
        print(f"🤖 BOT VS BOT SIMULATION: {persona.name} ({persona.__class__.__name__})")
        print(f"🌍 Language: {persona.language} | Initial Mood: {persona.mood}")
        print("="*60 + "\n")

        conversation_log = []
        customer_reply = ""

        # Main dialogue loop
        for turn in range(num_turns):
            print(Fore.CYAN + f"--- Turn {turn + 1}/{num_turns} ---")
            
            # 1. AI Brain thinks and speaks
            print(Style.DIM + "🧠 AI Brain thinking...")
            time.sleep(1) # Fake thinking delay
            ai_msg = self.simulate_ai_brain(customer_reply, turn, persona.__class__.__name__)
            
            # Log & Print AI
            print(Fore.BLUE + Style.BRIGHT + f"🤖 AI Agent: " + Fore.BLUE + ai_msg)
            conversation_log.append({"role": "AI", "text": ai_msg, "turn": turn + 1})
            
            # Optional: Play TTS audio
            if self.use_tts and self.tts_engine:
                 try:
                     # Simple language mapping for TTS
                     lang = "english"
                     if "hindi" in persona.language.lower() or "hinglish" in persona.language.lower(): lang = "hindi"
                     elif "kannada" in persona.language.lower(): lang = "kannada"
                     
                     speaker = "meera" if "cooperative" in persona.__class__.__name__.lower() or "confused" in persona.__class__.__name__.lower() else "arjun"
                     self.tts_engine.speak(ai_msg, language=lang, speaker=speaker)
                     time.sleep(0.5)
                 except Exception as e:
                     print(Fore.RED + f"   (TTS Error: {e})")

            # 2. Customer Persona reacts
            print(Style.DIM + f"👤 {persona.name} reacting...")
            time.sleep(1.5) # Fake reacting delay
            customer_reply = persona.respond(ai_msg)
            mood_emoji = persona.get_mood_emoji()
            
            # Determine text color based on mood
            if persona.mood in ["angry", "frustrated"]:
                color = Fore.RED
            elif persona.mood in ["confused", "evasive"]:
                color = Fore.YELLOW
            else:
                color = Fore.GREEN
                
            # Log & Print Customer
            print(color + Style.BRIGHT + f"{mood_emoji} {persona.name}: " + color + customer_reply)
            conversation_log.append({
                "role": "Customer", 
                "text": customer_reply, 
                "mood": persona.mood,
                "escalation_level": persona.escalation_level,
                "turn": turn + 1
            })
            
            print()
            time.sleep(1) # Pause between turns for readability

        # 3. End of Simulation
        print("\n" + "="*60)
        print("🏁 SIMULATION ENDED")
        print("="*60)

        # 4. Save Transcript
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/sim_{persona.__class__.__name__.lower()}_{timestamp}.json"
        
        sim_data = {
            "metadata": {
                "timestamp": timestamp,
                "persona": persona.to_dict(),
                "total_turns": num_turns
            },
            "transcript": conversation_log
        }
        
        try:
            with open(filename, 'w') as f:
                 json.dump(sim_data, f, indent=2, ensure_ascii=False)
            print(Fore.GREEN + f"💾 Transcript saved to {filename}")
        except Exception as e:
             print(Fore.RED + f"Error saving transcript: {e}")
             
        return sim_data
