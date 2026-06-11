export const bankingUseCase = {
  fileSlug: "vaaksetu_banking_report",
  verticalLabel: "Financial Services & Debt Recovery",
  title: "Loan & Debt Automation",
  subtitle: "Multilingual verification, automated repayment tracking, and legal compliance auditing.",
  executiveSummary: "This report summaries the outbound calling KYC and collection simulation results. The dialogue engine tracked customer intent, categorized payment status, and logged compliance flags.",
  structuredTitle: "Financial Analytics & Intent",
  transcript: [
    {
      role: "assistant",
      label: "VaakSetu Outbound Voice Agent",
      text: "Namaskar Vikram ji, main ABC Finance se bol raha hoon. Kya aap sun sakte hain?",
      meta: "Outbound Call Started · English-Hindi Mix"
    },
    {
      role: "customer",
      label: "Customer (Vikram Mehta)",
      text: "Haan haan boliye, kya baat hai? Main abhi thoda busy hoon.",
      meta: "Detected: Hinglish · Evasive Dialect"
    },
    {
      role: "assistant",
      label: "VaakSetu Outbound Voice Agent",
      text: "Sir, aapka credit card ka repayment pichle 2 months se pending hai. Kya aap isse aaj settle kar sakte hain?",
      meta: "AI Intent: Settle Request"
    },
    {
      role: "customer",
      label: "Customer (Vikram Mehta)",
      text: "Actually job ka problem chal raha hai, Friday ko salary aayegi tab pakka transfer kar dunga.",
      meta: "Detected: Hinglish · Promise to Pay"
    }
  ],
  structuredRows: [
    { label: "Customer Name", value: "Vikram Mehta" },
    { label: "Account ID", value: "ACT-889021-DEB" },
    { label: "Outstanding Due", value: "₹24,500.00" },
    { label: "Payment Status", value: "Promise to Pay (Friday)" },
    { label: "Confidence", value: "High (89% historical match)" }
  ],
  compliance: {
    title: "Compliance Audit Status",
    bullets: [
      "No verbal threats or unlawful harassment patterns detected in outbound voice streams.",
      "Customer provided explicit promise-to-pay date which was log-registered in SQLite.",
      "Conversation recorded, transcript audited, and token usage pushed to dashboard analytics."
    ]
  }
};
