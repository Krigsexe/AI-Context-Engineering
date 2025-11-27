import path from "node:path"
import type { PrismaConfig } from "prisma"

export default {
  earlyAccess: true,
  schema: path.join(__dirname, "schema.prisma"),

  // For prisma db push and prisma migrate
  datasource: {
    async adapter() {
      const connectionString = process.env.DATABASE_URL
      if (!connectionString) {
        throw new Error("DATABASE_URL environment variable is not set")
      }

      const { PrismaNeon } = await import("@prisma/adapter-neon")
      const { neon } = await import("@neondatabase/serverless")

      const sql = neon(connectionString)
      return new PrismaNeon(sql)
    },
  },
} satisfies PrismaConfig

