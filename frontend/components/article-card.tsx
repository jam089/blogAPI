import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { Calendar, User, TrendingUp } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Article } from "@/lib/types"

interface ArticleCardProps {
  article: Article
  showScore?: boolean
}

export function ArticleCard({ article, showScore = false }: ArticleCardProps) {
  return (
    <Link href={`/article/${article.id}`}>
      <Card className="group transition-all hover:border-primary/50 hover:shadow-lg">
        <CardHeader className="space-y-3">
          <div className="flex items-start justify-between gap-4">
            <h3 className="text-balance text-xl font-bold leading-tight group-hover:text-primary">{article.title}</h3>
            {showScore && (
              <Badge variant="secondary" className="flex items-center gap-1 whitespace-nowrap">
                <TrendingUp className="h-3 w-3" />
                {article.score}
              </Badge>
            )}
          </div>
          <Badge variant="outline" className="w-fit">
            {article.topic}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="line-clamp-3 text-pretty leading-relaxed text-muted-foreground">{article.text}</p>
          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <User className="h-4 w-4" />
              <span>{article.author_name}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="h-4 w-4" />
              <span>{formatDistanceToNow(new Date(article.created_at), { addSuffix: true })}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
