"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { getArticle, deleteArticle } from "@/lib/api"
import type { Article } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Calendar, User, Edit2, Trash2, TrendingUp } from "lucide-react"
import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { CommentCard } from "@/components/comment-card"
import { CommentForm } from "@/components/comment-form"
import { Spinner } from "@/components/ui/spinner"

export default function ArticlePage() {
  const params = useParams()
  const router = useRouter()
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    loadArticle()
  }, [params.id])

  const loadArticle = async () => {
    try {
      setLoading(true)
      console.log("[v0] Loading article with ID:", params.id)
      const data = await getArticle(params.id as string)
      console.log("[v0] Article loaded successfully:", data)
      setArticle(data)
    } catch (err) {
      console.log("[v0] Error loading article:", err)
      setError(err instanceof Error ? err.message : "Failed to load article")
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this article?")) return

    try {
      setIsDeleting(true)
      await deleteArticle(params.id as string)
      router.push("/articles")
    } catch (error) {
      alert("Failed to delete article")
      setIsDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    )
  }

  if (error || !article) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
          <p className="text-destructive">{error || "Article not found"}</p>
          <Link href="/">
            <Button variant="outline" className="mt-4 bg-transparent">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <Link href="/">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </Link>

      <article className="space-y-8">
        <header className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-balance text-4xl font-bold leading-tight">{article.title}</h1>
            <Badge variant="secondary" className="flex items-center gap-1 whitespace-nowrap">
              <TrendingUp className="h-3 w-3" />
              {article.score}
            </Badge>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <Badge variant="outline">{article.topic}</Badge>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{article.author_name}</span>
            </div>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>{formatDistanceToNow(new Date(article.created_at), { addSuffix: true })}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href={`/article/${article.id}/edit`}>
              <Button variant="outline" className="gap-2 bg-transparent">
                <Edit2 className="h-4 w-4" />
                Edit
              </Button>
            </Link>
            <Button
              variant="outline"
              className="gap-2 text-destructive hover:bg-destructive/10 hover:text-destructive bg-transparent"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </div>
        </header>

        <div className="prose prose-lg max-w-none dark:prose-invert">
          <p className="text-pretty leading-relaxed">{article.text}</p>
        </div>

        <div className="border-t pt-8">
          <h2 className="mb-6 text-2xl font-bold">Comments {article.comments && `(${article.comments.length})`}</h2>

          <div className="space-y-6">
            <CommentForm articleId={article.id} onSuccess={loadArticle} />

            {article.comments && article.comments.length > 0 ? (
              <div className="space-y-4">
                {article.comments.map((comment) => (
                  <CommentCard key={comment.id} comment={comment} onDelete={loadArticle} />
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed p-8 text-center">
                <p className="text-muted-foreground">No comments yet. Be the first to comment!</p>
              </div>
            )}
          </div>
        </div>
      </article>
    </div>
  )
}
