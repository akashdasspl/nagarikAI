import { createContext, useContext, useState, ReactNode } from 'react'

type Language = 'en' | 'hi'

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

// Translations object
const translations: Record<string, Record<Language, string>> = {
  // Header
  'header.title': {
    en: 'NagarikAI Platform',
    hi: 'नागरिक AI प्लेटफॉर्म'
  },
  'header.tagline': {
    en: 'AI-Powered Citizen Service Intelligence',
    hi: 'AI-संचालित नागरिक सेवा बुद्धिमत्ता'
  },
  
  // Navigation
  'nav.beneficiary': {
    en: 'Beneficiary Discovery',
    hi: 'लाभार्थी खोज'
  },
  'nav.grievance': {
    en: 'Grievance Portal',
    hi: 'शिकायत पोर्टल'
  },
  'nav.operator': {
    en: 'Operator Assistant',
    hi: 'ऑपरेटर सहायक'
  },
  'nav.dashboard': {
    en: 'Dashboard',
    hi: 'डैशबोर्ड'
  },
  
  // Common
  'common.submit': {
    en: 'Submit',
    hi: 'जमा करें'
  },
  'common.loading': {
    en: 'Loading',
    hi: 'लोड हो रहा है'
  },
  'common.error': {
    en: 'Error',
    hi: 'त्रुटि'
  },
  'common.success': {
    en: 'Success',
    hi: 'सफलता'
  },
  
  // Beneficiary Discovery
  'beneficiary.title': {
    en: 'Beneficiary Discovery Engine',
    hi: 'लाभार्थी खोज इंजन'
  },
  'beneficiary.description': {
    en: 'Identify eligible but unenrolled citizens for welfare schemes using AI-powered entity resolution',
    hi: 'AI-संचालित इकाई समाधान का उपयोग करके कल्याण योजनाओं के लिए पात्र लेकिन अनामांकित नागरिकों की पहचान करें'
  },
  'beneficiary.deathRecordId': {
    en: 'Death Record ID',
    hi: 'मृत्यु रिकॉर्ड आईडी'
  },
  'beneficiary.deceasedName': {
    en: 'Deceased Name',
    hi: 'मृतक का नाम'
  },
  'beneficiary.fatherName': {
    en: "Father's Name",
    hi: 'पिता का नाम'
  },
  'beneficiary.dateOfDeath': {
    en: 'Date of Death',
    hi: 'मृत्यु की तारीख'
  },
  'beneficiary.age': {
    en: 'Age at Death',
    hi: 'मृत्यु के समय आयु'
  },
  'beneficiary.gender': {
    en: 'Gender',
    hi: 'लिंग'
  },
  'beneficiary.male': {
    en: 'Male',
    hi: 'पुरुष'
  },
  'beneficiary.female': {
    en: 'Female',
    hi: 'महिला'
  },
  'beneficiary.district': {
    en: 'District',
    hi: 'जिला'
  },
  'beneficiary.village': {
    en: 'Village',
    hi: 'गांव'
  },
  'beneficiary.discover': {
    en: 'Discover Beneficiaries',
    hi: 'लाभार्थियों की खोज करें'
  },
  'beneficiary.discovering': {
    en: 'Discovering Beneficiaries...',
    hi: 'लाभार्थियों की खोज हो रही है...'
  },
  'beneficiary.results': {
    en: 'Discovered Beneficiaries',
    hi: 'खोजे गए लाभार्थी'
  },
  'beneficiary.rank': {
    en: 'Rank',
    hi: 'रैंक'
  },
  'beneficiary.name': {
    en: 'Name',
    hi: 'नाम'
  },
  'beneficiary.confidence': {
    en: 'Confidence',
    hi: 'विश्वास'
  },
  'beneficiary.reasoning': {
    en: 'Eligibility Reasoning',
    hi: 'पात्रता तर्क'
  },
  'beneficiary.details': {
    en: 'Details',
    hi: 'विवरण'
  },
  'beneficiary.high': {
    en: 'High',
    hi: 'उच्च'
  },
  'beneficiary.medium': {
    en: 'Medium',
    hi: 'मध्यम'
  },
  'beneficiary.low': {
    en: 'Low',
    hi: 'निम्न'
  },
  
  // Grievance Portal
  'grievance.title': {
    en: 'Grievance Intelligence Portal',
    hi: 'शिकायत बुद्धिमत्ता पोर्टल'
  },
  'grievance.description': {
    en: 'Submit grievances in Hindi or English for automatic routing and tracking',
    hi: 'स्वचालित रूटिंग और ट्रैकिंग के लिए हिंदी या अंग्रेजी में शिकायतें जमा करें'
  },
  'grievance.language': {
    en: 'Language',
    hi: 'भाषा'
  },
  'grievance.hindi': {
    en: 'Hindi',
    hi: 'हिंदी'
  },
  'grievance.english': {
    en: 'English',
    hi: 'अंग्रेजी'
  },
  'grievance.description_label': {
    en: 'Grievance Description',
    hi: 'शिकायत विवरण'
  },
  'grievance.placeholder_hi': {
    en: 'Enter your grievance here...',
    hi: 'अपनी शिकायत यहाँ लिखें...'
  },
  'grievance.submit': {
    en: 'Submit Grievance',
    hi: 'शिकायत दर्ज करें'
  },
  'grievance.submitting': {
    en: 'Submitting...',
    hi: 'जमा हो रहा है...'
  },
  'grievance.submitted': {
    en: 'Grievance Submitted Successfully',
    hi: 'शिकायत सफलतापूर्वक दर्ज की गई'
  },
  'grievance.classification': {
    en: 'Classification Results',
    hi: 'वर्गीकरण परिणाम'
  },
  'grievance.category': {
    en: 'Category',
    hi: 'श्रेणी'
  },
  'grievance.id': {
    en: 'Grievance ID',
    hi: 'शिकायत आईडी'
  },
  'grievance.sla': {
    en: 'Predicted SLA Timeline',
    hi: 'अनुमानित SLA समयरेखा'
  },
  'grievance.hours': {
    en: 'hours',
    hi: 'घंटे'
  },
  'grievance.deadline': {
    en: 'Deadline',
    hi: 'समय सीमा'
  },
  'grievance.status': {
    en: 'Status Tracking',
    hi: 'स्थिति ट्रैकिंग'
  },
  'grievance.escalation': {
    en: 'Escalation Alerts',
    hi: 'एस्केलेशन अलर्ट'
  },
  
  // Operator Assistant
  'operator.title': {
    en: 'CSC Operator Assistant',
    hi: 'CSC ऑपरेटर सहायक'
  },
  'operator.description': {
    en: 'Validate applications before submission to reduce rejection rates. Real-time validation updates as you type.',
    hi: 'अस्वीकृति दर को कम करने के लिए सबमिशन से पहले आवेदनों को मान्य करें। टाइप करते समय रीयल-टाइम सत्यापन अपडेट।'
  },
  'operator.applicantName': {
    en: 'Applicant Name',
    hi: 'आवेदक का नाम'
  },
  'operator.age': {
    en: 'Age',
    hi: 'आयु'
  },
  'operator.dob': {
    en: 'Date of Birth',
    hi: 'जन्म तिथि'
  },
  'operator.income': {
    en: 'Annual Income (₹)',
    hi: 'वार्षिक आय (₹)'
  },
  'operator.address': {
    en: 'Address',
    hi: 'पता'
  },
  'operator.phone': {
    en: 'Phone Number',
    hi: 'फोन नंबर'
  },
  'operator.scheme': {
    en: 'Scheme Type',
    hi: 'योजना प्रकार'
  },
  'operator.documents': {
    en: 'Documents Submitted',
    hi: 'जमा किए गए दस्तावेज़'
  },
  'operator.validate': {
    en: 'Validate Application',
    hi: 'आवेदन सत्यापित करें'
  },
  'operator.validating': {
    en: 'Validating...',
    hi: 'सत्यापन हो रहा है...'
  },
  'operator.riskScore': {
    en: 'Rejection Risk Score',
    hi: 'अस्वीकृति जोखिम स्कोर'
  },
  'operator.highRisk': {
    en: 'HIGH RISK',
    hi: 'उच्च जोखिम'
  },
  'operator.mediumRisk': {
    en: 'MEDIUM RISK',
    hi: 'मध्यम जोखिम'
  },
  'operator.lowRisk': {
    en: 'LOW RISK',
    hi: 'कम जोखिम'
  },
  'operator.issues': {
    en: 'Validation Issues',
    hi: 'सत्यापन समस्याएं'
  },
  'operator.guidance': {
    en: 'Corrective Guidance',
    hi: 'सुधारात्मक मार्गदर्शन'
  },
  'operator.priority': {
    en: 'Priority',
    hi: 'प्राथमिकता'
  },
  'operator.ready': {
    en: 'Application Ready',
    hi: 'आवेदन तैयार'
  },
  
  // Dashboard
  'dashboard.title': {
    en: 'Analytics Dashboard',
    hi: 'विश्लेषण डैशबोर्ड'
  },
  'dashboard.subtitle': {
    en: 'Platform usage and impact metrics',
    hi: 'प्लेटफॉर्म उपयोग और प्रभाव मेट्रिक्स'
  },
  'dashboard.enrollments': {
    en: 'Enrollments Discovered',
    hi: 'खोजे गए नामांकन'
  },
  'dashboard.enrollmentsLabel': {
    en: 'Potential beneficiaries identified',
    hi: 'संभावित लाभार्थियों की पहचान की गई'
  },
  'dashboard.grievances': {
    en: 'Grievances Resolved',
    hi: 'हल की गई शिकायतें'
  },
  'dashboard.grievancesLabel': {
    en: 'Avg. {days} days resolution time',
    hi: 'औसत {days} दिन समाधान समय'
  },
  'dashboard.applications': {
    en: 'Applications Validated',
    hi: 'सत्यापित आवेदन'
  },
  'dashboard.applicationsLabel': {
    en: '{rate}% approval rate',
    hi: '{rate}% अनुमोदन दर'
  },
  'dashboard.trends': {
    en: 'Trends Over Time',
    hi: 'समय के साथ रुझान'
  },
  'dashboard.weekly': {
    en: 'Weekly',
    hi: 'साप्ताहिक'
  },
  'dashboard.monthly': {
    en: 'Monthly',
    hi: 'मासिक'
  },
  'dashboard.geographic': {
    en: 'Geographic Distribution by District',
    hi: 'जिले के अनुसार भौगोलिक वितरण'
  },
  'dashboard.district': {
    en: 'District',
    hi: 'जिला'
  },
  'dashboard.total': {
    en: 'Total',
    hi: 'कुल'
  },
  'dashboard.impact': {
    en: 'Platform Impact',
    hi: 'प्लेटफॉर्म प्रभाव'
  },
  'dashboard.beneficiariesReached': {
    en: 'Beneficiaries Reached:',
    hi: 'लाभार्थी पहुंचे:'
  },
  'dashboard.families': {
    en: 'families',
    hi: 'परिवार'
  },
  'dashboard.avgResolution': {
    en: 'Avg. Grievance Resolution:',
    hi: 'औसत शिकायत समाधान:'
  },
  'dashboard.days': {
    en: 'days',
    hi: 'दिन'
  },
  'dashboard.approvalRate': {
    en: 'Application Approval Rate:',
    hi: 'आवेदन अनुमोदन दर:'
  },
  'dashboard.districtsCovered': {
    en: 'Districts Covered:',
    hi: 'जिले कवर किए गए:'
  },
  'dashboard.districts': {
    en: 'districts',
    hi: 'जिले'
  },
  
  // Footer
  'footer.text': {
    en: 'Hackathon 2026 - Team blueBox - Chhattisgarh NIC Smart Governance Initiative',
    hi: 'हैकथॉन 2026 - टीम blueBox - छत्तीसगढ़ NIC स्मार्ट गवर्नेंस पहल'
  }
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en')

  const t = (key: string): string => {
    return translations[key]?.[language] || key
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
