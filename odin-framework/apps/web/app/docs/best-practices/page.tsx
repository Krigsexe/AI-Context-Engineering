import { Navbar } from "@/components/layout/navbar"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export default function BestPracticesPage() {
    const practices = [
        {
            title: "Be Specific with Context",
            description: "Provide clear, relevant information",
            content: "Always include only the most relevant context for each interaction. Avoid dumping entire codebases or documents. Instead, carefully select the specific sections that matter for the task at hand.",
        },
        {
            title: "Structure Your Prompts",
            description: "Use consistent formatting patterns",
            content: "Organize your prompts with clear sections: role definition, context, task description, output format, and constraints. This helps AI models parse and respond to your requests more effectively.",
        },
        {
            title: "Iterate and Refine",
            description: "Continuously improve your templates",
            content: "Treat your prompts as living documents. Collect feedback, analyze results, and refine your templates over time. Small adjustments can lead to significant improvements in output quality.",
        },
        {
            title: "Use Examples Wisely",
            description: "Demonstrate desired outputs",
            content: "Include 2-3 high-quality examples in your prompts to show the AI exactly what you expect. This few-shot approach dramatically improves consistency and accuracy.",
        },
        {
            title: "Manage Token Budgets",
            description: "Optimize context window usage",
            content: "Be mindful of token limits. Prioritize the most important information, use summarization for lengthy content, and leverage ODIN's chunking features to maximize the value of every token.",
        },
        {
            title: "Version Your Prompts",
            description: "Track changes over time",
            content: "Use version control for your prompt templates just like code. This allows you to track what works, roll back changes, and collaborate effectively with your team.",
        },
        {
            title: "Test Across Scenarios",
            description: "Validate with diverse inputs",
            content: "Test your prompts with various edge cases and input types. What works for one scenario may fail for another. Build a test suite for your critical prompts.",
        },
        {
            title: "Document Your Patterns",
            description: "Share knowledge across your team",
            content: "Create a library of proven prompt patterns and share them with your team. Document what works, what doesn't, and why. This accelerates learning and ensures consistency.",
        },
    ]

    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">Best Practices</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Proven strategies for effective context engineering and prompt design.
                    </p>

                    <div className="space-y-6">
                        {practices.map((practice, index) => (
                            <Card key={index}>
                                <CardHeader>
                                    <div className="flex items-center gap-3">
                                        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-cyan-500/10 text-cyan-400 text-sm font-bold">
                                            {index + 1}
                                        </span>
                                        <div>
                                            <CardTitle>{practice.title}</CardTitle>
                                            <CardDescription>{practice.description}</CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-muted-foreground">{practice.content}</p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </main>
        </>
    )
}
