import { useState, useEffect, useCallback } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import RejectionPatternDashboard from '../components/RejectionPatternDashboard'
import GuidanceOverlay from '../components/GuidanceOverlay'
import TriageQueue from '../components/TriageQueue'

interface ValidationIssue {
  field_name: string
  issue_type: string
  severity: string
  impact_on_risk: number
}

interface CorrectionGuidance {
  guidance_text_hindi: string
  guidance_text_english: string
  suggested_action: string
  priority: number
}

interface ValidationResult {
  rejection_risk_score: number
  validation_issues: ValidationIssue[]
  corrective_guidance: CorrectionGuidance[]
}

function OperatorAssistant() {
  const { t, language } = useLanguage()
  const [loading, setLoading] = useState(false)
  const [focusedField, setFocusedField] = useState('')
  const [validating, setValidating] = useState(false)
  const [result, setResult] = useState<ValidationResult | null>(null)
  const [formData, setFormData] = useState({
    applicant_name: '',
    age: '',
    income: '',
    date_of_birth: '',
    address: '',
    phone: '',
    bank_account: '',
    aadhaar_number: '',
    scheme_type: 'widow_pension',
    documents: {
      aadhaar: false,
      death_certificate: false,
      disability_certificate: false,
      income_certificate: false,
      age_proof: false,
      address_proof: false,
    },
  })
  const [fieldErrors, setFieldErrors] = useState<Set<string>>(new Set())
  const [showRejectionPatterns, setShowRejectionPatterns] = useState(false)
  const [highRiskFields, setHighRiskFields] = useState<Map<string, number>>(new Map())

  // Real-time validation with debouncing
  const validateApplication = useCallback(async (data: typeof formData) => {
    setValidating(true)
    
    try {
      const response = await fetch('/api/application/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          application_id: `app_${Date.now()}`,
          scheme_type: data.scheme_type,
          operator_id: 'operator_demo',
          application_data: data,
        }),
      })
      
      const responseData = await response.json()
      
      if (responseData.success && responseData.validation) {
        setResult(responseData.validation)
        
        // Update field errors based on validation issues
        const errors = new Set<string>(
          responseData.validation.validation_issues.map((issue: ValidationIssue) => issue.field_name)
        )
        setFieldErrors(errors)
      }
    } catch (error) {
      console.error('Error validating application:', error)
    } finally {
      setValidating(false)
    }
  }, [])

  // Fetch rejection patterns when scheme type changes
  useEffect(() => {
    if (!formData.scheme_type) return
    fetch(`/api/rejection-patterns/${formData.scheme_type}`)
      .then((res) => res.json())
      .then((data) => {
        const map = new Map<string, number>()
        if (data.patterns) {
          for (const pattern of data.patterns) {
            if (pattern.rejection_frequency_score > 0.3) {
              map.set(pattern.field_name, pattern.rejection_frequency_score)
            }
          }
        }
        setHighRiskFields(map)
      })
      .catch(() => setHighRiskFields(new Map()))
  }, [formData.scheme_type])

  // Debounced validation effect
  useEffect(() => {
    // Only validate if we have some data
    if (formData.applicant_name || formData.age || formData.income) {
      const timeoutId = setTimeout(() => {
        validateApplication(formData)
      }, 800) // 800ms debounce
      
      return () => clearTimeout(timeoutId)
    }
  }, [formData, validateApplication])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await validateApplication(formData)
    } catch (error) {
      console.error('Error validating application:', error)
      alert('Failed to validate application')
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevel = (score: number) => {
    if (score >= 0.7) return t('operator.highRisk')
    if (score >= 0.4) return t('operator.mediumRisk')
    return t('operator.lowRisk')
  }

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return '#ef4444'
    if (score >= 0.4) return '#f59e0b'
    return '#10b981'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'severity-critical'
      case 'high': return 'severity-high'
      case 'medium': return 'severity-medium'
      default: return 'severity-low'
    }
  }

  const hasFieldError = (fieldName: string) => {
    return fieldErrors.has(fieldName)
  }

  const getFieldClassName = (fieldName: string) => {
    return hasFieldError(fieldName) ? 'field-error' : ''
  }

  const renderHighRiskBadge = (fieldName: string) => {
    const score = highRiskFields.get(fieldName)
    if (score === undefined) return null
    return (
      <span style={{ color: '#f59e0b', fontSize: '0.8rem', marginLeft: '0.4rem', fontWeight: 500 }}>
        ⚠ High rejection risk ({(score * 100).toFixed(0)}%)
      </span>
    )
  }

  return (
    <div className="page">
      <h2>{t('operator.title')}</h2>
      <p className="description">
        {t('operator.description')}
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Left Column: Form */}
        <div>
          <form onSubmit={handleSubmit} className="form">
            <h3 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#667eea' }}>Application Details</h3>
            
            <div className="form-group">
              <label>{t('operator.applicantName')}: *{renderHighRiskBadge('applicant_name')}</label>
              <input
                type="text"
                value={formData.applicant_name}
                onChange={(e) => setFormData({ ...formData, applicant_name: e.target.value })}
                onFocus={() => setFocusedField('applicant_name')}
                className={getFieldClassName('applicant_name')}
                placeholder="Enter full name"
                required
              />
              {hasFieldError('applicant_name') && (
                <span className="field-error-indicator">⚠ Issue detected</span>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label>{t('operator.age')}: *{renderHighRiskBadge('age')}</label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  onFocus={() => setFocusedField('age')}
                  className={getFieldClassName('age')}
                  placeholder="Age in years"
                  required
                />
                {hasFieldError('age') && (
                  <span className="field-error-indicator">⚠ Issue detected</span>
                )}
              </div>

              <div className="form-group">
                <label>{t('operator.dob')}:{renderHighRiskBadge('date_of_birth')}</label>
                <input
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  onFocus={() => setFocusedField('date_of_birth')}
                  className={getFieldClassName('date_of_birth')}
                />
              </div>
            </div>

            <div className="form-group">
              <label>{t('operator.income')}: *{renderHighRiskBadge('income')}</label>
              <input
                type="number"
                value={formData.income}
                onChange={(e) => setFormData({ ...formData, income: e.target.value })}
                onFocus={() => setFocusedField('income')}
                className={getFieldClassName('income')}
                placeholder="Annual income in rupees"
                required
              />
              {hasFieldError('income') && (
                <span className="field-error-indicator">⚠ Issue detected</span>
              )}
            </div>

            <div className="form-group">
              <label>{t('operator.address')}:{renderHighRiskBadge('address')}</label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                onFocus={() => setFocusedField('address')}
                className={getFieldClassName('address')}
                placeholder="Complete address with village and district"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label>{t('operator.phone')}:{renderHighRiskBadge('phone')}</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                onFocus={() => setFocusedField('phone')}
                className={getFieldClassName('phone')}
                placeholder="10-digit mobile number"
              />
            </div>

            <div className="form-group">
              <label>Bank Account Number: *{renderHighRiskBadge('bank_account')}</label>
              <input
                type="text"
                value={formData.bank_account || ''}
                onChange={(e) => setFormData({ ...formData, bank_account: e.target.value })}
                onFocus={() => setFocusedField('bank_account')}
                className={getFieldClassName('bank_account')}
                placeholder="Bank account number"
                required
              />
              {hasFieldError('bank_account') && (
                <span className="field-error-indicator">⚠ Issue detected</span>
              )}
            </div>

            <div className="form-group">
              <label>Aadhaar Number: *{renderHighRiskBadge('aadhaar_number')}</label>
              <input
                type="text"
                value={formData.aadhaar_number || ''}
                onChange={(e) => setFormData({ ...formData, aadhaar_number: e.target.value })}
                onFocus={() => setFocusedField('aadhaar_number')}
                className={getFieldClassName('aadhaar_number')}
                placeholder="12-digit Aadhaar number"
                required
              />
              {hasFieldError('aadhaar_number') && (
                <span className="field-error-indicator">⚠ Issue detected</span>
              )}
            </div>

            <div className="form-group">
              <label>{t('operator.scheme')}: *</label>
              <select
                value={formData.scheme_type}
                onChange={(e) => setFormData({ ...formData, scheme_type: e.target.value })}
              >
                <option value="widow_pension">Widow Pension</option>
                <option value="disability_pension">Disability Pension</option>
                <option value="old_age_pension">Old Age Pension</option>
                <option value="ration_card">Ration Card</option>
                <option value="bpl_card">BPL Card</option>
              </select>
            </div>

            <div className="form-group">
              <label>Documents Submitted:</label>
              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.documents.aadhaar}
                    onChange={(e) => setFormData({
                      ...formData,
                      documents: { ...formData.documents, aadhaar: e.target.checked }
                    })}
                  />
                  Aadhaar Card
                </label>
                {formData.scheme_type === 'widow_pension' && (
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.documents.death_certificate}
                      onChange={(e) => setFormData({
                        ...formData,
                        documents: { ...formData.documents, death_certificate: e.target.checked }
                      })}
                    />
                    Death Certificate
                  </label>
                )}
                {formData.scheme_type === 'disability_pension' && (
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.documents.disability_certificate}
                      onChange={(e) => setFormData({
                        ...formData,
                        documents: { ...formData.documents, disability_certificate: e.target.checked }
                      })}
                    />
                    Disability Certificate
                  </label>
                )}
                {(formData.scheme_type === 'old_age_pension') && (
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.documents.age_proof}
                      onChange={(e) => setFormData({
                        ...formData,
                        documents: { ...formData.documents, age_proof: e.target.checked }
                      })}
                    />
                    Age Proof
                  </label>
                )}
                {(formData.scheme_type === 'ration_card' || formData.scheme_type === 'bpl_card') && (
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.documents.income_certificate}
                      onChange={(e) => setFormData({
                        ...formData,
                        documents: { ...formData.documents, income_certificate: e.target.checked }
                      })}
                    />
                    Income Certificate
                  </label>
                )}
                <label>
                  <input
                    type="checkbox"
                    checked={formData.documents.address_proof}
                    onChange={(e) => setFormData({
                      ...formData,
                      documents: { ...formData.documents, address_proof: e.target.checked }
                    })}
                  />
                  Address Proof
                </label>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? (
                  <span className="btn-loading">
                    <span className="spinner" aria-hidden="true" />
                    Validating...
                  </span>
                ) : 'Validate Application'}
              </button>
              {validating && (
                <span style={{ color: '#888', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span className="spinner spinner-sm" aria-hidden="true" />
                  Validating in real-time...
                </span>
              )}
            </div>
          </form>
        </div>

        {/* Right Column: Validation Results */}
        <div>
          {result && (
            <div className="results">
              <div 
                className={`risk-score-card ${getRiskLevel(result.rejection_risk_score)}`}
                style={{ borderColor: getRiskColor(result.rejection_risk_score) }}
              >
                <h3 style={{ margin: 0, fontSize: '1rem', color: '#888' }}>Rejection Risk Score</h3>
                <div 
                  className="risk-score"
                  style={{ color: getRiskColor(result.rejection_risk_score) }}
                >
                  {(result.rejection_risk_score * 100).toFixed(0)}%
                </div>
                <p className="risk-label" style={{ color: getRiskColor(result.rejection_risk_score) }}>
                  {getRiskLevel(result.rejection_risk_score).toUpperCase()} RISK
                </p>
                
                {/* Risk indicator bar */}
                <div style={{ 
                  width: '100%', 
                  height: '8px', 
                  backgroundColor: '#2a2a2a', 
                  borderRadius: '4px',
                  overflow: 'hidden',
                  marginTop: '1rem'
                }}>
                  <div style={{
                    width: `${result.rejection_risk_score * 100}%`,
                    height: '100%',
                    backgroundColor: getRiskColor(result.rejection_risk_score),
                    transition: 'width 0.5s ease'
                  }} />
                </div>
              </div>

              {result.validation_issues.length > 0 && (
                <div className="issues-section">
                  <h3>Validation Issues ({result.validation_issues.length})</h3>
                  <div className="issues-list">
                    {result.validation_issues.map((issue, index) => (
                      <div key={index} className={`issue-card ${getSeverityColor(issue.severity)}`}>
                        <div className="issue-header">
                          <span className="severity-badge">{issue.severity}</span>
                          <span className="field-name">{issue.field_name}</span>
                        </div>
                        <p className="issue-type">{issue.issue_type}</p>
                        <p className="impact">Impact on risk: +{(issue.impact_on_risk * 100).toFixed(0)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.corrective_guidance.length > 0 && (
                <div className="guidance-section">
                  <h3>Corrective Guidance</h3>
                  <div className="guidance-list">
                    {result.corrective_guidance.map((guidance, index) => (
                      <div key={index} className="guidance-card">
                        <div className="priority-badge">Priority {guidance.priority}</div>
                        <div className="guidance-content">
                          <p className="guidance-english"><strong>English:</strong> {guidance.guidance_text_english}</p>
                          <p className="guidance-hindi"><strong>हिंदी:</strong> {guidance.guidance_text_hindi}</p>
                          <p className="suggested-action">
                            <strong>Suggested Action:</strong> {guidance.suggested_action}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.validation_issues.length === 0 && (
                <div className="success-box">
                  <h3 style={{ color: '#10b981', marginTop: 0 }}>✓ Application Ready</h3>
                  <p>No validation issues found</p>
                  <p>Application is ready for submission</p>
                  <p style={{ fontSize: '0.9rem', color: '#888', marginTop: '1rem' }}>
                    The application meets all eligibility criteria and has all required documents.
                  </p>
                </div>
              )}
            </div>
          )}

          {!result && (
            <div style={{ 
              backgroundColor: '#1a1a1a', 
              padding: '2rem', 
              borderRadius: '8px',
              textAlign: 'center',
              color: '#888'
            }}>
              <p style={{ fontSize: '3rem', margin: '0 0 1rem 0' }}>📋</p>
              <p>Fill in the application details to see real-time validation results</p>
              <p style={{ fontSize: '0.9rem', marginTop: '1rem' }}>
                Validation updates automatically as you type
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Rejection Pattern Analysis — collapsible */}
      <div style={{ marginTop: '2rem' }}>
        <button
          onClick={() => setShowRejectionPatterns((prev) => !prev)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'none',
            border: '1px solid #333',
            borderRadius: '6px',
            color: '#667eea',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: 'pointer',
            padding: '0.6rem 1.25rem',
            transition: 'border-color 0.2s ease, background-color 0.2s ease',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = '#2a2a2a'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = '#667eea'
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = 'transparent'
            ;(e.currentTarget as HTMLButtonElement).style.borderColor = '#333'
          }}
        >
          <span style={{ fontSize: '0.85rem', transition: 'transform 0.2s ease', display: 'inline-block', transform: showRejectionPatterns ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
          Rejection Pattern Analysis
        </button>

        {showRejectionPatterns && (
          <RejectionPatternDashboard schemeType={formData.scheme_type} />
        )}
      </div>

      {/* Triage Queue */}
      <TriageQueue />

      {/* Guidance Overlay — slide-in panel */}
      <GuidanceOverlay
        schemeType={formData.scheme_type}
        activeField={focusedField}
        language={language}
      />
    </div>
  )
}

export default OperatorAssistant
