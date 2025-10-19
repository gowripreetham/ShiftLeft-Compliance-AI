'use client'

import { useState, useMemo } from 'react'
import useSWR from 'swr'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Policy, PolicyStats } from '@/lib/types'
import { CheckCircle, XCircle, Shield, TrendingUp } from 'lucide-react'
import Link from 'next/link'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function CompliancePosture() {
  const [frameworkFilter, setFrameworkFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data: policies, error: policiesError, isLoading: policiesLoading } = useSWR('/api/policies', fetcher, {
    refreshInterval: 10000,
  })

  const policyList: Policy[] = policies || []

  const filteredPolicies = useMemo(() => {
    return policyList.filter((policy) => {
      const matchesFramework = frameworkFilter === 'all' || policy.framework === frameworkFilter
      const matchesStatus = statusFilter === 'all' || policy.status === statusFilter
      return matchesFramework && matchesStatus
    })
  }, [policyList, frameworkFilter, statusFilter])

  // Calculate stats from filtered policies
  const policyStats = useMemo(() => {
    const totalCount = filteredPolicies.length
    const passingCount = filteredPolicies.filter(p => p.status === 'passing').length
    const failingCount = filteredPolicies.filter(p => p.status === 'failing').length
    const complianceScore = totalCount > 0 
      ? ((passingCount / totalCount) * 100).toFixed(1)
      : '0.0'

    return {
      totalCount,
      passingCount,
      failingCount,
      complianceScore: parseFloat(complianceScore),
    }
  }, [filteredPolicies])

  const frameworks = useMemo(() => {
    const unique = new Set(policyList.map(p => p.framework))
    return Array.from(unique).sort()
  }, [policyList])

  if (policiesLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading compliance posture...</div>
        </div>
      </div>
    )
  }

  if (policiesError) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading compliance data</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Controls Library</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Monitor your compliance controls and framework adherence</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Total Controls</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{policyStats.totalCount}</p>
            </div>
            <Shield className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Passing Controls</p>
              <p className="text-2xl font-semibold text-green-600">{policyStats.passingCount}</p>
            </div>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Failing Controls</p>
              <p className="text-2xl font-semibold text-red-600">{policyStats.failingCount}</p>
            </div>
            <XCircle className="h-5 w-5 text-red-600" />
          </div>
        </div>

        <div className="command-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-black/60 dark:text-white/60 mb-1">Compliance Score</p>
              <p className="text-2xl font-semibold text-black dark:text-white">{policyStats.complianceScore}%</p>
            </div>
            <TrendingUp className="h-5 w-5 text-black/40 dark:text-white/40" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="command-card mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Select value={frameworkFilter} onValueChange={setFrameworkFilter}>
              <SelectTrigger className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]">
                <SelectValue placeholder="Filter by framework" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
                <SelectItem value="all" className="text-black dark:text-white">All Frameworks</SelectItem>
                {frameworks.map((framework) => (
                  <SelectItem key={framework} value={framework} className="text-black dark:text-white">
                    {framework}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
                <SelectItem value="all" className="text-black dark:text-white">All Status</SelectItem>
                <SelectItem value="passing" className="text-black dark:text-white">Passing</SelectItem>
                <SelectItem value="failing" className="text-black dark:text-white">Failing</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Policies Table */}
      <div className="command-card">
        <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
          <h2 className="text-sm font-semibold text-black dark:text-white">
            Compliance Controls ({filteredPolicies.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#DDDDDD] dark:border-[#333333]">
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Status</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Control ID</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Framework</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Title</th>
              </tr>
            </thead>
            <tbody>
              {filteredPolicies.map((policy) => (
                <tr key={policy.id} className="border-b border-[#DDDDDD] dark:border-[#333333] hover:bg-[#F6F6F6] dark:hover:bg-[#1A1A1A]">
                  <td className="py-2 px-3">
                    <span className={`command-badge ${
                      policy.status === 'passing' 
                        ? 'text-green-600 border-green-600' 
                        : 'text-red-600 border-red-600'
                    }`}>
                      {policy.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    <Link 
                      href={`/posture?control=${policy.control_id}`}
                      className="text-[#0693E3] hover:underline font-mono text-xs"
                    >
                      {policy.control_id}
                    </Link>
                  </td>
                  <td className="py-2 px-3 text-xs text-black/80 dark:text-white/80">{policy.framework}</td>
                  <td className="py-2 px-3 text-xs text-black dark:text-white">{policy.title}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredPolicies.length === 0 && (
            <div className="text-center py-12 text-black/40 dark:text-white/40 text-xs">
              No controls found matching your filters
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

