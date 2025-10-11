"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { getArticle, updateArticle } from "@/lib/api"
import type { Article, UpdateArticleInput } from "@/lib/types"
import { ArticleForm } from "@/components/article-form"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { Spinner } from "@/components/ui/spinner"

export default function EditArticlePage() {
  const params = useParams()
  const router = useRouter()
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadArticle() {
      try {
        setLoading(true)
        const data = await getArticle(params.id as string)
        setArticle(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load article")
      } finally {
        setLoading(false)
      }
    }

    loadArticle()
  }, [params.id])

  const handleSubmit = async (data: UpdateArticleInput) => {
    await updateArticle(params.id as string, data)
    router.push(`/article/${params.id}`)
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
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
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
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <Link href={`/article/${params.id}`}>
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Article
        </Button>
      </Link>

      <ArticleForm article={article} onSubmit={handleSubmit} submitLabel="Update Article" />
    </div>
  )
}
