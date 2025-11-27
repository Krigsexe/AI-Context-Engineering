"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Clock, MessageSquare, Send, User } from "lucide-react"

interface Comment {
    id: string
    content: string
    createdAt: string
}

interface Topic {
    id: string
    title: string
    content: string
    category: string
    createdAt: string
    comments: Comment[]
}

export default function TopicPage() {
    const params = useParams()
    const [topic, setTopic] = useState<Topic | null>(null)
    const [loading, setLoading] = useState(true)
    const [comment, setComment] = useState("")
    const [submitting, setSubmitting] = useState(false)

    const fetchTopic = async () => {
        try {
            const res = await fetch(`/api/topics/${params.id}`)
            if (res.ok) {
                const data = await res.json()
                setTopic(data)
            }
        } catch (error) {
            console.error("Failed to fetch topic:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (params.id) {
            fetchTopic()
        }
    }, [params.id])

    const handleSubmitComment = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!comment.trim()) return

        setSubmitting(true)
        try {
            const res = await fetch(`/api/topics/${params.id}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: comment })
            })

            if (res.ok) {
                setComment("")
                fetchTopic()
            }
        } catch (error) {
            console.error("Failed to add comment:", error)
        } finally {
            setSubmitting(false)
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        })
    }

    if (loading) {
        return (
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <div className="text-center py-12">
                        <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4" />
                        <p className="text-muted-foreground">Loading topic...</p>
                    </div>
                </div>
            </main>
        )
    }

    if (!topic) {
        return (
            <main className="min-h-screen pt-24 pb-16">
                <div className="container mx-auto px-4 max-w-4xl">
                    <div className="text-center py-12">
                        <p className="text-muted-foreground mb-4">Topic not found</p>
                        <Link href="/blog" className="text-cyan-500 hover:underline">
                            Back to topics
                        </Link>
                    </div>
                </div>
            </main>
        )
    }

    return (
        <main className="min-h-screen pt-24 pb-16">
            <div className="container mx-auto px-4 max-w-4xl">
                {/* Back Link */}
                <Link
                    href="/blog"
                    className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back to topics
                </Link>

                {/* Topic */}
                <Card className="mb-8">
                    <CardHeader>
                        <div className="flex items-center gap-2 mb-4">
                            <Badge variant="secondary" className="capitalize">
                                {topic.category}
                            </Badge>
                            <div className="flex items-center gap-1 text-sm text-muted-foreground">
                                <Clock className="h-4 w-4" />
                                {formatDate(topic.createdAt)}
                            </div>
                        </div>
                        <CardTitle className="text-2xl">{topic.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="whitespace-pre-wrap text-foreground/90">{topic.content}</p>
                    </CardContent>
                </Card>

                {/* Comments Section */}
                <div className="space-y-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <MessageSquare className="h-5 w-5 text-cyan-500" />
                        Comments ({topic.comments.length})
                    </h2>

                    {/* Add Comment Form */}
                    <form onSubmit={handleSubmitComment} className="flex gap-2">
                        <input
                            type="text"
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                            placeholder="Add a comment..."
                            className="flex-1 bg-muted rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
                            maxLength={5000}
                        />
                        <button
                            type="submit"
                            disabled={submitting || !comment.trim()}
                            className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all"
                        >
                            <Send className="h-4 w-4" />
                        </button>
                    </form>

                    {/* Comments List */}
                    {topic.comments.length === 0 ? (
                        <p className="text-muted-foreground text-center py-8">
                            No comments yet. Be the first to share your thoughts!
                        </p>
                    ) : (
                        <div className="space-y-4">
                            {topic.comments.map((c) => (
                                <div key={c.id} className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                                        <User className="h-4 w-4 text-cyan-400" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="bg-muted rounded-lg px-4 py-3">
                                            <p className="whitespace-pre-wrap">{c.content}</p>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            {formatDate(c.createdAt)}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </main>
    )
}
