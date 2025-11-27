import { NextResponse } from "next/server"
import { prisma } from "@/lib/db"

const GITHUB_REPO = "Krigsexe/AI-Context-Engineering"
const GITHUB_API = "https://api.github.com"

interface GitHubFile {
    name: string
    path: string
    sha: string
    download_url: string | null
    type: string
}

interface GitHubRelease {
    id: number
    tag_name: string
    name: string
    body: string
    html_url: string
    published_at: string
}

interface GitHubPR {
    id: number
    number: number
    title: string
    body: string | null
    html_url: string
    state: string
    created_at: string
    updated_at: string
    user: { login: string }
}

// Verify cron secret to prevent unauthorized access
function verifyCronSecret(request: Request): boolean {
    const authHeader = request.headers.get("authorization")
    const cronSecret = process.env.CRON_SECRET

    if (!cronSecret) return true // Allow if no secret configured (dev mode)
    return authHeader === `Bearer ${cronSecret}`
}

// Start a worker run
async function startWorkerRun(workerId: string) {
    return prisma.workerRun.create({
        data: { workerId, status: "running" }
    })
}

// Complete a worker run
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

// Fetch markdown docs from repo
async function syncDocs(): Promise<number> {
    let synced = 0

    try {
        // Fetch docs directory
        const docsResponse = await fetch(`${GITHUB_API}/repos/${GITHUB_REPO}/contents/docs`, {
            headers: {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ODIN-Framework-Worker"
            }
        })

        if (!docsResponse.ok) return synced

        const files: GitHubFile[] = await docsResponse.json()
        const mdFiles = files.filter(f => f.name.endsWith(".md"))

        for (const file of mdFiles) {
            if (!file.download_url) continue

            const contentResponse = await fetch(file.download_url)
            if (!contentResponse.ok) continue

            const content = await contentResponse.text()

            await prisma.syncedContent.upsert({
                where: {
                    source_externalId: {
                        source: `github:${GITHUB_REPO}`,
                        externalId: file.sha
                    }
                },
                update: {
                    content,
                    updatedAt: new Date()
                },
                create: {
                    type: "doc",
                    source: `github:${GITHUB_REPO}`,
                    externalId: file.sha,
                    title: file.name.replace(".md", ""),
                    content,
                    url: `https://github.com/${GITHUB_REPO}/blob/main/docs/${file.name}`,
                    metadata: JSON.stringify({ path: file.path })
                }
            })
            synced++
        }
    } catch (error) {
        console.error("Error syncing docs:", error)
    }

    return synced
}

// Fetch releases from repo
async function syncReleases(): Promise<number> {
    let synced = 0

    try {
        const response = await fetch(`${GITHUB_API}/repos/${GITHUB_REPO}/releases?per_page=10`, {
            headers: {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ODIN-Framework-Worker"
            }
        })

        if (!response.ok) return synced

        const releases: GitHubRelease[] = await response.json()

        for (const release of releases) {
            await prisma.syncedContent.upsert({
                where: {
                    source_externalId: {
                        source: `github:${GITHUB_REPO}`,
                        externalId: `release-${release.id}`
                    }
                },
                update: {
                    title: release.name || release.tag_name,
                    content: release.body || "",
                    updatedAt: new Date()
                },
                create: {
                    type: "release",
                    source: `github:${GITHUB_REPO}`,
                    externalId: `release-${release.id}`,
                    title: release.name || release.tag_name,
                    content: release.body || "",
                    url: release.html_url,
                    version: release.tag_name,
                    metadata: JSON.stringify({
                        published_at: release.published_at
                    })
                }
            })
            synced++
        }
    } catch (error) {
        console.error("Error syncing releases:", error)
    }

    return synced
}

// Fetch recent PRs from repo
async function syncPRs(): Promise<number> {
    let synced = 0

    try {
        const response = await fetch(
            `${GITHUB_API}/repos/${GITHUB_REPO}/pulls?state=all&per_page=20&sort=updated`,
            {
                headers: {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "ODIN-Framework-Worker"
                }
            }
        )

        if (!response.ok) return synced

        const prs: GitHubPR[] = await response.json()

        for (const pr of prs) {
            await prisma.syncedContent.upsert({
                where: {
                    source_externalId: {
                        source: `github:${GITHUB_REPO}`,
                        externalId: `pr-${pr.id}`
                    }
                },
                update: {
                    title: pr.title,
                    content: pr.body || "",
                    updatedAt: new Date()
                },
                create: {
                    type: "pr",
                    source: `github:${GITHUB_REPO}`,
                    externalId: `pr-${pr.id}`,
                    title: pr.title,
                    content: pr.body || "",
                    url: pr.html_url,
                    metadata: JSON.stringify({
                        number: pr.number,
                        state: pr.state,
                        author: pr.user.login,
                        created_at: pr.created_at,
                        updated_at: pr.updated_at
                    })
                }
            })
            synced++
        }
    } catch (error) {
        console.error("Error syncing PRs:", error)
    }

    return synced
}

export async function GET(request: Request) {
    // Verify authorization
    if (!verifyCronSecret(request)) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const run = await startWorkerRun("github-sync")

    try {
        // Run all sync tasks in parallel
        const [docsCount, releasesCount, prsCount] = await Promise.all([
            syncDocs(),
            syncReleases(),
            syncPRs()
        ])

        const totalSynced = docsCount + releasesCount + prsCount

        await completeWorkerRun(run.id, totalSynced)

        return NextResponse.json({
            success: true,
            runId: run.id,
            synced: {
                docs: docsCount,
                releases: releasesCount,
                prs: prsCount,
                total: totalSynced
            }
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
