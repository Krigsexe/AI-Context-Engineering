import { Navbar } from "@/components/layout/navbar"
import { Card, CardContent } from "@/components/ui/card"

export default function GettingStartedPage() {
    return (
        <>
            <Navbar />
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <h1 className="text-4xl font-bold mb-4">Getting Started</h1>
                    <p className="text-xl text-muted-foreground mb-12">
                        Get up and running with ODIN in just a few minutes.
                    </p>

                    <div className="space-y-8">
                        <section>
                            <h2 className="text-2xl font-semibold mb-4">Installation</h2>
                            <Card>
                                <CardContent className="pt-6">
                                    <p className="mb-4">Install ODIN globally using npm:</p>
                                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                                        <code>npm install -g @odin/cli</code>
                                    </pre>
                                </CardContent>
                            </Card>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold mb-4">Initialize a Project</h2>
                            <Card>
                                <CardContent className="pt-6">
                                    <p className="mb-4">Create a new ODIN project:</p>
                                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                                        <code>odin init my-project{"\n"}cd my-project</code>
                                    </pre>
                                </CardContent>
                            </Card>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold mb-4">Configure Your API Key</h2>
                            <Card>
                                <CardContent className="pt-6">
                                    <p className="mb-4">Set your OpenAI or Anthropic API key:</p>
                                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                                        <code>odin config set api-key YOUR_API_KEY</code>
                                    </pre>
                                </CardContent>
                            </Card>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold mb-4">Run Your First Command</h2>
                            <Card>
                                <CardContent className="pt-6">
                                    <p className="mb-4">Test ODIN with a simple prompt:</p>
                                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                                        <code>odin run "Explain context engineering in simple terms"</code>
                                    </pre>
                                </CardContent>
                            </Card>
                        </section>

                        <section>
                            <h2 className="text-2xl font-semibold mb-4">Next Steps</h2>
                            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                                <li>Learn about <a href="/docs/concepts" className="text-primary hover:underline">Core Concepts</a></li>
                                <li>Explore the <a href="/docs/cli" className="text-primary hover:underline">CLI Reference</a></li>
                                <li>Read our <a href="/blog" className="text-primary hover:underline">Blog</a> for tips and tutorials</li>
                            </ul>
                        </section>
                    </div>
                </div>
            </main>
        </>
    )
}
