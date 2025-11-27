import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import Groq from "groq-sdk"

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY
})

const WORKER_ID = "content-moderator"
const BATCH_SIZE = 10

// Moderation thresholds
const AUTO_APPROVE_THRESHOLD = 80
const AUTO_REJECT_THRESHOLD = 40

interface ModerationAnalysis {
    score: number
    spam_likelihood: number
    toxicity_level: number
    malicious_content: boolean
    off_topic: boolean
    reasons: string[]
    summary: string
}

// Verify cron secret
function verifyCronSecret(request: Request): boolean {
    const authHeader = request.headers.get("authorization")
    const cronSecret = process.env.CRON_SECRET
    if (!cronSecret) return true
    return authHeader === `Bearer ${cronSecret}`
}

// Start worker run
async function startWorkerRun() {
    return prisma.workerRun.create({
        data: { workerId: WORKER_ID, status: "running" }
    })
}

// Complete worker run
async function completeWorkerRun(runId: string, itemsProcessed: number, error?: string) {
    return prisma.workerRun.update({
        where: { id: runId },
        data: {
            status: error ? "failed" : "success",
            itemsProcessed,
            errors: error,
            completedAt: new Date()
        }
    })
}

// Analyze content with Groq LLM
async function analyzeContent(content: string, contentType: string): Promise<ModerationAnalysis> {
    const systemPrompt = `You are a content moderation AI for the ODIN Framework community platform.
Your job is to analyze user-submitted content and determine if it should be approved, flagged for review, or rejected.

ODIN Framework is an open-source AI reliability framework. The community discusses:
- AI safety and reliability
- Code contributions and improvements
- Technical documentation
- Best practices for AI development

Analyze the content for:
1. Spam or promotional content
2. Toxicity, harassment, or hate speech
3. Malicious links or code
4. Off-topic content unrelated to AI/ODIN
5. Quality and constructiveness

Respond with a JSON object only, no other text:
{
    "score": <0-100, higher = more trustworthy>,
    "spam_likelihood": <0-100>,
    "toxicity_level": <0-100>,
    "malicious_content": <true/false>,
    "off_topic": <true/false>,
    "reasons": [<list of concerns if any>],
    "summary": "<brief analysis summary>"
}`

    try {
        const response = await groq.chat.completions.create({
            model: "llama-3.1-70b-versatile",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: `Content type: ${contentType}\n\nContent to analyze:\n${content.substring(0, 2000)}` }
            ],
            temperature: 0.1,
            max_tokens: 500
        })

        const analysisText = response.choices[0]?.message?.content || "{}"

        // Extract JSON from response
        const jsonMatch = analysisText.match(/\{[\s\S]*\}/)
        if (!jsonMatch) {
            throw new Error("No JSON found in response")
        }

        return JSON.parse(jsonMatch[0]) as ModerationAnalysis
    } catch (error) {
        console.error("Error analyzing content:", error)
        // Return neutral analysis on error
        return {
            score: 50,
            spam_likelihood: 50,
            toxicity_level: 0,
            malicious_content: false,
            off_topic: false,
            reasons: ["Analysis failed - manual review recommended"],
            summary: "Automated analysis failed"
        }
    }
}

// Determine action based on analysis
function determineAction(analysis: ModerationAnalysis): string {
    if (analysis.malicious_content || analysis.toxicity_level > 80) {
        return "auto_reject"
    }
    if (analysis.score >= AUTO_APPROVE_THRESHOLD && analysis.spam_likelihood < 20) {
        return "auto_approve"
    }
    if (analysis.score < AUTO_REJECT_THRESHOLD || analysis.spam_likelihood > 70) {
        return "auto_reject"
    }
    return "flag_review"
}

// Process a single moderation item
async function processItem(item: { id: string; content: string; contentType: string; contentId: string }) {
    const analysis = await analyzeContent(item.content, item.contentType)
    const action = determineAction(analysis)

    // Update the queue item
    await prisma.moderationQueue.update({
        where: { id: item.id },
        data: {
            status: action === "auto_approve" ? "approved"
                  : action === "auto_reject" ? "rejected"
                  : "flagged",
            score: analysis.score,
            reason: analysis.reasons.length > 0 ? analysis.reasons.join("; ") : null,
            analyzedBy: WORKER_ID,
            analyzedAt: new Date()
        }
    })

    // Log the moderation decision
    await prisma.moderationLog.create({
        data: {
            queueId: item.id,
            action,
            score: analysis.score,
            analysis: JSON.stringify(analysis),
            workerId: WORKER_ID
        }
    })

    // If auto-approved, update the original content status
    if (action === "auto_approve" && item.contentType === "topic") {
        // Topics are already visible, but we could add a "verified" flag
        // For now, just log it
    }

    // If auto-rejected, we could hide or delete the content
    if (action === "auto_reject") {
        if (item.contentType === "topic") {
            await prisma.topic.update({
                where: { id: item.contentId },
                data: { category: "rejected" } // Mark as rejected
            })
        } else if (item.contentType === "comment") {
            await prisma.comment.delete({
                where: { id: item.contentId }
            }).catch(() => {}) // Ignore if already deleted
        }
    }

    return { action, score: analysis.score }
}

export async function GET(request: Request) {
    if (!verifyCronSecret(request)) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const run = await startWorkerRun()

    try {
        // Get pending items
        const pendingItems = await prisma.moderationQueue.findMany({
            where: { status: "pending" },
            take: BATCH_SIZE,
            orderBy: { createdAt: "asc" }
        })

        if (pendingItems.length === 0) {
            await completeWorkerRun(run.id, 0)
            return NextResponse.json({
                success: true,
                runId: run.id,
                message: "No pending items to moderate",
                processed: 0
            })
        }

        const results = {
            auto_approve: 0,
            auto_reject: 0,
            flag_review: 0
        }

        // Process each item
        for (const item of pendingItems) {
            const result = await processItem(item)
            results[result.action as keyof typeof results]++
        }

        await completeWorkerRun(run.id, pendingItems.length)

        return NextResponse.json({
            success: true,
            runId: run.id,
            processed: pendingItems.length,
            results
        })
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error"
        await completeWorkerRun(run.id, 0, errorMessage)

        return NextResponse.json({
            success: false,
            runId: run.id,
            error: errorMessage
        }, { status: 500 })
    }
}

// Allow manual trigger via POST with specific content
export async function POST(request: Request) {
    try {
        const { contentType, contentId, content } = await request.json()

        if (!contentType || !contentId || !content) {
            return NextResponse.json(
                { error: "Missing required fields: contentType, contentId, content" },
                { status: 400 }
            )
        }

        // Add to moderation queue
        const queueItem = await prisma.moderationQueue.create({
            data: {
                contentType,
                contentId,
                content
            }
        })

        // Immediately process it
        const result = await processItem({
            id: queueItem.id,
            content,
            contentType,
            contentId
        })

        // Get updated queue item
        const updatedItem = await prisma.moderationQueue.findUnique({
            where: { id: queueItem.id }
        })

        return NextResponse.json({
            success: true,
            queueId: queueItem.id,
            action: result.action,
            score: result.score,
            status: updatedItem?.status
        })
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : "Unknown error" },
            { status: 500 }
        )
    }
}
