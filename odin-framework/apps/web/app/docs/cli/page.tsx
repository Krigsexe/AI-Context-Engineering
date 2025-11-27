import { Navbar } from "@/components/layout/navbar"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"

export default function CliPage() {
    const commands = [
        {
            title: "odin init",
            description: "Initialize a new ODIN project",
            content: "Creates a new ODIN project with the recommended structure, configuration files, and default prompts. Use --template to start from a pre-built template.",
            usage: "odin init [project-name] [--template <name>]",
        },
        {
            title: "odin add",
            description: "Add a new context or prompt template",
            content: "Adds a new context file or prompt template to your project. Supports various formats including markdown, JSON, and YAML.",
            usage: "odin add <type> <name> [--format <format>]",
        },
        {
            title: "odin build",
            description: "Build and optimize your context files",
            content: "Compiles and optimizes all context files, generating the final artifacts ready for deployment. Includes validation and token counting.",
            usage: "odin build [--output <dir>] [--minify]",
        },
        {
            title: "odin validate",
            description: "Validate your context configuration",
            content: "Checks your context files for errors, validates token limits, and ensures all references are resolved correctly.",
            usage: "odin validate [--strict] [--fix]",
        },
        {
            title: "odin serve",
            description: "Start a local development server",
            content: "Launches a local server for testing your prompts and contexts in real-time with hot reloading support.",
            usage: "odin serve [--port <number>] [--open]",
        },
        {
            title: "odin deploy",
            description: "Deploy your context to production",
            content: "Deploys your built context files to your configured production environment. Supports multiple deployment targets.",
            usage: "odin deploy [--env <environment>] [--dry-run]",
        },
    ]

    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">CLI Reference</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Complete reference for all ODIN command-line interface commands.
                    </p>

                    <div className="space-y-6">
                        {commands.map((command, index) => (
                            <Card key={index}>
                                <CardHeader>
                                    <CardTitle className="font-mono text-cyan-400">{command.title}</CardTitle>
                                    <CardDescription>{command.description}</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <p className="text-muted-foreground">{command.content}</p>
                                    <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm">
                                        <span className="text-muted-foreground">$ </span>
                                        <span>{command.usage}</span>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </main>
        </>
    )
}
