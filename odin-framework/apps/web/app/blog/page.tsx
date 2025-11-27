"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, MessageSquare, Clock, Send } from "lucide-react"

interface Topic {
    id: string
    title: string
    content: string
    category: string
    createdAt: string
    _count?: { comments: number }
}

const CATEGORIES = ["general", "tutorial", "question", "announcement", "discussion"]

export default function BlogPage() {
    const [topics, setTopics] = useState<Topic[]>([])
    const [loading, setLoading] = useState(true)
    const [showForm, setShowForm] = useState(false)
    const [newTopic, setNewTopic] = useState({ title: "", content: "", category: "general" })
    const [submitting, setSubmitting] = useState(false)
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

    const fetchTopics = async () => {
        try {
            const url = selectedCategory
                ? `/api/topics?category=${selectedCategory}`
                : "/api/topics"
            const res = await fetch(url)
            const data = await res.json()
            setTopics(data.topics || [])
        } catch (error) {
            console.error("Failed to fetch topics:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchTopics()
    }, [selectedCategory])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newTopic.title.trim() || !newTopic.content.trim()) return

        setSubmitting(true)
        try {
            const res = await fetch("/api/topics", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newTopic)
            })

            if (res.ok) {
                setNewTopic({ title: "", content: "", category: "general" })
                setShowForm(false)
                fetchTopics()
            }
        } catch (error) {
            console.error("Failed to create topic:", error)
        } finally {
            setSubmitting(false)
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric"
        })
    }

    return (
        <main className="min-h-screen pt-24 pb-16">
            <div className="container mx-auto px-4 max-w-4xl">
                <div className="flex items-center justify-between mb-4">
                    <h1 className="text-4xl font-bold">Community Topics</h1>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="group flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-all"
                    >
                        <Plus className="h-5 w-5" />
                        <span>New Topic</span>
                    </button>
                </div>
                <p className="text-xl text-muted-foreground mb-8">
                    Share knowledge, ask questions, and discuss ODIN with the community.
                    <span className="block text-sm mt-1 text-cyan-500">All posts are anonymous.</span>
                </p>

                {/* New Topic Form */}
                {showForm && (
                    <Card className="mb-8 border-cyan-500/30">
                        <CardHeader>
                            <CardTitle>Create New Topic</CardTitle>
                            <CardDescription>Share your thoughts with the community</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Title</label>
                                    <input
                                        type="text"
                                        value={newTopic.title}
                                        onChange={(e) => setNewTopic({ ...newTopic, title: e.target.value })}
                                        placeholder="What's your topic about?"
                                        className="w-full bg-muted rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                                        maxLength={200}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Category</label>
                                    <select
                                        value={newTopic.category}
                                        onChange={(e) => setNewTopic({ ...newTopic, category: e.target.value })}
                                        className="w-full bg-muted rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                                    >
                                        {CATEGORIES.map((cat) => (
                                            <option key={cat} value={cat}>
                                                {cat.charAt(0).toUpperCase() + cat.slice(1)}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Content</label>
                                    <textarea
                                        value={newTopic.content}
                                        onChange={(e) => setNewTopic({ ...newTopic, content: e.target.value })}
                                        placeholder="Share your knowledge, ask a question, or start a discussion..."
                                        className="w-full bg-muted rounded-lg px-4 py-2 h-32 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                                        maxLength={10000}
                                    />
                                </div>
                                <div className="flex justify-end gap-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowForm(false)}
                                        className="px-4 py-2 text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={submitting || !newTopic.title.trim() || !newTopic.content.trim()}
                                        className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all"
                                    >
                                        <Send className="h-4 w-4" />
                                        {submitting ? "Posting..." : "Post Topic"}
                                    </button>
                                </div>
                            </form>
                        </CardContent>
                    </Card>
                )}

                {/* Category Filter */}
                <div className="flex flex-wrap gap-2 mb-8">
                    <button
                        onClick={() => setSelectedCategory(null)}
                        className={`px-3 py-1 rounded-full text-sm transition-all ${
                            !selectedCategory
                                ? "bg-cyan-500 text-white"
                                : "bg-muted hover:bg-muted/80"
                        }`}
                    >
                        All
                    </button>
                    {CATEGORIES.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setSelectedCategory(cat)}
                            className={`px-3 py-1 rounded-full text-sm transition-all ${
                                selectedCategory === cat
                                    ? "bg-cyan-500 text-white"
                                    : "bg-muted hover:bg-muted/80"
                            }`}
                        >
                            {cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Topics List */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4" />
                        <p className="text-muted-foreground">Loading topics...</p>
                    </div>
                ) : topics.length === 0 ? (
                    <div className="text-center py-12">
                        <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <p className="text-muted-foreground">No topics yet. Be the first to start a discussion!</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {topics.map((topic) => (
                            <Link key={topic.id} href={`/blog/${topic.id}`}>
                                <Card className="hover:border-cyan-500/50 transition-all cursor-pointer group">
                                    <CardHeader>
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge variant="secondary" className="capitalize">
                                                {topic.category}
                                            </Badge>
                                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                                <Clock className="h-3 w-3" />
                                                {formatDate(topic.createdAt)}
                                            </div>
                                            {topic._count && topic._count.comments > 0 && (
                                                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                                    <MessageSquare className="h-3 w-3" />
                                                    {topic._count.comments}
                                                </div>
                                            )}
                                        </div>
                                        <CardTitle className="group-hover:text-cyan-400 transition-colors">
                                            {topic.title}
                                        </CardTitle>
                                        <CardDescription className="line-clamp-2">
                                            {topic.content}
                                        </CardDescription>
                                    </CardHeader>
                                </Card>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </main>
    )
}
