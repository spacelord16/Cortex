"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Activity, Cpu, HardDrive, Zap } from "lucide-react"

interface SystemStatsData {
  cpu_percent: number
  memory_percent: number
  memory_used_gb: number
  disk_percent: number
  disk_free_gb: number
  battery_percent?: number
  battery_plugged?: boolean
  timestamp: string
}

export function SystemStats() {
  const [stats, setStats] = useState<SystemStatsData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchStats = async () => {
    try {
      const res = await fetch("http://localhost:8000/stats")
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (error) {
      console.error("Failed to fetch stats", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="text-sm text-muted-foreground p-4">Loading system stats...</div>
  if (!stats) return <div className="text-sm text-red-500 p-4">System offline</div>

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
          <Cpu className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.cpu_percent}%</div>
          <p className="text-xs text-muted-foreground">
            {stats.cpu_percent > 80 ? "High Load" : "Normal"}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Memory</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.memory_percent}%</div>
          <p className="text-xs text-muted-foreground">
            {stats.memory_used_gb} GB Used
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Disk</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.disk_percent}%</div>
          <p className="text-xs text-muted-foreground">
            {stats.disk_free_gb} GB Free
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Battery</CardTitle>
          <Zap className={`h-4 w-4 ${stats.battery_plugged ? "text-yellow-500" : "text-muted-foreground"}`} />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.battery_percent ?? "N/A"}%</div>
          <p className="text-xs text-muted-foreground">
            {stats.battery_plugged ? "Charging" : "On Battery"}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
