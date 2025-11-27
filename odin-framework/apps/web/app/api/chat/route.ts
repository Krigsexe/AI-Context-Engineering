import { NextRequest, NextResponse } from "next/server"
import { chat } from "@/lib/groq"
import { getCache, setCache } from "@/lib/redis"

export async function POST(request: NextRequest) {
    try {
        const { messages, sessionId } = await request.json()

        if (!messages || !Array.isArray(messages)) {
            return NextResponse.json(
                { error: "Messages array required" },
                { status: 400 }
            )
        }

        // Check cache for identical conversation
        const cacheKey = `chat:${sessionId}:${JSON.stringify(messages)}`
        const cached = await getCache<string>(cacheKey)
        if (cached) {
            return NextResponse.json({ response: cached, cached: true })
        }

        // Get response from Groq
        const response = await chat(messages)

        // Cache the response for 1 hour
        await setCache(cacheKey, response, 3600)

        return NextResponse.json({ response, cached: false })
    } catch (error) {
        console.error("Chat API error:", error)
        return NextResponse.json(
            { error: "Failed to process chat request" },
            { status: 500 }
        )
    }
}
