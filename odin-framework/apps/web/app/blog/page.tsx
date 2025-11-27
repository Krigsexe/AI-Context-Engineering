import Link from "next/link"
import { Navbar } from "@/components/layout/navbar"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function BlogPage() {
    const posts = [
        {
            title: "Introducing ODIN: A New Era of Context Engineering",
            description: "Discover how ODIN revolutionizes the way developers interact with AI through intelligent context management.",
            date: "2024-01-15",
            category: "Announcement",
            slug: "introducing-odin",
        },
        {
            title: "Why Context Engineering Matters More Than Prompt Engineering",
            description: "Learn why focusing solely on prompts is limiting and how context engineering provides a more holistic approach.",
            date: "2024-01-10",
            category: "Tutorial",
            slug: "context-vs-prompt-engineering",
        },
        {
            title: "Building Your First AI-Powered CLI with ODIN",
            description: "A step-by-step guide to creating a command-line tool that leverages AI capabilities.",
            date: "2024-01-05",
            category: "Tutorial",
            slug: "first-ai-cli",
        },
        {
            title: "Best Practices for Managing Large Context Windows",
            description: "Tips and techniques for efficiently utilizing context windows in production applications.",
            date: "2024-01-01",
            category: "Best Practices",
            slug: "managing-context-windows",
        },
    ]

    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">Blog</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Insights, tutorials, and updates from the ODIN team.
                    </p>

                    <div className="space-y-6">
                        {posts.map((post) => (
                            <Link key={post.slug} href={`/blog/${post.slug}`}>
                                <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                                    <CardHeader>
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge variant="secondary">{post.category}</Badge>
                                            <span className="text-sm text-muted-foreground">{post.date}</span>
                                        </div>
                                        <CardTitle>{post.title}</CardTitle>
                                        <CardDescription>{post.description}</CardDescription>
                                    </CardHeader>
                                </Card>
                            </Link>
                        ))}
                    </div>
                </div>
            </main>
        </>
    )
}
