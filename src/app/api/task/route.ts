import { NextRequest, NextResponse } from 'next/server';

// Configuration - set this to your Python backend URL
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

// In-memory session store (in production, use Redis or database)
const sessionStore: Map<string, SessionState> = new Map();

interface SessionState {
  sessionId: string;
  activeTopic?: string;
  workflowStage: string;
  conversationMode: string;
  discoveredInsights: string[];
  conversationHistory: { role: string; content: string; timestamp: string }[];
  lastUpdated: number;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, mode, sessionId: clientSessionId, sessionState: clientSessionState } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Get or create session - prefer client-provided state for serverless environments
    const sessionId = clientSessionId || generateSessionId();
    console.log('[GIDBoy] Request:', query.substring(0, 30), '| sessionId:', sessionId?.substring(0, 10));

    let session: SessionState;
    if (clientSessionState?.activeTopic) {
      console.log('[GIDBoy] Restoring from client. Topic:', clientSessionState.activeTopic);
      session = restoreSession(sessionId, clientSessionState);
    } else {
      session = getOrCreateSession(sessionId);
    }

    console.log('[GIDBoy] Session state - activeTopic:', session.activeTopic || 'NONE', '| stage:', session.workflowStage);

    // Update session with user message
    session.conversationHistory.push({
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    });

    // FALLBACK: Process with session-aware logic
    const result = processWithSession(query, session);

    // Update session with assistant response
    session.conversationHistory.push({
      role: 'assistant',
      content: result.result,
      timestamp: new Date().toISOString()
    });

    // Save session
    sessionStore.set(sessionId, session);

    // Return full session state for client storage
    return NextResponse.json({
      ...result,
      sessionId: sessionId,
      sessionState: {
        activeTopic: session.activeTopic,
        workflowStage: session.workflowStage,
        conversationMode: session.conversationMode,
        discoveredInsights: session.discoveredInsights,
        conversationHistory: session.conversationHistory.slice(-20),
      },
      activeTopic: session.activeTopic,
      workflowStage: session.workflowStage,
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

function generateSessionId(): string {
  return 'sess_' + Math.random().toString(36).substring(2, 15);
}

function getOrCreateSession(sessionId: string): SessionState {
  const existing = sessionStore.get(sessionId);
  if (existing) {
    existing.lastUpdated = Date.now();
    return existing;
  }

  const newSession: SessionState = {
    sessionId,
    workflowStage: 'initial',
    conversationMode: 'conversational',
    discoveredInsights: [],
    conversationHistory: [],
    lastUpdated: Date.now(),
  };

  sessionStore.set(sessionId, newSession);
  return newSession;
}

function restoreSession(sessionId: string, state: Partial<SessionState>): SessionState {
  const restored: SessionState = {
    sessionId,
    activeTopic: state.activeTopic,
    workflowStage: state.workflowStage || 'initial',
    conversationMode: state.conversationMode || 'conversational',
    discoveredInsights: state.discoveredInsights || [],
    conversationHistory: state.conversationHistory || [],
    lastUpdated: Date.now(),
  };

  sessionStore.set(sessionId, restored);
  return restored;
}

// MAIN SESSION-AWARE PROCESSING
function processWithSession(query: string, session: SessionState) {
  const query_lower = query.toLowerCase().trim();

  // ==== STEP 1: GREETING (ignore session) ====
  if (/^(hi|hello|hey|yo|hiya|greetings|what's up|howdy|sup)[\s!.,]*$/i.test(query_lower)) {
    return {
      mode: 'greeting',
      result: getGreetingResponse(),
      confidence: 0.95,
      requires_research: false,
      workflow: 'conversational',
      isContinuation: false,
    };
  }

  // ==== STEP 2: IF WE HAVE ACTIVE TOPIC, CHECK FOR CONTINUATION FIRST ====
  if (session.activeTopic) {
    console.log('[GIDBoy] Have active topic, checking continuation...');

    // Check for explicit problem/solution requests
    const isProblemRequest = /\b(list|what are|show me|find|tell me about|explain)\s+(the\s+)?(problems?|challenges?|issues?|risks?|obstacles?)\b/i.test(query_lower);
    const isSolutionRequest = /\b(list|what are|show me|find|who|which)\s+(the\s+)?(solutions?|protocols?|projects?|players?|is solving|addresses?)\b/i.test(query_lower);
    const isTransitionWord = /^(first|next|then|now|okay|ok|so|alright|great|cool)[,\s]+/i.test(query_lower);
    const hasTopicWord = session.activeTopic.toLowerCase().split(/\s+/).some(word =>
      word.length > 3 && query_lower.includes(word)
    );

    console.log('[GIDBoy] isProblemRequest:', isProblemRequest, '| hasTopicWord:', hasTopicWord);

    // If ANY continuation signal exists, continue the session
    if (isProblemRequest || isSolutionRequest || isTransitionWord || hasTopicWord) {
      session.workflowStage = 'investigation';

      if (isProblemRequest) {
        return {
          mode: 'research',
          result: `Continuing our research on ${session.activeTopic}. Let me identify the key problems and challenges...`,
          confidence: 0.92,
          requires_research: true,
          workflow: 'problem_identification',
          isContinuation: true,
        };
      }

      if (isSolutionRequest) {
        return {
          mode: 'research',
          result: `Continuing our research on ${session.activeTopic}. Let me map the ecosystem solutions...`,
          confidence: 0.90,
          requires_research: true,
          workflow: 'solution_mapping',
          isContinuation: true,
        };
      }

      // Generic continuation
      return {
        mode: 'research',
        result: `Continuing our investigation on ${session.activeTopic}. What would you like to explore?`,
        confidence: 0.85,
        requires_research: true,
        workflow: 'research_continuation',
        isContinuation: true,
      };
    }

    // Has active topic but unclear intent - ask for clarification in context
    return {
      mode: 'clarification',
      result: `We're currently discussing "${session.activeTopic}". Would you like to explore problems, solutions, or something else about this topic?`,
      confidence: 0.70,
      requires_research: false,
      workflow: 'clarification',
      isContinuation: true,
    };
  }

  // ==== STEP 3: NO ACTIVE TOPIC - Classify new intent ====

  // Collaboration inquiry
  if (/\b(work together|collaborate|can we work|help me with|assist with|looking for help)\b/i.test(query_lower)) {
    return {
      mode: 'collaboration',
      result: getCollaborationResponse(),
      confidence: 0.88,
      requires_research: false,
      workflow: 'collaborative',
      isContinuation: false,
    };
  }

  // Research request - extract topic
  const hasResearchKeyword = /\b(research|investigate|study|analyze|deep dive|explore|examine)\b/i.test(query_lower);
  const hasCryptoKeyword = /\b(liquidity|solana|ethereum|bitcoin|defi|protocol|validator|tokenomics|ecosystem|blockchain|crypto|nft|dao)\b/i.test(query_lower);

  if (hasResearchKeyword || hasCryptoKeyword) {
    // Extract topic
    let topic = query;
    const patterns = [
      /\b(?:research|investigate|study|analyze|explore|examine)\s+(?:on|into|about)?\s*(.+?)(?:\s+in\s+\d{4})?$/i,
      /\b(?:deep dive|deep analysis)\s+(?:into|on)?\s*(.+?)(?:\s+in\s+\d{4})?$/i,
      /\b(?:on|about|into)\s+(.+?)(?:\s+in\s+\d{4})?$/i,
    ];

    for (const pattern of patterns) {
      const match = query.match(pattern);
      if (match?.[1]) {
        topic = match[1].trim();
        break;
      }
    }

    session.activeTopic = topic;
    session.workflowStage = 'understanding';
    session.conversationMode = 'research';

    return {
      mode: 'research',
      result: `I'd be happy to research ${topic}. Let me dive deep into this and provide comprehensive analysis.`,
      confidence: 0.92,
      requires_research: true,
      workflow: 'deep_research',
      isContinuation: false,
    };
  }

  // Opportunity search
  if (/\b(find|search|looking for)\b.*\b(grants?|jobs?|funding|opportunities?|bounties?)\b/i.test(query_lower)) {
    return {
      mode: 'opportunity',
      result: "I can help you find opportunities. Let me search for relevant grants, jobs, or positions...",
      confidence: 0.85,
      requires_research: true,
      workflow: 'opportunity_discovery',
      isContinuation: false,
    };
  }

  // Casual conversation (only when no session)
  if (/\b(how are you|what's up|thanks|thank you|great|awesome|cool)\b/i.test(query_lower)) {
    return {
      mode: 'casual',
      result: "I'm here to help with deep research. What topic would you like to explore?",
      confidence: 0.80,
      requires_research: false,
      workflow: 'conversational',
      isContinuation: false,
    };
  }

  // Default - ask for topic
  return {
    mode: 'clarification',
    result: `I'd like to help with "${query}". Could you tell me more about what you'd like to research? For example:\n\n• A specific crypto ecosystem or protocol?\n• Market analysis or trends?\n• Opportunities or grants?`,
    confidence: 0.60,
    requires_research: false,
    workflow: 'clarification',
    isContinuation: false,
  };
}

function getGreetingResponse(): string {
  const greetings = [
    "Hey there! Ready to dig into some research?",
    "Hi! What are we exploring today?",
    "Hello! What ecosystem or topic should we investigate?",
    "Hey! I'm here to help with deep research. What's on your mind?",
  ];
  return greetings[Math.floor(Math.random() * greetings.length)];
}

function getCollaborationResponse(): string {
  return `I'd love to collaborate! Here's how we can work together:

**What I can help with:**
• Deep research on crypto ecosystems, protocols, or markets
• Strategic analysis and opportunity discovery
• Content generation from original research
• Positioning strategy and execution planning

**How it works:**
1. Share what you're interested in or working on
2. I'll do deep investigation with structured reasoning
3. We'll discover opportunities and strategic implications together
4. Turn insights into actionable positioning

What area are you exploring?`;
}
