"use client"

import Link from "next/link"
import { useState } from "react"
import { ThemeToggle } from "@/components/theme-toggle"
import { Github, ChevronDown, BookOpen, Lightbulb, FileText, Rocket, Code } from "lucide-react"

const menuItems = [
    {
        label: "Documentation",
        href: "/docs",
        icon: BookOpen,
        description: "Guides et références complètes"
    },
    {
        label: "Getting Started",
        href: "/docs/getting-started",
        icon: Rocket,
        description: "Démarrer en quelques minutes"
    },
    {
        label: "Concepts",
        href: "/docs/concepts",
        icon: Lightbulb,
        description: "Comprendre le Context Engineering"
    },
    {
        label: "Blog",
        href: "/blog",
        icon: FileText,
        description: "Articles et tutoriels"
    },
]

export function Navbar() {
    const [isOpen, setIsOpen] = useState(false)

    return (
        <header className="fixed top-0 w-full z-50 border-b border-cyan-500/10 bg-background/80 backdrop-blur-md">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                {/* Center: Logo */}
                <Link href="/" className="absolute left-1/2 -translate-x-1/2 flex items-center gap-2 font-bold">
                    <span className="hidden md:flex items-baseline gap-2">
                        <span className="text-sm lg:text-base font-semibold tracking-tight logo-gradient">
                            Orchestrated.Development.Intelligence.Network
                        </span>
                        <span className="text-xs text-muted-foreground typing-text">
                            for your AI
                        </span>
                    </span>
                    <span className="md:hidden text-lg logo-gradient font-bold">✳ ODIN</span>
                </Link>

                {/* Left: Empty space for balance */}
                <div className="w-24" />

                {/* Right: Theme Toggle + GitHub + Dropdown */}
                <div className="flex items-center gap-2">
                    <ThemeToggle />

                    <Link
                        href="https://github.com/Krigsexe/AI-Context-Engineering"
                        target="_blank"
                        className="group p-2 rounded-lg transition-all"
                    >
                        <Github className="h-5 w-5 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
                        <span className="sr-only">GitHub</span>
                    </Link>

                    {/* Dropdown Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            onBlur={() => setTimeout(() => setIsOpen(false), 150)}
                            className="group flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-all border border-cyan-500/20 hover:border-cyan-500/40"
                        >
                            <Code className="h-4 w-4 text-cyan-400 group-hover:text-cyan-300 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
                            <span className="hidden sm:inline text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all">Explore</span>
                            <ChevronDown className={`h-4 w-4 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all duration-200 ${isOpen ? 'rotate-180' : ''}`} />
                        </button>

                        {/* Dropdown Panel */}
                        <div className={`absolute right-0 mt-2 w-72 origin-top-right transition-all duration-200 ease-out ${
                            isOpen
                                ? 'opacity-100 scale-100 translate-y-0'
                                : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'
                        }`}>
                            <div className="bg-card border border-cyan-500/20 rounded-xl shadow-xl shadow-cyan-500/5 overflow-hidden backdrop-blur-xl">
                                <div className="p-2">
                                    {menuItems.map((item) => (
                                        <Link
                                            key={item.href}
                                            href={item.href}
                                            onClick={() => setIsOpen(false)}
                                            className="flex items-start gap-3 p-3 rounded-lg transition-all group/item"
                                        >
                                            <div className="p-2 rounded-md bg-transparent border border-cyan-500/20 group-hover/item:border-cyan-500/40 transition-all">
                                                <item.icon className="h-4 w-4 text-foreground group-hover/item:text-cyan-400 group-hover/item:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="font-medium text-sm text-foreground group-hover/item:text-cyan-400 group-hover/item:drop-shadow-[0_0_6px_rgba(0,255,255,0.6)] transition-all">{item.label}</div>
                                                <div className="text-xs text-muted-foreground truncate">
                                                    {item.description}
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
}
