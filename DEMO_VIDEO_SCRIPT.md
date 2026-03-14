# NagarikAI Platform — Demo Video Script

**Team blueBox | Hackathon 2026 Chhattisgarh NIC Smart Governance Initiative**  
**Target Duration:** 2 minutes 45 seconds  
**Format:** Screen recording with voiceover

---

## Recording Setup

### Screen & Browser
- **Resolution:** 1920×1080 (Full HD)
- **Browser:** Chrome or Edge, maximized to full screen
- **Browser Zoom:** 110% (Ctrl + Plus once from default)
- **Font Rendering:** Enable ClearType / subpixel antialiasing
- **Extensions:** Disable all browser extensions before recording
- **URL bar:** Hide (press F11 for fullscreen, or use a presentation extension)

### Application Setup (do this before hitting Record)
1. Start backend: `cd backend && uvicorn main:app --reload` → wait for `Application startup complete`
2. Start frontend: `cd frontend && npm run dev` → wait for `Local: http://localhost:5173`
3. Open `http://localhost:5173` in browser
4. Set language toggle to **English (EN)**
5. Navigate to the **Dashboard** tab — this is the opening shot
6. Pre-fill (but do NOT submit) the Beneficiary Discovery form with Scenario 1 data so it's ready to go
7. Open a second browser tab at `http://localhost:5173` for the Grievance Portal (optional — reduces navigation time)

### Audio
- **Microphone:** USB condenser or headset mic (avoid laptop built-in)
- **Room:** Quiet room, no echo; hang a blanket behind you if needed
- **Sample Rate:** 44.1 kHz, 16-bit mono
- **Record voiceover separately** from screen capture, then sync in post (easier to re-record lines)

### Screen Recorder
- **Recommended:** OBS Studio (free) or Loom
- **OBS Settings:** MP4 output, H.264, CRF 18, 30 fps
- **Cursor:** Use a large, highlighted cursor (OBS cursor plugin or Windows pointer settings → Large Black)
- **Do a 10-second test recording** before the real take to check audio levels

---

## Shot-by-Shot Script

> **Legend:**  
> `[SCREEN]` — what is visible on screen  
> `[ACTION]` — what the presenter does (mouse/keyboard)  
> `[VO]` — voiceover text (read this word-for-word)  
> `[PAUSE]` — brief natural pause (≈ 0.5 s) for emphasis

---

### SHOT 1 — Title Card / Hook
**Timestamp: 0:00 – 0:12**

```
[SCREEN]  Dashboard page of NagarikAI — metrics visible:
          "1,247 Beneficiaries Discovered", "89% Grievances Routed",
          "73% Rejection Rate Reduced"

[ACTION]  No mouse movement. Let the dashboard breathe.
```

**[VO]:**
> "In Chhattisgarh, thousands of eligible citizens never receive the welfare benefits they're entitled to — not because they don't qualify, but because the system never finds them. NagarikAI changes that."

**[PAUSE]**

---

### SHOT 2 — Platform Introduction
**Timestamp: 0:12 – 0:22**

```
[SCREEN]  Dashboard — slowly scroll down to show the three feature cards:
          Beneficiary Discovery, Grievance Intelligence, Operator Assistant

[ACTION]  Slow mouse scroll down the dashboard page.
```

**[VO]:**
> "NagarikAI is an AI-powered citizen service platform with three integrated capabilities: proactive beneficiary discovery, intelligent grievance routing, and real-time application validation."

---

### SHOT 3 — Navigate to Beneficiary Discovery
**Timestamp: 0:22 – 0:28**

```
[SCREEN]  Click the "Beneficiary Discovery" tab in the top navigation.
          The Beneficiary Discovery form appears.

[ACTION]  Click "Beneficiary Discovery" in the nav bar.
          Pause 1 second for the page to load.
```

**[VO]:**
> "Let's start with beneficiary discovery. A civil death record has just been registered."

---

### SHOT 4 — Fill Death Record Form
**Timestamp: 0:28 – 0:45**

```
[SCREEN]  The death record input form. Fields fill in one by one.

[ACTION]  Type (or paste) the following values into each field:
          - Name:          राम कुमार शर्मा
          - Father's Name: श्री मोहन लाल शर्मा
          - Date of Death: 2023-03-15
          - Age:           67
          - Gender:        Male (select from dropdown)
          - District:      रायपुर
          - Village:       खमतराई

          Type at a natural pace — not too fast, not too slow.
          Pause 0.5 s after filling the last field before clicking submit.
```

**[VO]:**
> "Ram Kumar Sharma, age 67, from Khamtarai village in Raipur district, passed away on March 15th, 2023. He was a ration card holder. The system now cross-references three disconnected databases — Civil Death Records, Ration Cards, and Aadhaar — to find his surviving family."

---

### SHOT 5 — Submit and Show Results
**Timestamp: 0:45 – 1:05**

```
[SCREEN]  Click "Discover Beneficiaries" button.
          Loading spinner appears briefly (≈ 1–2 seconds).
          Results table appears showing:
          - Match in Ration Card DB (RC2023001) — confidence 92%
          - Match in Aadhaar DB (234567890123) — confidence 88%
          - Spouse flagged as potential widow pension beneficiary
          - Results sorted by confidence score (highest first)

[ACTION]  Click "Discover Beneficiaries".
          Let results load naturally — do NOT skip the spinner.
          Slowly move mouse to highlight the top result row.
          Hover over the confidence score badge.
```

**[VO]:**
> "In under two seconds, the system finds two matching records with confidence scores of 92 and 88 percent. The spouse is automatically flagged as a potential widow pension beneficiary — someone who would never have known she qualifies without this system."

**[PAUSE]**

> "The fuzzy matching handles OCR errors and name spelling variations that are common in government records. Field workers are ranked by confidence score so they know which cases to prioritize."

---

### SHOT 6 — Navigate to Grievance Portal
**Timestamp: 1:05 – 1:12**

```
[SCREEN]  Click "Grievance Portal" tab in the navigation.
          The grievance submission form appears.

[ACTION]  Click "Grievance Portal" in the nav bar.
          Pause 1 second.
```

**[VO]:**
> "Now let's look at grievance intelligence. A citizen submits a complaint in Hindi."

---

### SHOT 7 — Submit Hindi Grievance (Pension)
**Timestamp: 1:12 – 1:30**

```
[SCREEN]  Grievance text area and language selector visible.

[ACTION]  Set language selector to "Hindi (hi)".
          Paste the following text into the grievance text area:

          "मेरी विधवा पेंशन तीन महीने से नहीं आई है। बैंक में पूछा तो
           कहा कि विभाग से पैसा नहीं आया। मैं बहुत परेशान हूं,
           कृपया जल्दी कार्रवाई करें।"

          Click "Submit Grievance".
          Let the result load.
```

**[VO]:**
> "The citizen writes: 'My widow pension has not arrived for three months. The bank says the department hasn't sent the money. Please take action urgently.' The mBERT multilingual model reads the Hindi text and classifies it instantly."

---

### SHOT 8 — Show Classification Result
**Timestamp: 1:30 – 1:45**

```
[SCREEN]  Classification result card appears:
          - Department: समाज कल्याण विभाग (Social Welfare Department)
          - Confidence: 87%
          - Predicted SLA: 72 hours
          - Status: Submitted

[ACTION]  Move mouse slowly to highlight the department name.
          Then move to the SLA badge.
          Pause on each for 1 second.
```

**[VO]:**
> "Classified: Social Welfare Department, 87% confidence, with a 72-hour resolution SLA. No manual triage. No routing delays. What used to take two to three days now happens in milliseconds — and if the SLA is breached, the system auto-escalates to the next supervisory level."

---

### SHOT 9 — Language Toggle to Hindi UI
**Timestamp: 1:45 – 1:55**

```
[SCREEN]  Top navigation bar with EN/HI toggle visible.

[ACTION]  Click the language toggle to switch from EN to HI.
          The entire UI re-renders in Hindi.
          Pan the mouse slowly across the navigation bar and form labels
          to show that all text is now in Hindi.
```

**[VO]:**
> "The entire interface works in Hindi — critical for CSC operators in rural Chhattisgarh. Every label, button, and guidance message is translated. Language is not a barrier."

```
[ACTION]  Click the toggle again to switch back to English (EN)
          before the next scene.
```

---

### SHOT 10 — Navigate to Operator Assistant
**Timestamp: 1:55 – 2:02**

```
[SCREEN]  Click "Operator Assistant" tab in the navigation.
          The application validation form appears.

[ACTION]  Click "Operator Assistant" in the nav bar.
          Pause 1 second.
```

**[VO]:**
> "Finally, the CSC Operator Assistant. A field operator is about to submit a disability pension application."

---

### SHOT 11 — Enter High-Risk Application
**Timestamp: 2:02 – 2:18**

```
[SCREEN]  Application validation form with fields for scheme type,
          applicant details, and documents.

[ACTION]  Select scheme type: "Disability Pension"
          Fill in the following fields:
          - Applicant Name:        Mohan Singh
          - Date of Birth:         2010-01-01
          - Address:               Village Raigarh, District Raigarh
          - Bank Account:          123
          - Aadhaar Number:        12345
          - Disability Percentage: 30
          - Annual Income:         200000

          Type at a natural pace. Pause after the last field.
```

**[VO]:**
> "This application has several problems — but the operator doesn't know that yet. Watch what happens when they validate it."

---

### SHOT 12 — Show High-Risk Validation Result
**Timestamp: 2:18 – 2:35**

```
[SCREEN]  Click "Validate Application".
          Risk score appears: 0.91 — shown in RED with label "HIGH RISK"
          Issues list appears:
          ❌ Date of Birth — Age below minimum (Critical)
          ❌ Disability Percentage — Below 40% minimum (High)
          ❌ Annual Income — Above income threshold (High)
          ⚠️  Bank Account — Invalid format (Medium)
          ⚠️  Aadhaar Number — Invalid format (Medium)

          Each issue has Hindi and English guidance text below it.

[ACTION]  Click "Validate Application".
          Let the result load.
          Slowly scroll down through the issues list.
          Pause on the first issue (Date of Birth) for 1.5 seconds.
          Continue scrolling to show all five issues.
```

**[VO]:**
> "Five issues caught before submission — each one would have caused a rejection. The risk score is 91%. The guidance is in Hindi so the operator knows exactly what to fix: the applicant is too young, the disability percentage is below the 40% minimum, and the income exceeds the threshold."

**[PAUSE]**

> "Without NagarikAI, this application would have been rejected, the citizen would have waited weeks, and the operator would have had to start over."

---

### SHOT 13 — Closing / Impact Statement
**Timestamp: 2:35 – 2:45**

```
[SCREEN]  Navigate back to the Dashboard.
          The metrics are visible: beneficiaries discovered, grievances
          routed, rejection rate reduced.

[ACTION]  Click "Dashboard" in the nav bar.
          Let the page load.
          No mouse movement — let the numbers speak.
```

**[VO]:**
> "NagarikAI: moving from digitization to intelligent governance. Built for Chhattisgarh. Built for every citizen who deserves better."

---

## Full Voiceover Text (Continuous Read)

> "In Chhattisgarh, thousands of eligible citizens never receive the welfare benefits they're entitled to — not because they don't qualify, but because the system never finds them. NagarikAI changes that.
>
> NagarikAI is an AI-powered citizen service platform with three integrated capabilities: proactive beneficiary discovery, intelligent grievance routing, and real-time application validation.
>
> Let's start with beneficiary discovery. A civil death record has just been registered. Ram Kumar Sharma, age 67, from Khamtarai village in Raipur district, passed away on March 15th, 2023. He was a ration card holder. The system now cross-references three disconnected databases — Civil Death Records, Ration Cards, and Aadhaar — to find his surviving family.
>
> In under two seconds, the system finds two matching records with confidence scores of 92 and 88 percent. The spouse is automatically flagged as a potential widow pension beneficiary — someone who would never have known she qualifies without this system. The fuzzy matching handles OCR errors and name spelling variations that are common in government records. Field workers are ranked by confidence score so they know which cases to prioritize.
>
> Now let's look at grievance intelligence. A citizen submits a complaint in Hindi. The citizen writes: 'My widow pension has not arrived for three months. The bank says the department hasn't sent the money. Please take action urgently.' The mBERT multilingual model reads the Hindi text and classifies it instantly.
>
> Classified: Social Welfare Department, 87% confidence, with a 72-hour resolution SLA. No manual triage. No routing delays. What used to take two to three days now happens in milliseconds — and if the SLA is breached, the system auto-escalates to the next supervisory level.
>
> The entire interface works in Hindi — critical for CSC operators in rural Chhattisgarh. Every label, button, and guidance message is translated. Language is not a barrier.
>
> Finally, the CSC Operator Assistant. A field operator is about to submit a disability pension application. This application has several problems — but the operator doesn't know that yet. Watch what happens when they validate it.
>
> Five issues caught before submission — each one would have caused a rejection. The risk score is 91%. The guidance is in Hindi so the operator knows exactly what to fix: the applicant is too young, the disability percentage is below the 40% minimum, and the income exceeds the threshold. Without NagarikAI, this application would have been rejected, the citizen would have waited weeks, and the operator would have had to start over.
>
> NagarikAI: moving from digitization to intelligent governance. Built for Chhattisgarh. Built for every citizen who deserves better."

---

## Timing Summary

| Shot | Scene | Start | End | Duration |
|------|-------|-------|-----|----------|
| 1 | Title / Hook | 0:00 | 0:12 | 12 s |
| 2 | Platform Introduction | 0:12 | 0:22 | 10 s |
| 3 | Navigate to Beneficiary Discovery | 0:22 | 0:28 | 6 s |
| 4 | Fill Death Record Form | 0:28 | 0:45 | 17 s |
| 5 | Submit and Show Results | 0:45 | 1:05 | 20 s |
| 6 | Navigate to Grievance Portal | 1:05 | 1:12 | 7 s |
| 7 | Submit Hindi Grievance | 1:12 | 1:30 | 18 s |
| 8 | Show Classification Result | 1:30 | 1:45 | 15 s |
| 9 | Language Toggle to Hindi UI | 1:45 | 1:55 | 10 s |
| 10 | Navigate to Operator Assistant | 1:55 | 2:02 | 7 s |
| 11 | Enter High-Risk Application | 2:02 | 2:18 | 16 s |
| 12 | Show High-Risk Validation Result | 2:18 | 2:35 | 17 s |
| 13 | Closing / Impact Statement | 2:35 | 2:45 | 10 s |
| **Total** | | **0:00** | **2:45** | **165 s** |

---

## Post-Production Notes

### Editing Software
- **Free:** DaVinci Resolve (recommended), OpenShot, Kdenlive
- **Paid:** Adobe Premiere Pro, Camtasia

### Captions
- Add English subtitles for all voiceover lines
- Font: Arial or Noto Sans, size 36–40pt, white text with black drop shadow
- Position: Bottom center, 10% from bottom edge
- Also add Hindi transliteration captions for the Hindi grievance text in Shot 7 (show what the citizen typed)

### Zoom / Highlight Effects
- **Shot 5 (Results):** Add a subtle zoom-in (1.0x → 1.15x over 1 second) on the confidence score badges
- **Shot 8 (Classification):** Add a brief highlight box (yellow border, 2px) around the department name for 1.5 seconds
- **Shot 12 (Issues List):** Add a slow pan-down effect as the issues list scrolls into view; add a red highlight box on the "HIGH RISK" score badge for 2 seconds

### Transitions
- Use **cut** (no transition) between all shots — keeps the pace tight
- Exception: Use a **0.3-second cross-dissolve** between Shot 9 (Hindi UI) and Shot 10 (Operator Assistant) to signal a scene change

### Background Music
- **Style:** Subtle, optimistic, corporate-tech instrumental (no lyrics)
- **Volume:** -18 dB under voiceover (barely audible)
- **Suggested search terms:** "corporate background music no copyright", "uplifting tech background music"
- **Fade out:** Start fading at 2:35, reach silence by 2:45
- **Recommended free source:** Pixabay Music (pixabay.com/music) — filter by "Corporate" genre

### Color Grading
- Slight brightness boost (+5%) and contrast (+10%) to make the UI pop on screen
- No heavy color grading — the UI colors should look natural

### Export Settings
- **Format:** MP4 (H.264)
- **Resolution:** 1920×1080
- **Frame Rate:** 30 fps
- **Bitrate:** 8–12 Mbps (for upload to YouTube/Google Drive)
- **Audio:** AAC, 192 kbps, stereo
- **File name:** `NagarikAI_Demo_TeamBlueBox_Hackathon2026.mp4`

### Upload / Submission
- Upload to Google Drive or YouTube (unlisted)
- Include the public link in the hackathon submission form
- Thumbnail: Screenshot of Shot 5 (results table with confidence scores) with the NagarikAI logo overlaid

---

## Backup Plan (if live demo has issues)

If the backend is not running or returns errors during recording:

1. Use the pre-recorded screenshots from `frontend/TASK_7.1_VISUAL_TEST.md` as static slides
2. Run `python backend/demo_runner.py` in a terminal and screen-record the terminal output for the API response shots
3. For the Beneficiary Discovery result, the expected JSON response is:
   ```json
   {
     "matches": [
       {"record_id": "RC2023001", "database": "ration_card", "confidence": 0.92},
       {"record_id": "234567890123", "database": "aadhaar", "confidence": 0.88}
     ],
     "beneficiary_type": "widow_pension",
     "ranked_by": "confidence_score"
   }
   ```
4. For the validation result, the expected response is:
   ```json
   {
     "rejection_risk_score": 0.91,
     "risk_level": "HIGH",
     "issues": [
       {"field": "date_of_birth", "severity": "critical"},
       {"field": "disability_percentage", "severity": "high"},
       {"field": "annual_income", "severity": "high"},
       {"field": "bank_account", "severity": "medium"},
       {"field": "aadhaar_number", "severity": "medium"}
     ]
   }
   ```

---

*Script version 1.0 — Team blueBox — Hackathon 2026*
