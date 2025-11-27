import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Terminal, Shield, GitBranch, Github } from "lucide-react"
import { TerminalDemo } from "@/components/terminal-demo"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-28 pb-32 overflow-hidden">
        <div className="container px-4 mx-auto relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <Badge className="mb-6 px-4 py-2 text-sm bg-cyan-500/10 text-cyan-500 border-cyan-500/20 hover:bg-cyan-500/20">
              v7.0 Now Available
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8">
              Reliable AI Development <br />
              <span className="logo-gradient">Without Hallucinations</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl leading-relaxed">
              ODIN is an open framework that wraps any LLM with a disciplinary system.
              Traceable, verifiable, and 100% local.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
              <Link href="/docs/getting-started" className="group h-12 px-8 text-base bg-transparent border border-cyan-500/30 rounded-lg font-medium flex items-center justify-center gap-2 transition-all hover:border-cyan-500/50">
                <span className="text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all">Get Started</span>
                <ArrowRight className="h-4 w-4 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
              </Link>
              <Link href="https://github.com/Krigsexe/AI-Context-Engineering" target="_blank" className="group h-12 px-8 text-base bg-transparent border border-cyan-500/30 rounded-lg font-medium flex items-center justify-center gap-2 transition-all hover:border-cyan-500/50">
                <Github className="h-4 w-4 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
                <span className="text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all">View on GitHub</span>
              </Link>
            </div>

            {/* Terminal Preview */}
            <div className="mt-16 w-full max-w-3xl">
              <TerminalDemo />
            </div>
          </div>
        </div>

        {/* Background Gradient - Animated */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl -z-10 opacity-30 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/40 rounded-full blur-3xl animate-pulse-glow" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-400/30 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-muted/30">
        <div className="container px-4 mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Shield className="h-8 w-8 text-cyan-500" />}
              title="Anti-Hallucination"
              description="5-level confidence system. ODIN refuses to answer if it can't verify the information."
            />
            <FeatureCard
              icon={<Terminal className="h-8 w-8 text-cyan-500" />}
              title="100% Local Data"
              description="Your code and context never leave your machine. SQLite database stores everything locally."
            />
            <FeatureCard
              icon={<GitBranch className="h-8 w-8 text-cyan-500" />}
              title="Checkpoint & Rollback"
              description="Every action is logged and reversible. Restore any previous state instantly."
            />
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-24">
        <div className="container px-4 mx-auto">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-6">Not Just Another Assistant</h2>
              <p className="text-lg text-muted-foreground mb-6">
                ODIN doesn't replace your LLM. It builds a disciplinary system around it.
                Think of it as giving your brilliant but chaotic AI student a strict supervisor.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 group">
                  <div className="h-6 w-6 rounded-full bg-cyan-500/20 flex items-center justify-center mt-1 group-hover:bg-cyan-500 group-hover:scale-110 transition-all">
                    <span className="text-cyan-500 text-sm font-bold group-hover:text-black transition-colors">1</span>
                  </div>
                  <div>
                    <strong className="block text-foreground">Pre-Processing</strong>
                    <span className="text-muted-foreground">Context retrieval and verification before the LLM sees anything.</span>
                  </div>
                </li>
                <li className="flex items-start gap-3 group">
                  <div className="h-6 w-6 rounded-full bg-cyan-500/20 flex items-center justify-center mt-1 group-hover:bg-cyan-500 group-hover:scale-110 transition-all">
                    <span className="text-cyan-500 text-sm font-bold group-hover:text-black transition-colors">2</span>
                  </div>
                  <div>
                    <strong className="block text-foreground">Post-Validation</strong>
                    <span className="text-muted-foreground">Oracle checks, security scans, and tests on every output.</span>
                  </div>
                </li>
                <li className="flex items-start gap-3 group">
                  <div className="h-6 w-6 rounded-full bg-cyan-500/20 flex items-center justify-center mt-1 group-hover:bg-cyan-500 group-hover:scale-110 transition-all">
                    <span className="text-cyan-500 text-sm font-bold group-hover:text-black transition-colors">3</span>
                  </div>
                  <div>
                    <strong className="block text-foreground">Persistence</strong>
                    <span className="text-muted-foreground">Long-term memory and audit trails stored locally.</span>
                  </div>
                </li>
              </ul>
            </div>
            <div className="flex-1 bg-card border border-cyan-500/20 rounded-xl p-8 shadow-lg shadow-cyan-500/5 hover-lift animate-shimmer">
              <pre className="text-xs md:text-sm font-mono overflow-x-auto text-cyan-500">
                {`┌──────────────────────────────────────────┐
│          ODIN COGNITIVE SYSTEM           │
├──────────────────────────────────────────┤
│  METACOGNITIVE LAYER                     │
│  ├─ 40+ Specialized Agents               │
│  └─ Validation Oracles                   │
│            ↓                             │
│  LLM LAYER (Unchanged)                   │
│  ├─ Qwen, Claude, GPT, etc.              │
│  └─ Chain-of-thought prompting           │
│            ↓                             │
│  POST-VALIDATION LAYER                   │
│  ├─ Oracle checks                        │
│  └─ Security scan                        │
└──────────────────────────────────────────┘`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-b from-transparent to-cyan-500/5">
        <div className="container px-4 mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to build reliable AI?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
            Join thousands of developers using ODIN to create AI-powered applications without the chaos.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/docs/getting-started" className="group h-12 px-8 text-base bg-transparent border border-cyan-500/30 rounded-lg font-medium flex items-center justify-center gap-2 transition-all hover:border-cyan-500/50">
              <span className="text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all">Start Building</span>
              <ArrowRight className="h-4 w-4 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
            </Link>
            <Link href="/docs" className="group h-12 px-8 text-base bg-transparent border border-cyan-500/30 rounded-lg font-medium flex items-center justify-center gap-2 transition-all hover:border-cyan-500/50">
              <span className="text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all">Read Documentation</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-card border border-cyan-500/10 rounded-xl p-6 hover-lift hover:border-cyan-500/30 transition-all group">
      <div className="mb-4 group-hover:scale-110 transition-transform">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  )
}
