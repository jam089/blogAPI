"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getTrendingArticles } from "@/lib/api"
import type { Article } from "@/lib/types"
import { ArticleCard } from "@/components/article-card"
import { TrendingUp, Plus } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import { Button } from "@/components/ui/button"

export default function HomePage() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadTrendingArticles() {
      try {
        setLoading(true)
        const data = await getTrendingArticles()
        setArticles(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load articles")
      } finally {
        setLoading(false)
      }
    }

    loadTrendingArticles()
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
          <p className="text-destructive">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-3 text-balance text-4xl font-bold">
            <TrendingUp className="h-8 w-8" />
            Trending Articles
          </h1>
          <p className="mt-2 text-pretty leading-relaxed text-muted-foreground">
            Discover the most popular articles right now
          </p>
        </div>
        <Link href="/new-article">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Article
          </Button>
        </Link>
      </div>

      {articles.length === 0 ? (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <p className="text-muted-foreground">No trending articles found</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} showScore />
          ))}
        </div>
      )}
    </div>
  )
}
