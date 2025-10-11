"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { createComment } from "@/lib/api"
import { useRouter } from "next/navigation"

interface CommentFormProps {
  articleId: number
  onSuccess?: () => void
}

export function CommentForm({ articleId, onSuccess }: CommentFormProps) {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    comment_text: "",
    author_name: "",
    score: 5,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      setIsSubmitting(true)
      await createComment({
        ...formData,
        article_id: articleId,
      })
      setFormData({ comment_text: "", author_name: "", score: 5 })
      onSuccess?.()
      router.refresh()
    } catch (error) {
      alert("Failed to create comment")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add a Comment</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="author_name">Your Name</Label>
            <Input
              id="author_name"
              value={formData.author_name}
              onChange={(e) => setFormData({ ...formData, author_name: e.target.value })}
              required
              placeholder="Enter your name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="comment_text">Comment</Label>
            <Textarea
              id="comment_text"
              value={formData.comment_text}
              onChange={(e) => setFormData({ ...formData, comment_text: e.target.value })}
              placeholder="Share your thoughts..."
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="score">Score (1-10)</Label>
            <Input
              id="score"
              type="number"
              min="1"
              max="10"
              value={formData.score}
              onChange={(e) => setFormData({ ...formData, score: Number(e.target.value) })}
              required
            />
          </div>

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? "Posting..." : "Post Comment"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
