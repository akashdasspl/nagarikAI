import { useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'

interface Beneficiary {
  beneficiary_name: string
  relationship: string
  scheme_type: string
  confidence_score: number
  eligibility_reasoning: string
  contact_info?: {
    aadhaar_id?: string
    address?: string
  }
}

function BeneficiaryDiscovery() {
  const { t } = useLanguage()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([])
  const [searchMode, setSearchMode] = useState<'death' | 'aadhaar'>('death')
  const [formData, setFormData] = useState({
    record_id: '',
    name: '',
    father_name: '',
    date_of_death: '',
    age: '',
    gender: 'M',
    district: '',
    village: '',
  })
  const [aadhaarFormData, setAadhaarFormData] = useState({
    aadhaar_number: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      let endpoint = '/api/beneficiary/discover'
      let payload: any
      
      if (searchMode === 'death') {
        // Death record search
        payload = {
          record_id: formData.record_id,
          name: formData.name,
          father_name: formData.father_name,
          date_of_death: formData.date_of_death,
          age: parseInt(formData.age),
          gender: formData.gender,
          district: formData.district,
          village: formData.village,
        }
      } else {
        // Aadhaar search
        endpoint = '/api/beneficiary/search-by-aadhaar'
        payload = {
          aadhaar_number: aadhaarFormData.aadhaar_number,
        }
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }
      
      const data = await response.json()
      // Backend already sorts by confidence score (Requirement 1.4), but ensure it
      const sortedBeneficiaries = (data.beneficiaries || []).sort(
        (a: Beneficiary, b: Beneficiary) => b.confidence_score - a.confidence_score
      )
      setBeneficiaries(sortedBeneficiaries)
    } catch (error) {
      console.error('Error discovering beneficiaries:', error)
      setError(error instanceof Error ? error.message : 'Failed to discover beneficiaries. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceLevel = (score: number): 'high' | 'medium' | 'low' => {
    if (score >= 0.8) return 'high'
    if (score >= 0.6) return 'medium'
    return 'low'
  }

  const getConfidenceLabel = (score: number): string => {
    const level = getConfidenceLevel(score)
    if (level === 'high') return t('beneficiary.high')
    if (level === 'medium') return t('beneficiary.medium')
    return t('beneficiary.low')
  }

  return (
    <div className="page">
      <h2>{t('beneficiary.title')}</h2>
      <p className="description">
        {t('beneficiary.description')}
      </p>

      {/* Search Mode Toggle */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '1rem', backgroundColor: '#1a1a1a', padding: '0.5rem', borderRadius: '8px', width: 'fit-content' }}>
          <button
            type="button"
            onClick={() => setSearchMode('death')}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: searchMode === 'death' ? '#6366f1' : 'transparent',
              color: searchMode === 'death' ? 'white' : '#888',
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'all 0.2s'
            }}
          >
            🪦 Death Record Search
          </button>
          <button
            type="button"
            onClick={() => setSearchMode('aadhaar')}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: searchMode === 'aadhaar' ? '#6366f1' : 'transparent',
              color: searchMode === 'aadhaar' ? 'white' : '#888',
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'all 0.2s'
            }}
          >
            🆔 Aadhaar Search
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="form">
        {searchMode === 'death' ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="form-group">
              <label>{t('beneficiary.deathRecordId')} *</label>
              <input
                type="text"
                value={formData.record_id}
                onChange={(e) => setFormData({ ...formData, record_id: e.target.value })}
                placeholder="e.g., CDR001"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.deceasedName')} *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Full name of deceased"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.fatherName')} *</label>
              <input
                type="text"
                value={formData.father_name}
                onChange={(e) => setFormData({ ...formData, father_name: e.target.value })}
                placeholder="Father's name"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.dateOfDeath')} *</label>
              <input
                type="date"
                value={formData.date_of_death}
                onChange={(e) => setFormData({ ...formData, date_of_death: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.age')} *</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                placeholder="Age"
                min="0"
                max="150"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.gender')} *</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                required
              >
                <option value="M">{t('beneficiary.male')}</option>
                <option value="F">{t('beneficiary.female')}</option>
              </select>
            </div>

            <div className="form-group">
              <label>{t('beneficiary.district')} *</label>
              <input
                type="text"
                value={formData.district}
                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                placeholder="District name"
                required
              />
            </div>

            <div className="form-group">
              <label>{t('beneficiary.village')} *</label>
              <input
                type="text"
                value={formData.village}
                onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                placeholder="Village name"
                required
              />
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '500px' }}>
            <div className="form-group">
              <label>Aadhaar Number *</label>
              <input
                type="text"
                value={aadhaarFormData.aadhaar_number}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 12)
                  setAadhaarFormData({ aadhaar_number: value })
                }}
                placeholder="Enter 12-digit Aadhaar number"
                pattern="[0-9]{12}"
                maxLength={12}
                required
              />
              <small style={{ color: '#888', marginTop: '0.5rem', display: 'block' }}>
                Enter the 12-digit Aadhaar number to find family members and check scheme eligibility
              </small>
            </div>
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary" style={{ marginTop: '1rem' }}>
          {loading ? (
            <span className="btn-loading">
              <span className="spinner" aria-hidden="true" />
              {searchMode === 'death' ? t('beneficiary.discovering') : 'Searching...'}
            </span>
          ) : (searchMode === 'death' ? t('beneficiary.discover') : 'Search by Aadhaar')}
        </button>
      </form>

      {error && (
        <div className="error-message" style={{
          backgroundColor: '#ef4444',
          color: 'white',
          padding: '1rem',
          borderRadius: '8px',
          marginTop: '1rem'
        }}>
          {error}
        </div>
      )}

      {loading && (
        <div className="skeleton-container" aria-busy="true" aria-label="Loading results">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton-row" />
          ))}
        </div>
      )}

      {beneficiaries.length > 0 && (
        <div className="results">
          <h3>{t('beneficiary.results')} ({beneficiaries.length})</h3>
          <p style={{ color: '#888', marginBottom: '1.5rem' }}>
            Potential widow pension beneficiaries ranked by eligibility confidence
          </p>
          
          <div className="beneficiary-table-container" style={{ overflowX: 'auto' }}>
            <table className="beneficiary-table" style={{
              width: '100%',
              backgroundColor: '#1a1a1a',
              borderRadius: '8px',
              overflow: 'hidden',
              borderCollapse: 'collapse'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#2a2a2a' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', color: '#fff', fontWeight: 600 }}>
                    {t('beneficiary.rank')}
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', color: '#fff', fontWeight: 600 }}>
                    {t('beneficiary.name')}
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', color: '#fff', fontWeight: 600 }}>
                    {t('beneficiary.confidence')}
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', color: '#fff', fontWeight: 600 }}>
                    {t('beneficiary.reasoning')}
                  </th>
                  <th style={{ padding: '1rem', textAlign: 'left', color: '#fff', fontWeight: 600 }}>
                    {t('beneficiary.details')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {beneficiaries.map((beneficiary, index) => (
                  <tr key={index} style={{
                    borderTop: '1px solid #333',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2a2a2a'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <td style={{ padding: '1rem', color: '#888', fontWeight: 600 }}>
                      #{index + 1}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ color: '#fff', fontWeight: 500, marginBottom: '0.25rem' }}>
                        {beneficiary.beneficiary_name}
                      </div>
                      <div style={{ color: '#888', fontSize: '0.85rem' }}>
                        {beneficiary.relationship} • {beneficiary.scheme_type.replace(/_/g, ' ')}
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                          width: '60px',
                          height: '8px',
                          backgroundColor: '#333',
                          borderRadius: '4px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            width: `${beneficiary.confidence_score * 100}%`,
                            height: '100%',
                            backgroundColor: getConfidenceLevel(beneficiary.confidence_score) === 'high' 
                              ? '#10b981' 
                              : getConfidenceLevel(beneficiary.confidence_score) === 'medium'
                              ? '#f59e0b'
                              : '#ef4444',
                            transition: 'width 0.3s ease'
                          }} />
                        </div>
                        <span className={`confidence-badge ${getConfidenceLevel(beneficiary.confidence_score)}`}>
                          {(beneficiary.confidence_score * 100).toFixed(0)}% {getConfidenceLabel(beneficiary.confidence_score)}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '1rem', color: '#ccc', lineHeight: 1.6 }}>
                      {beneficiary.eligibility_reasoning}
                    </td>
                    <td style={{ padding: '1rem', color: '#888', fontSize: '0.9rem' }}>
                      {beneficiary.contact_info?.aadhaar_id && (
                        <div style={{ marginBottom: '0.25rem' }}>
                          <strong style={{ color: '#aaa' }}>Aadhaar:</strong> {beneficiary.contact_info.aadhaar_id}
                        </div>
                      )}
                      {beneficiary.contact_info?.address && (
                        <div>
                          <strong style={{ color: '#aaa' }}>Address:</strong> {beneficiary.contact_info.address}
                        </div>
                      )}
                      {!beneficiary.contact_info?.aadhaar_id && !beneficiary.contact_info?.address && (
                        <span style={{ color: '#666' }}>No additional details</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="info-box" style={{ marginTop: '2rem' }}>
            <h4 style={{ color: '#10b981', marginBottom: '0.75rem' }}>Confidence Level Guide</h4>
            <div style={{ display: 'grid', gap: '0.5rem' }}>
              <p style={{ margin: 0 }}>
                <span className="confidence-badge high" style={{ marginRight: '0.5rem' }}>{t('beneficiary.high')} (≥80%)</span>
                Strong match across multiple databases - ready for field worker assignment
              </p>
              <p style={{ margin: 0 }}>
                <span className="confidence-badge medium" style={{ marginRight: '0.5rem' }}>{t('beneficiary.medium')} (60-79%)</span>
                Probable match - may require additional verification
              </p>
              <p style={{ margin: 0 }}>
                <span className="confidence-badge low" style={{ marginRight: '0.5rem' }}>{t('beneficiary.low')} (&lt;60%)</span>
                Possible match - manual review recommended
              </p>
            </div>
          </div>
        </div>
      )}

      {!loading && beneficiaries.length === 0 && !error && (
        <div className="info-box" style={{ marginTop: '2rem' }}>
          <p style={{ margin: 0, color: '#888' }}>
            {searchMode === 'death' 
              ? 'Enter death record details above to discover potential beneficiaries using AI-powered entity resolution across Civil Death Records, Ration Card Database, and Aadhaar Database.'
              : 'Enter an Aadhaar number to search for the person and their family members across government databases. The system will check eligibility for various welfare schemes.'}
          </p>
        </div>
      )}
    </div>
  )
}

export default BeneficiaryDiscovery
