import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useLanguage } from '../contexts/LanguageContext'

// Mock data for metrics
const mockMetrics = {
  enrollmentsDiscovered: 247,
  grievancesResolved: 189,
  applicationsValidated: 412,
  avgResolutionTime: 4.2, // days
  approvalRate: 78.5 // percentage
}

// Mock data for weekly trends
const weeklyTrends = [
  { period: 'Week 1', enrollments: 45, grievances: 32, applications: 78 },
  { period: 'Week 2', enrollments: 52, grievances: 41, applications: 85 },
  { period: 'Week 3', enrollments: 61, grievances: 38, applications: 92 },
  { period: 'Week 4', enrollments: 48, grievances: 45, applications: 88 },
  { period: 'Week 5', enrollments: 41, grievances: 33, applications: 69 }
]

// Mock data for monthly trends
const monthlyTrends = [
  { period: 'Jan', enrollments: 180, grievances: 145, applications: 320 },
  { period: 'Feb', enrollments: 195, grievances: 158, applications: 345 },
  { period: 'Mar', enrollments: 210, grievances: 172, applications: 380 },
  { period: 'Apr', enrollments: 247, grievances: 189, applications: 412 }
]

// Mock data for geographic distribution
const geographicData = [
  { district: 'Raipur', enrollments: 68, grievances: 52, applications: 115 },
  { district: 'Bilaspur', enrollments: 45, grievances: 38, applications: 87 },
  { district: 'Durg', enrollments: 52, grievances: 41, applications: 95 },
  { district: 'Rajnandgaon', enrollments: 31, grievances: 24, applications: 58 },
  { district: 'Korba', enrollments: 28, grievances: 19, applications: 42 },
  { district: 'Raigarh', enrollments: 23, grievances: 15, applications: 35 }
]

function Dashboard() {
  const { t } = useLanguage()
  const [timeRange, setTimeRange] = useState<'weekly' | 'monthly'>('weekly')

  const trendData = timeRange === 'weekly' ? weeklyTrends : monthlyTrends

  return (
    <div className="dashboard">
      {/* Hero / Landing Section */}
      <div className="hero-section">
        <div className="hero-headline">
          <span className="hero-icon">🏛️</span>
          <div>
            <h2 className="hero-title">Moving from digitization to intelligent governance</h2>
            <p className="hero-subtitle">
              NagarikAI brings AI-powered intelligence to citizen services — proactively reaching
              eligible beneficiaries, resolving grievances faster, and guiding operators to
              higher-quality applications.
            </p>
          </div>
        </div>
        <div className="pillars-grid">
          <div className="pillar-card pillar-blue">
            <div className="pillar-icon">👥</div>
            <h3>Beneficiary Discovery</h3>
            <p>
              Cross-references civil death records with welfare databases to proactively identify
              eligible but unenrolled citizens — no one falls through the cracks.
            </p>
          </div>
          <div className="pillar-card pillar-amber">
            <div className="pillar-icon">📣</div>
            <h3>Grievance Intelligence</h3>
            <p>
              Classifies Hindi and English grievances using multilingual AI, routes them to the
              right department, and auto-escalates when SLA deadlines are at risk.
            </p>
          </div>
          <div className="pillar-card pillar-green">
            <div className="pillar-icon">📋</div>
            <h3>CSC Operator Assistant</h3>
            <p>
              Validates applications in real-time, predicts rejection risk, and provides bilingual
              corrective guidance so operators submit complete, accurate applications.
            </p>
          </div>
        </div>
      </div>

      <h2>{t('dashboard.title')}</h2>
      <p className="subtitle">{t('dashboard.subtitle')}</p>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <h3>{t('dashboard.enrollments')}</h3>
            <div className="metric-value">{mockMetrics.enrollmentsDiscovered}</div>
            <div className="metric-label">{t('dashboard.enrollmentsLabel')}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <h3>{t('dashboard.grievances')}</h3>
            <div className="metric-value">{mockMetrics.grievancesResolved}</div>
            <div className="metric-label">{t('dashboard.grievancesLabel').replace('{days}', mockMetrics.avgResolutionTime.toString())}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📋</div>
          <div className="metric-content">
            <h3>{t('dashboard.applications')}</h3>
            <div className="metric-value">{mockMetrics.applicationsValidated}</div>
            <div className="metric-label">{t('dashboard.applicationsLabel').replace('{rate}', mockMetrics.approvalRate.toString())}</div>
          </div>
        </div>
      </div>

      {/* Trends Section */}
      <div className="dashboard-section">
        <div className="section-header">
          <h3>{t('dashboard.trends')}</h3>
          <div className="time-range-toggle">
            <button 
              className={timeRange === 'weekly' ? 'active' : ''}
              onClick={() => setTimeRange('weekly')}
            >
              {t('dashboard.weekly')}
            </button>
            <button 
              className={timeRange === 'monthly' ? 'active' : ''}
              onClick={() => setTimeRange('monthly')}
            >
              {t('dashboard.monthly')}
            </button>
          </div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="period" stroke="#aaa" />
              <YAxis stroke="#aaa" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#2a2a2a', border: '1px solid #444' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Bar dataKey="enrollments" fill="#4CAF50" name={t('dashboard.enrollments')} />
              <Bar dataKey="grievances" fill="#2196F3" name={t('dashboard.grievances')} />
              <Bar dataKey="applications" fill="#FF9800" name={t('dashboard.applications')} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Geographic Distribution Section */}
      <div className="dashboard-section">
        <h3>{t('dashboard.geographic')}</h3>
        <div className="geo-table-container">
          <table className="geo-table">
            <thead>
              <tr>
                <th>{t('dashboard.district')}</th>
                <th>{t('dashboard.enrollments')}</th>
                <th>{t('dashboard.grievances')}</th>
                <th>{t('dashboard.applications')}</th>
                <th>{t('dashboard.total')}</th>
              </tr>
            </thead>
            <tbody>
              {geographicData.map((row) => (
                <tr key={row.district}>
                  <td className="district-name">{row.district}</td>
                  <td>{row.enrollments}</td>
                  <td>{row.grievances}</td>
                  <td>{row.applications}</td>
                  <td className="total-cell">
                    {row.enrollments + row.grievances + row.applications}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="total-row">
                <td>{t('dashboard.total')}</td>
                <td>{geographicData.reduce((sum, row) => sum + row.enrollments, 0)}</td>
                <td>{geographicData.reduce((sum, row) => sum + row.grievances, 0)}</td>
                <td>{geographicData.reduce((sum, row) => sum + row.applications, 0)}</td>
                <td className="total-cell">
                  {geographicData.reduce((sum, row) => 
                    sum + row.enrollments + row.grievances + row.applications, 0
                  )}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Impact Summary */}
      <div className="dashboard-section impact-summary">
        <h3>{t('dashboard.impact')}</h3>
        <div className="impact-grid">
          <div className="impact-item">
            <span className="impact-label">{t('dashboard.beneficiariesReached')}</span>
            <span className="impact-value">247 {t('dashboard.families')}</span>
          </div>
          <div className="impact-item">
            <span className="impact-label">{t('dashboard.avgResolution')}</span>
            <span className="impact-value">4.2 {t('dashboard.days')}</span>
          </div>
          <div className="impact-item">
            <span className="impact-label">{t('dashboard.approvalRate')}</span>
            <span className="impact-value">78.5%</span>
          </div>
          <div className="impact-item">
            <span className="impact-label">{t('dashboard.districtsCovered')}</span>
            <span className="impact-value">6 {t('dashboard.districts')}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
