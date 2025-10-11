"use client"

import { useState } from "react"
import { importData, indexArticles, pingServer } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, Search, Activity, CheckCircle2, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default function AdminPage() {
  const [importLoading, setImportLoading] = useState(false)
  const [importStatus, setImportStatus] = useState<"idle" | "success" | "error">("idle")

  const [indexLoading, setIndexLoading] = useState(false)
  const [indexStatus, setIndexStatus] = useState<"idle" | "success" | "error">("idle")

  const [pingLoading, setPingLoading] = useState(false)
  const [pingStatus, setPingStatus] = useState<"idle" | "success" | "error">("idle")
  const [pingMessage, setPingMessage] = useState<string>("")

  const handleImportData = async () => {
    try {
      setImportLoading(true)
      setImportStatus("idle")
      await importData()
      setImportStatus("success")
    } catch (error) {
      setImportStatus("error")
      alert("Failed to import data")
    } finally {
      setImportLoading(false)
    }
  }

  const handleIndexArticles = async () => {
    try {
      setIndexLoading(true)
      setIndexStatus("idle")
      await indexArticles()
      setIndexStatus("success")
    } catch (error) {
      setIndexStatus("error")
      alert("Failed to index articles")
    } finally {
      setIndexLoading(false)
    }
  }

  const handlePing = async () => {
    try {
      setPingLoading(true)
      setPingStatus("idle")
      setPingMessage("")
      const response = await pingServer()
      setPingStatus("success")
      setPingMessage(response.status)
    } catch (error) {
      setPingStatus("error")
      setPingMessage("")
    } finally {
      setPingLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-balance text-4xl font-bold">Admin Panel</h1>
          <p className="mt-2 text-pretty leading-relaxed text-muted-foreground">
            Manage data import, indexing, and system health
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handlePing}
          disabled={pingLoading}
          className="gap-2 bg-transparent"
        >
          <Activity className="h-4 w-4" />
          {pingLoading ? "Pinging..." : "Ping"}
        </Button>
      </div>

      {pingMessage && pingStatus === "success" && (
        <div className="mb-6 rounded-lg border border-primary/50 bg-primary/10 p-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            <span className="font-medium">Server Status: {pingMessage}</span>
          </div>
        </div>
      )}

      {pingStatus === "error" && (
        <div className="mb-6 rounded-lg border border-destructive bg-destructive/10 p-4">
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-destructive" />
            <span className="font-medium text-destructive">Server is not responding</span>
          </div>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Database className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle>Import Data</CardTitle>
                <CardDescription>Load initial data into the database</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted-foreground">
              This will import sample articles and comments into your database. Use this to populate your blog with
              initial content.
            </p>
            <div className="flex items-center gap-3">
              <Button onClick={handleImportData} disabled={importLoading} className="gap-2">
                <Database className="h-4 w-4" />
                {importLoading ? "Importing..." : "Import Data"}
              </Button>
              {importStatus === "success" && (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Success
                </Badge>
              )}
              {importStatus === "error" && (
                <Badge variant="destructive" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Failed
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Search className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle>Index Articles</CardTitle>
                <CardDescription>Update Elasticsearch index</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted-foreground">
              This will index all articles in Elasticsearch for full-text search. Run this after importing data or when
              search results seem outdated.
            </p>
            <div className="flex items-center gap-3">
              <Button onClick={handleIndexArticles} disabled={indexLoading} className="gap-2">
                <Search className="h-4 w-4" />
                {indexLoading ? "Indexing..." : "Index Articles"}
              </Button>
              {indexStatus === "success" && (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Success
                </Badge>
              )}
              {indexStatus === "error" && (
                <Badge variant="destructive" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Failed
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>System Information</CardTitle>
          <CardDescription>Current system status and configuration</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between rounded-lg border p-3">
              <span className="text-muted-foreground">API Base URL</span>
              <code className="rounded bg-muted px-2 py-1 font-mono text-xs">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </code>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <span className="text-muted-foreground">Server Status</span>
              <Badge
                variant={pingStatus === "success" ? "default" : pingStatus === "error" ? "destructive" : "secondary"}
              >
                {pingStatus === "success" ? "Online" : pingStatus === "error" ? "Offline" : "Unknown"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
