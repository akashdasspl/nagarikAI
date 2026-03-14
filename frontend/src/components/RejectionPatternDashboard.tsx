import { useState, useEffect } from 'react'

interface RejectionPattern {
  field_name: string
  scheme_type: string
  rejected_count: number
  total_applications: number
  rejection_frequency_score: number
  last_refreshed: string
}

interface RejectionPatternResponse {
  scheme_type: string
  patterns: RejectionPattern[]
}

interface RejectionPatternDashboardProps {
  schemeType: string
}

function RejectionPatternDashboard({ schemeType }: RejectionPatternDashboardProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<RejectionPatternResponse | null>(null)

  useEffect(() => {
    if (!schemeType) return

    const fetchPatterns = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`/api/rejection-patterns/${schemeType}`)
        if (!response.ok) {
          throw new Error(`Failed to fetch rejection patterns: ${response.statusText}`)
        }
        const json: RejectionPatternResponse = await response.json()
        setData(json)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchPatterns()
  }, [schemeType])

  const handleExportCSV = () => {
    window.open(`/api/rejection-patterns/${schemeType}/export`, '_blank')
  }

  const getScoreColor = (score: number) => {
    if (score > 0.6) return '#ef4444'
    if (score > 0.3) return '#f59e0b'
    return '#10b981'
  }

  const formatLastRefreshed = (ts: string) => {
    try {
      return new Date(ts).toLocaleString()
    } catch {
      return ts
    }
  }

  return (
    <div style={{
      backgroundColor: '#1a1a1a',
      borderRadius: '10px',
      padding: '1.5rem',
      marginTop: '2rem',
      boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h3 style={{ margin: 0, color: '#667eea', fontSize: '1.2rem' }}>
            📊 Rejection Pattern Analysis
          </h3>
          <p style={{ margin: '0.25rem 0 0 0', color: '#888', fontSize: '0.85rem' }}>
            Top high-risk fields for <strong style={{ color: '#ccc' }}>{schemeType.replace(/_/g, ' ')}</strong>
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          disabled={!data || loading}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '0.5rem 1.25rem',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: data && !loading ? 'pointer' : 'not-allowed',
            opacity: data && !loading ? 1 : 0.5,
            transition: 'opacity 0.2s ease',
          }}
        >
          ⬇ Export CSV
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              style={{
                height: '48px',
                borderRadius: '6px',
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
        <div style={{
          backgroundColor: '#2a1a1a',
          border: '1px solid #ef4444',
          borderRadius: '6px',
          padding: '1rem',
          color: '#ef4444',
          fontSize: '0.9rem',
        }}>
          ⚠ {error}
        </div>
      )}

      {/* Table */}
      {data && !loading && (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#2a2a2a' }}>
                  {['Rank', 'Field Name', 'Rejection Frequency Score', 'Rejected', 'Total'].map((col) => (
                    <th
                      key={col}
                      style={{
                        padding: '0.75rem 1rem',
                        textAlign: 'left',
                        color: '#fff',
                        fontWeight: 600,
                        fontSize: '0.85rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        borderBottom: '2px solid #667eea',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.patterns.map((pattern, index) => {
                  const isHighRisk = pattern.rejection_frequency_score > 0.3
                  const scoreColor = getScoreColor(pattern.rejection_frequency_score)
                  return (
                    <tr
                      key={pattern.field_name}
                      style={{
                        borderBottom: '1px solid #333',
                        backgroundColor: isHighRisk ? 'rgba(239,68,68,0.06)' : 'transparent',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLTableRowElement).style.backgroundColor = isHighRisk
                          ? 'rgba(239,68,68,0.12)'
                          : '#2a2a2a'
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLTableRowElement).style.backgroundColor = isHighRisk
                          ? 'rgba(239,68,68,0.06)'
                          : 'transparent'
                      }}
                    >
                      {/* Rank */}
                      <td style={{ padding: '0.75rem 1rem', color: '#888', fontWeight: 600, fontSize: '0.9rem' }}>
                        #{index + 1}
                      </td>

                      {/* Field Name */}
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ color: '#fff', fontWeight: 500 }}>
                          {pattern.field_name.replace(/_/g, ' ')}
                        </span>
                        {isHighRisk && (
                          <span style={{
                            marginLeft: '0.5rem',
                            backgroundColor: 'rgba(239,68,68,0.2)',
                            color: '#ef4444',
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '0.1rem 0.4rem',
                            borderRadius: '4px',
                            textTransform: 'uppercase',
                          }}>
                            High Risk
                          </span>
                        )}
                      </td>

                      {/* Score with bar */}
                      <td style={{ padding: '0.75rem 1rem', minWidth: '180px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{
                            flex: 1,
                            height: '8px',
                            backgroundColor: '#2a2a2a',
                            borderRadius: '4px',
                            overflow: 'hidden',
                          }}>
                            <div style={{
                              width: `${pattern.rejection_frequency_score * 100}%`,
                              height: '100%',
                              backgroundColor: scoreColor,
                              borderRadius: '4px',
                              transition: 'width 0.5s ease',
                            }} />
                          </div>
                          <span style={{
                            color: scoreColor,
                            fontWeight: 700,
                            fontSize: '0.9rem',
                            minWidth: '40px',
                            textAlign: 'right',
                          }}>
                            {(pattern.rejection_frequency_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>

                      {/* Rejected count */}
                      <td style={{ padding: '0.75rem 1rem', color: '#ef4444', fontWeight: 600 }}>
                        {pattern.rejected_count}
                      </td>

                      {/* Total applications */}
                      <td style={{ padding: '0.75rem 1rem', color: '#ccc' }}>
                        {pattern.total_applications}
                      </td>
                    </tr>
                  )
                })}

                {data.patterns.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#888' }}>
                      No rejection patterns found for this scheme type.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Last refreshed */}
          {data.patterns.length > 0 && (
            <p style={{ margin: '0.75rem 0 0 0', color: '#555', fontSize: '0.8rem', textAlign: 'right' }}>
              Last refreshed: {formatLastRefreshed(data.patterns[0].last_refreshed)}
            </p>
          )}
        </>
      )}
    </div>
  )
}

export default RejectionPatternDashboard
