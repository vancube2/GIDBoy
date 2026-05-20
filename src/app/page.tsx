"use client";

import { useState, useRef, useEffect } from "react";
import React from "react";

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
  "Research Solana Liquidity Provision with data",
  "Analyze DeFi protocol metrics with charts",
  "Detect emerging narratives early",
  "Find research grants with workflows",
  "Compare L2 performance with data",
  "Identify problems in crypto custody",
];

// Rich content formatter component
const FormattedContent = ({ content }: { content: string }) => {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip END.
    if (line.trim() === "END." || line.trim() === "END") {
      i++;
      continue;
    }

    // Code blocks (```)
    if (line.startsWith("```")) {
      const language = line.slice(3).trim();
      let code = "";
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        code += lines[i] + "\n";
        i++;
      }
      elements.push(
        <pre key={i} className="bg-gray-950 border border-gray-800 rounded-lg p-4 my-4 overflow-x-auto">
          <code className="text-sm font-mono text-gray-300 whitespace-pre">{code}</code>
        </pre>
      );
      i++;
      continue;
    }

    // Tables (lines with |)
    if (line.includes("|") && i + 1 < lines.length && lines[i + 1].includes("-")) {
      const headers = line.split("|").map(h => h.trim()).filter(h => h);
      i += 2; // skip header and separator
      const rows: string[][] = [];
      while (i < lines.length && lines[i].includes("|")) {
        rows.push(lines[i].split("|").map(c => c.trim()).filter(c => c));
        i++;
      }
      elements.push(
        <div key={i} className="overflow-x-auto my-4">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-800">
                {headers.map((h, idx) => (
                  <th key={idx} className="px-4 py-2 text-left text-gray-300 font-semibold border border-gray-700">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, ridx) => (
                <tr key={ridx} className="bg-gray-900/50 hover:bg-gray-800/50">
                  {row.map((cell, cidx) => (
                    <td key={cidx} className="px-4 py-2 text-gray-400 border border-gray-800">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Headers ##
    if (line.startsWith("## ")) {
      elements.push(
        <h2 key={i} className="text-xl font-bold text-white mt-6 mb-3 border-b border-gray-700 pb-2">
          {line.replace("## ", "")}
        </h2>
      );
      i++;
      continue;
    }

    // Headers ###
    if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="text-lg font-semibold text-blue-400 mt-5 mb-2">
          {line.replace("### ", "")}
        </h3>
      );
      i++;
      continue;
    }

    // Headers ####
    if (line.startsWith("#### ")) {
      elements.push(
        <h4 key={i} className="text-base font-medium text-gray-300 mt-4 mb-2">
          {line.replace("#### ", "")}
        </h4>
      );
      i++;
      continue;
    }

    // Bold text **
    if (line.includes("**")) {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      elements.push(
        <p key={i} className="mb-2 text-gray-300">
          {parts.map((part, idx) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return <strong key={idx} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
        </p>
      );
      i++;
      continue;
    }

    // ASCII Art / Charts (preserve whitespace)
    if (line.startsWith("  ") || (line.match(/^[│┌┐└┘├┤┬┴┼╭╮╯╰─═]/))) {
      let art = "";
      while (i < lines.length && (lines[i].startsWith("  ") || lines[i].match(/^[│┌┐└┘├┤┬┴┼╭╮╯╰─═\[\]│/>\-_\\\/\\^╱╲]/))) {
        art += lines[i] + "\n";
        i++;
      }
      elements.push(
        <pre key={i} className="bg-gray-950 border border-gray-800 rounded-lg p-3 my-3 overflow-x-auto">
          <code className="text-xs font-mono text-gray-400 whitespace-pre">{art}</code>
        </pre>
      );
      continue;
    }

    // Numbered lists
    if (line.match(/^\d+\./)) {
      elements.push(
        <div key={i} className="ml-4 mb-2 text-gray-300 flex gap-2">
          <span className="text-blue-400 font-semibold min-w-[1.5rem]">{line.match(/^\d+/)?.[0]}.</span>
          <span>{line.replace(/^\d+\.\s*/, "")}</span>
        </div>
      );
      i++;
      continue;
    }

    // Bullet lists with content
    if (line.startsWith("- ") || line.startsWith("• ")) {
      const content = line.replace(/^[-•]\s*/, "");
      // Check if it's a sub-item
      if (content.includes(":")) {
        const [label, ...rest] = content.split(":");
        elements.push(
          <div key={i} className="ml-4 mb-1 text-gray-400 flex gap-2">
            <span className="text-blue-500">•</span>
            <span>
              <span className="text-gray-300 font-medium">{label}:</span>
              {rest.join(":")}
            </span>
          </div>
        );
      } else {
        elements.push(
          <div key={i} className="ml-4 mb-1 text-gray-400 flex gap-2">
            <span className="text-blue-500">•</span>
            <span>{content}</span>
          </div>
        );
      }
      i++;
      continue;
    }

    // Empty lines
    if (line.trim() === "") {
      elements.push(<div key={i} className="h-2" />);
      i++;
      continue;
    }

    // Regular paragraphs
    elements.push(
      <p key={i} className="mb-2 text-gray-300 leading-relaxed">
        {line}
      </p>
    );
    i++;
  }

  return <>{elements}</>;
};

// Move this outside component to avoid temporal dead zone
const generateSessionId = (): string => {
  return 'sess_' + Math.random().toString(36).substring(2, 15);
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedMode, setSelectedMode] = useState("AUTO");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>(() => {
    // Restore session from localStorage or create new
    if (typeof window !== 'undefined') {
      return localStorage.getItem('gidboy_session_id') || generateSessionId();
    }
    return generateSessionId();
  });
  const [activeTopic, setActiveTopic] = useState<string | null>(null);
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
      const result = await generateResponse(input, mode);

      // Update active topic state
      if (result.activeTopic) {
        setActiveTopic(result.activeTopic);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: result.response,
        mode: result.workflowStage || mode,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I encountered an error. Please try again.",
        mode: "error",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const detectMode = (query: string): string => {
    const q = query.toLowerCase();
    if (q.includes("deep") || q.includes("comprehensive") || q.includes("in-depth")) return "RESEARCH";
    if (q.includes("grant") || q.includes("job") || q.includes("fellowship")) return "OPPORTUNITY";
    if (q.includes("trend") || q.includes("signal") || q.includes("emerging")) return "SIGNAL";
    if (q.includes("analyze") || q.includes("data") || q.includes("metric") || q.includes("chart")) return "ANALYSIS";
    if (q.includes("post") || q.includes("thread") || q.includes("content")) return "CONTENT";
    if (q.includes("career") || q.includes("resume")) return "CAREER";
    if (q.includes("apply") || q.includes("email") || q.includes("draft")) return "EXECUTION";
    return "RESEARCH";
  };

  const generateResponse = async (query: string, mode: string): Promise<{ response: string; activeTopic?: string; workflowStage?: string }> => {
    // Call the API endpoint for intent classification with session context
    const response = await fetch('/api/task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        mode: mode === 'AUTO' ? undefined : mode,
        sessionId: sessionId,
        history: messages.map(m => ({
          role: m.role,
          content: m.content
        }))
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to get response from API');
    }

    const data = await response.json();

    // Update session ID if server returned a new one
    if (data.sessionId && data.sessionId !== sessionId) {
      setSessionId(data.sessionId);
      localStorage.setItem('gidboy_session_id', data.sessionId);
    }

    // Update active topic from response
    if (data.activeTopic) {
      setActiveTopic(data.activeTopic);
    }

    return {
      response: data.result || data.response || "I'm here to help. What would you like to explore?",
      activeTopic: data.activeTopic,
      workflowStage: data.workflowStage,
    };
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-xl font-bold">
              G
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                GIDBoy
              </h1>
              <p className="text-xs text-gray-500">Deep Research Intelligence OS</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-gray-600 hidden sm:block">
              Contextual Mode
            </div>
            <div className="text-xs bg-gray-800 px-3 py-1 rounded-full text-gray-400">
              v2.1
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        <aside className="w-72 hidden lg:block flex-shrink-0">
          <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800 sticky top-24">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Intelligence Mode
            </h3>
            <div className="space-y-1">
              {MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                    selectedMode === mode.id
                      ? `${mode.color} text-white shadow-lg`
                      : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                  }`}
                >
                  <span className="text-lg">{mode.icon}</span>
                  <div className="text-left">
                    <div className="font-medium">{mode.label}</div>
                    {selectedMode === mode.id && (
                      <div className="text-xs opacity-70">
                        {mode.id === "RESEARCH" && "Deep analysis with data"}
                        {mode.id === "ANALYSIS" && "Metrics & correlations"}
                        {mode.id === "SIGNAL" && "Early detection"}
                        {mode.id === "OPPORTUNITY" && "Jobs & grants"}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-gray-900/50 rounded-xl p-4 border border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Quick Start
            </h3>
            <div className="space-y-2">
              {EXAMPLE_QUERIES.map((query, i) => (
                <button
                  key={i}
                  onClick={() => setInput(query)}
                  className="w-full text-left px-3 py-2 text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded-lg transition-colors border border-transparent hover:border-gray-700"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-blue-900/20 border border-blue-800/50 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-blue-400 mb-2">
              💡 Pro Tips
            </h3>
            <ul className="text-xs text-gray-400 space-y-1.5">
              <li>• Try "Solana liquidity provision"</li>
              <li>• Use "deep" for comprehensive analysis</li>
              <li>• Add "with data" for metrics</li>
              <li>• Request "workflows" for processes</li>
            </ul>
          </div>

          {/* Session Context */}
          {activeTopic && (
            <div className="mt-4 bg-green-900/20 border border-green-800/50 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-green-400 mb-2">
                🔬 Active Research
              </h3>
              <p className="text-xs text-gray-300 mb-2 font-medium">{activeTopic}</p>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-xs text-gray-500">Session active</span>
              </div>
            </div>
          )}
        </aside>

        <main className="flex-1 flex flex-col min-h-[calc(100vh-140px)] max-w-4xl">
          <div className="flex-1 overflow-y-auto space-y-6 mb-6">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="text-7xl mb-6 bg-gradient-to-br from-blue-500 to-purple-600 w-24 h-24 rounded-2xl mx-auto flex items-center justify-center shadow-2xl shadow-blue-500/20">
                  🤖
                </div>
                <h2 className="text-3xl font-bold text-gray-200 mb-3">
                  Deep Research Intelligence
                </h2>
                <p className="text-gray-400 max-w-lg mx-auto mb-2">
                  GIDBoy now delivers contextual analysis based on your query:
                </p>
                <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Liquidity Research</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Validator Analysis</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Deep Protocol Dive</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Data & Metrics</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Solutions</span>
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
                  className={`max-w-3xl rounded-2xl ${
                    message.role === "user"
                      ? "bg-blue-600 text-white px-6 py-4"
                      : "bg-gray-900/50 border border-gray-800 w-full"
                  }`}
                >
                  {message.role === "assistant" && message.mode && (
                    <div className="flex items-center gap-3 px-6 py-3 border-b border-gray-800 bg-gray-800/30 rounded-t-2xl">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${
                        MODES.find(m => m.id === message.mode)?.color || "bg-gray-700"
                      } text-white`}>
                        {message.mode}
                      </span>
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="text-xs text-gray-600 ml-auto">
                        Contextual Analysis
                      </span>
                    </div>
                  )}
                  <div className={message.role === "assistant" ? "p-6" : ""}>
                    <div className="prose prose-invert prose-sm max-w-none">
                      {message.role === "assistant" ? (
                        <FormattedContent content={message.content} />
                      ) : (
                        <p className="text-white">{message.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl px-6 py-8 max-w-3xl w-full">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" />
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-100" />
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-200" />
                    <span className="text-gray-500 text-sm ml-2">Analyzing your query context...</span>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="h-2 bg-gray-800 rounded-full w-3/4 animate-pulse" />
                    <div className="h-2 bg-gray-800 rounded-full w-1/2 animate-pulse" />
                    <div className="h-2 bg-gray-800 rounded-full w-2/3 animate-pulse" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="relative">
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-3 shadow-2xl">
              <div className="flex items-center gap-2 mb-2 px-2">
                <span className="text-xs text-gray-500">Mode:</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${
                    MODES.find((m) => m.id === selectedMode)?.color || "bg-gray-700"
                  } text-white`}
                >
                  {MODES.find((m) => m.id === selectedMode)?.label || "Auto"}
                </span>
                {selectedMode === "AUTO" && (
                  <span className="text-xs text-gray-600 ml-2">
                    Will auto-detect based on query
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about Solana liquidity, Firedancer, or any crypto topic..."
                  className="flex-1 bg-transparent text-white placeholder-gray-500 px-4 py-4 text-base focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-blue-500/20"
                >
                  {isLoading ? "Analyzing..." : "Research"}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3 text-center">
              Try: "Do a deep dive into Blockchain Liquidity provision on Solana" • GIDBoy provides contextual analysis
            </p>
          </form>
        </main>
      </div>
    </div>
  );
}
