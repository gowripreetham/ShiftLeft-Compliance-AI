'use client'

import { useState, useMemo } from 'react'
import useSWR from 'swr'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { AuditLog, RiskLevel } from '@/lib/types'
import { formatDate } from '@/lib/utils'
import { ExternalLink, CheckCircle, Wand2, Copy, Loader2 } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Findings() {
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [riskFilter, setRiskFilter] = useState<string>('all')
  const [resolvedFilter, setResolvedFilter] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<string>('all')
  const [fixModalOpen, setFixModalOpen] = useState(false)
  const [fixData, setFixData] = useState<{
    finding: AuditLog | null
    explanation: string
    originalCode: string
    fixedCode: string
  } | null>(null)
  const [loadingFix, setLoadingFix] = useState(false)

  const { data, error, isLoading, mutate } = useSWR('/api/findings', fetcher, {
    refreshInterval: 10000,
  })

  const handleResolve = async (jiraKey: string) => {
    try {
      const response = await fetch(`/api/findings/resolve/${jiraKey}`, {
        method: 'POST',
      })

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Finding marked as resolved',
        })
        mutate() // Refresh the data
      } else {
        throw new Error('Failed to resolve finding')
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to mark finding as resolved',
        variant: 'destructive',
      })
    }
  }

  const handleSuggestFix = async (finding: AuditLog) => {
    setLoadingFix(true)
    setFixModalOpen(true)
    setFixData({
      finding,
      explanation: '',
      originalCode: '',
      fixedCode: '',
    })

    try {
      const response = await fetch(`/api/findings/${finding.id}/suggest-fix`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        setFixData({
          finding,
          explanation: data.explanation || '',
          originalCode: data.original_code || '',
          fixedCode: data.fixed_code || '',
        })
      } else {
        throw new Error('Failed to generate fix')
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate AI fix suggestion',
        variant: 'destructive',
      })
      setFixModalOpen(false)
    } finally {
      setLoadingFix(false)
    }
  }

  const handleCopyFix = () => {
    if (fixData?.fixedCode) {
      navigator.clipboard.writeText(fixData.fixedCode)
      toast({
        title: 'Copied',
        description: 'Fixed code copied to clipboard',
      })
    }
  }

  const findings: AuditLog[] = data || []

  const filteredFindings = useMemo(() => {
    return findings.filter((finding) => {
      const matchesSearch = finding.summary.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesRisk = riskFilter === 'all' || finding.risk_level === riskFilter
      const matchesResolved = resolvedFilter === 'all' || 
        (resolvedFilter === 'open' && finding.resolved === 0) ||
        (resolvedFilter === 'resolved' && finding.resolved === 1)
      const matchesSource = sourceFilter === 'all' || finding.source === sourceFilter

      return matchesSearch && matchesRisk && matchesResolved && matchesSource
    })
  }, [findings, searchTerm, riskFilter, resolvedFilter, sourceFilter])

  const getRiskBadgeClass = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case 'high':
        return 'bg-red-100 text-red-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading findings...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading findings</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Findings Inbox</h1>
        <p className="text-sm text-black/60 dark:text-white/60">View and manage all security findings</p>
      </div>

      {/* Filters */}
      <div className="command-card mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Input
              placeholder="Search findings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333] placeholder:text-black/40 dark:placeholder:text-white/40"
            />
          </div>
          
          <div>
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

          <div>
            <Select value={resolvedFilter} onValueChange={setResolvedFilter}>
              <SelectTrigger className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
                <SelectItem value="all" className="text-black dark:text-white">All Status</SelectItem>
                <SelectItem value="open" className="text-black dark:text-white">Open</SelectItem>
                <SelectItem value="resolved" className="text-black dark:text-white">Resolved</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]">
                <SelectValue placeholder="Filter by source" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
                <SelectItem value="all" className="text-black dark:text-white">All Sources</SelectItem>
                <SelectItem value="code" className="text-black dark:text-white">Code</SelectItem>
                <SelectItem value="screenshot" className="text-black dark:text-white">Screenshot</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="command-card">
        <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
          <h2 className="text-sm font-semibold text-black dark:text-white">
            Findings ({filteredFindings.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#DDDDDD] dark:border-[#333333]">
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Timestamp</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Summary</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Risk</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Source</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Control ID</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Jira</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">GitHub</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Status</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-black dark:text-white">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredFindings.map((finding) => (
                <tr key={finding.id} className="border-b border-[#DDDDDD] dark:border-[#333333] hover:bg-[#F6F6F6] dark:hover:bg-[#1A1A1A]">
                  <td className="py-2 px-3 text-xs text-black/80 dark:text-white/80">
                    {formatDate(finding.timestamp)}
                  </td>
                  <td className="py-2 px-3 text-xs text-black dark:text-white max-w-md">
                    {finding.summary}
                  </td>
                  <td className="py-2 px-3">
                    <span className={`command-badge ${
                      finding.risk_level === 'high' ? 'text-red-600 border-red-600' :
                      finding.risk_level === 'medium' ? 'text-yellow-600 border-yellow-600' :
                      'text-green-600 border-green-600'
                    }`}>
                      {finding.risk_level.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    <span className="text-xs text-black/60 dark:text-white/60">
                      {finding.source === 'screenshot' ? 'Screenshot' : 'Code'}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    {finding.control_id ? (
                      <Link 
                        href={`/posture?control=${finding.control_id}`}
                        className="text-[#0693E3] hover:underline font-mono text-xs"
                      >
                        {finding.control_id}
                      </Link>
                    ) : (
                      <span className="text-black/30 dark:text-white/30">-</span>
                    )}
                  </td>
                  <td className="py-2 px-3">
                    {finding.jira_key ? (
                      <a
                        href={finding.jira_key}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#0693E3] hover:underline flex items-center space-x-1 text-xs"
                      >
                        <span>{finding.jira_key}</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    ) : (
                      <span className="text-black/30 dark:text-white/30">-</span>
                    )}
                  </td>
                  <td className="py-2 px-3">
                    {finding.github_link ? (
                      <a
                        href={finding.github_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#0693E3] hover:underline flex items-center space-x-1 text-xs"
                      >
                        <span>View</span>
                        <ExternalLink className="h-3 w-3" />
                      </a>
                      ) : (
                        <span className="text-black/30 dark:text-white/30">-</span>
                      )}
                    </td>
                    <td className="py-2 px-3">
                      {finding.resolved === 1 ? (
                        <span className="command-badge text-green-600 border-green-600">
                          Resolved
                        </span>
                      ) : (
                        <span className="command-badge text-black dark:text-white border-black dark:border-white">
                          Open
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex items-center space-x-2">
                        {finding.source === 'code' && finding.resolved === 0 && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleSuggestFix(finding)}
                            className="flex items-center space-x-1 border-black dark:border-white bg-white dark:bg-transparent text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black text-xs"
                          >
                            <Wand2 className="h-3 w-3" />
                            <span>Fix</span>
                          </Button>
                        )}
                        {finding.resolved === 0 && finding.jira_key && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleResolve(finding.jira_key!)}
                            className="flex items-center space-x-1 border-black dark:border-white bg-white dark:bg-transparent text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black text-xs"
                          >
                            <CheckCircle className="h-3 w-3" />
                            <span>Resolve</span>
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredFindings.length === 0 && (
              <div className="text-center py-12 text-black/40 dark:text-white/40 text-xs">
                No findings found matching your filters
              </div>
            )}
          </div>
        </div>

        {/* AI Suggest Fix Modal */}
        <Dialog open={fixModalOpen} onOpenChange={setFixModalOpen}>
        <DialogContent className="max-w-4xl bg-white dark:bg-[#1A1A1A] border-[#DDDDDD] dark:border-[#333333]">
          <DialogHeader>
            <DialogTitle className="text-black dark:text-white">AI-Generated Solution</DialogTitle>
            <DialogDescription className="text-black/60 dark:text-white/60">
              {fixData?.finding?.summary}
            </DialogDescription>
          </DialogHeader>

          {loadingFix ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-black dark:text-white" />
              <span className="ml-3 text-black dark:text-white">Generating fix...</span>
            </div>
          ) : fixData ? (
            <div className="space-y-4">
              {/* Explanation */}
              {fixData.explanation && (
                <div className="command-card">
                  <h4 className="text-sm font-semibold text-black dark:text-white mb-2">Explanation</h4>
                  <p className="text-sm text-black dark:text-white">{fixData.explanation}</p>
                </div>
              )}

              {/* Code Diff */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Original Code */}
                <div className="command-card">
                  <h4 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-2">Original Code</h4>
                  <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-3 rounded overflow-x-auto text-black dark:text-white border border-red-200 dark:border-red-800">
                    <code>{fixData.originalCode || 'No code available'}</code>
                  </pre>
                </div>

                {/* Fixed Code */}
                <div className="command-card">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-green-600 dark:text-green-400">Fixed Code</h4>
                    {fixData.fixedCode && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleCopyFix}
                        className="flex items-center space-x-1 border-black dark:border-white bg-white dark:bg-transparent text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black text-xs h-6"
                      >
                        <Copy className="h-3 w-3" />
                        <span>Copy</span>
                      </Button>
                    )}
                  </div>
                  <pre className="text-xs bg-green-50 dark:bg-green-900/20 p-3 rounded overflow-x-auto text-black dark:text-white border border-green-200 dark:border-green-800">
                    <code>{fixData.fixedCode || 'No fix available'}</code>
                  </pre>
                </div>
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
      </div>
  )
}

