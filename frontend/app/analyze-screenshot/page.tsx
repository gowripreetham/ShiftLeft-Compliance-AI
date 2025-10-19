'use client'

import { useState, useRef, DragEvent } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/use-toast'
import { Camera, Upload, X, AlertTriangle, CheckCircle, Info, Shield, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import { RiskLevel } from '@/lib/types'

interface AnalysisResult {
  ok: boolean
  action_taken: string
  analysis: {
    risk_level: RiskLevel
    control_id: string | null
    summary: string
    description: string
    issues: Array<{
      type: string
      description: string
      recommendation: string
    }>
  }
}

export default function AnalyzeScreenshot() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleFileSelect = (file: File) => {
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a PNG, JPEG, JPG, or GIF image.',
        variant: 'destructive',
      })
      return
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 10MB.',
        variant: 'destructive',
      })
      return
    }

    setSelectedFile(file)
    setAnalysisResult(null)

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const clearImage = () => {
    setSelectedFile(null)
    setPreview(null)
    setAnalysisResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const analyzeImage = async () => {
    if (!selectedFile) return

    setIsAnalyzing(true)
    setAnalysisResult(null)

    try {
      const formData = new FormData()
      formData.append('image', selectedFile)

      const response = await fetch('/api/analyze-screenshot', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze screenshot')
      }

      // The response now comes from Python service with proper structure
      setAnalysisResult(data)
      
      toast({
        title: 'Analysis complete!',
        description: data.action_taken === 'duplicate' 
          ? 'Duplicate finding detected - no action taken'
          : 'Screenshot analyzed and actions taken successfully.',
      })
    } catch (error) {
      console.error('Error analyzing screenshot:', error)
      toast({
        title: 'Analysis failed',
        description: error instanceof Error ? error.message : 'Failed to analyze screenshot. Please try again.',
        variant: 'destructive',
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getRiskBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="p-6 bg-white dark:bg-black">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-black dark:text-white mb-1">Manual Analysis</h1>
        <p className="text-sm text-black/60 dark:text-white/60">Upload screenshots for real-time compliance analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="space-y-4">
          <div className="command-card">
            <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4">
              <h2 className="text-sm font-semibold text-black dark:text-white">Upload Screenshot</h2>
            </div>
            <div className="space-y-4">
              {/* Drag and Drop Zone */}
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`border-2 border-dashed p-8 text-center cursor-pointer transition-all ${
                  selectedFile
                    ? 'border-black dark:border-white bg-[#F6F6F6] dark:bg-[#1A1A1A]'
                    : 'border-black/30 dark:border-white/30 bg-[#F6F6F6] dark:bg-[#1A1A1A] hover:border-black dark:hover:border-white'
                }`}
              >
                {preview ? (
                  <div className="space-y-4">
                    <img
                      src={preview}
                      alt="Preview"
                      className="max-h-64 mx-auto"
                    />
                    <div className="text-xs text-black dark:text-white">
                      {selectedFile?.name}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex justify-center">
                      <div className="p-4 bg-black dark:bg-white">
                        <Camera className="h-12 w-12 text-white dark:text-black" />
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-black dark:text-white">
                        Drag and drop your screenshot here
                      </p>
                      <p className="text-xs text-black/60 dark:text-white/60 mt-1">
                        or click to browse
                      </p>
                    </div>
                    <p className="text-xs text-black/40 dark:text-white/40">
                      PNG, JPEG, JPG, GIF (max 10MB)
                    </p>
                  </div>
                )}
              </div>

              {/* File Input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg,image/gif"
                onChange={handleFileInputChange}
                className="hidden"
              />

              {/* Action Buttons */}
              <div className="flex gap-3">
                {!selectedFile ? (
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    className="flex-1 bg-black dark:bg-white text-white dark:text-black hover:bg-black/80 dark:hover:bg-white/80"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Select Image
                  </Button>
                ) : (
                  <>
                    <Button
                      onClick={() => fileInputRef.current?.click()}
                      variant="outline"
                      className="flex-1 border-black dark:border-white text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black"
                    >
                      Change Image
                    </Button>
                    <Button
                      onClick={clearImage}
                      variant="outline"
                      className="border-black dark:border-white text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>

              {/* Analyze Button */}
              <Button
                onClick={analyzeImage}
                disabled={!selectedFile || isAnalyzing}
                className="w-full bg-black dark:bg-white text-white dark:text-black hover:bg-black/80 dark:hover:bg-white/80"
              >
                {isAnalyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Analyze Screenshot
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Info Card */}
          <div className="command-card bg-[#F6F6F6] dark:bg-[#1A1A1A]">
            <div className="flex items-start space-x-3">
              <Info className="h-4 w-4 text-black dark:text-white mt-0.5 flex-shrink-0" />
              <div className="text-xs">
                <p className="font-semibold mb-2 text-black dark:text-white">What can be analyzed?</p>
                <ul className="list-disc list-inside space-y-1 text-black/80 dark:text-white/80">
                  <li>Terminal outputs with credentials</li>
                  <li>Code editors with sensitive data</li>
                  <li>Cloud console screenshots</li>
                  <li>Configuration files</li>
                  <li>Error messages with stack traces</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div>
          {analysisResult && analysisResult.analysis ? (
            <div className="command-card">
              <div className="border-b border-[#DDDDDD] dark:border-[#333333] pb-3 mb-4 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-black dark:text-white">Analysis Results</h2>
                <span className={`command-badge ${
                  analysisResult.analysis.risk_level === 'high' ? 'text-red-600 border-red-600' :
                  analysisResult.analysis.risk_level === 'medium' ? 'text-yellow-600 border-yellow-600' :
                  'text-green-600 border-green-600'
                }`}>
                  {analysisResult.analysis.risk_level.toUpperCase()}
                </span>
              </div>
              <div className="space-y-4">
                {/* Action Taken */}
                {analysisResult.action_taken && (
                  <div className="bg-[#F6F6F6] dark:bg-[#1A1A1A] border border-[#DDDDDD] dark:border-[#333333] p-3">
                    <p className="text-xs text-black dark:text-white">
                      <span className="font-semibold">Action:</span> {analysisResult.action_taken}
                    </p>
                  </div>
                )}

                {/* Summary */}
                <div>
                  <h3 className="text-xs font-semibold text-black dark:text-white mb-2 flex items-center">
                    <AlertTriangle className="h-3 w-3 mr-2" />
                    Summary
                  </h3>
                  <p className="text-sm text-black dark:text-white">{analysisResult.analysis.summary}</p>
                </div>

                {/* Description */}
                {analysisResult.analysis.description && (
                  <div>
                    <h3 className="text-xs font-semibold text-black dark:text-white mb-2">Description</h3>
                    <p className="text-xs text-black/80 dark:text-white/80">{analysisResult.analysis.description}</p>
                  </div>
                )}

                {/* Issues */}
                {analysisResult.analysis.issues && analysisResult.analysis.issues.length > 0 && (
                  <div>
                    <h3 className="text-xs font-semibold text-black dark:text-white mb-2">Issues Found</h3>
                    <div className="space-y-2">
                      {analysisResult.analysis.issues.map((issue, index) => (
                        <div key={index} className="bg-[#F6F6F6] dark:bg-[#1A1A1A] border border-[#DDDDDD] dark:border-[#333333] p-3">
                          <h4 className="font-semibold text-xs text-black dark:text-white mb-1">{issue.type}</h4>
                          <p className="text-xs text-black/80 dark:text-white/80 mb-2">{issue.description}</p>
                          {issue.recommendation && (
                            <div className="flex items-start space-x-2 mt-2 pt-2 border-t border-[#DDDDDD] dark:border-[#333333]">
                              <CheckCircle className="h-3 w-3 text-green-600 mt-0.5 flex-shrink-0" />
                              <p className="text-xs text-black/80 dark:text-white/80">
                                <span className="font-semibold">Recommendation:</span> {issue.recommendation}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Control ID */}
                {analysisResult.analysis.control_id && (
                  <div>
                    <h3 className="text-xs font-semibold text-black dark:text-white mb-2">Associated Control</h3>
                    <Link
                      href={`/posture?control=${analysisResult.analysis.control_id}`}
                      className="inline-flex items-center text-[#0693E3] hover:underline font-mono text-xs"
                    >
                      {analysisResult.analysis.control_id}
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </Link>
                  </div>
                )}

                {/* Actions */}
                <div className="pt-4 border-t border-[#DDDDDD] dark:border-[#333333]">
                  <Link href="/findings">
                    <Button variant="outline" className="w-full border-black dark:border-white text-black dark:text-white hover:bg-black dark:hover:bg-white hover:text-white dark:hover:text-black text-xs">
                      View All Findings
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ) : (
            <div className="command-card p-12 text-center">
              <div className="p-3 bg-[#F6F6F6] dark:bg-[#1A1A1A] w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Shield className="h-8 w-8 text-black/30 dark:text-white/30" />
              </div>
              <p className="text-xs text-black/60 dark:text-white/60">Upload and analyze a screenshot to see results here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

