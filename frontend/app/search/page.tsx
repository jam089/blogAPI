"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { searchArticles } from "@/lib/api"
import type { Article } from "@/lib/types"
import { ArticleCard } from "@/components/article-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Plus } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"

export default function SearchPage() {
  const [query, setQuery] = useState("")
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      setLoading(true)
      setError(null)
      setHasSearched(true)
      const data = await searchArticles(query)
      // Convert the articles object to an array
      const articlesArray = Object.values(data.articles)
      setArticles(articlesArray)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to search articles")
      setArticles([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="mb-2 text-balance text-4xl font-bold">Search Articles</h1>
          <p className="text-pretty leading-relaxed text-muted-foreground">
            Find articles using full-text search powered by Elasticsearch
          </p>
        </div>
        <Link href="/new-article">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Article
          </Button>
        </Link>
      </div>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search for articles..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button type="submit" disabled={loading || !query.trim()} size="lg">
            {loading ? "Searching..." : "Search"}
          </Button>
        </div>
      </form>

      {loading && (
        <div className="flex min-h-[40vh] items-center justify-center">
          <Spinner className="h-8 w-8" />
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
          <p className="text-destructive">{error}</p>
        </div>
      )}

      {!loading && !error && hasSearched && (
        <>
          {articles.length === 0 ? (
            <div className="rounded-lg border border-dashed p-12 text-center">
              <p className="text-muted-foreground">No articles found for "{query}"</p>
            </div>
          ) : (
            <>
              <div className="mb-4 text-sm text-muted-foreground">
                Found {articles.length} {articles.length === 1 ? "article" : "articles"}
              </div>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {articles.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            </>
          )}
        </>
      )}

      {!hasSearched && !loading && (
        <div className="rounded-lg border border-dashed p-12 text-center">
          <Search className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
          <p className="text-muted-foreground">Enter a search query to find articles</p>
        </div>
      )}
    </div>
  )
}
