"""
Customer Persona Definitions
==============================
Four distinct "actor" personas for Bot-vs-Bot testing.
Each persona has a unique personality, language, and response style.

Personas:
    1. FrustratedCustomer  — Short, angry Hinglish sentences
    2. ConfusedPatient     — Slow, formal Hindi, repeats questions
    3. EvasiveDebtor       — Avoids financial questions, Hindi-English mix
    4. CooperativeUser     — Clear, helpful responses in Kannada
"""

import random
from abc import ABC, abstractmethod


class BasePersona(ABC):
    """Base class for all customer personas."""

    def __init__(self):
        self.name = "Unknown"
        self.language = "english"
        self.mood = "neutral"
        self.dialect = "standard"
        self.description = ""
        self.turn_count = 0
        self.escalation_level = 0  # 0 = calm, 5 = maximum frustration

    @abstractmethod
    def respond(self, ai_message: str) -> str:
        """Generate a response to the AI's message."""
        pass

    def get_mood_emoji(self) -> str:
        """Return emoji based on current mood."""
        moods = {
            "angry": "😤",
            "frustrated": "😠",
            "confused": "😕",
            "evasive": "😏",
            "cooperative": "😊",
            "neutral": "😐",
            "happy": "😄",
            "sad": "😢",
        }
        return moods.get(self.mood, "😐")

    def to_dict(self) -> dict:
        """Serialize persona info."""
        return {
            "name": self.name,
            "language": self.language,
            "mood": self.mood,
            "dialect": self.dialect,
            "description": self.description,
            "turn_count": self.turn_count,
            "escalation_level": self.escalation_level,
        }


# ═══════════════════════════════════════════════════════════════════
# PERSONA 1: THE FRUSTRATED CUSTOMER
# ═══════════════════════════════════════════════════════════════════

class FrustratedCustomer(BasePersona):
    """
    Uses short, angry sentences in Hinglish.
    Escalates frustration over time. Uses slang like "yaar", "kya bakwas".
    Scenario: Bank loan recovery call.
    """

    def __init__(self):
        super().__init__()
        self.name = "Raju Sharma"
        self.language = "hinglish"
        self.mood = "frustrated"
        self.dialect = "Hinglish (Hindi + English mix)"
        self.description = "Angry bank customer tired of collection calls"

        self._responses = {
            "greeting": [
                "Haan haan, kya hai? Roz roz phone karte ho yaar!",
                "Phir se call? Kitni baar bolu, abhi paise nahi hai!",
                "Hello... dekho mujhe bahut kaam hai, jaldi bolo.",
            ],
            "payment_ask": [
                "Dekho bhai, abhi mere paas paise nahi hai. Next month dunga.",
                "Kya bakwas hai ye! EMI EMI EMI... aur kuch puchna hai?",
                "Yaar tum log samajhte kyu nahi? Job chali gayi meri!",
                "Arey! Maine kaha na wait karo. Kya problem hai tumhe?",
            ],
            "escalation": [
                "Bas! Ab mujhe manager se baat karni hai!",
                "Tumhara naam kya hai? Main complaint karunga!",
                "Ye harassment hai! Consumer court jaaunga main!",
                "Roz roz phone karke pareshan kar diya hai tumne!",
            ],
            "deflection": [
                "Abhi meeting mein hoon, baad mein call karo.",
                "Network problem hai... hello? Hello? ... *hangs up*",
                "Meri wife se baat karo, mujhe nahi pata ye sab.",
            ],
            "calming_down": [
                "Achha theek hai... kitna pending hai exactly?",
                "Ok ok, gussa nahi hona chahiye tha. Bolo kya option hai.",
                "Fine. Agar installment mein de sakta hoon toh batao.",
            ],
        }

    def respond(self, ai_message: str) -> str:
        self.turn_count += 1
        ai_lower = ai_message.lower()

        # Escalate over time
        if self.turn_count > 4:
            self.escalation_level = min(5, self.escalation_level + 1)

        # Choose response category based on AI message
        if self.turn_count == 1:
            category = "greeting"
        elif any(w in ai_lower for w in ["pay", "emi", "amount", "due", "pending", "payment", "loan"]):
            if self.escalation_level >= 3:
                category = "escalation"
            else:
                category = "payment_ask"
        elif any(w in ai_lower for w in ["understand", "sorry", "help", "option", "plan"]):
            self.escalation_level = max(0, self.escalation_level - 1)
            category = "calming_down"
        elif self.escalation_level >= 4:
            category = "escalation"
        else:
            category = random.choice(["payment_ask", "deflection"])

        self.mood = "angry" if self.escalation_level >= 3 else "frustrated"
        return random.choice(self._responses[category])


# ═══════════════════════════════════════════════════════════════════
# PERSONA 2: THE CONFUSED PATIENT
# ═══════════════════════════════════════════════════════════════════

class ConfusedPatient(BasePersona):
    """
    Speaks slowly in formal Hindi. Repeats questions often.
    Scenario: Healthcare follow-up call with ASHA worker AI.
    """

    def __init__(self):
        super().__init__()
        self.name = "Kamla Devi"
        self.language = "hindi"
        self.mood = "confused"
        self.dialect = "Formal Hindi"
        self.description = "Elderly patient confused about medication schedule"

        self._responses = {
            "greeting": [
                "Haan ji... kaun bol raha hai? Mujhe sunaai kam deta hai.",
                "Ji haan... ASHA didi ka phone hai kya? Bataiye bataiye.",
                "Namaste ji... aap kaun? Hospital se hai kya?",
            ],
            "confused": [
                "Ji? Mujhe samajh nahi aaya. Phir se boliye na zara.",
                "Ye dawai... kaunsi dawai? Mujhe bahut saari di thi doctor ne.",
                "Subah ya shaam? Ji mujhe yaad nahi... confused ho gayi hoon.",
                "Achha achha... lekin ye wahi dawai hai jo gol wali hai ya lambi wali?",
                "Beta, mujhe samajh nahi aata ye sab. Seedha seedha batao na.",
            ],
            "repetition": [
                "Aapne kya kaha? Phir se boliye na, dhire dhire boliye.",
                "Rukiye rukiye... main likh leti hoon... aapne kya bola?",
                "Haan ji haan ji... lekin ye pehle wali dawai band karni hai kya?",
                "Ek minute... mera beta aayega toh usko bhi samjha dena.",
            ],
            "compliance": [
                "Achha ji theek hai. Subah khali pet leni hai na?",
                "Ji haan, main le rahi hoon dawai. Roz leti hoon.",
                "Theek hai didi, aap jo bologe woh karungi.",
            ],
            "worry": [
                "Didi, mujhe dar lagta hai... koi side effect toh nahi hoga na?",
                "Pichli dawai se chakkar aate the... ye wali se toh nahi aayenge?",
                "Doctor sahab ne bola tha serious nahi hai na? Sach bolo didi.",
            ],
        }

    def respond(self, ai_message: str) -> str:
        self.turn_count += 1
        ai_lower = ai_message.lower()

        if self.turn_count == 1:
            category = "greeting"
        elif any(w in ai_lower for w in ["dawai", "medicine", "tablet", "dose", "prescription"]):
            category = random.choice(["confused", "repetition"])
        elif any(w in ai_lower for w in ["samjh", "understand", "clear", "simple"]):
            category = "compliance"
        elif any(w in ai_lower for w in ["health", "condition", "report", "test", "serious"]):
            category = "worry"
        elif self.turn_count % 2 == 0:
            category = "repetition"
        else:
            category = "confused"

        return random.choice(self._responses[category])


# ═══════════════════════════════════════════════════════════════════
# PERSONA 3: THE EVASIVE DEBTOR
# ═══════════════════════════════════════════════════════════════════

class EvasiveDebtor(BasePersona):
    """
    Avoids financial questions. Changes topic. Hindi-English mix.
    Scenario: Credit card debt collection call.
    """

    def __init__(self):
        super().__init__()
        self.name = "Vikram Mehta"
        self.language = "hindi-english"
        self.mood = "evasive"
        self.dialect = "Hindi-English mix (code-switching)"
        self.description = "Avoids answering financial questions, changes topic"

        self._responses = {
            "greeting": [
                "Hello hello... haan boliye, kaun hai?",
                "Yes yes, who's this? I'm a bit busy right now.",
                "Ji haan Vikram bol raha hoon... kya kaam hai?",
            ],
            "evasion": [
                "Haan woh toh... actually abhi main drive kar raha hoon. Baad mein baat karte hain.",
                "Payment? Woh toh meri wife handle karti hai. Unse baat karo na.",
                "Actually mere account mein koi issue tha na... woh resolve hua kya?",
                "Arey sun, ek minute... *muffled sounds* ... haan sorry kya bol rahe the?",
                "Hmm hmm... waise aapki company kaafi acchi hai. Kab se kaam kar rahe ho?",
            ],
            "topic_change": [
                "By the way, mujhe ek aur credit card chahiye tha. Mil sakta hai kya?",
                "Achha ye batao, aapke paas koi investment plan hai kya? Fixed deposit types?",
                "Waise aaj weather kaisa hai wahan? Yahan toh bahut garmi hai bhai.",
                "Ek second... mera dusra phone baj raha hai... hold karo.",
            ],
            "false_promise": [
                "Haan haan, next week definitely kar dunga payment. Pakka. 100%.",
                "Actually maine kal hi transfer kiya tha. Check karo na system mein.",
                "Bhai, Friday ko salary aayegi. Saturday ko hi bhej dunga. Promise.",
                "Main aaj hi net banking se kar deta hoon. Bas abhi busy hoon thoda.",
            ],
            "caught": [
                "Achha achha theek hai... kitna exact amount hai? Mujhe bhi pata nahi hai.",
                "Ok fine, I know it's pending. But genuinely paise nahi hain abhi.",
                "Dekho bhai, solemnly bol raha hoon, situation tight hai. Thoda time do.",
            ],
        }

    def respond(self, ai_message: str) -> str:
        self.turn_count += 1
        ai_lower = ai_message.lower()

        if self.turn_count == 1:
            category = "greeting"
        elif any(w in ai_lower for w in ["pay", "amount", "due", "emi", "pending", "outstanding", "balance"]):
            # 60% chance of evasion, 40% false promise
            category = random.choice(["evasion", "evasion", "evasion", "false_promise", "false_promise"])
        elif any(w in ai_lower for w in ["last time", "promise", "said", "earlier", "already"]):
            category = "caught"
        elif any(w in ai_lower for w in ["record", "legal", "action", "consequence"]):
            category = "false_promise"
        else:
            category = random.choice(["evasion", "topic_change"])

        return random.choice(self._responses[category])


# ═══════════════════════════════════════════════════════════════════
# PERSONA 4: THE COOPERATIVE USER
# ═══════════════════════════════════════════════════════════════════

class CooperativeUser(BasePersona):
    """
    Provides information clearly in Kannada.
    Responds positively to all questions.
    Scenario: Health insurance enrollment or bank KYC verification.
    """

    def __init__(self):
        super().__init__()
        self.name = "Lakshmi Gowda"
        self.language = "kannada"
        self.mood = "cooperative"
        self.dialect = "Standard Kannada"
        self.description = "Cooperative user who gives all information clearly"

        self._responses = {
            "greeting": [
                "Namaskara! Haan, Lakshmi Gowda matadtidini. Heli.",
                "Namaskara sir/madam. Neevu yaarige phone maDtiddira?",
                "Haan ji, nanu Lakshmi. Heli, yenu sahaaya beku?",
            ],
            "provide_info": [
                "Haadu, nanna Aadhaar number: 1234-5678-9012. Bere yenu beku?",
                "Nanna date of birth: 15th March 1985. Sari aagide?",
                "Address: #42, 3rd Cross, Jayanagar, Bangalore - 560041.",
                "Nanna phone number ee number-alli call maDtiddira adhe.",
                "Haan, nanna PAN card number: ABCPG1234H. Bareyiri.",
            ],
            "confirm": [
                "Haan, adhu sari. Correct aagiide.",
                "Haadu, nanu agree maDtini. Munduvarisi.",
                "Theek aagide, ella sari ide. Next step yenu?",
                "OK sir/madam, nanu ready. Yenu maDabeku heli.",
            ],
            "question": [
                "Ondu doubt ittu - ee scheme nalli yenu benefit sigatte?",
                "Premium eShTu aagutte tingalige? Nange thiliyabeku.",
                "Documentation yenu yenu beku? Nanu tayaar maDkonDu barthini.",
            ],
            "thanks": [
                "Dhanyavaadagalu! Tumba channagi explain maDdiri.",
                "Thank you so much. Nimage tumba grateful aagiidini.",
                "Tumba thanks. Neevu tumba helpful aagiddiri.",
                "Sariyaagi heLidiri. Nange tumba samaadhana aaytu.",
            ],
        }

    def respond(self, ai_message: str) -> str:
        self.turn_count += 1
        ai_lower = ai_message.lower()

        if self.turn_count == 1:
            category = "greeting"
        elif any(w in ai_lower for w in ["name", "aadhaar", "address", "phone", "pan", "dob", "birth", "number", "detail"]):
            category = "provide_info"
        elif any(w in ai_lower for w in ["confirm", "verify", "correct", "right", "agree"]):
            category = "confirm"
        elif any(w in ai_lower for w in ["benefit", "plan", "scheme", "premium", "cost", "document"]):
            category = "question"
        elif any(w in ai_lower for w in ["thank", "complete", "done", "finished", "success"]):
            category = "thanks"
        elif self.turn_count >= 6:
            category = "thanks"
        else:
            category = random.choice(["provide_info", "confirm"])

        self.mood = "happy" if self.turn_count > 3 else "cooperative"
        return random.choice(self._responses[category])


# ─── Persona Registry ────────────────────────────────────────────
PERSONAS = {
    "frustrated": FrustratedCustomer,
    "confused": ConfusedPatient,
    "evasive": EvasiveDebtor,
    "cooperative": CooperativeUser,
}

def get_persona(name: str) -> BasePersona:
    """Get a persona instance by name."""
    persona_class = PERSONAS.get(name.lower())
    if not persona_class:
        available = ", ".join(PERSONAS.keys())
        raise ValueError(f"Unknown persona '{name}'. Available: {available}")
    return persona_class()
