import { Navbar } from "@/components/layout/navbar"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export default function ConceptsPage() {
    const concepts = [
        {
            title: "Context Engineering",
            description: "The art of crafting the perfect context for AI interactions",
            content: "Context engineering is about providing AI models with precisely the right information at the right time. Unlike simple prompt engineering, it considers the entire information architecture around your AI interactions.",
        },
        {
            title: "Prompt Templates",
            description: "Reusable, parameterized prompts for consistent results",
            content: "ODIN uses a templating system that allows you to create standardized prompts with variable placeholders. This ensures consistency across your team and makes it easy to iterate on prompt strategies.",
        },
        {
            title: "Context Windows",
            description: "Managing token limits effectively",
            content: "Every AI model has a limited context window. ODIN helps you manage this constraint by intelligently selecting and prioritizing the most relevant information for each interaction.",
        },
        {
            title: "Semantic Chunking",
            description: "Breaking down content intelligently",
            content: "Rather than arbitrary splits, ODIN uses semantic analysis to chunk your content at natural boundaries, preserving meaning and improving AI comprehension.",
        },
        {
            title: "Memory Layers",
            description: "Short-term, long-term, and episodic memory for AI",
            content: "ODIN implements a multi-layered memory system that mimics human cognition, allowing AI to maintain context across sessions and learn from past interactions.",
        },
        {
            title: "Retrieval Augmented Generation",
            description: "Grounding AI responses in your data",
            content: "RAG combines the power of large language models with your specific knowledge base, ensuring responses are accurate and relevant to your domain.",
        },
    ]

    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">Core Concepts</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Understanding the fundamental principles that power ODIN.
                    </p>

                    <div className="space-y-6">
                        {concepts.map((concept, index) => (
                            <Card key={index}>
                                <CardHeader>
                                    <CardTitle>{concept.title}</CardTitle>
                                    <CardDescription>{concept.description}</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-muted-foreground">{concept.content}</p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </main>
        </>
    )
}
