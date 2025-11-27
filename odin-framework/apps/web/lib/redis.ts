import Redis from "ioredis"

const globalForRedis = globalThis as unknown as {
    redis: Redis | undefined
}

function getRedisClient() {
    if (!process.env.REDIS_URL) {
        console.warn("REDIS_URL not set, caching disabled")
        return null
    }
    return new Redis(process.env.REDIS_URL)
}

export const redis = globalForRedis.redis ?? getRedisClient()

if (process.env.NODE_ENV !== "production" && redis) {
    globalForRedis.redis = redis
}

// Cache helper functions
export async function getCache<T>(key: string): Promise<T | null> {
    if (!redis) return null
    try {
        const data = await redis.get(key)
        return data ? JSON.parse(data) : null
    } catch {
        return null
    }
}

export async function setCache(key: string, value: unknown, ttlSeconds = 3600): Promise<void> {
    if (!redis) return
    try {
        await redis.setex(key, ttlSeconds, JSON.stringify(value))
    } catch (error) {
        console.error("Redis cache error:", error)
    }
}

export async function deleteCache(key: string): Promise<void> {
    if (!redis) return
    try {
        await redis.del(key)
    } catch (error) {
        console.error("Redis delete error:", error)
    }
}

export async function invalidatePattern(pattern: string): Promise<void> {
    if (!redis) return
    try {
        const keys = await redis.keys(pattern)
        if (keys.length > 0) {
            await redis.del(...keys)
        }
    } catch (error) {
        console.error("Redis invalidate error:", error)
    }
}
