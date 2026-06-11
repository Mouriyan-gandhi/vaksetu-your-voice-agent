export const healthcareUseCase = {
  fileSlug: "vaaksetu_healthcare_report",
  verticalLabel: "Healthcare & Emergency Response",
  title: "Clinical Voice Automation",
  subtitle: "Real-time multilingual intake and structured triage scoring for ASHA workers and hospital emergency pods.",
  executiveSummary: "This report demonstrates the deployment of VaakSetu for real-time clinical intake. The system processes multilingual speech, structures clinical data, and assigns priority risk levels dynamically.",
  structuredTitle: "Clinical Structured Data",
  highlight: {
    title: "Automatic Escalation",
    body: "System detected high-fever indicators and acute headache symptoms. Alert dispatched to hospital triage team via API Webhook."
  },
  transcript: [
    {
      role: "patient",
      label: "Patient (Mrs. Rao)",
      text: "Mujhe teen din se bahut tez bukhar hai aur sir mein bhayanak dard ho raha hai.",
      meta: "Detected: Hindi (code-mixed) · Sarvam ASR"
    },
    {
      role: "assistant",
      label: "VaakSetu AI (Clinical Assistant)",
      text: "Aapko bukhar kitna hai? Kya aapne koi dawai li hai?",
      meta: "AI Response · Sentiment: Empathetic"
    },
    {
      role: "patient",
      label: "Patient (Mrs. Rao)",
      text: "Bukhar 102 degree hai, maine paracetamol li thi par koi fayda nahi hua.",
      meta: "Detected: Hinglish · Sarvam ASR"
    },
    {
      role: "assistant",
      label: "VaakSetu AI (Clinical Assistant)",
      text: "Theek hai, main aapki details hospital triage dashboard mein update kar rahi hoon. Kripya thoda aaram karein.",
      meta: "AI Action: Escalating"
    }
  ],
  structuredRows: [
    { label: "Symptoms", value: "Severe High Fever, Acute Headache" },
    { label: "Duration", value: "3 Days" },
    { label: "Medications", value: "Paracetamol (Ineffective)" },
    { label: "Risk Level", value: "High / Urgent Escalation" }
  ],
  features: [
    {
      title: "Multilingual Intake",
      desc: "ASHA workers can document patient data in 11+ Indic languages or code-mixed dialects without manual form entry."
    },
    {
      title: "Clinical Information Extraction",
      desc: "Automatically extracts clinical symptoms, duration, dosage, and patient history into standardized tables."
    },
    {
      title: "Emergency Triaging",
      desc: "Real-time risk scoring using clinical guidelines and immediate dispatch alerts to local emergency response teams."
    }
  ]
};
