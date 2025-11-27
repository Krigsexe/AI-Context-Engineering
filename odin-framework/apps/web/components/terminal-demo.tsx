"use client"

import { useState, useEffect } from "react"

const terminalLines = [
    { text: "$ npx @odin/cli init", type: "command", delay: 0 },
    { text: "", type: "empty", delay: 800 },
    { text: "[ODIN] Framework Initialization v7.0.0", type: "info", delay: 1000 },
    { text: "", type: "empty", delay: 1200 },
    { text: "Detecting environment...", type: "normal", delay: 1400 },
    { text: "[OK] Detected: VS Code / Cursor", type: "success", delay: 2200 },
    { text: "[OK] Node.js v20.11.0", type: "success", delay: 2600 },
    { text: "[OK] pnpm 9.0.0", type: "success", delay: 3000 },
    { text: "", type: "empty", delay: 3200 },
    { text: "Installing dependencies...", type: "normal", delay: 3400 },
    { text: "  @odin/core", type: "package", delay: 3800 },
    { text: "  @odin/agents", type: "package", delay: 4100 },
    { text: "  @odin/validators", type: "package", delay: 4400 },
    { text: "  @odin/memory", type: "package", delay: 4700 },
    { text: "", type: "empty", delay: 5000 },
    { text: "Configuring ODIN layers...", type: "normal", delay: 5200 },
    { text: "  [1/3] Metacognitive layer", type: "step", delay: 5600 },
    { text: "  [2/3] Validation oracles", type: "step", delay: 6000 },
    { text: "  [3/3] Local persistence", type: "step", delay: 6400 },
    { text: "", type: "empty", delay: 6800 },
    { text: "[DONE] Project initialized successfully!", type: "success", delay: 7200 },
    { text: "", type: "empty", delay: 7600 },
    { text: "$ odin serve", type: "command", delay: 8000 },
    { text: "[ODIN] Server running on http://localhost:3333", type: "info", delay: 8800 },
    { text: "[ODIN] Dashboard: http://localhost:3333/dashboard", type: "info", delay: 9200 },
    { text: "", type: "empty", delay: 9600 },
    { text: "Ready. Your AI now has supervision.", type: "final", delay: 10000 },
]

export function TerminalDemo() {
    const [visibleLines, setVisibleLines] = useState<number>(0)
    const [isTyping, setIsTyping] = useState(true)

    useEffect(() => {
        const timers: NodeJS.Timeout[] = []

        terminalLines.forEach((line, index) => {
            const timer = setTimeout(() => {
                setVisibleLines(index + 1)
                if (index === terminalLines.length - 1) {
                    setIsTyping(false)
                    // Restart animation after pause
                    setTimeout(() => {
                        setVisibleLines(0)
                        setIsTyping(true)
                    }, 4000)
                }
            }, line.delay)
            timers.push(timer)
        })

        return () => timers.forEach(timer => clearTimeout(timer))
    }, [visibleLines === 0])

    const getLineStyle = (type: string) => {
        switch (type) {
            case "command":
                return "text-cyan-400"
            case "info":
                return "text-cyan-500"
            case "success":
                return "text-green-400"
            case "package":
                return "text-muted-foreground"
            case "step":
                return "text-foreground"
            case "final":
                return "text-cyan-400 font-semibold"
            default:
                return "text-muted-foreground"
        }
    }

    return (
        <div className="bg-card border border-cyan-500/20 rounded-xl shadow-2xl shadow-cyan-500/10 overflow-hidden text-left hover-lift">
            <div className="bg-muted/50 px-4 py-3 border-b border-cyan-500/20 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <div className="ml-2 text-xs text-muted-foreground font-mono">odin-cli - 80x24</div>
            </div>
            <div className="p-6 font-mono text-sm h-[320px] overflow-hidden">
                {terminalLines.slice(0, visibleLines).map((line, index) => (
                    <div key={index} className={`${getLineStyle(line.type)} leading-relaxed`}>
                        {line.text || "\u00A0"}
                    </div>
                ))}
                {isTyping && (
                    <span className="inline-block w-2 h-4 bg-cyan-400 animate-pulse ml-1" />
                )}
            </div>
        </div>
    )
}
