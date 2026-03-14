import { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface Grievance {
  grievance_id: string
  citizen_id: string
  text: string
  language: string
  category: string
  classification_confidence: number
  predicted_sla: number
  assigned_department: string
  assigned_officer_id: string | null
  status: string
  escalation_level: number
  submitted_at: string
  sla_deadline: string
  resolved_at: string | null
  status_history: any[]
}

interface GrievanceResponse {
  success: boolean
  message: string
  grievance: Grievance
}

interface EscalationAlert {
  grievance_id: string
  category: string
  assigned_department: string
  status: string
  submitted_at: string
  sla_deadline: string
  hours_overdue: number
}

function GrievancePortal() {
  const { t } = useLanguage()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GrievanceResponse | null>(null)
  const [escalations, setEscalations] = useState<EscalationAlert[]>([])
  const [, setLoadingEscalations] = useState(false)
  const [formData, setFormData] = useState({
    text: '',
    language: 'hi',
    citizen_id: 'DEMO_CITIZEN_001',
  })

  // Load escalation alerts on component mount
  useEffect(() => {
    loadEscalations()
  }, [])

  const loadEscalations = async () => {
    setLoadingEscalations(true)
    try {
      const response = await fetch('/api/grievance/check-escalations')
      const data = await response.json()
      
      if (data.success && data.grievances) {
        // Calculate hours overdue for each grievance
        const now = new Date()
        const alerts: EscalationAlert[] = data.grievances.map((g: Grievance) => {
          const deadline = new Date(g.sla_deadline)
          const hoursOverdue = Math.floor((now.getTime() - deadline.getTime()) / (1000 * 60 * 60))
          
          return {
            grievance_id: g.grievance_id,
            category: g.category,
            assigned_department: g.assigned_department,
            status: g.status,
            submitted_at: g.submitted_at,
            sla_deadline: g.sla_deadline,
            hours_overdue: hoursOverdue
          }
        })
        
        setEscalations(alerts)
      }
    } catch (error) {
      console.error('Error loading escalations:', error)
    } finally {
      setLoadingEscalations(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const response = await fetch('/api/grievance/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      
      if (!response.ok) {
        throw new Error('Failed to submit grievance')
      }
      
      const data: GrievanceResponse = await response.json()
      setResult(data)
      
      // Reload escalations after submission
      loadEscalations()
    } catch (error) {
      console.error('Error submitting grievance:', error)
      alert('Failed to submit grievance. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return '#10b981' // green
    if (confidence >= 0.6) return '#f59e0b' // orange
    return '#ef4444' // red
  }

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return t('beneficiary.high')
    if (confidence >= 0.6) return t('beneficiary.medium')
    return t('beneficiary.low')
  }

  const formatDateTime = (dateStr: string): string => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const calculateTimeRemaining = (deadline: string): string => {
    const now = new Date()
    const slaDate = new Date(deadline)
    const diffMs = slaDate.getTime() - now.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffMs < 0) {
      return 'Overdue'
    } else if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} remaining`
    } else {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} remaining`
    }
  }

  return (
    <div className="page">
      <h2>{t('grievance.title')}</h2>
      <p className="description">
        {t('grievance.description')}
      </p>

      {/* Escalation Alerts Section */}
      {escalations.length > 0 && (
        <div className="escalation-alerts">
          <h3>⚠️ {t('grievance.escalation')} ({escalations.length})</h3>
          <div className="escalation-list">
            {escalations.map((alert) => (
              <div key={alert.grievance_id} className="escalation-card">
                <div className="escalation-header">
                  <span className="escalation-id">ID: {alert.grievance_id.substring(0, 8)}</span>
                  <span className="overdue-badge">{alert.hours_overdue}h overdue</span>
                </div>
                <div className="escalation-details">
                  <p><strong>Department:</strong> {alert.assigned_department}</p>
                  <p><strong>Category:</strong> {alert.category}</p>
                  <p><strong>Status:</strong> {alert.status}</p>
                  <p><strong>Deadline:</strong> {formatDateTime(alert.sla_deadline)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grievance Submission Form */}
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label>{t('grievance.language')} / भाषा:</label>
          <select
            value={formData.language}
            onChange={(e) => setFormData({ ...formData, language: e.target.value })}
          >
            <option value="hi">{t('grievance.hindi')} (हिंदी)</option>
            <option value="en">{t('grievance.english')}</option>
          </select>
        </div>

        <div className="form-group">
          <label>{t('grievance.description_label')} / शिकायत विवरण:</label>
          <textarea
            value={formData.text}
            onChange={(e) => setFormData({ ...formData, text: e.target.value })}
            rows={6}
            placeholder={formData.language === 'hi' ? t('grievance.placeholder_hi') : 'Enter your grievance here...'}
            required
          />
        </div>

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? (
            <span className="btn-loading">
              <span className="spinner" aria-hidden="true" />
              {t('grievance.submitting')}
            </span>
          ) : t('grievance.submit')}
        </button>
      </form>

      {loading && (
        <div className="skeleton-container" aria-busy="true" aria-label="Processing grievance">
          {[1, 2].map((i) => (
            <div key={i} className="skeleton-row" style={{ height: '80px' }} />
          ))}
        </div>
      )}

      {/* Classification Results */}
      {result && result.grievance && (
        <div className="results">
          <h3>✓ {t('grievance.submitted')}</h3>
          
          {/* Classification Card */}
          <div className="classification-card">
            <h4>{t('grievance.classification')}</h4>
            <div className="classification-content">
              <div className="classification-main">
                <div className="department-badge">
                  {result.grievance.assigned_department}
                </div>
                <div className="confidence-indicator">
                  <div className="confidence-bar-container">
                    <div 
                      className="confidence-bar-fill"
                      style={{ 
                        width: `${result.grievance.classification_confidence * 100}%`,
                        backgroundColor: getConfidenceColor(result.grievance.classification_confidence)
                      }}
                    />
                  </div>
                  <div className="confidence-label">
                    <span style={{ color: getConfidenceColor(result.grievance.classification_confidence) }}>
                      {getConfidenceLabel(result.grievance.classification_confidence)} {t('beneficiary.confidence')}
                    </span>
                    <span className="confidence-value">
                      {(result.grievance.classification_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="classification-details">
                <div className="detail-item">
                  <span className="detail-label">{t('grievance.category')}:</span>
                  <span className="detail-value">{result.grievance.category}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">{t('grievance.id')}:</span>
                  <span className="detail-value">{result.grievance.grievance_id}</span>
                </div>
              </div>
            </div>
          </div>

          {/* SLA Timeline Card */}
          <div className="sla-card">
            <h4>{t('grievance.sla')}</h4>
            <div className="sla-content">
              <div className="sla-main">
                <div className="sla-hours">
                  {result.grievance.predicted_sla}
                  <span className="sla-unit">{t('grievance.hours')}</span>
                </div>
                <div className="sla-deadline">
                  <p><strong>{t('grievance.deadline')}:</strong> {formatDateTime(result.grievance.sla_deadline)}</p>
                  <p className="time-remaining">{calculateTimeRemaining(result.grievance.sla_deadline)}</p>
                </div>
              </div>
              <div className="sla-info">
                <p>⏰ Auto-escalation at 80% SLA threshold</p>
                <p>📧 Notifications enabled for status updates</p>
              </div>
            </div>
          </div>

          {/* Status Tracking Card */}
          <div className="status-card">
            <h4>{t('grievance.status')}</h4>
            <div className="status-timeline">
              <div className="timeline-item active">
                <div className="timeline-marker completed"></div>
                <div className="timeline-content">
                  <div className="timeline-title">Submitted</div>
                  <div className="timeline-time">{formatDateTime(result.grievance.submitted_at)}</div>
                  <div className="timeline-desc">Grievance received and classified</div>
                </div>
              </div>
              <div className="timeline-item">
                <div className="timeline-marker pending"></div>
                <div className="timeline-content">
                  <div className="timeline-title">Assigned</div>
                  <div className="timeline-desc">Awaiting officer assignment</div>
                </div>
              </div>
              <div className="timeline-item">
                <div className="timeline-marker pending"></div>
                <div className="timeline-content">
                  <div className="timeline-title">In Progress</div>
                  <div className="timeline-desc">Officer investigating the issue</div>
                </div>
              </div>
              <div className="timeline-item">
                <div className="timeline-marker pending"></div>
                <div className="timeline-content">
                  <div className="timeline-title">Resolved</div>
                  <div className="timeline-desc">Issue resolved and closed</div>
                </div>
              </div>
            </div>
            <div className="current-status">
              <span className="status-label">Current Status:</span>
              <span className="status-value">{result.grievance.status.toUpperCase()}</span>
            </div>
          </div>

          {/* Success Message */}
          <div className="info-box">
            <p>✓ Your grievance has been automatically routed to the <strong>{result.grievance.assigned_department}</strong> department</p>
            <p>✓ Classification confidence: <strong>{getConfidenceLabel(result.grievance.classification_confidence)}</strong></p>
            <p>✓ Expected resolution within <strong>{result.grievance.predicted_sla} hours</strong></p>
            <p>✓ Auto-escalation enabled if resolution exceeds predicted timeline</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default GrievancePortal
