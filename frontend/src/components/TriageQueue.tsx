import { useState, useEffect, useCallback } from 'react'

interface ContributingFactor {
  factor: string
  weight: number
  raw_score: number
}

interface StallRiskAssessment {
  application_id: string
  stall_risk_score: number
  primary_stall_reason_hindi: string
  primary_stall_reason_english: string
  computed_at: string
  contributing_factors: ContributingFactor[]
}

interface TriageQueueResponse {
  triage_queue: StallRiskAssessment[]
  total: number
}

const REFRESH_INTERVAL_MS = 2 * 60 * 1000 // 2 minutes

function getRelativeTime(isoString: string): string {
  const now = Date.now()
  const then = new Date(isoString).getTime()
  const diffMs = now - then
  const diffSec = Math.floor(diffMs / 1000)
  if (diffSec < 60) return `${diffSec}s ago`
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin} min ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  return `${Math.floor(diffHr / 24)}d ago`
}

function getRiskColor(score: number): string {
  if (score >= 0.8) return '#ef4444'
  return '#f59e0b'
}

function getRiskLabel(score: number): string {
  if (score >= 0.8) return 'Critical'
  return 'High'
}

function TriageQueue() {
  const [queue, setQueue] = useState<StallRiskAssessment[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const fetchQueue = useCallback(async () => {
    try {
      const res = await fetch('/api/triage-queue')
      if (!res.ok) throw new Error(`Failed to fetch triage queue: ${res.statusText}`)
      const data: TriageQueueResponse = await res.json()
      // Filter to only stall_risk_score > 0.6, sorted descending (backend already sorts, but ensure)
      const filtered = (data.triage_queue ?? [])
        .filter((item) => item.stall_risk_score > 0.6)
        .sort((a, b) => b.stall_risk_score - a.stall_risk_score)
      setQueue(filtered)
      setTotal(data.total ?? filtered.length)
      setLastRefreshed(new Date())
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchQueue()
    const interval = setInterval(fetchQueue, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchQueue])

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id))
  }

  return (
    <div
      style={{
        backgroundColor: '#1a1a1a',
        borderRadius: '10px',
        padding: '1.5rem',
        marginTop: '2rem',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '1.25rem',
          flexWrap: 'wrap',
          gap: '0.75rem',
        }}
      >
        <div>
          <h3 style={{ margin: 0, color: '#667eea', fontSize: '1.2rem' }}>
            🚨 Triage Queue
          </h3>
          <p style={{ margin: '0.25rem 0 0 0', color: '#888', fontSize: '0.85rem' }}>
            In-progress applications at high stall risk — auto-refreshes every 2 minutes
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {lastRefreshed && (
            <span style={{ color: '#555', fontSize: '0.8rem' }}>
              Last refreshed: {lastRefreshed.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={fetchQueue}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '0.4rem 1rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              style={{
                height: '72px',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #2a2a2a 25%, #333 50%, #2a2a2a 75%)',
                backgroundSize: '800px 100%',
                animation: 'shimmer 1.4s infinite linear',
              }}
            />
          ))}
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div
          style={{
            backgroundColor: '#2a1a1a',
            border: '1px solid #ef4444',
            borderRadius: '6px',
            padding: '1rem',
            color: '#ef4444',
            fontSize: '0.9rem',
          }}
        >
          ⚠ {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && queue.length === 0 && (
        <div
          style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: '#555',
          }}
        >
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>✅</div>
          <p style={{ margin: 0, fontSize: '1rem', color: '#888' }}>No applications currently at high stall risk</p>
          <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#555' }}>
            The queue will update automatically every 2 minutes
          </p>
        </div>
      )}

      {/* Queue list */}
      {!loading && !error && queue.length > 0 && (
        <>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.75rem',
            }}
          >
            <span style={{ color: '#888', fontSize: '0.85rem' }}>
              Showing {queue.length} of {total} at-risk applications
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {queue.map((item) => {
              const riskColor = getRiskColor(item.stall_risk_score)
              const isExpanded = expandedId === item.application_id
              return (
                <div
                  key={item.application_id}
                  style={{
                    backgroundColor: '#242424',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${riskColor}`,
                    overflow: 'hidden',
                    transition: 'box-shadow 0.2s ease',
                  }}
                >
                  {/* Main row */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr auto',
                      gap: '1rem',
                      padding: '1rem 1.25rem',
                      alignItems: 'start',
                    }}
                  >
                    {/* Left: ID + reasons */}
                    <div>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.75rem',
                          marginBottom: '0.5rem',
                          flexWrap: 'wrap',
                        }}
                      >
                        <span
                          style={{
                            color: '#fff',
                            fontWeight: 600,
                            fontFamily: 'monospace',
                            fontSize: '0.95rem',
                          }}
                        >
                          {item.application_id}
                        </span>
                        <span
                          style={{
                            backgroundColor: `${riskColor}22`,
                            color: riskColor,
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                          }}
                        >
                          {getRiskLabel(item.stall_risk_score)}
                        </span>
                        <span style={{ color: '#555', fontSize: '0.8rem' }}>
                          {getRelativeTime(item.computed_at)}
                        </span>
                      </div>

                      {/* English reason */}
                      <p
                        style={{
                          margin: '0 0 0.3rem 0',
                          color: '#ccc',
                          fontSize: '0.9rem',
                          lineHeight: 1.5,
                        }}
                      >
                        <span style={{ color: '#888', fontSize: '0.8rem', marginRight: '0.4rem' }}>EN:</span>
                        {item.primary_stall_reason_english}
                      </p>

                      {/* Hindi reason */}
                      <p
                        style={{
                          margin: 0,
                          color: '#aaa',
                          fontSize: '0.9rem',
                          fontStyle: 'italic',
                          lineHeight: 1.5,
                        }}
                      >
                        <span style={{ color: '#888', fontSize: '0.8rem', marginRight: '0.4rem', fontStyle: 'normal' }}>HI:</span>
                        {item.primary_stall_reason_hindi}
                      </p>
                    </div>

                    {/* Right: score + expand */}
                    <div
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'flex-end',
                        gap: '0.5rem',
                        minWidth: '80px',
                      }}
                    >
                      <span
                        style={{
                          color: riskColor,
                          fontWeight: 700,
                          fontSize: '1.6rem',
                          lineHeight: 1,
                        }}
                      >
                        {(item.stall_risk_score * 100).toFixed(0)}%
                      </span>
                      {/* Score bar */}
                      <div
                        style={{
                          width: '72px',
                          height: '6px',
                          backgroundColor: '#333',
                          borderRadius: '3px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            width: `${item.stall_risk_score * 100}%`,
                            height: '100%',
                            backgroundColor: riskColor,
                            borderRadius: '3px',
                          }}
                        />
                      </div>
                      {item.contributing_factors && item.contributing_factors.length > 0 && (
                        <button
                          onClick={() => toggleExpand(item.application_id)}
                          style={{
                            background: 'none',
                            border: '1px solid #333',
                            borderRadius: '4px',
                            color: '#667eea',
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            padding: '0.2rem 0.5rem',
                            marginTop: '0.25rem',
                          }}
                        >
                          {isExpanded ? '▲ Hide' : '▼ Factors'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Expanded: contributing factors */}
                  {isExpanded && item.contributing_factors && item.contributing_factors.length > 0 && (
                    <div
                      style={{
                        borderTop: '1px solid #333',
                        padding: '0.75rem 1.25rem',
                        backgroundColor: '#1e1e1e',
                      }}
                    >
                      <p
                        style={{
                          margin: '0 0 0.5rem 0',
                          color: '#888',
                          fontSize: '0.8rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontWeight: 600,
                        }}
                      >
                        Contributing Factors
                      </p>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {item.contributing_factors
                          .slice()
                          .sort((a, b) => b.weight - a.weight)
                          .map((f, idx) => (
                            <div
                              key={idx}
                              style={{
                                display: 'grid',
                                gridTemplateColumns: '1fr auto auto',
                                gap: '0.75rem',
                                alignItems: 'center',
                              }}
                            >
                              <span style={{ color: '#ccc', fontSize: '0.85rem' }}>
                                {f.factor.replace(/_/g, ' ')}
                              </span>
                              <div
                                style={{
                                  width: '80px',
                                  height: '5px',
                                  backgroundColor: '#333',
                                  borderRadius: '3px',
                                  overflow: 'hidden',
                                }}
                              >
                                <div
                                  style={{
                                    width: `${f.raw_score * 100}%`,
                                    height: '100%',
                                    backgroundColor: '#667eea',
                                    borderRadius: '3px',
                                  }}
                                />
                              </div>
                              <span style={{ color: '#667eea', fontSize: '0.8rem', fontWeight: 600, minWidth: '36px', textAlign: 'right' }}>
                                {(f.weight * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}

export default TriageQueue
