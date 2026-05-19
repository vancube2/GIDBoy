"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode?: string;
  timestamp: Date;
}

const MODES = [
  { id: "AUTO", label: "Auto", icon: "🤖", color: "bg-gray-700" },
  { id: "RESEARCH", label: "Research", icon: "🔬", color: "bg-blue-600" },
  { id: "OPPORTUNITY", label: "Opportunity", icon: "💼", color: "bg-green-600" },
  { id: "SIGNAL", label: "Signal", icon: "⚡", color: "bg-yellow-600" },
  { id: "ANALYSIS", label: "Analysis", icon: "📊", color: "bg-purple-600" },
  { id: "CONTENT", label: "Content", icon: "📝", color: "bg-pink-600" },
  { id: "CAREER", label: "Career", icon: "🎯", color: "bg-indigo-600" },
  { id: "EXECUTION", label: "Execution", icon: "⚙️", color: "bg-gray-600" },
];

const EXAMPLE_QUERIES = [
  "Research Solana's Firedancer upgrade",
  "Find grants for crypto researchers",
  "Detect emerging DeFi trends",
  "Analyze Solana vs Ethereum fees",
  "Write a thread about MEV",
  "Draft outreach to a VC",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedMode, setSelectedMode] = useState("AUTO");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const mode = selectedMode === "AUTO" ? detectMode(input) : selectedMode;
      const response = await generateResponse(input, mode);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response,
        mode: mode,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const detectMode = (query: string): string => {
    const q = query.toLowerCase();
    if (q.includes("grant") || q.includes("job") || q.includes("fellowship")) return "OPPORTUNITY";
    if (q.includes("trend") || q.includes("signal") || q.includes("emerging")) return "SIGNAL";
    if (q.includes("analyze") || q.includes("data") || q.includes("metric")) return "ANALYSIS";
    if (q.includes("post") || q.includes("thread") || q.includes("content")) return "CONTENT";
    if (q.includes("career") || q.includes("resume")) return "CAREER";
    if (q.includes("apply") || q.includes("email") || q.includes("draft")) return "EXECUTION";
    return "RESEARCH";
  };

  const generateResponse = async (query: string, mode: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const responses: Record<string, string> = {
      RESEARCH: `INSIGHTS:
- Solana's Firedancer client is entering mainnet beta in Q1 2025
- Jito's MEV infrastructure now processes 80% of Solana transactions
- Institutional custody solutions (Fireblocks, Copper) expanded Solana support

ANALYSIS:
- Why: Network reliability concerns drove validator client diversification
- How: Firedancer uses C++ rewrite for 10x throughput improvement
- Impact: Solana becomes enterprise-grade infrastructure

OPPORTUNITIES:
1. Firedancer RPC node operators - early positioning for validator business
2. Jito restaking derivatives - liquid staking yield optimization
3. Institutional DeFi bridges - compliance-first lending protocols

SIGNALS:
- Coinbase institutional custody quietly added SPL token support

ACTIONS:
- Benchmark Firedancer RPC latency vs Agave
- Research JitoSOL integrations for DeFi protocols

END.`,

      OPPORTUNITY: `TOP OPPORTUNITIES:

1. Messari - Crypto Research Analyst
   - What: Produce sector-specific research reports on DeFi/DePIN
   - Who For: Researchers (in crypto)
   - Why: Leading crypto intelligence firm, high visibility
   - Skill Match: high
   - Difficulty: 7
   - Action: Submit writing sample via messari.io/careers

2. Open Society Foundations - Digital Rights Research Grant
   - What: $100K grant for studying surveillance tech and democracy
   - Who For: Researchers (outside crypto)
   - Why: No crypto background required, focuses on policy/impact
   - Skill Match: medium
   - Difficulty: 4
   - Action: Apply at opensociety.org/grants by March 30

3. a16z crypto - Research Fellow
   - What: 6-month fellowship exploring cryptographic primitives
   - Who For: Researchers (in crypto)
   - Why: Access to portfolio companies, publish under a16z brand
   - Skill Match: high
   - Difficulty: 9
   - Action: Email research@a16zcrypto.com with thesis proposal

END.`,

      SIGNAL: `SIGNALS:
1. AI agent tokens on Solana up 400% QoQ with real usage metrics
2. PayPal USD stablecoin volume shifting to Solana from Ethereum
3. Institutional validators increasing stake weight significantly

WHY IT MATTERS:
- Real transaction volume, not speculation
- Payment rails choosing Solana for cost/speed
- Validator decentralization improving

EARLY OPPORTUNITIES:
1. AI x DeFi infrastructure plays
2. Payment SDK integrations
3. Institutional validator tooling

END.`,

      ANALYSIS: `DATA POINTS:
- Solana daily fees: $2.8M (7-day avg)
- Active addresses: 1.2M (90-day high)
- Staked SOL ratio: 68% (decreasing, indicating utilization)

PATTERNS:
- Fee revenue inversely correlated with spam transactions
- Address growth outpacing Ethereum L2s

INSIGHT:
Network activity is quality-driven, not airdrop farming.

IMPLICATIONS:
- Sustainable revenue for validators
- Real user adoption vs mercenary capital

END.`,

      CONTENT: `X THREAD:
1. Hook: Solana just did something Ethereum couldn't in 8 years
2. Context: Firedancer validator client hit mainnet
3. Key Insight 1: 10x throughput with same hardware
4. Key Insight 2: Written in C++, audited by 3 firms
5. Opportunity: Early validator node operators
6. Implication: Solana is now enterprise-grade infra
7. Closing: The L1 wars are over. Solana won.

LINKEDIN POST:
Solana's Firedancer client launch marks a pivotal moment for blockchain infrastructure. After years of client diversity challenges, Solana now has a production-grade alternative validator implementation—something no other L1 has achieved. For institutional investors, this represents derisked infrastructure worth evaluating.

END.`,

      CAREER: `MATCHED ROLES:
1. Senior Rust Engineer at Phantom
   - Fit: Wallet infrastructure, high growth
   - Gap: Mobile development experience

2. Protocol Engineer at Marinade
   - Fit: Liquid staking, DeFi expertise
   - Gap: Formal verification knowledge

3. Research Analyst at Multicoin
   - Fit: Technical writing, ecosystem knowledge
   - Gap: Traditional finance background

POSITIONING:
Frame as Solana-native builder with protocol research skills.

ACTIONS:
- Contribute to Solana Stack Exchange
- Publish technical analysis on X
- Open-source a small Rust tool

END.`,

      EXECUTION: `TASK BREAKDOWN:
- Research target company background
- Draft personalized outreach
- Prepare relevant work samples
- Follow up timeline

OUTPUTS:
Cold outreach email + project README

MESSAGES:
Subject: Protocol Engineer Application - [Your Name]

Hi [Name],

I've been following [Company]'s work on [specific project]. Recently built [relevant project] that aligns with your roadmap.

Would love to discuss how I can contribute.

Best,
[Your Name]

NEXT ACTION:
Send email to hiring manager today.

END.`,
    };

    return responses[mode] || responses.RESEARCH;
  };

  const formatContent = (content: string) => {
    return content.split("\n").map((line, i) => {
      if (line.startsWith("END.")) return null;
      if (line.match(/^(INSIGHTS|SIGNALS|TOP|DATA|X|LINKEDIN|MATCHED|TASK|OUTPUTS|MESSAGES|NEXT|ANALYSIS|OPPORTUNITIES|WHY|EARLY|PATTERNS|IMPLICATIONS|POSITIONING|ACTIONS):/)) {
        return (
          <h3 key={i} className="text-lg font-bold text-blue-400 mt-4 mb-2">
            {line}
          </h3>
        );
      }
      if (line.match(/^\d+\./)) {
        return (
          <div key={i} className="ml-4 mb-2 text-gray-300">
            {line}
          </div>
        );
      }
      if (line.startsWith("-")) {
        return (
          <div key={i} className="ml-4 mb-1 text-gray-400">
            {line}
          </div>
        );
      }
      return line ? (
        <p key={i} className="mb-2 text-gray-300">
          {line}
        </p>
      ) : null;
    });
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              GIDBoy
            </h1>
            <p className="text-sm text-gray-500">Intelligence OS for Crypto Research</p>
          </div>
          <div className="text-xs text-gray-600">v1.0.0</div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-6">
        <aside className="w-64 hidden lg:block">
          <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Mode
            </h3>
            <div className="space-y-2">
              {MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${
                    selectedMode === mode.id
                      ? `${mode.color} text-white`
                      : "text-gray-400 hover:bg-gray-800"
                  }`}
                >
                  <span>{mode.icon}</span>
                  <span>{mode.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 bg-gray-900/50 rounded-xl p-4 border border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Examples
            </h3>
            <div className="space-y-2">
              {EXAMPLE_QUERIES.map((query, i) => (
                <button
                  key={i}
                  onClick={() => setInput(query)}
                  className="w-full text-left px-3 py-2 text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded-lg transition-colors"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-h-[calc(100vh-140px)]">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 && (
              <div className="text-center py-20">
                <div className="text-6xl mb-4">🤖</div>
                <h2 className="text-2xl font-bold text-gray-300 mb-2">Welcome to GIDBoy</h2>
                <p className="text-gray-500 max-w-md mx-auto">
                  Your autonomous intelligence agent for crypto research, opportunities, and execution.
                </p>
                <div className="mt-8 flex flex-wrap justify-center gap-2">
                  {EXAMPLE_QUERIES.slice(0, 3).map((query, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(query)}
                      className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-full text-sm text-gray-400 transition-colors"
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-6 py-4 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800/50 border border-gray-700"
                  }`}
                >
                  {message.role === "assistant" && message.mode && (
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-700">
                      <span className="text-xs font-mono text-blue-400">
                        [{message.mode}]
                      </span>
                      <span className="text-xs text-gray-600">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  )}
                  <div className="prose prose-invert prose-sm max-w-none">
                    {formatContent(message.content)}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800/50 border border-gray-700 rounded-2xl px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="relative">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-2">
              <div className="flex items-center gap-2 mb-2 px-2">
                <span className="text-xs text-gray-500">Mode:</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    MODES.find((m) => m.id === selectedMode)?.color || "bg-gray-700"
                  } text-white`}
                >
                  {MODES.find((m) => m.id === selectedMode)?.label || "Auto"}
                </span>
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask GIDBoy anything about crypto..."
                  className="flex-1 bg-transparent text-white placeholder-gray-500 px-4 py-3 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg font-medium transition-colors"
                >
                  {isLoading ? "..." : "Send"}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-2 text-center">
              Use /MODE prefix or select mode from sidebar • GIDBoy may produce inaccurate information
            </p>
          </form>
        </main>
      </div>
    </div>
  );
}