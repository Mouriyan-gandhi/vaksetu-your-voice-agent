import sqlite3
import json
import os
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "..", "vaaksetu.db")

HEALTH_PROMPT = """You are Aarogya Sahayak, a compassionate multilingual health triage manager. Your goal is to gather patient details, understand their symptoms, assess the risk level (Low, Medium, High), and book a clinical appointment.

CONVERSATION & GREETING RULES:
- Ask only ONE short question at a time. Keep responses to 1-2 sentences maximum.
- Talk exactly like a live human on a voice call—empathetic, friendly, and brief.
- DO NOT list all fields at once. Collect them naturally.
- DO NOT repeat back everything the user says in a loop.
- If the patient sounds distressed, acknowledge it with empathy before proceeding.

LANGUAGE RULES:
- Support 11 Indic languages and English.
- Always respond in the EXACT language the user is speaking (e.g., Hindi, English, Hinglish, Kannada, Tamil, etc.). 
- Switch languages smoothly mid-conversation if the user changes their language.

Triaging & Risk Assessment:
- HIGH RISK (e.g., severe chest pain, extreme breathing difficulty): Advise calling an ambulance (108) immediately and stop the flow.
- LOW/MEDIUM RISK (e.g., fever, mild pain, cold): Collect patient age, gender, symptom duration, and then proceed to book an appointment.

APPOINTMENT BOOKING:
- Once symptoms are understood, ask for their preferred date and time for booking the clinical appointment.
- Confirm the appointment details before ending the call/session.
"""

def update_agents():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Update Test Health Bot (4232e541)
    fields = ["patient_name", "age", "gender", "symptoms", "symptom_duration", "risk_level", "appointment_date_time"]
    inputs = ["Voice", "Keyboard"]
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        UPDATE agents 
        SET name = ?, fields = ?, system_prompt = ?, greeting = ?, default_language = ?, updated_at = ?
        WHERE id = ?
    """, (
        "Aarogya Sahayak (Healthcare Assistant)",
        json.dumps(fields),
        HEALTH_PROMPT,
        "Namaste! Main Aarogya Sahayak hoon. Aapki swasthya jaankari aur appointment book karne mein madad karunga. Pehle, kya aap apna naam bata sakte hain?",
        "hi-IN",
        now,
        "4232e541"
    ))
    
    print("Updated agent '4232e541'.")
    
    # 2. Check if aarogya-sahayak agent exists, if not create it
    cursor.execute("SELECT id FROM agents WHERE id = ?", ("aarogya-sahayak",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO agents (id, name, domain, custom_domain, inputs, fields, system_prompt, greeting, triggers, escalation, escalation_message, default_language, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "aarogya-sahayak",
            "Aarogya Sahayak (Healthcare Assistant)",
            "Healthcare",
            "",
            json.dumps(inputs),
            json.dumps(fields),
            HEALTH_PROMPT,
            "Namaste! Main Aarogya Sahayak hoon. Aapki swasthya jaankari aur appointment book karne mein madad karunga. Pehle, kya aap apna naam bata sakte hain?",
            json.dumps([]),
            json.dumps({}),
            "Emergency situation detected. Please dial 108 immediately.",
            "hi-IN",
            now,
            now
        ))
        print("Created agent 'aarogya-sahayak'.")
    else:
        cursor.execute("""
            UPDATE agents 
            SET name = ?, fields = ?, system_prompt = ?, greeting = ?, default_language = ?, updated_at = ?
            WHERE id = ?
        """, (
            "Aarogya Sahayak (Healthcare Assistant)",
            json.dumps(fields),
            HEALTH_PROMPT,
            "Namaste! Main Aarogya Sahayak hoon. Aapki swasthya jaankari aur appointment book karne mein madad karunga. Pehle, kya aap apna naam bata sakte hain?",
            "hi-IN",
            now,
            "aarogya-sahayak"
        ))
        print("Updated agent 'aarogya-sahayak'.")
        
    conn.commit()
    conn.close()
    print("Database agents updated successfully!")

if __name__ == "__main__":
    update_agents()
