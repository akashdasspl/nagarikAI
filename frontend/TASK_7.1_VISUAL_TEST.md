# Task 7.1: Visual Test Guide - Hindi Language Support

## Quick Visual Verification

This guide helps you quickly verify that Hindi translations are working correctly across all pages.

## Dashboard Page - Hindi Translations

### Page Header
- **English**: Analytics Dashboard
- **Hindi**: विश्लेषण डैशबोर्ड

### Subtitle
- **English**: Platform usage and impact metrics
- **Hindi**: प्लेटफॉर्म उपयोग और प्रभाव मेट्रिक्स

### Metric Cards

#### Card 1: Enrollments
- **Title (EN)**: Enrollments Discovered
- **Title (HI)**: खोजे गए नामांकन
- **Label (EN)**: Potential beneficiaries identified
- **Label (HI)**: संभावित लाभार्थियों की पहचान की गई

#### Card 2: Grievances
- **Title (EN)**: Grievances Resolved
- **Title (HI)**: हल की गई शिकायतें
- **Label (EN)**: Avg. 4.2 days resolution time
- **Label (HI)**: औसत 4.2 दिन समाधान समय

#### Card 3: Applications
- **Title (EN)**: Applications Validated
- **Title (HI)**: सत्यापित आवेदन
- **Label (EN)**: 78.5% approval rate
- **Label (HI)**: 78.5% अनुमोदन दर

### Trends Section

#### Section Header
- **English**: Trends Over Time
- **Hindi**: समय के साथ रुझान

#### Toggle Buttons
- **Weekly (EN)**: Weekly
- **Weekly (HI)**: साप्ताहिक
- **Monthly (EN)**: Monthly
- **Monthly (HI)**: मासिक

#### Chart Legend
- **Enrollments (EN)**: Enrollments Discovered
- **Enrollments (HI)**: खोजे गए नामांकन
- **Grievances (EN)**: Grievances Resolved
- **Grievances (HI)**: हल की गई शिकायतें
- **Applications (EN)**: Applications Validated
- **Applications (HI)**: सत्यापित आवेदन

### Geographic Distribution Table

#### Table Header
- **English**: Geographic Distribution by District
- **Hindi**: जिले के अनुसार भौगोलिक वितरण

#### Column Headers
- **District (EN)**: District
- **District (HI)**: जिला
- **Enrollments (EN)**: Enrollments Discovered
- **Enrollments (HI)**: खोजे गए नामांकन
- **Grievances (EN)**: Grievances Resolved
- **Grievances (HI)**: हल की गई शिकायतें
- **Applications (EN)**: Applications Validated
- **Applications (HI)**: सत्यापित आवेदन
- **Total (EN)**: Total
- **Total (HI)**: कुल

### Platform Impact Section

#### Section Header
- **English**: Platform Impact
- **Hindi**: प्लेटफॉर्म प्रभाव

#### Impact Items

1. **Beneficiaries Reached**
   - **Label (EN)**: Beneficiaries Reached:
   - **Label (HI)**: लाभार्थी पहुंचे:
   - **Value (EN)**: 247 families
   - **Value (HI)**: 247 परिवार

2. **Average Resolution**
   - **Label (EN)**: Avg. Grievance Resolution:
   - **Label (HI)**: औसत शिकायत समाधान:
   - **Value (EN)**: 4.2 days
   - **Value (HI)**: 4.2 दिन

3. **Approval Rate**
   - **Label (EN)**: Application Approval Rate:
   - **Label (HI)**: आवेदन अनुमोदन दर:
   - **Value**: 78.5% (same in both languages)

4. **Districts Covered**
   - **Label (EN)**: Districts Covered:
   - **Label (HI)**: जिले कवर किए गए:
   - **Value (EN)**: 6 districts
   - **Value (HI)**: 6 जिले

## Navigation Menu - Hindi Translations

- **Beneficiary Discovery (EN)**: Beneficiary Discovery
- **Beneficiary Discovery (HI)**: लाभार्थी खोज

- **Grievance Portal (EN)**: Grievance Portal
- **Grievance Portal (HI)**: शिकायत पोर्टल

- **Operator Assistant (EN)**: Operator Assistant
- **Operator Assistant (HI)**: ऑपरेटर सहायक

- **Dashboard (EN)**: Dashboard
- **Dashboard (HI)**: डैशबोर्ड

## Header - Hindi Translations

- **Title (EN)**: NagarikAI Platform
- **Title (HI)**: नागरिक AI प्लेटफॉर्म

- **Tagline (EN)**: AI-Powered Citizen Service Intelligence
- **Tagline (HI)**: AI-संचालित नागरिक सेवा बुद्धिमत्ता

- **Language Toggle**: Shows "हिंदी" when in English mode, shows "English" when in Hindi mode

## Footer - Hindi Translations

- **English**: Hackathon 2026 - Team blueBox - Chhattisgarh NIC Smart Governance Initiative
- **Hindi**: हैकथॉन 2026 - टीम blueBox - छत्तीसगढ़ NIC स्मार्ट गवर्नेंस पहल

## Font Rendering Verification

### Devanagari Characters to Check

The following Hindi characters should render clearly with proper spacing:

**Vowels**: अ आ इ ई उ ऊ ए ऐ ओ औ
**Consonants**: क ख ग घ च छ ज झ ट ठ ड ढ त थ द ध न प फ ब भ म य र ल व श ष स ह
**Conjuncts**: क्ष त्र ज्ञ श्र
**Vowel Marks**: का की कु कू के कै को कौ
**Numbers**: ० १ २ ३ ४ ५ ६ ७ ८ ९

### Sample Sentences

1. **विश्लेषण डैशबोर्ड** (Analytics Dashboard)
2. **प्लेटफॉर्म उपयोग और प्रभाव मेट्रिक्स** (Platform usage and impact metrics)
3. **संभावित लाभार्थियों की पहचान की गई** (Potential beneficiaries identified)
4. **औसत शिकायत समाधान** (Average grievance resolution)

## Testing Checklist

### Functional Tests
- [ ] Language toggle button is visible in header
- [ ] Clicking toggle switches language immediately
- [ ] All pages respond to language change
- [ ] Language persists during navigation between pages
- [ ] No console errors when switching languages

### Visual Tests
- [ ] Hindi text renders clearly (no boxes or missing characters)
- [ ] Font weight hierarchy is maintained (headings vs body text)
- [ ] Text alignment is correct
- [ ] No text overflow or wrapping issues
- [ ] Proper spacing between Hindi characters
- [ ] Numbers display correctly in both languages

### Cross-Browser Tests
- [ ] Chrome/Chromium - Hindi renders correctly
- [ ] Firefox - Hindi renders correctly
- [ ] Safari - Hindi renders correctly
- [ ] Edge - Hindi renders correctly

### Responsive Tests
- [ ] Mobile view - language toggle accessible
- [ ] Mobile view - Hindi text wraps properly
- [ ] Tablet view - all elements visible
- [ ] Desktop view - optimal layout

## Expected Behavior

1. **On Page Load**: Application starts in English by default
2. **On Toggle Click**: All UI elements switch to Hindi instantly
3. **On Navigation**: Language preference is maintained across pages
4. **On Refresh**: Language resets to English (no persistence implemented yet)

## Known Good States

### Dashboard in Hindi Mode
```
विश्लेषण डैशबोर्ड
प्लेटफॉर्म उपयोग और प्रभाव मेट्रिक्स

[Metric Cards showing Hindi labels]
खोजे गए नामांकन: 247
हल की गई शिकायतें: 189
सत्यापित आवेदन: 412

[Trends section with Hindi toggle buttons]
समय के साथ रुझान
[साप्ताहिक] [मासिक]

[Geographic table with Hindi headers]
जिला | खोजे गए नामांकन | हल की गई शिकायतें | सत्यापित आवेदन | कुल

[Impact summary with Hindi labels]
प्लेटफॉर्म प्रभाव
लाभार्थी पहुंचे: 247 परिवार
औसत शिकायत समाधान: 4.2 दिन
आवेदन अनुमोदन दर: 78.5%
जिले कवर किए गए: 6 जिले
```

## Troubleshooting

### Issue: Hindi text shows boxes (□)
**Solution**: Font not loaded. Check browser console for font loading errors. Verify Google Fonts CDN is accessible.

### Issue: Hindi text looks too thin/bold
**Solution**: Check font-weight in CSS. Noto Sans Devanagari supports weights 400, 500, 600, 700.

### Issue: Language doesn't switch
**Solution**: Check browser console for React errors. Verify LanguageContext is properly wrapped around App component.

### Issue: Some text remains in English
**Solution**: Check if translation key exists in LanguageContext. Verify component is using `t()` function correctly.

## Success Criteria

✅ All Dashboard UI elements translate to Hindi
✅ Hindi Devanagari script renders clearly
✅ Language toggle works instantly
✅ No visual layout issues in Hindi mode
✅ Font weights are appropriate for readability
✅ Works across all major browsers
✅ Responsive design maintained in both languages

## Conclusion

This visual test guide provides a comprehensive checklist for verifying the Hindi language support implementation. Follow the testing checklist to ensure all requirements are met and the user experience is consistent across both English and Hindi languages.
