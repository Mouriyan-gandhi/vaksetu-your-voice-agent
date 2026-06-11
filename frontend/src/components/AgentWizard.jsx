import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Activity, 
  Wallet, 
  GraduationCap, 
  Phone, 
  Sparkles, 
  CheckCircle2, 
  Mic, 
  Camera, 
  Keyboard,
  Cpu,
  ShieldCheck,
  AlertCircle
} from "lucide-react";

const DOMAINS = {
  Healthcare: { 
    fields: ["symptoms", "medications", "history", "duration"],
    triggers: ["chest pain", "breathing difficulty", "severe bleeding"],
    icon: Activity
  },
  Finance: { 
    fields: ["loan_id", "amount", "payment_mode", "pan_card"],
    triggers: ["high overdue", "fraud suspicion", "payment failure"],
    icon: Wallet 
  },
  Education: { 
    fields: ["student_id", "course", "progress", "intent_type"],
    triggers: ["conceptual doubt", "session expiry", "low engagement"],
    icon: GraduationCap
  },
  Sales: { 
    fields: ["prospect_name", "product_interest", "budget", "timeline"],
    triggers: ["strong intent", "objection raised", "demo scheduled"],
    icon: Phone 
  },
  Others: {
    fields: ["generic_input", "priority_score"],
    triggers: ["general query"],
    icon: Sparkles
  }
};

const STEPS = [
  { id: 1, name: "Input Mode" },
  { id: 2, name: "Domain" },
  { id: 3, name: "Identity" },
  { id: 4, name: "Greeting" },
  { id: 5, name: "Fields" },
  { id: 6, name: "Intelligence" },
  { id: 7, name: "Triggers" },
  { id: 8, name: "Escalation" }
];

export default function AgentWizard({ onClose, onSave, initialData }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState(initialData || {
    inputs: ["Voice"],
    domain: "",
    customDomain: "",
    name: "",
    greeting: "",
    fields: [],
    prompt: "",
    triggers: [],
    escalation: {}
  });

  const isEdit = !!initialData;

  const next = () => setStep(s => Math.min(s + 1, 8));
  const back = () => setStep(s => Math.max(s - 1, 1));

  const handleFinish = async () => {
    setLoading(true);
    // Brief delay for loading animation
    await new Promise(r => setTimeout(r, 800));
    setLoading(false);
    setSuccess(true);
    setTimeout(() => {
      onSave(formData);
    }, 1500);
  };

  const update = (key, val) => setFormData(prev => ({ ...prev, [key]: val }));

  const toggleInput = (type) => {
    const current = formData.inputs;
    if (current.includes(type)) {
      update("inputs", current.filter(i => i !== type));
    } else {
      update("inputs", [...current, type]);
    }
  };

  const addField = (f) => {
    if (!formData.fields.includes(f)) {
      update("fields", [...formData.fields, f]);
    }
  };

  const removeField = (f) => update("fields", formData.fields.filter(field => field !== f));

  const addTrigger = (t) => {
    if (!formData.triggers.includes(t)) {
      update("triggers", [...formData.triggers, t]);
    }
  };

  const removeTrigger = (t) => update("triggers", formData.triggers.filter(trig => trig !== t));

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 sm:p-12">
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="absolute inset-0 bg-black/80 backdrop-blur-md"
      />

      <motion.div 
        initial={{ scale: 0.9, opacity: 0, y: 30 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 30 }}
        className="relative w-full max-w-4xl bg-background/40 border border-white/10 rounded-[3rem] overflow-hidden shadow-2xl flex flex-col md:flex-row h-full md:max-h-[85vh] backdrop-blur-3xl"
      >
        {/* Left Side: Sidebar / Step Indicator */}
        <div className="md:w-80 bg-white/[0.03] border-r border-white/5 p-8 flex flex-col justify-between">
          <div className="space-y-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-saffron flex items-center justify-center text-black font-bold">A</div>
              <span className="font-display text-xl">{isEdit ? "Update Agent" : "Agent Builder"}</span>
            </div>
            
            <nav className="space-y-4">
              {STEPS.map((s) => (
                <div key={s.id} className="flex items-center gap-4">
                   <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold transition-all duration-500
                     ${step >= s.id ? 'bg-saffron border-saffron text-black' : 'border-white/10 text-muted'}`}>
                     {s.id}
                   </div>
                   <span className={`text-xs font-mono uppercase tracking-widest transition-colors
                     ${step === s.id ? 'text-white' : 'text-muted'}`}>{s.name}</span>
                </div>
              ))}
            </nav>
          </div>

          <div className="pt-8 border-t border-white/5 opacity-40">
             <p className="text-[10px] font-mono leading-relaxed">
               Crafting sovereign AI agents with intelligent conversational extraction.
             </p>
          </div>
        </div>

        {/* Right Side: Content Area */}
        <div className="flex-1 p-12 flex flex-col justify-between overflow-y-auto">
          <AnimatePresence mode="wait">
            {!success ? (
              <motion.div 
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-8"
              >
                {/* STEP 1: INPUT MODE */}
                {step === 1 && (
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-4xl font-display mb-4">Select Input Type</h2>
                      <p className="text-muted leading-relaxed font-light">Choose how your AI agent captures knowledge. Multimodal is the standard.</p>
                    </div>
                    <div className="flex flex-wrap gap-4">
                      {[
                        { name: "Voice", icon: Mic },
                        { name: "Camera", icon: Camera },
                        { name: "Keyboard", icon: Keyboard }
                      ].map(item => (
                        <button
                          key={item.name}
                          onClick={() => toggleInput(item.name)}
                          className={`px-8 py-4 rounded-2xl border-2 font-mono text-xs uppercase tracking-widest transition-all duration-300 flex items-center gap-3
                            ${formData.inputs.includes(item.name) ? 
                              'border-saffron bg-saffron/10 text-white shadow-[0_0_20px_rgba(249,115,22,0.2)] scale-105' : 
                              'border-white/5 bg-white/[0.01] text-muted hover:border-white/20'}`}
                        >
                          <item.icon size={16} />
                          {item.name}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* STEP 2: DOMAIN */}
                {step === 2 && (
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-4xl font-display mb-4">Select Domain</h2>
                      <p className="text-muted font-light leading-relaxed">Defining your context unlocks intelligent auto-suggestions for your pipeline.</p>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.keys(DOMAINS).map(dom => {
                        const Icon = DOMAINS[dom].icon;
                        return (
                          <button
                            key={dom}
                            onClick={() => {
                              update("domain", dom);
                              update("fields", DOMAINS[dom].fields);
                            }}
                            className={`p-6 rounded-3xl border-2 flex flex-col items-center gap-4 transition-all duration-500
                               ${formData.domain === dom ? 
                                 'border-saffron bg-saffron/10 scale-[1.02] shadow-2xl' : 
                                 'border-white/5 bg-white/[0.01] hover:border-white/20'}`}
                          >
                            <Icon size={32} className={formData.domain === dom ? 'text-saffron' : 'opacity-40'} />
                            <span className="font-mono text-[10px] uppercase tracking-[0.2em]">{dom}</span>
                          </button>
                        );
                      })}
                    </div>
                    
                    <AnimatePresence>
                      {formData.domain === "Others" && (
                        <motion.div 
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="pt-4"
                        >
                          <input 
                            type="text"
                            placeholder="Specify custom industry..."
                            className="w-full bg-white/[0.03] border-b-2 border-white/10 p-4 text-xl font-display focus:outline-none focus:border-saffron transition-colors"
                            value={formData.customDomain}
                            onChange={(e) => update("customDomain", e.target.value)}
                            autoFocus
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                    <div className="flex justify-center italic text-xs text-muted/60">— Smart domain mapping enabled —</div>
                  </div>
                )}

                {/* STEP 3: IDENTITY */}
                {step === 3 && (
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-4xl font-display mb-4">Agent Identity</h2>
                      <p className="text-muted font-light leading-relaxed">Give your agent a professional persona. This reflects in audit logs.</p>
                    </div>
                    <div className="space-y-4">
                      <input 
                        type="text"
                        placeholder="e.g., Aarogya Assistant"
                        className="w-full bg-white/[0.03] border-b-2 border-white/10 p-6 text-2xl font-display focus:outline-none focus:border-saffron transition-colors"
                        value={formData.name}
                        onChange={(e) => update("name", e.target.value)}
                        autoFocus
                      />
                      <div className="flex gap-4 text-xs font-mono opacity-40">
                         <span>loan_bot_v1</span>
                         <span>emergency_ai_v2</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* STEP 4: GREETING */}
                {step === 4 && (
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-4xl font-display mb-4">Greeting Message</h2>
                      <p className="text-muted font-light leading-relaxed">The first message your agent sends when a session starts. Leave blank for auto-generated.</p>
                    </div>
                    <textarea 
                      className="w-full h-32 bg-white/[0.03] border border-white/5 rounded-3xl p-6 text-sm font-body leading-relaxed focus:outline-none focus:border-saffron/40 transition-all"
                      placeholder="e.g., Namaste! Main Aarogya Sahayak hoon. Aapki swasthya jaankari note karne mein madad karunga."
                      value={formData.greeting}
                      onChange={(e) => update("greeting", e.target.value)}
                    />
                    <div className="text-[10px] font-mono text-muted opacity-60 italic">Tip: Write in the language your users speak. Code-mixing (Hinglish) works great.</div>
                  </div>
                )}

                {/* STEP 5: FIELDS */}
                {step === 5 && (
                   <div className="space-y-8">
                      <div>
                        <h2 className="text-4xl font-display mb-4">Required Fields</h2>
                        <p className="text-muted font-light leading-relaxed">What data points should be structured from the conversation?</p>
                      </div>
                      <div className="flex flex-wrap gap-3">
                         {formData.fields.map(f => (
                           <span key={f} className="group flex items-center gap-2 px-4 py-2 rounded-full bg-saffron/10 border border-saffron/20 text-xs font-mono text-white">
                             {f}
                             <button onClick={() => removeField(f)} className="hover:text-red-400 transition-colors">✕</button>
                           </span>
                         ))}
                         <input 
                            placeholder="+ Add custom field"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                addField(e.currentTarget.value);
                                e.currentTarget.value = "";
                              }
                            }}
                            className="bg-transparent border-b border-white/20 focus:border-saffron text-xs font-mono p-2 focus:outline-none"
                         />
                      </div>
                      {formData.domain && (
                        <div className="space-y-4">
                           <p className="text-[10px] font-mono text-muted uppercase tracking-widest">Recommended for {formData.domain}:</p>
                           <div className="flex flex-wrap gap-2">
                             {DOMAINS[formData.domain].fields.filter(f => !formData.fields.includes(f)).map(f => (
                               <button key={f} onClick={() => addField(f)} className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-[10px] font-mono text-muted border border-white/5">
                                 {f}
                               </button>
                             ))}
                           </div>
                        </div>
                      )}
                   </div>
                )}

                {/* STEP 6: PROMPT */}
                {step === 6 && (
                  <div className="space-y-8">
                     <div>
                       <h2 className="text-4xl font-display mb-4">Intelligence</h2>
                       <p className="text-muted font-light leading-relaxed">Define behavioral constraints and the system's core persona.</p>
                     </div>
                     <div className="relative group">
                        <textarea 
                          className="w-full h-48 bg-white/[0.03] border border-white/5 rounded-3xl p-6 text-sm font-body leading-relaxed focus:outline-none focus:border-saffron/40 transition-all"
                          placeholder="You are an empathetic medical assistant who specializes in symptoms triage in Hindi and Kannada..."
                          value={formData.prompt}
                          onChange={(e) => update("prompt", e.target.value)}
                        />
                        <div className="absolute bottom-4 right-4 text-[10px] font-mono text-muted bg-background/80 px-2 py-1 rounded">
                           RLAIF Enabled
                        </div>
                     </div>
                  </div>
                )}

                {/* STEP 7: TRIGGERS */}
                {step === 7 && (
                   <div className="space-y-8">
                      <div>
                        <h2 className="text-4xl font-display mb-4">System Triggers</h2>
                        <p className="text-muted font-light leading-relaxed">Identify critical phrases that require immediate workflow actions.</p>
                      </div>
                      <div className="flex flex-wrap gap-3">
                         {formData.triggers.map(t => (
                           <span key={t} className="flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-mono text-blue-400">
                             {t}
                             <button onClick={() => removeTrigger(t)} className="hover:text-red-400 transition-colors">✕</button>
                           </span>
                         ))}
                         <input 
                            placeholder="+ Add trigger condition"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                addTrigger(e.currentTarget.value);
                                e.currentTarget.value = "";
                              }
                            }}
                            className="bg-transparent border-b border-white/20 focus:border-saffron text-xs font-mono p-2 focus:outline-none"
                         />
                      </div>
                      {formData.domain && (
                        <div className="space-y-4">
                           <p className="text-[10px] font-mono text-muted uppercase tracking-widest">Contextual Suggestions:</p>
                           <div className="flex flex-wrap gap-2">
                             {DOMAINS[formData.domain].triggers.filter(t => !formData.triggers.includes(t)).map(t => (
                               <button key={t} onClick={() => addTrigger(t)} className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-[10px] font-mono text-muted border border-white/5">
                                 {t}
                               </button>
                             ))}
                           </div>
                        </div>
                      )}
                   </div>
                )}

                {/* STEP 8: ESCALATION */}
                {step === 8 && (
                  <div className="space-y-8">
                     <div>
                       <h2 className="text-4xl font-display mb-4">Escalation Logic</h2>
                       <p className="text-muted font-light leading-relaxed">When a trigger is fired, define the immediate emergency response.</p>
                     </div>
                     <div className="space-y-6">
                        {formData.triggers.length > 0 ? (
                           formData.triggers.map(t => (
                             <div key={t} className="flex items-center gap-6 p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                                <div className="text-xs font-mono text-blue-400 uppercase tracking-widest w-40 truncate">{t}</div>
                                <div className="text-muted">→</div>
                                <input 
                                   className="flex-1 bg-transparent border-b border-white/10 py-2 text-sm focus:outline-none focus:border-saffron transition-all"
                                   placeholder="Escalation message..."
                                   value={formData.escalation[t] || ""}
                                   onChange={(e) => update("escalation", { ...formData.escalation, [t]: e.target.value })}
                                />
                             </div>
                           ))
                        ) : (
                          <div className="text-center py-10 opacity-30 text-xs italic">— No triggers defined —</div>
                        )}
                     </div>
                  </div>
                )}
              </motion.div>
            ) : (
              /* SUCCESS STATE */
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center p-20 text-center space-y-8"
              >
                <div className="w-40 h-40 rounded-full border-4 border-emerald-500/20 bg-emerald-500/10 flex items-center justify-center text-8xl shadow-[0_0_50px_rgba(16,185,129,0.2)]">
                   <CheckCircle2 size={80} className="text-emerald-500" />
                </div>
                <h2 className="text-5xl font-display text-white">{isEdit ? "Agent Updated" : "Agent Created"}</h2>
                <p className="text-muted text-xl max-w-sm mx-auto font-light">
                  {formData.name} {isEdit ? "has been successfully updated and synchronized." : "is now deployed and ready to process infrastructure conversations."}
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Action Buttons */}
          {!success && (
            <div className="mt-12 flex justify-between pt-8 border-t border-white/5">
              <button 
                onClick={step === 1 ? onClose : back}
                className="text-xs font-mono uppercase tracking-widest text-muted hover:text-white transition-colors"
              >
                {step === 1 ? "Cancel" : "Previous Step"}
              </button>
              
              <button 
                onClick={step === 8 ? handleFinish : next}
                disabled={loading}
                className="btn-primary px-12 py-4 text-xs font-bold rounded-full relative group overflow-hidden"
              >
                {loading ? (
                   <span className="flex items-center gap-2">
                     <div className="w-3 h-3 rounded-full border-2 border-black/30 border-t-black animate-spin" />
                     {isEdit ? "Updating..." : "Building..."}
                   </span>
                ) : (
                  step === 8 ? (isEdit ? "Update Agent" : "Create Agent") : "Next Module"
                )}
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
