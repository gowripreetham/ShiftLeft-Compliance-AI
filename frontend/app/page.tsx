'use client'

import { useEffect, useState } from 'react'
import useSWR from 'swr'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, CheckCircle, XCircle, TrendingUp, Shield, Inbox } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { DashboardStats, FindingStats } from '@/lib/types'
import { useToast } from '@/components/ui/use-toast'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Dashboard() {
  const { toast } = useToast()
  const [lastHighRiskCount, setLastHighRiskCount] = useState(0)

  const { data, error, isLoading } = useSWR('/api/findings/stats', fetcher, {
    refreshInterval: 10000, // Poll every 10 seconds
  })

  const { data: myFindingsData } = useSWR('/api/queues/my-findings', fetcher, {
    refreshInterval: 10000,
  })

  const { data: triageData } = useSWR('/api/queues/triage', fetcher, {
    refreshInterval: 10000,
  })

  useEffect(() => {
    if (data?.stats) {
      const currentHighRisk = data.stats.highRisk
      
      // Check for new high-risk findings
      if (lastHighRiskCount > 0 && currentHighRisk > lastHighRiskCount) {
        toast({
          title: '🚨 New High-Risk Finding',
          description: 'A new high-risk security issue has been detected!',
          variant: 'destructive',
        })
      }
      
      setLastHighRiskCount(currentHighRisk)
    }
  }, [data, lastHighRiskCount, toast])

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading dashboard...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading dashboard data</div>
        </div>
      </div>
    )
  }

  const stats: DashboardStats = data?.stats || {
    openFindings: 0,
    resolvedFindings: 0,
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0,
  }

  const riskStats: FindingStats[] = data?.riskStats || []

  const chartData = riskStats.map((stat) => ({
    name: stat.risk_level.charAt(0).toUpperCase() + stat.risk_level.slice(1),
    value: stat.count,
  }))

  const COLORS = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981',
  }

  const totalFindings = stats.openFindings + stats.resolvedFindings

  const myFindings = myFindingsData?.findings || []
  const triageFindings = triageData?.findings || []

  const getRiskBadgeClass = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-300 dark:border-red-700'
      case 'medium':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700'
      case 'low':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-300 dark:border-green-700'
      default:
        return 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-400 border-gray-300 dark:border-gray-700'
    }
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Posture Overview</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Real-time security compliance monitoring</p>
      </div>

      {/* Compact Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Open Findings</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.openFindings}</p>
            </div>
            <AlertTriangle className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Failing Controls</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.highRisk}</p>
            </div>
            <XCircle className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Findings Today</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.openFindings + stats.resolvedFindings}</p>
            </div>
            <TrendingUp className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>
      </div>

      {/* Risk Distribution - Compact Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">High Risk</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.highRisk}</p>
              <p className="text-xs text-black/40 dark:text-white/40 mt-1">
                {totalFindings > 0 ? Math.round((stats.highRisk / totalFindings) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-2 h-2 bg-red-500"></div>
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Medium Risk</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.mediumRisk}</p>
              <p className="text-xs text-black/40 dark:text-white/40 mt-1">
                {totalFindings > 0 ? Math.round((stats.mediumRisk / totalFindings) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-2 h-2 bg-yellow-500"></div>
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Low Risk</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{stats.lowRisk}</p>
              <p className="text-xs text-black/40 dark:text-white/40 mt-1">
                {totalFindings > 0 ? Math.round((stats.lowRisk / totalFindings) * 100) : 0}% of total
              </p>
            </div>
            <div className="w-2 h-2 bg-green-500"></div>
          </div>
        </div>
      </div>

      {/* Action Queue */}
      <div>
          <div className="command-card">
            <div className="flex items-center space-x-2 mb-4">
              <Inbox className="h-4 w-4 text-black dark:text-white" />
              <h3 className="text-sm font-semibold text-black dark:text-white">Action Queue</h3>
            </div>

            {/* My Open Findings */}
            <div className="mb-4">
              <h4 className="text-xs font-medium text-black/60 dark:text-white/60 mb-2 uppercase tracking-wider">
                My Open Findings
              </h4>
              <div className="space-y-2">
                {myFindings.length > 0 ? (
                  myFindings.map((finding: any) => (
                    <div
                      key={finding.id}
                      className="text-xs text-black dark:text-white flex items-start space-x-2"
                    >
                      <Badge className={`command-badge ${getRiskBadgeClass(finding.risk_level)}`}>
                        {finding.risk_level?.toUpperCase().charAt(0)}
                      </Badge>
                      <span className="flex-1 line-clamp-2">{finding.summary}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-black/40 dark:text-white/40 italic">No assigned findings</p>
                )}
              </div>
            </div>

            <Separator className="my-4 bg-[#DDDDDD] dark:bg-[#333333]" />

            {/* Awaiting Triage */}
            <div>
              <h4 className="text-xs font-medium text-black/60 dark:text-white/60 mb-2 uppercase tracking-wider">
                Awaiting Triage
              </h4>
              <div className="space-y-2">
                {triageFindings.length > 0 ? (
                  triageFindings.map((finding: any) => (
                    <div
                      key={finding.id}
                      className="text-xs text-black dark:text-white flex items-start space-x-2"
                    >
                      <Badge className={`command-badge ${getRiskBadgeClass(finding.risk_level)}`}>
                        {finding.risk_level?.toUpperCase().charAt(0)}
                      </Badge>
                      <span className="flex-1 line-clamp-2">{finding.summary}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-black/40 dark:text-white/40 italic">No findings awaiting triage</p>
                )}
              </div>
            </div>
          </div>
        </div>
    </div>
  )
}

