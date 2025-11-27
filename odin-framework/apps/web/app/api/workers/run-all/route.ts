import { NextResponse } from "next/server"

// Combined worker for Vercel Hobby plan (1 cron/day limit)
// Runs all workers sequentially: github-sync -> moderator -> publisher

function verifyCronSecret(request: Request): boolean {
    const authHeader = request.headers.get("authorization")
    const cronSecret = process.env.CRON_SECRET
    if (!cronSecret) return true
    return authHeader === `Bearer ${cronSecret}`
}

async function runWorker(baseUrl: string, path: string, secret?: string): Promise<{ success: boolean; data?: unknown; error?: string }> {
    try {
        const headers: Record<string, string> = {}
        if (secret) {
            headers["Authorization"] = `Bearer ${secret}`
        }

        const response = await fetch(`${baseUrl}${path}`, { headers })
        const data = await response.json()

        return {
            success: response.ok,
            data
        }
    } catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error.message : "Unknown error"
        }
    }
}

export async function GET(request: Request) {
    if (!verifyCronSecret(request)) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const baseUrl = process.env.VERCEL_URL
        ? `https://${process.env.VERCEL_URL}`
        : "http://localhost:3000"

    const cronSecret = process.env.CRON_SECRET

    const results: Record<string, unknown> = {
        startedAt: new Date().toISOString(),
        workers: {}
    }

    // 1. GitHub Sync - fetch latest docs, PRs, releases
    console.log("[run-all] Starting github-sync...")
    const githubSync = await runWorker(baseUrl, "/api/workers/github-sync", cronSecret)
    results.workers = { ...results.workers as object, "github-sync": githubSync }

    // 2. Moderator - analyze pending content
    console.log("[run-all] Starting moderator...")
    const moderator = await runWorker(baseUrl, "/api/workers/moderator", cronSecret)
    results.workers = { ...results.workers as object, moderator }

    // 3. Publisher - publish approved content and generate summaries
    console.log("[run-all] Starting publisher...")
    const publisher = await runWorker(baseUrl, "/api/workers/publisher", cronSecret)
    results.workers = { ...results.workers as object, publisher }

    results.completedAt = new Date().toISOString()
    results.allSuccess = githubSync.success && moderator.success && publisher.success

    return NextResponse.json(results)
}
