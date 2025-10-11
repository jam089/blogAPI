"use client"

import { useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { Calendar, User, Trash2, Edit2, TrendingUp, X, Check } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { Comment } from "@/lib/types"
import { deleteComment, updateComment } from "@/lib/api"
import { useRouter } from "next/navigation"

interface CommentCardProps {
  comment: Comment
  onDelete?: () => void
}

export function CommentCard({ comment, onDelete }: CommentCardProps) {
  const router = useRouter()
  const [isDeleting, setIsDeleting] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [editData, setEditData] = useState({
    comment_text: comment.comment_text,
    author_name: comment.author_name,
    score: comment.score,
  })

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this comment?")) return

    try {
      setIsDeleting(true)
      await deleteComment(String(comment.id))
      onDelete?.()
      router.refresh()
    } catch (error) {
      alert("Failed to delete comment")
    } finally {
      setIsDeleting(false)
    }
  }

  const handleUpdate = async () => {
    try {
      setIsUpdating(true)
      await updateComment(String(comment.id), editData)
      setIsEditing(false)
      onDelete?.() // Refresh the comments list
      router.refresh()
    } catch (error) {
      alert("Failed to update comment")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleCancel = () => {
    setEditData({
      comment_text: comment.comment_text,
      author_name: comment.author_name,
      score: comment.score,
    })
    setIsEditing(false)
  }

  if (isEditing) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Edit Comment</h3>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={handleCancel} disabled={isUpdating}>
                <X className="h-4 w-4" />
              </Button>
              <Button size="sm" onClick={handleUpdate} disabled={isUpdating} className="gap-2">
                <Check className="h-4 w-4" />
                Save
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="comment_text">Comment</Label>
            <Textarea
              id="comment_text"
              value={editData.comment_text}
              onChange={(e) => setEditData({ ...editData, comment_text: e.target.value })}
              rows={3}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="author_name">Author</Label>
              <Input
                id="author_name"
                value={editData.author_name}
                onChange={(e) => setEditData({ ...editData, author_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="score">Score</Label>
              <Input
                id="score"
                type="number"
                min="1"
                max="10"
                value={editData.score}
                onChange={(e) => setEditData({ ...editData, score: Number(e.target.value) })}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <User className="h-4 w-4" />
              <span className="font-medium">{comment.author_name}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="h-4 w-4" />
              <span>{formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}</span>
            </div>
            <Badge variant="secondary" className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              {comment.score}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsEditing(true)}>
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-pretty leading-relaxed">{comment.comment_text}</p>
      </CardContent>
    </Card>
  )
}
