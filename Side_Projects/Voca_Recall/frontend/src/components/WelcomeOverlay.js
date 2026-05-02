import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ChevronRight, ChevronLeft, Key, Database, Mail, Sparkles } from 'lucide-react';

export const WELCOME_STORAGE_KEY = 'voca_welcome_seen';

/* ─── SVG Owl mascot ───────────────────────────────────────────────────────── */
const MascotOwl = ({ celebrate = false }) => (
  <svg
    viewBox="0 0 160 200"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    className={`w-full h-full drop-shadow-xl ${celebrate ? 'animate-celebrate' : 'animate-mascot-bob'}`}
  >
    {/* ── Body ── */}
    <ellipse cx="80" cy="148" rx="52" ry="58" fill="#2563eb" />
    {/* ── Belly ── */}
    <ellipse cx="80" cy="158" rx="34" ry="40" fill="#dbeafe" />

    {/* ── Left wing (static) ── */}
    <ellipse
      cx="34"
      cy="140"
      rx="20"
      ry="44"
      fill="#1d4ed8"
      transform="rotate(18 34 140)"
    />

    {/* ── Right wing / waving arm (animated) ── */}
    <g className="animate-mascot-wave">
      <ellipse
        cx="126"
        cy="132"
        rx="20"
        ry="44"
        fill="#1d4ed8"
        transform="rotate(-18 126 132)"
      />
    </g>

    {/* ── Head ── */}
    <circle cx="80" cy="74" r="46" fill="#2563eb" />

    {/* ── Ear tufts ── */}
    <polygon points="53,36 44,10 68,32" fill="#1d4ed8" />
    <polygon points="107,36 116,10 92,32" fill="#1d4ed8" />

    {/* ── Graduation cap ── */}
    <rect x="54" y="32" width="52" height="9" rx="2" fill="#0f172a" />
    <polygon points="80,16 46,34 114,34" fill="#0f172a" />
    <line x1="114" y1="34" x2="122" y2="50" stroke="#0f172a" strokeWidth="2.5" />
    <circle cx="122" cy="53" r="5" fill="#f59e0b" />

    {/* ── Eye whites ── */}
    <circle cx="62" cy="72" r="19" fill="white" />
    <circle cx="98" cy="72" r="19" fill="white" />

    {/* ── Pupils ── */}
    <circle cx="64" cy="74" r="11" fill="#1e3a8a" />
    <circle cx="100" cy="74" r="11" fill="#1e3a8a" />

    {/* ── Eye highlights ── */}
    <circle cx="68" cy="70" r="4" fill="white" />
    <circle cx="104" cy="70" r="4" fill="white" />

    {/* ── Beak ── */}
    <polygon points="80,86 71,100 89,100" fill="#f59e0b" />

    {/* ── Book in left wing ── */}
    <rect x="10" y="116" width="34" height="44" rx="3" fill="#ef4444" />
    <rect x="13" y="119" width="28" height="38" rx="2" fill="#fecaca" />
    <line x1="27" y1="119" x2="27" y2="157" stroke="#ef4444" strokeWidth="2" />
    <line x1="20" y1="130" x2="34" y2="130" stroke="#ef4444" strokeWidth="1.5" />
    <line x1="20" y1="138" x2="34" y2="138" stroke="#ef4444" strokeWidth="1.5" />
    <line x1="20" y1="146" x2="34" y2="146" stroke="#ef4444" strokeWidth="1.5" />

    {/* ── Feet ── */}
    <ellipse cx="64" cy="200" rx="15" ry="7" fill="#f59e0b" />
    <ellipse cx="96" cy="200" rx="15" ry="7" fill="#f59e0b" />
  </svg>
);

/* ─── Step badge icon inside a coloured bubble ───────────────────────────── */
const StepBadge = ({ step }) => {
  const Icon = step.Icon;
  return (
    <div
      className={`inline-flex items-center justify-center w-12 h-12 rounded-2xl ${step.badgeBg} mb-4`}
    >
      {Icon ? (
        <Icon className={`h-6 w-6 ${step.badgeColor}`} />
      ) : (
        <span className="text-2xl leading-none">{step.emoji}</span>
      )}
    </div>
  );
};

/* ─── Tour step data ─────────────────────────────────────────────────────── */
const tourSteps = [
  {
    emoji: '👋',
    Icon: null,
    badgeBg: 'bg-blue-100',
    badgeColor: '',
    gradientFrom: 'from-primary-500',
    gradientTo: 'to-indigo-600',
    title: 'Welcome to Voca Recaller!',
    subtitle: 'Your daily vocabulary learning companion',
    body: "I'll walk you through four quick steps so you can start getting daily vocabulary emails from your Notion workspace.",
    isLast: false,
  },
  {
    emoji: '',
    Icon: Key,
    badgeBg: 'bg-violet-100',
    badgeColor: 'text-violet-600',
    gradientFrom: 'from-violet-500',
    gradientTo: 'to-purple-600',
    title: 'Step 1 — Grab Your Notion Token',
    subtitle: 'Create a Notion integration',
    body: 'Go to notion.so/my-integrations, create a new integration, and copy the Internal Integration Secret. Then paste it in Settings → Manage Tokens.',
    isLast: false,
  },
  {
    emoji: '',
    Icon: Database,
    badgeBg: 'bg-purple-100',
    badgeColor: 'text-purple-600',
    gradientFrom: 'from-purple-500',
    gradientTo: 'to-pink-600',
    title: 'Step 2 — Connect a Database',
    subtitle: 'Share your Notion vocab database',
    body: 'In Notion open your vocabulary database, click ••• → Add connections, and select your integration. Then add the database URL in the Databases page.',
    isLast: false,
  },
  {
    emoji: '',
    Icon: Mail,
    badgeBg: 'bg-green-100',
    badgeColor: 'text-green-600',
    gradientFrom: 'from-green-500',
    gradientTo: 'to-emerald-600',
    title: 'Step 3 — Schedule Daily Emails',
    subtitle: 'Set your learning rhythm',
    body: 'Head to Services, tap Add Service, pick your database and word count, then choose a daily delivery time. Your vocab emails will start arriving automatically!',
    isLast: false,
  },
  {
    emoji: '🎉',
    Icon: Sparkles,
    badgeBg: 'bg-amber-100',
    badgeColor: 'text-amber-600',
    gradientFrom: 'from-orange-500',
    gradientTo: 'to-amber-500',
    title: "You're All Set!",
    subtitle: 'Start building your vocabulary habit',
    body: 'Daily vocab emails are on their way. Check Email Logs to see delivery history and visit How to Use any time for a refresher.',
    isLast: true,
  },
];

/* ─── Main overlay component ─────────────────────────────────────────────── */
const WelcomeOverlay = ({ onClose }) => {
  const [step, setStep] = useState(0);
  const [stepKey, setStepKey] = useState(0); // force re-mount for step fade animation
  const navigate = useNavigate();

  const current = tourSteps[step];
  const isLast = current.isLast;
  const isCelebrate = isLast;

  const goTo = useCallback(
    (next) => {
      setStep(next);
      setStepKey((k) => k + 1);
    },
    []
  );

  const handleClose = useCallback(
    (goToDashboard = false) => {
      localStorage.setItem(WELCOME_STORAGE_KEY, 'true');
      onClose();
      if (goToDashboard) navigate('/dashboard');
    },
    [onClose, navigate]
  );

  return (
    /* ── Backdrop ── */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-overlay-in"
      style={{ background: 'rgba(15,23,42,0.72)', backdropFilter: 'blur(4px)' }}
      role="dialog"
      aria-modal="true"
      aria-label="Welcome tour"
    >
      {/* ── Card ── */}
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-card-in">

        {/* ── Gradient header strip ── */}
        <div className={`h-2 bg-gradient-to-r ${current.gradientFrom} ${current.gradientTo} transition-all duration-500`} />

        {/* ── Skip button ── */}
        <button
          onClick={() => handleClose(false)}
          className="absolute top-4 right-4 p-1.5 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors duration-150 focus:outline-none"
          aria-label="Skip tour"
        >
          <X className="h-5 w-5" />
        </button>

        {/* ── Body layout: mascot + content ── */}
        <div className="flex flex-col sm:flex-row gap-0">

          {/* ── Mascot panel ── */}
          <div
            className={`flex items-end justify-center sm:w-48 py-6 px-4 sm:py-10 bg-gradient-to-b ${current.gradientFrom} ${current.gradientTo} transition-all duration-500`}
          >
            <div className="w-32 h-40 sm:w-36 sm:h-44">
              <MascotOwl celebrate={isCelebrate} />
            </div>
          </div>

          {/* ── Step content ── */}
          <div className="flex-1 p-6 sm:p-8 flex flex-col justify-between">
            <div key={stepKey} className="animate-step-fade">
              <StepBadge step={current} />
              <h2 className="text-2xl font-bold text-gray-900 mb-1">{current.title}</h2>
              <p className="text-sm font-medium text-primary-500 mb-3">{current.subtitle}</p>
              <p className="text-gray-600 leading-relaxed">{current.body}</p>
            </div>

            {/* ── Navigation ── */}
            <div className="mt-8 flex items-center justify-between">
              {/* Dot indicators */}
              <div className="flex gap-2">
                {tourSteps.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => goTo(i)}
                    aria-label={`Go to step ${i + 1}`}
                    className={`rounded-full transition-all duration-300 focus:outline-none ${
                      i === step
                        ? 'w-6 h-2.5 bg-primary-500'
                        : 'w-2.5 h-2.5 bg-gray-200 hover:bg-gray-300'
                    }`}
                  />
                ))}
              </div>

              {/* Prev / Next */}
              <div className="flex items-center gap-2">
                {step > 0 && (
                  <button
                    onClick={() => goTo(step - 1)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors duration-150 focus:outline-none"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Back
                  </button>
                )}

                {isLast ? (
                  <button
                    onClick={() => handleClose(false)}
                    className={`flex items-center gap-1.5 px-5 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r ${current.gradientFrom} ${current.gradientTo} shadow-md hover:opacity-90 transition-opacity duration-150 focus:outline-none`}
                  >
                    <Sparkles className="h-4 w-4" />
                    Start Learning!
                  </button>
                ) : (
                  <button
                    onClick={() => goTo(step + 1)}
                    className="flex items-center gap-1 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-primary-600 hover:bg-primary-700 shadow-sm transition-colors duration-150 focus:outline-none"
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeOverlay;
