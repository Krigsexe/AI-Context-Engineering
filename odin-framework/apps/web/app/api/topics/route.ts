import { NextRequest, NextResponse } from "next/server"
import { prisma } from "@/lib/db"
import { getCache, setCache, invalidatePattern } from "@/lib/redis"

// GET - List all topics with caching
export async function GET(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url)
        const category = searchParams.get("category")
        const page = parseInt(searchParams.get("page") || "1")
        const limit = parseInt(searchParams.get("limit") || "10")
        const skip = (page - 1) * limit

        // Cache key based on params
        const cacheKey = `topics:${category || "all"}:${page}:${limit}`
        const cached = await getCache<{ topics: unknown[]; total: number }>(cacheKey)
        if (cached) {
            return NextResponse.json({ ...cached, cached: true })
        }

        const where = category ? { category } : {}

        const [topics, total] = await Promise.all([
            prisma.topic.findMany({
                where,
                orderBy: { createdAt: "desc" },
                skip,
                take: limit,
                include: {
                    _count: { select: { comments: true } }
                }
            }),
            prisma.topic.count({ where })
        ])

        const result = { topics, total, page, limit }

        // Cache for 5 minutes
        await setCache(cacheKey, result, 300)

        return NextResponse.json({ ...result, cached: false })
    } catch (error) {
        console.error("Topics GET error:", error)
        return NextResponse.json(
            { error: "Failed to fetch topics" },
            { status: 500 }
        )
    }
}

// POST - Create new topic (anonymous)
export async function POST(request: NextRequest) {
    try {
        const { title, content, category = "general" } = await request.json()

        if (!title || !content) {
            return NextResponse.json(
                { error: "Title and content required" },
                { status: 400 }
            )
        }

        if (title.length > 200) {
            return NextResponse.json(
                { error: "Title too long (max 200 chars)" },
                { status: 400 }
            )
        }

        if (content.length > 10000) {
            return NextResponse.json(
                { error: "Content too long (max 10000 chars)" },
                { status: 400 }
            )
        }

        const topic = await prisma.topic.create({
            data: { title, content, category }
        })

        // Invalidate topics cache
        await invalidatePattern("topics:*")

        return NextResponse.json(topic, { status: 201 })
    } catch (error) {
        console.error("Topics POST error:", error)
        return NextResponse.json(
            { error: "Failed to create topic" },
            { status: 500 }
        )
    }
}
