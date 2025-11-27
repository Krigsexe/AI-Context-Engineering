"use client"

import { useState, useRef, useEffect } from "react"
import { MessageCircle, X, Send, Bot, User } from "lucide-react"

interface Message {
    role: "user" | "assistant"
    content: string
}

export function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [sessionId] = useState(() => Math.random().toString(36).substring(7))
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return

        const userMessage: Message = { role: "user", content: input.trim() }
        const newMessages = [...messages, userMessage]
        setMessages(newMessages)
        setInput("")
        setIsLoading(true)

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: newMessages,
                    sessionId
                })
            })

            if (!response.ok) throw new Error("Failed to get response")

            const data = await response.json()
            setMessages([...newMessages, { role: "assistant", content: data.response }])
        } catch (error) {
            console.error("Chat error:", error)
            setMessages([
                ...newMessages,
                { role: "assistant", content: "Sorry, I encountered an error. Please try again." }
            ])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <>
            {/* Chat Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-lg transition-all duration-300 ${
                    isOpen
                        ? "bg-red-500 hover:bg-red-600"
                        : "bg-cyan-500 hover:bg-cyan-600 hover:shadow-cyan-500/50 hover:shadow-xl"
                }`}
            >
                {isOpen ? (
                    <X className="h-6 w-6 text-white" />
                ) : (
                    <MessageCircle className="h-6 w-6 text-white" />
                )}
            </button>

            {/* Chat Window */}
            <div className={`fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] transition-all duration-300 ${
                isOpen
                    ? "opacity-100 translate-y-0 pointer-events-auto"
                    : "opacity-0 translate-y-4 pointer-events-none"
            }`}>
                <div className="bg-card border border-cyan-500/20 rounded-xl shadow-2xl shadow-cyan-500/10 overflow-hidden flex flex-col h-[500px]">
                    {/* Header */}
                    <div className="bg-muted/50 px-4 py-3 border-b border-cyan-500/20 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
                            <Bot className="h-5 w-5 text-cyan-400" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-sm">ODIN Assistant</h3>
                            <p className="text-xs text-muted-foreground">Powered by Groq</p>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.length === 0 && (
                            <div className="text-center text-muted-foreground py-8">
                                <Bot className="h-12 w-12 mx-auto mb-4 text-cyan-500/50" />
                                <p className="text-sm">Hi! I'm ODIN Assistant.</p>
                                <p className="text-xs mt-1">Ask me anything about the ODIN Framework.</p>
                            </div>
                        )}
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                            >
                                {msg.role === "assistant" && (
                                    <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                                        <Bot className="h-4 w-4 text-cyan-400" />
                                    </div>
                                )}
                                <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                                    msg.role === "user"
                                        ? "bg-cyan-500 text-white"
                                        : "bg-muted"
                                }`}>
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                </div>
                                {msg.role === "user" && (
                                    <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center flex-shrink-0">
                                        <User className="h-4 w-4 text-white" />
                                    </div>
                                )}
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
                                    <Bot className="h-4 w-4 text-cyan-400 animate-pulse" />
                                </div>
                                <div className="bg-muted rounded-lg px-4 py-2">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-cyan-500/20">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask about ODIN..."
                                className="flex-1 bg-muted rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                                disabled={isLoading}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                className="p-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                            >
                                <Send className="h-5 w-5 text-white" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
