import type {
  Article,
  Comment,
  SearchResponse,
  CreateArticleInput,
  UpdateArticleInput,
  CreateCommentInput,
  UpdateCommentInput,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Article endpoints
export async function getTrendingArticles(): Promise<Article[]> {
  const response = await fetch(`${API_BASE_URL}/api/article/trends/`)
  if (!response.ok) throw new Error("Failed to fetch trending articles")
  return response.json()
}

export async function searchArticles(query: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/article/search/?query=${encodeURIComponent(query)}`)
  if (!response.ok) throw new Error("Failed to search articles")
  return response.json()
}

export async function getArticle(articleId: string): Promise<Article> {
  const response = await fetch(`${API_BASE_URL}/api/article/${articleId}/`)
  if (!response.ok) throw new Error("Failed to fetch article")
  return response.json()
}

export async function getAllArticles(): Promise<Article[]> {
  const response = await fetch(`${API_BASE_URL}/api/article/`)
  if (!response.ok) throw new Error("Failed to fetch articles")
  return response.json()
}

export async function createArticle(data: CreateArticleInput): Promise<Article> {
  const response = await fetch(`${API_BASE_URL}/api/article/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error("Failed to create article")
  return response.json()
}

export async function updateArticle(articleId: string, data: UpdateArticleInput): Promise<Article> {
  const response = await fetch(`${API_BASE_URL}/api/article/${articleId}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error("Failed to update article")
  return response.json()
}

export async function deleteArticle(articleId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/article/${articleId}/`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error("Failed to delete article")
}

// Comment endpoints
export async function getArticleComments(articleId: string): Promise<Comment[]> {
  const response = await fetch(`${API_BASE_URL}/api/comment/article/${articleId}/`)
  if (!response.ok) throw new Error("Failed to fetch comments")
  return response.json()
}

export async function getComment(commentId: string): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/api/comment/${commentId}/`)
  if (!response.ok) throw new Error("Failed to fetch comment")
  return response.json()
}

export async function createComment(data: CreateCommentInput): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/api/comment/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error("Failed to create comment")
  return response.json()
}

export async function updateComment(commentId: string, data: UpdateCommentInput): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/api/comment/${commentId}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error("Failed to update comment")
  return response.json()
}

export async function deleteComment(commentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/comment/${commentId}/`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error("Failed to delete comment")
}

// Admin endpoints
export async function importData(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/admin/import-data/`)
  if (response.status !== 201) throw new Error("Failed to import data")
}

export async function indexArticles(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/admin/es_index_articles/`)
  if (!response.ok) throw new Error("Failed to index articles")
}

export async function pingServer(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/admin/ping/`)
  if (!response.ok) throw new Error("Failed to ping server")
  return response.json()
}
