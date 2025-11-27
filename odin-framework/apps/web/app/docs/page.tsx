import Link from "next/link"
import { Navbar } from "@/components/layout/navbar"
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { BookOpen, Lightbulb, Rocket, Code } from "lucide-react"

export default function DocsPage() {
    const sections = [
        {
            title: "Getting Started",
            description: "Install ODIN and create your first AI-powered project in minutes.",
            href: "/docs/getting-started",
            icon: Rocket,
        },
        {
            title: "Core Concepts",
            description: "Understand the fundamental principles behind ODIN's context engineering approach.",
            href: "/docs/concepts",
            icon: Lightbulb,
        },
        {
            title: "CLI Reference",
            description: "Complete reference for all ODIN CLI commands and options.",
            href: "/docs/cli",
            icon: Code,
        },
        {
            title: "Best Practices",
            description: "Learn how to write effective prompts and structure your AI projects.",
            href: "/docs/best-practices",
            icon: BookOpen,
        },
    ]

    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">Documentation</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Everything you need to master context engineering with ODIN.
                    </p>

                    <div className="grid md:grid-cols-2 gap-6">
                        {sections.map((section) => (
                            <Link key={section.href} href={section.href}>
                                <Card className="h-full hover:border-primary/50 transition-colors cursor-pointer">
                                    <CardHeader>
                                        <div className="flex items-center gap-3 mb-2">
                                            <section.icon className="h-6 w-6 text-primary" />
                                            <CardTitle>{section.title}</CardTitle>
                                        </div>
                                        <CardDescription>{section.description}</CardDescription>
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
