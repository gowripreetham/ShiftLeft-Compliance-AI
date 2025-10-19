'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TrendData } from '@/lib/types'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Trends() {
  const [riskFilter, setRiskFilter] = useState<string>('all')

  const { data, error, isLoading } = useSWR(
    `/api/trends${riskFilter !== 'all' ? `?risk_level=${riskFilter}` : ''}`,
    fetcher,
    {
      refreshInterval: 10000,
    }
  )

  const trends: TrendData[] = data || []

  const chartData = trends.map((trend) => ({
    date: new Date(trend.day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    count: trend.count,
  }))

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading trends...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading trends</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Risk Analytics</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Track findings over time</p>
      </div>

      {/* Filter */}
      <div className="command-card mb-4">
        <div className="max-w-xs">
            <Select value={riskFilter} onValueChange={setRiskFilter}>
              <SelectTrigger className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]">
                <SelectValue placeholder="Filter by risk level" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
                <SelectItem value="all" className="text-black dark:text-white">All Risk Levels</SelectItem>
                <SelectItem value="high" className="text-black dark:text-white">High Risk</SelectItem>
                <SelectItem value="medium" className="text-black dark:text-white">Medium Risk</SelectItem>
                <SelectItem value="low" className="text-black dark:text-white">Low Risk</SelectItem>
              </SelectContent>
            </Select>
          </div>
      </div>

      {/* Chart */}
      <div className="command-card mb-4">
        <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
          <h2 className="text-sm font-semibold text-black dark:text-white">
            Findings Over Time
            {riskFilter !== 'all' && ` (${riskFilter.toUpperCase()} Risk)`}
          </h2>
        </div>
        <div className="pt-4">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EEEEEE" />
                <XAxis dataKey="date" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #DDDDDD',
                    borderRadius: '0',
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#0693E3" 
                  strokeWidth={2}
                  dot={{ fill: '#0693E3' }}
                  name="Findings"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-black/40 text-xs">
              No trend data available
            </div>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Total Findings</p>
              <p className="text-2xl font-semibold text-black dark:text-white">
                {trends.reduce((sum, trend) => sum + trend.count, 0)}
              </p>
            </div>
            <TrendingUp className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Average per Day</p>
              <p className="text-2xl font-semibold text-black dark:text-white">
                {trends.length > 0 
                  ? Math.round(trends.reduce((sum, trend) => sum + trend.count, 0) / trends.length)
                  : 0}
              </p>
            </div>
            <TrendingUp className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Peak Day</p>
              <p className="text-2xl font-semibold text-black dark:text-white">
                {trends.length > 0 
                  ? Math.max(...trends.map(t => t.count))
                  : 0}
              </p>
            </div>
            <TrendingUp className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>
      </div>
    </div>
  )
}

