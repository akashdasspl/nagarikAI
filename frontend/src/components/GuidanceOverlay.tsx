import { useState, useRef, useEffect } from 'react'

interface GuidanceResponse {
  intent: string
  scheme_type: string
  referenced_field: string
  referenced_scheme: string
  response_text: string
  language: string
}

interface Message {
  role: 'user' | 'assistant'
  text: string
}

interface GuidanceOverlayProps {
  schemeType: string
  activeField: string
  language: string
}

// Extend window for Web Speech API
declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    SpeechRecognition: any
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitSpeechRecognition: any
  }
}

function GuidanceOverlay({ schemeType, activeField, language }: GuidanceOverlayProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [voiceError, setVoiceError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<unknown>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Local guidance cache — mirrors backend guidance_interface.py
  const GUIDANCE: Record<string, Record<string, Record<string, string>>> = {
    document_list: {
      widow_pension: { hi: 'विधवा पेंशन के लिए आवश्यक दस्तावेज़: मृत्यु प्रमाण पत्र, आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।' },
      disability_pension: { hi: 'विकलांग पेंशन के लिए: विकलांगता प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।' },
      old_age_pension: { hi: 'वृद्धावस्था पेंशन के लिए: आयु प्रमाण पत्र, आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।' },
      ration_card: { hi: 'राशन कार्ड के लिए: आधार कार्ड, निवास प्रमाण पत्र, परिवार के सदस्यों की जानकारी।' },
      scholarship: { hi: 'छात्रवृत्ति के लिए: आयु प्रमाण पत्र, शैक्षणिक प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।' },
      _default: { hi: 'आवश्यक दस्तावेज़: आधार कार्ड, निवास प्रमाण पत्र, बैंक पासबुक।' },
    },
    eligibility_criteria: {
      widow_pension: { hi: 'विधवा पेंशन के लिए पात्रता: आवेदक विधवा होनी चाहिए, आयु 18 वर्ष से अधिक, वार्षिक आय 1 लाख से कम।' },
      disability_pension: { hi: 'विकलांग पेंशन के लिए: 40% या अधिक विकलांगता, आयु 18 वर्ष से अधिक।' },
      old_age_pension: { hi: 'वृद्धावस्था पेंशन के लिए: आयु 60 वर्ष या अधिक, वार्षिक आय 80,000 से कम।' },
      ration_card: { hi: 'राशन कार्ड के लिए: परिवार की वार्षिक आय 1.5 लाख से कम।' },
      scholarship: { hi: 'छात्रवृत्ति के लिए: आयु 5-25 वर्ष, शैक्षणिक संस्थान में नामांकित।' },
      _default: { hi: 'पात्रता के लिए कृपया संबंधित योजना की शर्तें जांचें।' },
    },
    rejection_reasons: {
      widow_pension: { hi: 'विधवा पेंशन अस्वीकृति के सामान्य कारण: मृत्यु प्रमाण पत्र नहीं, आय सीमा से अधिक, दस्तावेज़ अपूर्ण।' },
      disability_pension: { hi: 'विकलांग पेंशन अस्वीकृति: विकलांगता प्रमाण पत्र की वैधता समाप्त, प्रतिशत कम।' },
      old_age_pension: { hi: 'वृद्धावस्था पेंशन अस्वीकृति: आयु प्रमाण नहीं, आय सीमा से अधिक।' },
      ration_card: { hi: 'राशन कार्ड अस्वीकृति: आय सीमा से अधिक, पहले से कार्ड मौजूद।' },
      scholarship: { hi: 'छात्रवृत्ति अस्वीकृति: आयु सीमा से बाहर, संस्थान मान्यता प्राप्त नहीं।' },
      _default: { hi: 'अस्वीकृति के सामान्य कारण: दस्तावेज़ अपूर्ण, पात्रता शर्तें पूरी नहीं।' },
    },
    field_definition: {
      _default: { hi: 'कृपया इस फ़ील्ड में सही और पूर्ण जानकारी भरें। यदि आपको सहायता चाहिए तो दस्तावेज़, पात्रता या अस्वीकृति के बारे में पूछें।' },
    },
  }

  const inferIntent = (text: string): string => {
    const lower = text.toLowerCase()
    
    // Document list
    if (lower.match(/document|कागज|दस्तावेज|certificate|proof|attach|form|fill|भर|kya chahiye|kya lagega|kaun se|which doc|what doc|papers|kagaz/)) 
      return 'document_list'
    
    // Eligibility criteria
    if (lower.match(/eligible|eligib|पात्र|qualify|criteria|condition|शर्त|kaun apply|who can|age limit|income limit|umar|aayu|आयु|आय सीमा|patrata/)) 
      return 'eligibility_criteria'
    
    // Rejection reasons
    if (lower.match(/reject|अस्वीकृत|नामंजूर|denied|reason|why|क्यों|kyun|kyu|refuse|namanzu|cancel|रद्द/)) 
      return 'rejection_reasons'
    
    // Application process
    if (lower.match(/process|प्रक्रिया|prakriya|how to apply|kaise bhare|कैसे भरें|steps|procedure|submit|जमा|apply kaise|application kaise/)) 
      return 'application_process'
    
    // Fees and charges
    if (lower.match(/fee|fees|charge|शुल्क|shulk|cost|kitna lagega|कितना लगेगा|paisa|rupees|money|payment/)) 
      return 'fees_and_charges'
    
    // Processing time
    if (lower.match(/time|समय|kitne din|कितने दिन|how long|duration|when|kab|कब|milega|मिलेगा|processing|approval/)) 
      return 'processing_time'
    
    // Contact support
    if (lower.match(/contact|संपर्क|sampark|help|मदद|madad|support|helpline|phone|number|call|office|karyalay|कार्यालय/)) 
      return 'contact_support'
    
    // Common mistakes
    if (lower.match(/mistake|गलती|galti|error|wrong|गलत|avoid|बचें|common|problem|issue|dhyan|ध्यान/)) 
      return 'common_mistakes'
    
    // Field-specific context
    if (lower.match(/age|umar|aayu|dob|date of birth|जन्म/)) return 'eligibility_criteria'
    if (lower.match(/income|salary|aamdani|आय|paisa/)) return 'eligibility_criteria'
    if (lower.match(/name|naam|नाम/)) return 'field_definition'
    
    // Default to most useful answer
    return 'document_list'
  }

  const getLocalGuidance = (intent: string, scheme: string, question: string): string => {
    const lower = question.toLowerCase()
    const intentMap = GUIDANCE[intent] || GUIDANCE['document_list']
    const schemeMap = intentMap[scheme] || intentMap['_default'] || {}
    const base = schemeMap['hi'] || ''

    // Add field-specific context if active field is set
    const fieldHints: Record<string, string> = {
      age: ' आयु फ़ील्ड में वर्षों में आयु भरें (जैसे: 45)।',
      date_of_birth: ' जन्म तिथि DD/MM/YYYY प्रारूप में भरें।',
      income: ' वार्षिक आय रुपयों में भरें (जैसे: 80000)।',
      applicant_name: ' आवेदक का पूरा नाम भरें जैसा आधार कार्ड पर है।',
      address: ' पूरा पता भरें — गाँव, तहसील, जिला सहित।',
      phone: ' 10 अंकों का मोबाइल नंबर भरें।',
    }

    // Short/unclear queries get a helpful prompt
    if (lower.length <= 3 || lower.match(/^(h|hi|hello|help|kya|what|how|bata|batao)$/)) {
      const scheme_name = scheme.replace(/_/g, ' ')
      return `${scheme_name} के बारे में पूछें:\n• दस्तावेज़ के लिए: "कौन से दस्तावेज़ चाहिए"\n• पात्रता के लिए: "कौन आवेदन कर सकता है"\n• अस्वीकृति के लिए: "आवेदन क्यों रद्द होता है"`
    }

    const fieldHint = activeField ? (fieldHints[activeField] || '') : ''
    return base + fieldHint
  }

  const sendQuery = async (questionText: string) => {
    if (!questionText.trim()) return

    const userMsg: Message = { role: 'user', text: questionText }
    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    setLoading(true)

    const intent = inferIntent(questionText)
    const scheme = schemeType || 'widow_pension'

    // Try API first, fall back to local cache
    try {
      const res = await fetch('/api/guidance/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent,
          scheme_type: scheme,
          active_field: activeField || '',
          language: 'hi',
          question_text: questionText,
        }),
        signal: AbortSignal.timeout(3000),
      })
      if (res.ok) {
        const data: GuidanceResponse = await res.json()
        const text = data.response_text?.trim()
        if (text && !text.includes('{field}')) {
          setMessages((prev) => [...prev, { role: 'assistant', text }])
          setLoading(false)
          return
        }
      }
    } catch {
      // fall through to local
    }

    // Local fallback
    const localText = getLocalGuidance(intent, scheme, questionText)
    setMessages((prev) => [...prev, { role: 'assistant', text: localText }])
    setLoading(false)
  }

  const handleTextSend = () => {
    if (inputText.trim()) sendQuery(inputText.trim())
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleTextSend()
    }
  }

  const startVoiceInput = async () => {
    console.log('startVoiceInput called')
    setVoiceError(null)
    
    // First check microphone access
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      console.log('✓ Microphone accessible')
      stream.getTracks().forEach(track => track.stop())
    } catch (err) {
      console.error('✗ Microphone access denied:', err)
      setVoiceError('Cannot access microphone. Please allow microphone permission.')
      return
    }
    
    // Check browser support
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognitionAPI) {
      setVoiceError('Voice input not supported. Please use Chrome or Edge.')
      return
    }

    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const recognition: any = new SpeechRecognitionAPI()
      recognition.lang = 'hi-IN'
      recognition.interimResults = true
      recognition.maxAlternatives = 1
      recognition.continuous = true

      let transcript = ''
      let silenceTimeout: NodeJS.Timeout | null = null
      let hasStartedSpeaking = false
      let restartCount = 0
      const MAX_RESTARTS = 3

      recognition.onstart = () => {
        console.log('🎤 Recording started')
        setIsRecording(true)
        transcript = ''
      }

      recognition.onresult = (event: any) => {
        console.log('📝 Got result')
        hasStartedSpeaking = true
        
        // Clear previous silence timeout
        if (silenceTimeout) clearTimeout(silenceTimeout)
        
        // Build transcript
        transcript = ''
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript + ' '
          }
        }
        
        console.log('Transcript so far:', transcript)
        
        // Stop after 2 seconds of silence if we have text
        if (transcript.trim()) {
          silenceTimeout = setTimeout(() => {
            console.log('⏹ Stopping due to silence')
            recognition.stop()
          }, 2000)
        }
      }

      recognition.onerror = (event: any) => {
        console.error('❌ Error:', event.error)
        if (silenceTimeout) clearTimeout(silenceTimeout)
        setIsRecording(false)
        
        if (event.error === 'no-speech') {
          setVoiceError('No speech detected. Please speak clearly.')
        } else if (event.error === 'not-allowed') {
          setVoiceError('Microphone permission denied.')
        } else {
          setVoiceError('Voice recognition failed. Please try again.')
        }
      }

      recognition.onend = () => {
        console.log('⏹ Recording ended. Transcript:', transcript, 'hasStartedSpeaking:', hasStartedSpeaking)
        if (silenceTimeout) clearTimeout(silenceTimeout)
        
        if (transcript.trim()) {
          setInputText(transcript.trim())
          setIsRecording(false)
          console.log('✓ Text added to search bar')
        } else if (!hasStartedSpeaking && restartCount < MAX_RESTARTS) {
          // No speech detected yet, try restarting
          restartCount++
          console.log(`🔄 Restarting (attempt ${restartCount}/${MAX_RESTARTS})...`)
          try {
            setTimeout(() => recognition.start(), 100)
          } catch (err) {
            console.error('Failed to restart:', err)
            setIsRecording(false)
            setVoiceError('No speech detected. Please try again.')
          }
        } else {
          setIsRecording(false)
          setVoiceError('No speech detected. Please speak clearly and try again.')
        }
      }

      recognitionRef.current = recognition
      recognition.start()
    } catch (error) {
      console.error('Failed to start:', error)
      setVoiceError('Failed to start voice input.')
      setIsRecording(false)
    }
  }

  const stopVoiceInput = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ;(recognitionRef.current as any)?.stop()
    setIsRecording(false)
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label={isOpen ? 'Close guidance panel' : 'Open guidance panel'}
        style={{
          position: 'fixed',
          right: isOpen ? '364px' : '0',
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1001,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: isOpen ? '8px 0 0 8px' : '8px 0 0 8px',
          padding: '0.75rem 0.6rem',
          cursor: 'pointer',
          fontSize: '1.4rem',
          boxShadow: '-2px 0 12px rgba(0,0,0,0.4)',
          transition: 'right 0.3s ease',
          writingMode: 'vertical-rl',
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          lineHeight: 1,
        }}
      >
        💬
      </button>

      {/* Slide-in panel */}
      <div
        role="complementary"
        aria-label="Guidance assistant panel"
        style={{
          position: 'fixed',
          top: 0,
          right: isOpen ? 0 : '-364px',
          width: '360px',
          height: '100vh',
          backgroundColor: '#1a1a1a',
          borderLeft: '1px solid #333',
          boxShadow: '-4px 0 24px rgba(0,0,0,0.5)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          transition: 'right 0.3s ease',
        }}
      >
        {/* Header */}
        <div
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            padding: '1rem 1.25rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0,
          }}
        >
          <div>
            <div style={{ color: '#fff', fontWeight: 700, fontSize: '1rem' }}>
              💡 Guidance Assistant
            </div>
            <div style={{ color: 'rgba(255,255,255,0.75)', fontSize: '0.8rem', marginTop: '0.2rem' }}>
              {schemeType ? schemeType.replace(/_/g, ' ') : 'Select a scheme'}{activeField ? ` · ${activeField}` : ''}
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            aria-label="Close guidance panel"
            style={{
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: '#fff',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              fontSize: '1.1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            ×
          </button>
        </div>

        {/* Messages area */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
          }}
        >
          {messages.length === 0 && (
            <div style={{ color: '#666', fontSize: '0.9rem', textAlign: 'center', marginTop: '1rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🤝</div>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: '#888' }}>
                Quick questions or type your own
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                backgroundColor: msg.role === 'user' ? '#667eea' : '#2a2a2a',
                color: '#fff',
                borderRadius: msg.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                padding: '0.6rem 0.9rem',
                fontSize: '0.9rem',
                lineHeight: 1.5,
                wordBreak: 'break-word',
              }}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div
              style={{
                alignSelf: 'flex-start',
                backgroundColor: '#2a2a2a',
                borderRadius: '12px 12px 12px 2px',
                padding: '0.6rem 0.9rem',
                color: '#888',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <span
                style={{
                  display: 'inline-block',
                  width: '12px',
                  height: '12px',
                  border: '2px solid rgba(255,255,255,0.2)',
                  borderTopColor: '#667eea',
                  borderRadius: '50%',
                  animation: 'spin 0.7s linear infinite',
                }}
              />
              Thinking…
            </div>
          )}

          <div ref={messagesEndRef} />
          
          {/* Quick question buttons - always visible */}
          <div style={{ marginTop: messages.length > 0 ? '1rem' : '0', paddingTop: messages.length > 0 ? '1rem' : '0', borderTop: messages.length > 0 ? '1px solid #333' : 'none' }}>
            <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem', color: '#888', textAlign: 'center' }}>
              {messages.length > 0 ? 'Ask another question:' : ''}
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <button
                onClick={() => sendQuery('कौन से दस्तावेज़ चाहिए')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                📄 कौन से दस्तावेज़ चाहिए?
              </button>
              
              <button
                onClick={() => sendQuery('पात्रता क्या है')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                ✅ पात्रता क्या है?
              </button>
              
              <button
                onClick={() => sendQuery('आवेदन कैसे करें')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                📝 आवेदन कैसे करें?
              </button>
              
              <button
                onClick={() => sendQuery('कितने दिन में मिलेगा')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                ⏱️ कितने दिन में मिलेगा?
              </button>
              
              <button
                onClick={() => sendQuery('आवेदन क्यों रद्द होता है')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                ❌ आवेदन क्यों रद्द होता है?
              </button>
              
              <button
                onClick={() => sendQuery('कितना शुल्क लगेगा')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                💰 कितना शुल्क लगेगा?
              </button>
              
              <button
                onClick={() => sendQuery('हेल्पलाइन नंबर')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                📞 हेल्पलाइन नंबर?
              </button>
              
              <button
                onClick={() => sendQuery('आम गलतियां')}
                disabled={loading}
                style={{
                  background: 'rgba(102,126,234,0.1)',
                  border: '1px solid rgba(102,126,234,0.3)',
                  borderRadius: '8px',
                  color: '#667eea',
                  padding: '0.7rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.background = 'rgba(102,126,234,0.2)'
                    e.currentTarget.style.borderColor = '#667eea'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(102,126,234,0.1)'
                  e.currentTarget.style.borderColor = 'rgba(102,126,234,0.3)'
                }}
              >
                ⚠️ आम गलतियां क्या हैं?
              </button>
            </div>
          </div>
        </div>

        {/* Voice error */}
        {voiceError && (
          <div
            style={{
              backgroundColor: 'rgba(239,68,68,0.1)',
              borderTop: '1px solid #ef4444',
              padding: '0.5rem 1rem',
              color: '#ef4444',
              fontSize: '0.8rem',
              flexShrink: 0,
            }}
          >
            {voiceError}
          </div>
        )}

        {/* Input area */}
        <div
          style={{
            borderTop: '1px solid #333',
            padding: '0.75rem 1rem',
            flexShrink: 0,
            backgroundColor: '#1a1a1a',
          }}
        >
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={language === 'hi' ? 'प्रश्न पूछें…' : 'Ask a question…'}
              aria-label="Type your guidance question"
              disabled={loading}
              style={{
                flex: 1,
                backgroundColor: '#2a2a2a',
                border: '1px solid #444',
                borderRadius: '6px',
                color: '#fff',
                padding: '0.55rem 0.75rem',
                fontSize: '0.9rem',
                outline: 'none',
              }}
            />

            {/* Voice button */}
            <button
              onClick={isRecording ? stopVoiceInput : startVoiceInput}
              aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
              disabled={loading}
              style={{
                background: isRecording
                  ? 'rgba(239,68,68,0.15)'
                  : 'rgba(102,126,234,0.15)',
                border: `1px solid ${isRecording ? '#ef4444' : '#667eea'}`,
                borderRadius: '6px',
                color: isRecording ? '#ef4444' : '#667eea',
                width: '36px',
                height: '36px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                transition: 'all 0.2s ease',
                opacity: loading ? 0.5 : 1,
              }}
            >
              {isRecording ? '⏹' : '🎤'}
            </button>

            {/* Send button */}
            <button
              onClick={handleTextSend}
              aria-label="Send message"
              disabled={loading || !inputText.trim()}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '6px',
                color: '#fff',
                width: '36px',
                height: '36px',
                cursor: inputText.trim() ? 'pointer' : 'not-allowed',
                opacity: inputText.trim() ? 1 : 0.5,
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                transition: 'opacity 0.2s ease',
              }}
            >
              ➤
            </button>
          </div>

          {isRecording && (
            <p style={{ color: '#ef4444', fontSize: '0.78rem', margin: '0.4rem 0 0 0', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', animation: 'pulse 1s infinite' }} />
              Recording… speak now
            </p>
          )}
        </div>
      </div>

      {/* Inline keyframe styles */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  )
}

export default GuidanceOverlay
