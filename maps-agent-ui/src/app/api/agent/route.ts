import { NextRequest, NextResponse } from 'next/server';

interface MapsResponse {
  topic: string;
  description: string;
  source: string[];
  tools_used: string[];
}

export async function POST(req: NextRequest) {
  try {
    const { query } = await req.json();
    
    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Call your Python agent server
    const agentResponse = await fetch('http://localhost:3001/agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!agentResponse.ok) {
      throw new Error(`Agent server responded with status: ${agentResponse.status}`);
    }

    const result = await agentResponse.json();
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error calling agent:', error);
    return NextResponse.json(
      { error: 'Failed to process request' }, 
      { status: 500 }
    );
  }
}