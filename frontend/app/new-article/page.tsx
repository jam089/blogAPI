"use client"

import { useRouter } from "next/navigation"
import { createArticle } from "@/lib/api"
import type { CreateArticleInput } from "@/lib/types"
import { ArticleForm } from "@/components/article-form"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function NewArticlePage() {
  const router = useRouter()

  const handleSubmit = async (data: CreateArticleInput) => {
    const article = await createArticle(data)
    router.push(`/article/${article.id}`)
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <Link href="/">
        <Button variant="ghost" className="mb-6 gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </Link>

      <ArticleForm onSubmit={handleSubmit} submitLabel="Create Article" />
    </div>
  )
}
