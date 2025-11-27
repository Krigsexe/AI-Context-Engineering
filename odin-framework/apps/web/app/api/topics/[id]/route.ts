import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getCache, setCache, deleteCache, invalidatePattern } from "@/lib/redis"

// GET - Get single topic with comments
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params

        // Check cache
        const cacheKey = `topic:${id}`
        const cached = await getCache(cacheKey)
        if (cached) {
            return NextResponse.json({ ...cached as object, cached: true })
        }

        const topic = await prisma.topic.findUnique({
            where: { id },
            include: {
                comments: {
                    orderBy: { createdAt: "asc" }
                }
            }
        })

        if (!topic) {
            return NextResponse.json(
                { error: "Topic not found" },
                { status: 404 }
            )
        }

        // Cache for 5 minutes
        await setCache(cacheKey, topic, 300)

        return NextResponse.json({ ...topic, cached: false })
    } catch (error) {
        console.error("Topic GET error:", error)
        return NextResponse.json(
            { error: "Failed to fetch topic" },
            { status: 500 }
        )
    }
}

// POST - Add comment to topic (anonymous)
export async function POST(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await params
        const { content } = await request.json()

        if (!content) {
            return NextResponse.json(
                { error: "Content required" },
                { status: 400 }
            )
        }

        if (content.length > 5000) {
            return NextResponse.json(
                { error: "Comment too long (max 5000 chars)" },
                { status: 400 }
            )
        }

        // Verify topic exists
        const topic = await prisma.topic.findUnique({
            where: { id }
        })

        if (!topic) {
            return NextResponse.json(
                { error: "Topic not found" },
                { status: 404 }
            )
        }

        const comment = await prisma.comment.create({
            data: { content, topicId: id }
        })

        // Invalidate topic cache
        await deleteCache(`topic:${id}`)

        return NextResponse.json(comment, { status: 201 })
    } catch (error) {
        console.error("Comment POST error:", error)
        return NextResponse.json(
            { error: "Failed to add comment" },
            { status: 500 }
        )
    }
}
