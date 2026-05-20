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
    const session = clientSessionState
      ? restoreSession(sessionId, clientSessionState)
      : getOrCreateSession(sessionId);

    // Update session with user message
    session.conversationHistory.push({
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    });

    // Try to forward to Python backend with session context
    try {
      const response = await fetch(`${PYTHON_API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: query,
          conversation_history: session.conversationHistory.slice(-10), // Last 10 messages
          session_id: sessionId,
        }),
      });

      if (response.ok) {
        const result = await response.json();

        // Update session state from backend response
        if (result.active_topic) {
          session.activeTopic = result.active_topic;
        }
        if (result.workflow_stage) {
          session.workflowStage = result.workflow_stage;
        }

        // Add assistant response to history
        session.conversationHistory.push({
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toISOString()
        });

        // Save session
        sessionStore.set(sessionId, session);

        return NextResponse.json({
          mode: result.intent || mode || 'conversational',
          result: result.response,
          query,
          confidence: result.confidence,
          requires_research: result.requires_research,
          workflow: result.workflow,
          sessionId: sessionId,
          isContinuation: result.is_continuation || false,
          activeTopic: session.activeTopic,
          workflowStage: session.workflowStage,
        });
      }
    } catch (error) {
      console.warn('Python backend unavailable, using fallback with session:', error);
    }

    // Fallback: Use session-aware intent classification
    const fallbackResult = fallbackResponse(query, mode, session);

    // Update session state
    session.conversationHistory.push({
      role: 'assistant',
      content: fallbackResult.result,
      timestamp: new Date().toISOString()
    });

    // Save session
    sessionStore.set(sessionId, session);

    // Return full session state for client storage (serverless compatibility)
    const sessionStateForClient = {
      activeTopic: session.activeTopic,
      workflowStage: session.workflowStage,
      conversationMode: session.conversationMode,
      discoveredInsights: session.discoveredInsights,
      conversationHistory: session.conversationHistory.slice(-20), // Last 20 messages
    };

    return NextResponse.json({
      ...fallbackResult,
      sessionId: sessionId,
      sessionState: sessionStateForClient,
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
  // In serverless environments, we rely on client-provided state
  // This is a fallback for when client doesn't provide state
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
  // Restore session from client-provided state (for serverless compatibility)
  const restored: SessionState = {
    sessionId,
    activeTopic: state.activeTopic,
    workflowStage: state.workflowStage || 'initial',
    conversationMode: state.conversationMode || 'conversational',
    discoveredInsights: state.discoveredInsights || [],
    conversationHistory: state.conversationHistory || [],
    lastUpdated: Date.now(),
  };

  // Also update server-side cache if available
  sessionStore.set(sessionId, restored);
  return restored;
}

// Session-aware fallback intent classification
function fallbackResponse(query: string, mode: string | undefined, session: SessionState) {
  const query_lower = query.toLowerCase().trim();

  console.log('[GIDBoy] Processing query:', query.substring(0, 50));
  console.log('[GIDBoy] Session active topic:', session.activeTopic);

  // Check for CONTINUATION first if we have active topic
  if (session.activeTopic) {
    const continuationResult = checkContinuation(query_lower, session);
    if (continuationResult) {
      console.log('[GIDBoy] Detected as continuation');
      return continuationResult;
    }
  }

  // Intent classification patterns
  const isGreeting = /^(hi|hello|hey|yo|hiya|greetings|what's up|howdy|sup)[\s!.,]*$/i.test(query_lower);

  const isCasual = /\b(how are you|how's it going|what are you up to|thanks|thank you|appreciate it|nice|cool|awesome|great|tell me about yourself)\b/i.test(query_lower);

  const isCollaboration = /\b(work together|collaborate|partner|join forces|can we work|help with|assist with|looking for help)\b/i.test(query_lower);

  // ENHANCED: More flexible research detection - SIMPLIFIED
  const hasDeepDive = /\b(deep dive|deep analysis)\b/i.test(query_lower);
  const hasResearchWord = /\b(research|investigate|investigation|study|analyze)\b/i.test(query_lower);
  const hasCryptoTopic = /\b(liquidity|provision|solana|ethereum|bitcoin|defi|protocol|validator|tokenomics|ecosystem)\b/i.test(query_lower);
  const hasProblemStatement = /\b(problems?|challenges?|issues?)\b/i.test(query_lower);
  const hasLetsResearch = /\b(let'?s|let us)\s+(do|a|some)?\s*(deep|research|analyze|study|look|explore)\b/i.test(query_lower);

  const isResearch = hasDeepDive || hasResearchWord || (hasCryptoTopic && hasProblemStatement) || hasLetsResearch;

  console.log('[GIDBoy] isGreeting:', isGreeting, '| isCasual:', isCasual, '| isCollaboration:', isCollaboration, '| isResearch:', isResearch);

  const isOpportunity = /\b(find|search|looking for)\b.*\b(grants?|jobs?|funding|opportunities?|bounties?|fellowship|stipend|position|role)\b/i.test(query_lower);

  // Check for transition words (continuation)
  const hasTransitionWords = /^(first|next|then|now|okay|ok|so|alright)[,\s]+/i.test(query_lower) ||
    /\b(go deeper|elaborate|tell me more|expand on|continue|proceed)\b/i.test(query_lower);

  console.log('[GIDBoy] activeTopic:', session.activeTopic, '| hasTransitionWords:', hasTransitionWords);

  // GREETING
  if (isGreeting) {
    return {
      mode: 'greeting',
      result: getGreetingResponse(),
      query,
      confidence: 0.95,
      requires_research: false,
      workflow: 'conversational',
      isContinuation: false,
    };
  }

  // CASUAL CONVERSATION
  if (isCasual && !isResearch) {
    return {
      mode: 'casual',
      result: getCasualResponse(query),
      query,
      confidence: 0.85,
      requires_research: false,
      workflow: 'conversational',
      isContinuation: false,
    };
  }

  // COLLABORATION INQUIRY
  if (isCollaboration) {
    session.conversationMode = 'collaborative';
    return {
      mode: 'collaboration',
      result: getCollaborationResponse(),
      query,
      confidence: 0.88,
      requires_research: false,
      workflow: 'collaborative',
      isContinuation: false,
    };
  }

  // RESEARCH REQUEST (new topic)
  if (isResearch && !session.activeTopic) {
    console.log('[GIDBoy] Entering RESEARCH REQUEST block (new topic)');

    // Extract topic from query - improved extraction
    let topic = query;

    // Try to extract topic after keywords like "on", "into", "about"
    const topicPatterns = [
      /\b(?:deep dive|research|analyze|study)\s+(?:into|on|about)\s+(.+?)(?:\s+in\s+\d{4})?$/i,
      /\b(?:let'?s|let us)\s+(?:do\s+a\s+)?(?:deep\s+dive|research)\s+(?:into|on)?\s*(.+?)(?:\s+in\s+\d{4})?$/i,
      /\b(?:on|about|into)\s+(.+?)(?:\s+in\s+\d{4})?$/i,
    ];

    for (const pattern of topicPatterns) {
      const match = query.match(pattern);
      if (match && match[1]) {
        topic = match[1].trim();
        break;
      }
    }

    console.log('[GIDBoy] Extracted topic:', topic);

    session.activeTopic = topic;
    session.workflowStage = 'understanding';
    session.conversationMode = 'research';

    return {
      mode: 'research',
      result: `I'd be happy to research ${topic}. Let me dive deep into this and provide comprehensive analysis.`,
      query,
      confidence: 0.92,
      requires_research: true,
      workflow: 'deep_research',
      isContinuation: false,
    };
  }

  // RESEARCH CONTINUATION (existing topic)
  if (isResearch && session.activeTopic) {
    console.log('[GIDBoy] Entering RESEARCH CONTINUATION block');
    session.workflowStage = 'investigation';

    // Check for specific sub-intents
    if (/\b(problems?|challenges?|issues?)\b/i.test(query_lower)) {
      console.log('[GIDBoy] Detected problem identification intent');
      return {
        mode: 'research',
        result: `Let me identify the key problems and challenges with ${session.activeTopic}. I'll analyze the current landscape...`,
        query,
        confidence: 0.92,
        requires_research: true,
        workflow: 'problem_identification',
        isContinuation: true,
      };
    }

    if (/\b(solutions?|protocols?|projects?|who|solving|addressing)\b/i.test(query_lower)) {
      return {
        mode: 'research',
        result: `Let me map the ecosystem to find who's addressing these challenges in ${session.activeTopic}...`,
        query,
        confidence: 0.90,
        requires_research: true,
        workflow: 'solution_mapping',
        isContinuation: true,
      };
    }

    // Generic continuation
    return {
      mode: 'research',
      result: `Continuing our investigation on ${session.activeTopic}. Let me dive deeper into this aspect...`,
      query,
      confidence: 0.88,
      requires_research: true,
      workflow: 'research_continuation',
      isContinuation: true,
    };
  }

  // If we have an active topic but unclear intent, try to continue
  if (session.activeTopic && hasTransitionWords) {
    return {
      mode: 'research',
      result: `Continuing with ${session.activeTopic}. What specific aspect would you like to explore?`,
      query,
      confidence: 0.75,
      requires_research: true,
      workflow: 'research_continuation',
      isContinuation: true,
    };
  }

  // OPPORTUNITY SEARCH
  if (isOpportunity) {
    return {
      mode: 'opportunity',
      result: "I can help you find opportunities. Let me search for relevant grants, jobs, or positions...",
      query,
      confidence: 0.85,
      requires_research: true,
      workflow: 'opportunity_discovery',
      isContinuation: false,
    };
  }

  // DEFAULT: Check if we should continue existing topic
  if (session.activeTopic) {
    return {
      mode: 'clarification',
      result: `I want to make sure I understand within the context of our discussion on "${session.activeTopic}". Are you asking about something specific regarding this topic?`,
      query,
      confidence: 0.60,
      requires_research: false,
      workflow: 'clarification',
      isContinuation: true,
    };
  }

  // FALLBACK RESEARCH: If it's clearly a research question but no patterns matched,
  // create a research session anyway
  if (hasCryptoTopic || hasResearchWord) {
    console.log('[GIDBoy] FALLBACK RESEARCH triggered');
    const topic = query.replace(/\b(let's|let us|do a|some|deep|research|on|about)\b/gi, '').trim();
    session.activeTopic = topic || query;
    session.workflowStage = 'understanding';
    session.conversationMode = 'research';

    return {
      mode: 'research',
      result: `I'd be happy to research ${session.activeTopic}. Let me dive deep into this and provide comprehensive analysis.`,
      query,
      confidence: 0.80,
      requires_research: true,
      workflow: 'deep_research',
      isContinuation: false,
    };
  }

  // Complete fallback
  console.log('[GIDBoy] COMPLETE FALLBACK - no patterns matched');
  return {
    mode: 'clarification',
    result: `I'd like to help with "${query}". Could you clarify what you're looking for?\n\n• Research on a specific topic?\n• Help finding opportunities?\n• Strategic brainstorming?\n• Or just chatting?`,
    query,
    confidence: 0.50,
    requires_research: false,
    workflow: 'clarification',
    isContinuation: false,
  };
}

// Check if this is a continuation of active research
function checkContinuation(query_lower: string, session: SessionState) {
  console.log('[GIDBoy] checkContinuation called with active topic:', session.activeTopic);

  // Strong continuation signals
  const continuationPatterns = [
    /^(first|next|then|now|okay|ok|so|alright)[,\s]+/i,
    /\b(go deeper|elaborate|tell me more|expand on|continue|proceed)\b/i,
    /^(what about|how about)\s+/i,
    /\b(list|what are)\s+(the\s+)?(problems?|challenges?|issues?)\b/i,
    /\b(list|what are)\s+(the\s+)?(solutions?|protocols?|projects?)\b/i,
    /\b(who|which)\s+(is|are)\s+(solving|addressing|working on)\b/i,
  ];

  const isContinuation = continuationPatterns.some(pattern => pattern.test(query_lower));
  console.log('[GIDBoy] isContinuation pattern match:', isContinuation);

  // Check for topic overlap
  const topicWords = session.activeTopic?.toLowerCase().split(' ') || [];
  const hasTopicWords = topicWords.some(word =>
    word.length > 3 && query_lower.includes(word)
  );
  console.log('[GIDBoy] hasTopicWords overlap:', hasTopicWords, 'words:', topicWords);

  if (isContinuation || hasTopicWords) {
    session.workflowStage = 'investigation';

    // Determine specific type of continuation
    if (/\b(problems?|challenges?|issues?)\b/i.test(query_lower)) {
      return {
        mode: 'research',
        result: `Analyzing the problems and challenges with ${session.activeTopic}...`,
        query: query_lower,
        confidence: 0.92,
        requires_research: true,
        workflow: 'problem_identification',
        isContinuation: true,
      };
    }

    if (/\b(solutions?|protocols?|projects?|solving|addressing)\b/i.test(query_lower)) {
      return {
        mode: 'research',
        result: `Mapping the ecosystem solutions for ${session.activeTopic}...`,
        query: query_lower,
        confidence: 0.90,
        requires_research: true,
        workflow: 'solution_mapping',
        isContinuation: true,
      };
    }

    return {
      mode: 'research',
      result: `Continuing our investigation on ${session.activeTopic}. Let me explore this further...`,
      query: query_lower,
      confidence: 0.85,
      requires_research: true,
      workflow: 'research_continuation',
      isContinuation: true,
    };
  }

  return null;
}

function getGreetingResponse(): string {
  const greetings = [
    "Hey there! Ready to dig into some research?",
    "Hi! What are we exploring today?",
    "Hello! What ecosystem or topic should we investigate?",
    "Hey! I'm here to help with deep research and strategic thinking. What's on your mind?",
  ];
  return greetings[Math.floor(Math.random() * greetings.length)];
}

function getCasualResponse(query: string): string {
  if (query.toLowerCase().includes('how are you')) {
    return "Doing well, thanks! Always ready to dive into some ecosystem research. What about you?";
  }
  if (query.toLowerCase().includes('thank')) {
    return "You're welcome! Let me know if there's anything else I can help research or analyze.";
  }
  const casuals = [
    "I'm here when you're ready to dive into something. What are you thinking about?",
    "Ready when you are! What ecosystem or topic should we explore?",
    "What's on your research radar today?",
  ];
  return casuals[Math.floor(Math.random() * casuals.length)];
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

What area are you exploring? Or what project are you working on?`;
}
