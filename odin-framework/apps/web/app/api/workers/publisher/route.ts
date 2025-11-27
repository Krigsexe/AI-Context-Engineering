import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { invalidatePattern } from "@/lib/redis"
import Groq from "groq-sdk"

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY
})

const WORKER_ID = "auto-publisher"

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

// Generate a summary of new content using Groq
async function generateContentSummary(contents: Array<{ type: string; title: string; content: string }>): Promise<string> {
    if (contents.length === 0) return ""

    const contentList = contents.map(c => `[${c.type.toUpperCase()}] ${c.title}: ${c.content.substring(0, 200)}...`).join("\n\n")

    try {
        const response = await groq.chat.completions.create({
            model: "llama-3.1-70b-versatile",
            messages: [
                {
                    role: "system",
                    content: "You are a technical writer for ODIN Framework. Generate a brief, professional summary of new content updates for the community. Keep it concise (2-3 sentences max)."
                },
                {
                    role: "user",
                    content: `Summarize these new updates:\n\n${contentList}`
                }
            ],
            temperature: 0.3,
            max_tokens: 200
        })

        return response.choices[0]?.message?.content || ""
    } catch (error) {
        console.error("Error generating summary:", error)
        return ""
    }
}

// Publish approved content from moderation queue
async function publishApprovedContent(): Promise<number> {
    // Find recently approved items that might need cache invalidation
    const recentlyApproved = await prisma.moderationQueue.findMany({
        where: {
            status: "approved",
            analyzedAt: {
                gte: new Date(Date.now() - 60 * 60 * 1000) // Last hour
            }
        },
        orderBy: { analyzedAt: "desc" }
    })

    // Invalidate relevant caches
    if (recentlyApproved.length > 0) {
        await invalidatePattern("topics:*")
        await invalidatePattern("docs:*")
    }

    return recentlyApproved.length
}

// Sync and publish GitHub content updates
async function publishGitHubUpdates(): Promise<{ docs: number; releases: number; prs: number }> {
    const counts = { docs: 0, releases: 0, prs: 0 }

    // Get recently synced content
    const recentContent = await prisma.syncedContent.findMany({
        where: {
            syncedAt: {
                gte: new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
            }
        },
        orderBy: { syncedAt: "desc" }
    })

    for (const content of recentContent) {
        switch (content.type) {
            case "doc":
                counts.docs++
                break
            case "release":
                counts.releases++
                break
            case "pr":
                counts.prs++
                break
        }
    }

    // Invalidate caches if there are updates
    if (recentContent.length > 0) {
        await invalidatePattern("synced:*")
        await invalidatePattern("releases:*")
        await invalidatePattern("docs:*")
    }

    return counts
}

// Create activity summary
async function createActivitySummary(): Promise<string | null> {
    // Get stats from last 24 hours
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

    const [newTopics, newComments, syncedContent, moderationStats] = await Promise.all([
        prisma.topic.count({ where: { createdAt: { gte: oneDayAgo } } }),
        prisma.comment.count({ where: { createdAt: { gte: oneDayAgo } } }),
        prisma.syncedContent.findMany({
            where: { syncedAt: { gte: oneDayAgo } },
            select: { type: true, title: true, content: true }
        }),
        prisma.moderationQueue.groupBy({
            by: ["status"],
            where: { createdAt: { gte: oneDayAgo } },
            _count: true
        })
    ])

    // If no activity, skip
    if (newTopics === 0 && newComments === 0 && syncedContent.length === 0) {
        return null
    }

    // Generate AI summary if there's new synced content
    let aiSummary = ""
    if (syncedContent.length > 0) {
        aiSummary = await generateContentSummary(syncedContent)
    }

    const stats = {
        period: "24h",
        topics: newTopics,
        comments: newComments,
        syncedContent: syncedContent.length,
        moderation: Object.fromEntries(
            moderationStats.map(s => [s.status, s._count])
        ),
        aiSummary,
        generatedAt: new Date().toISOString()
    }

    return JSON.stringify(stats)
}

export async function GET(request: Request) {
    if (!verifyCronSecret(request)) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const run = await startWorkerRun()

    try {
        // Run all publishing tasks
        const [approvedCount, githubCounts, activitySummary] = await Promise.all([
            publishApprovedContent(),
            publishGitHubUpdates(),
            createActivitySummary()
        ])

        const totalProcessed = approvedCount + githubCounts.docs + githubCounts.releases + githubCounts.prs

        await completeWorkerRun(run.id, totalProcessed)

        return NextResponse.json({
            success: true,
            runId: run.id,
            published: {
                approvedContent: approvedCount,
                github: githubCounts
            },
            activitySummary: activitySummary ? JSON.parse(activitySummary) : null
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

// Endpoint to get current activity stats
export async function POST(request: Request) {
    try {
        const summary = await createActivitySummary()

        if (!summary) {
            return NextResponse.json({
                message: "No recent activity",
                stats: null
            })
        }

        return NextResponse.json({
            success: true,
            stats: JSON.parse(summary)
        })
    } catch (error) {
        return NextResponse.json(
            { error: error instanceof Error ? error.message : "Unknown error" },
            { status: 500 }
        )
    }
}
