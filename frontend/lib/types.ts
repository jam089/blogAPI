export interface Article {
  title: string
  text: string
  topic: string
  author_name: string
  id: number
  created_at: string
  last_updated_at: string
  score: number
  comments?: Comment[]
}

export interface Comment {
  comment_text: string
  author_name: string
  score: number
  article_id: number
  id: number
  created_at: string
  last_updated_at: string
}

export interface SearchResponse {
  articles: Record<string, Article>
  search_response: Record<string, unknown>
}

export interface CreateArticleInput {
  title: string
  text: string
  topic: string
  author_name: string
}

export interface UpdateArticleInput {
  title?: string
  text?: string
  topic?: string
  author_name?: string
}

export interface CreateCommentInput {
  comment_text?: string
  author_name: string
  score: number
  article_id: number
}

export interface UpdateCommentInput {
  comment_text?: string
  author_name?: string
  score?: number
}
