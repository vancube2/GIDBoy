import { NextRequest, NextResponse } from 'next/server';

// Configuration - set this to your Python backend URL
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, mode } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // FORWARD to Python backend for intent classification
    // This ensures intent classification happens BEFORE any response generation
    const response = await fetch(`${PYTHON_API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: query,
        conversation_history: body.history || []
      }),
    });

    if (!response.ok) {
      // If Python backend is not available, use fallback intent classification
      console.warn('Python backend unavailable, using fallback');
      return fallbackResponse(query, mode);
    }

    const result = await response.json();

    // Return the properly classified response
    return NextResponse.json({
      mode: result.intent || mode || 'conversational',
      result: result.response || result.message || 'I\'m here to help. What would you like to explore?',
      query,
      confidence: result.confidence,
      requires_research: result.requires_research,
      workflow: result.workflow,
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

// Fallback intent classification (when Python backend unavailable)
function fallbackResponse(query: string, mode?: string) {
  const query_lower = query.toLowerCase().trim();

  // Intent classification patterns
  const isGreeting = /^(hi|hello|hey|yo|hiya|greetings|what's up|howdy|sup)[\s!.,]*$/i.test(query_lower);

  const isCasual = /\b(how are you|how's it going|what are you up to|thanks|thank you|appreciate it|nice|cool|awesome|great|tell me about yourself|ready when you are|what are you thinking about)\b/i.test(query_lower);

  const isCollaboration = /\b(work together|collaborate|partner|join forces|can we work|help with|assist with|looking for help)\b/i.test(query_lower);

  // ENHANCED: More flexible research detection
  const isResearch =
    /\b(deep dive|deep analysis|comprehensive study|in-depth analysis|research|investigate|investigation)\b/i.test(query_lower) ||
    /\b(analyze|analysis|study|examine|assessment|evaluation)\b.*\b(on|into|about|of)\b/i.test(query_lower) ||
    /\b(what is|how does|why does|how do|what are)\b.*\b(work|function|mechanism|ecosystem|problems|challenges|issues)\b/i.test(query_lower) ||
    /\b(validator economics|tokenomics|ecosystem analysis|market research|liquidity provision|defi)\b/i.test(query_lower) ||
    /\b(landscape|overview) of\b/i.test(query_lower) ||
    /\b(compare|contrast|versus|vs)\b.*\b(with|and|to)\b/i.test(query_lower) ||
    /\b(problems?|challenges?|issues?)\b.*\b(with|in|on)\b/i.test(query_lower);

  const isOpportunity = /\b(find|search|looking for)\b.*\b(grants?|jobs?|funding|opportunities?|bounties?|fellowship|stipend|position|role)\b/i.test(query_lower);

  // GREETING
  if (isGreeting) {
    return NextResponse.json({
      mode: 'greeting',
      result: getGreetingResponse(),
      query,
      confidence: 0.95,
      requires_research: false,
      workflow: 'conversational',
    });
  }

  // CASUAL CONVERSATION
  if (isCasual) {
    return NextResponse.json({
      mode: 'casual',
      result: getCasualResponse(query),
      query,
      confidence: 0.85,
      requires_research: false,
      workflow: 'conversational',
    });
  }

  // COLLABORATION INQUIRY
  if (isCollaboration) {
    return NextResponse.json({
      mode: 'collaboration',
      result: getCollaborationResponse(),
      query,
      confidence: 0.80,
      requires_research: false,
      workflow: 'collaborative',
    });
  }

  // RESEARCH REQUEST
  if (isResearch) {
    return NextResponse.json({
      mode: 'research',
      result: "I'd be happy to research that for you. Let me investigate this deeply...\n\n[Note: This is a fallback response. For full research capabilities, ensure the Python backend is running.]",
      query,
      confidence: 0.90,
      requires_research: true,
      workflow: 'deep_research',
    });
  }

  // OPPORTUNITY SEARCH
  if (isOpportunity) {
    return NextResponse.json({
      mode: 'opportunity',
      result: "I can help you find opportunities. Let me search for relevant grants, jobs, or positions...\n\n[Note: This is a fallback response. For full opportunity discovery, ensure the Python backend is running.]",
      query,
      confidence: 0.85,
      requires_research: true,
      workflow: 'opportunity_discovery',
    });
  }

  // DEFAULT: AMBIGUOUS - Ask for clarification
  return NextResponse.json({
    mode: 'clarification',
    result: `I'd like to help with "${query}". Could you clarify what you're looking for?\n\n• Research on a specific topic?\n• Help finding opportunities?\n• Strategic brainstorming?\n• Or just chatting?`,
    query,
    confidence: 0.50,
    requires_research: false,
    workflow: 'clarification',
  });
}

// Natural greeting response
function getGreetingResponse(): string {
  const greetings = [
    "Hey there! Ready to dig into some research?",
    "Hi! What are we exploring today?",
    "Hello! What ecosystem or topic should we investigate?",
    "Hey! I'm here to help with deep research and strategic thinking. What's on your mind?",
  ];
  return greetings[Math.floor(Math.random() * greetings.length)];
}

// Casual conversation response
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

// Collaboration response
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
