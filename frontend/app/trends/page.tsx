'use client'

import useSWR from 'swr'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { AlertTriangle, CheckCircle, Code, Camera, Target } from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Trends() {
  const { data, error, isLoading } = useSWR('/api/analytics', fetcher, {
    refreshInterval: 10000,
  })

  if (isLoading) {
    return (
      <div className="p-6 bg-white dark:bg-black">
        <div className="flex items-center justify-center h-64">
          <div className="text-black/60 dark:text-white/60">Loading analytics...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 bg-white dark:bg-black">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading analytics</div>
        </div>
      </div>
    )
  }

  const { riskDistribution, sourceDistribution, topControls, resolutionRate, totalFindings, resolvedFindings } = data || {}

  // Risk distribution colors
  const RISK_COLORS = {
    high: '#EF4444',
    medium: '#F59E0B',
    low: '#10B981',
  }

  // Source colors
  const SOURCE_COLORS = {
    code: '#0693E3',
    screenshot: '#8B5CF6',
  }

  const riskChartData = riskDistribution?.map((item: any) => ({
    name: item.risk_level.toUpperCase(),
    value: item.count,
    color: RISK_COLORS[item.risk_level as keyof typeof RISK_COLORS] || '#666',
  })) || []

  const sourceChartData = sourceDistribution?.map((item: any) => ({
    name: item.source === 'code' ? 'Code Analysis' : 'Screenshot',
    value: item.count,
    color: SOURCE_COLORS[item.source as keyof typeof SOURCE_COLORS] || '#666',
  })) || []

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Analytics</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Comprehensive compliance insights and metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Total Findings</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{totalFindings || 0}</p>
            </div>
            <AlertTriangle className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Resolved</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{resolvedFindings || 0}</p>
            </div>
            <CheckCircle className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Resolution Rate</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{resolutionRate || 0}%</p>
            </div>
            <Target className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Risk Distribution */}
        <div className="command-card">
          <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
            <h2 className="text-sm font-semibold text-black dark:text-white">Risk Distribution</h2>
          </div>
          <div className="pt-4">
            {riskChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={riskChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #DDDDDD',
                      borderRadius: '0',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-black/40 dark:text-white/40 text-xs">
                No risk data available
              </div>
            )}
          </div>
        </div>

        {/* Findings by Source */}
        <div className="command-card">
          <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
            <h2 className="text-sm font-semibold text-black dark:text-white">Findings by Source</h2>
          </div>
          <div className="pt-4">
            {sourceChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sourceChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#EEEEEE" />
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #DDDDDD',
                      borderRadius: '0',
                    }}
                  />
                  <Bar dataKey="value" fill="#0693E3" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-black/40 dark:text-white/40 text-xs">
                No source data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Violating Controls */}
      <div className="command-card">
        <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
          <h2 className="text-sm font-semibold text-black dark:text-white">Top Violating Controls</h2>
        </div>
        <div className="pt-4">
          {topControls && topControls.length > 0 ? (
            <div className="space-y-3">
              {topControls.slice(0, 5).map((control: any, index: number) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-[#EEEEEE] dark:border-[#333333] last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      control.risk_level === 'high' ? 'bg-red-500' :
                      control.risk_level === 'medium' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`} />
                    <span className="text-sm font-medium text-black dark:text-white">{control.control_id}</span>
                  </div>
                  <span className="text-sm text-black/60 dark:text-white/60">{control.count} findings</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-black/40 dark:text-white/40 text-xs">
              No control violations found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

