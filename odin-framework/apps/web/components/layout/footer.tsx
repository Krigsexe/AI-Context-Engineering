"use client"

import Link from "next/link"
import { Github } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"

export function Footer() {
    return (
        <footer className="border-t border-cyan-500/10 py-12 bg-muted/20">
            <div className="container mx-auto px-4">
                <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="text-center md:text-left">
                        <p className="text-muted-foreground text-sm mb-2">
                            Built with passion by Julien Gelee{" "}
                            <Link
                                href="https://github.com/Krigsexe"
                                target="_blank"
                                className="group/krigs inline-flex"
                            >
                                <span className="text-cyan-400 group-hover/krigs:text-cyan-300 group-hover/krigs:drop-shadow-[0_0_12px_rgba(0,255,255,0.9)] transition-all duration-300">(Krigs)</span>
                            </Link>
                            {" "}and the Open Source Community.
                        </p>
                        <p className="text-muted-foreground text-xs">
                            Released under MIT License. The code is yours.
                        </p>
                    </div>

                    <div className="flex items-center gap-4">
                        <Link
                            href="https://github.com/Krigsexe/AI-Context-Engineering"
                            target="_blank"
                            className="group p-2 rounded-lg transition-all"
                        >
                            <Github className="h-5 w-5 text-foreground group-hover:text-cyan-400 group-hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.8)] transition-all" />
                        </Link>
                        <div className="h-4 w-px bg-border" />
                        <ThemeToggle variant="outline" />
                    </div>
                </div>
            </div>
        </footer>
    )
}
