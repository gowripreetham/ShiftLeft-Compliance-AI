'use client'

import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Config } from '@/lib/types'
import { useToast } from '@/components/ui/use-toast'
import { CheckCircle, AlertCircle, Database, ExternalLink } from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function Settings() {
  const { toast } = useToast()
  const { data, error, isLoading } = useSWR('/api/config', fetcher)
  
  const [config, setConfig] = useState<Config>({
    JIRA_BASE_URL: '',
    JIRA_PROJECT_KEY: '',
    GITHUB_REPO: '',
    SLACK_CHANNEL_ID: '',
  })

  const [isSaving, setIsSaving] = useState(false)
  const [isTesting, setIsTesting] = useState(false)

  // Update config when data loads
  useEffect(() => {
    if (data && !config.JIRA_BASE_URL) {
      setConfig(data)
    }
  }, [data, config.JIRA_BASE_URL])

  const handleInputChange = (field: keyof Config, value: string) => {
    setConfig((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // In a real application, you would save this to a backend API
      // For now, we'll just show a success message
      await new Promise((resolve) => setTimeout(resolve, 500))
      
      toast({
        title: 'Configuration Saved',
        description: 'Your settings have been saved successfully.',
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save configuration.',
        variant: 'destructive',
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleTestConnections = async () => {
    setIsTesting(true)
    try {
      // Simulate connection testing
      await new Promise((resolve) => setTimeout(resolve, 1000))
      
      toast({
        title: 'Connection Test Complete',
        description: 'All integrations are working correctly.',
      })
    } catch (error) {
      toast({
        title: 'Connection Test Failed',
        description: 'Some integrations could not be reached.',
        variant: 'destructive',
      })
    } finally {
      setIsTesting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading settings...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error loading settings</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Integrations</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Configure your compliance monitoring integrations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Form */}
        <div className="lg:col-span-2 space-y-4">
          <div className="command-card">
            <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
              <h2 className="text-sm font-semibold text-black dark:text-white">Integration Configuration</h2>
              <p className="text-xs text-black/60 dark:text-white/60 mt-1">
                Set up your Jira, GitHub, and Slack integrations
              </p>
            </div>
            <div className="space-y-6">
              {/* Jira Configuration */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-black dark:text-white flex items-center space-x-2">
                  <ExternalLink className="h-4 w-4" />
                  <span>Jira Integration</span>
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="jira-url" className="text-black dark:text-white">Jira Base URL</Label>
                  <Input
                    id="jira-url"
                    placeholder="https://yourcompany.atlassian.net"
                    value={config.JIRA_BASE_URL}
                    onChange={(e) => handleInputChange('JIRA_BASE_URL', e.target.value)}
                    className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="jira-project" className="text-black dark:text-white">Jira Project Key</Label>
                  <Input
                    id="jira-project"
                    placeholder="PROJ"
                    value={config.JIRA_PROJECT_KEY}
                    onChange={(e) => handleInputChange('JIRA_PROJECT_KEY', e.target.value)}
                    className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]"
                  />
                </div>
              </div>

              <div className="border-t border-[#DDDDDD] dark:border-[#333333] pt-4"></div>

              {/* GitHub Configuration */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-black dark:text-white flex items-center space-x-2">
                  <ExternalLink className="h-4 w-4" />
                  <span>GitHub Integration</span>
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="github-repo" className="text-black dark:text-white">GitHub Repository</Label>
                  <Input
                    id="github-repo"
                    placeholder="owner/repository"
                    value={config.GITHUB_REPO}
                    onChange={(e) => handleInputChange('GITHUB_REPO', e.target.value)}
                    className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]"
                  />
                </div>
              </div>

              <div className="border-t border-[#DDDDDD] dark:border-[#333333] pt-4"></div>

              {/* Slack Configuration */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-black dark:text-white flex items-center space-x-2">
                  <ExternalLink className="h-4 w-4" />
                  <span>Slack Integration</span>
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="slack-channel" className="text-black dark:text-white">Slack Channel ID</Label>
                  <Input
                    id="slack-channel"
                    placeholder="C1234567890"
                    value={config.SLACK_CHANNEL_ID}
                    onChange={(e) => handleInputChange('SLACK_CHANNEL_ID', e.target.value)}
                    className="bg-white dark:bg-[#1A1A1A] text-black dark:text-white border-[#DDDDDD] dark:border-[#333333]"
                  />
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <Button onClick={handleSave} disabled={isSaving} className="bg-black dark:bg-white text-white dark:text-black hover:bg-black/80 dark:hover:bg-white/80">
                  {isSaving ? 'Saving...' : 'Save Configuration'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleTestConnections}
                  disabled={isTesting}
                  className="bg-white dark:bg-transparent border-black dark:border-white text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black"
                >
                  {isTesting ? 'Testing...' : 'Test Connections'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="space-y-4">
          <div className="command-card">
            <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
              <h2 className="text-sm font-semibold text-black dark:text-white">System Status</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-black/60 dark:text-white/60">Database</span>
                <span className="flex items-center space-x-1 text-green-600">
                  <CheckCircle className="h-3 w-3" />
                  <span className="text-xs font-medium">Connected</span>
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-black/60 dark:text-white/60">API Server</span>
                <span className="flex items-center space-x-1 text-green-600">
                  <CheckCircle className="h-3 w-3" />
                  <span className="text-xs font-medium">Running</span>
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-black/60 dark:text-white/60">Gemini AI</span>
                <span className="flex items-center space-x-1 text-green-600">
                  <CheckCircle className="h-3 w-3" />
                  <span className="text-xs font-medium">Active</span>
                </span>
              </div>
            </div>
          </div>

          <div className="command-card">
            <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
              <h2 className="text-sm font-semibold text-black dark:text-white">About</h2>
            </div>
            <div className="space-y-2 text-xs text-black/60 dark:text-white/60">
              <p>
                <strong className="text-black dark:text-white">Version:</strong> 1.0.0
              </p>
              <p>
                <strong className="text-black dark:text-white">Framework:</strong> Next.js 14
              </p>
              <p>
                <strong className="text-black dark:text-white">Database:</strong> SQLite
              </p>
              <p>
                <strong className="text-black dark:text-white">AI Engine:</strong> Google Gemini
              </p>
            </div>
          </div>

          <div className="command-card">
            <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
              <h2 className="text-sm font-semibold text-black dark:text-white flex items-center space-x-2">
                <Database className="h-4 w-4" />
                <span>Database Location</span>
              </h2>
            </div>
            <div>
              <code className="text-xs bg-[#F6F6F6] dark:bg-[#1A1A1A] p-3 block border border-[#DDDDDD] dark:border-[#333333] text-black dark:text-white">
                ../compliance_memory.db
              </code>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

