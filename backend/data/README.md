# Mock Data for NagarikAI Platform

This directory contains sample data for the NagarikAI Platform demo.

## Files

### 1. civil_death_records.csv (50 records)
Civil death records from Chhattisgarh districts.

**Fields:**
- record_id: Unique death record identifier
- name: Name of deceased (in Hindi)
- father_name: Father's name (in Hindi)
- date_of_death: Date of death
- age: Age at death
- gender: M/F
- district: District name
- village: Village/town name
- registration_date: Date of registration

### 2. ration_card_records.csv (50 records)
Ration card records with some matching names from death records.

**Fields:**
- card_number: Unique ration card number
- head_of_family: Name of head of family (in Hindi)
- father_name: Father's name (in Hindi)
- card_type: APL/BPL
- district: District name
- village: Village/town name
- issue_date: Date of issue
- members_count: Number of family members
- status: active/inactive

### 3. aadhaar_records.csv (50 records)
Aadhaar enrollment records.

**Fields:**
- aadhaar_number: 12-digit Aadhaar number
- name: Name (in Hindi)
- father_name: Father's name (in Hindi)
- date_of_birth: Date of birth
- gender: M/F
- district: District name
- village: Village/town name
- mobile: Mobile number
- enrollment_date: Date of enrollment

### 4. grievances.csv (100 records)
Historical grievances in Hindi with department labels.

**Fields:**
- grievance_id: Unique grievance identifier
- citizen_name: Name of citizen
- complaint_text: Complaint description (in Hindi)
- department: Department name (in Hindi)
- status: resolved/pending/in_progress
- submission_date: Date of submission
- resolution_date: Date of resolution (if resolved)

**Departments included:**
- खाद्य विभाग (Food Department)
- विद्युत विभाग (Electricity Department)
- लोक निर्माण विभाग (Public Works Department)
- राजस्व विभाग (Revenue Department)
- समाज कल्याण विभाग (Social Welfare Department)
- स्वास्थ्य विभाग (Health Department)
- शिक्षा विभाग (Education Department)
- जल संसाधन विभाग (Water Resources Department)
- महिला एवं बाल विकास विभाग (Women & Child Development)
- ग्रामीण विकास विभाग (Rural Development Department)
- नगर निगम (Municipal Corporation)
- पुलिस विभाग (Police Department)
- कृषि विभाग (Agriculture Department)
- परिवहन विभाग (Transport Department)

### 5. applications.csv (50 records)
Historical applications with rejection outcomes.

**Fields:**
- application_id: Unique application identifier
- applicant_name: Name of applicant (in Hindi)
- application_type: Type of application (in Hindi)
- department: Department name (in Hindi)
- status: approved/rejected
- submission_date: Date of submission
- decision_date: Date of decision
- rejection_reason: Reason for rejection (if rejected, in Hindi)

**Application types included:**
- राशन कार्ड (Ration Card)
- जाति प्रमाण पत्र (Caste Certificate)
- आय प्रमाण पत्र (Income Certificate)
- मृत्यु प्रमाण पत्र (Death Certificate)
- विधवा पेंशन (Widow Pension)
- बीपीएल कार्ड (BPL Card)
- निवास प्रमाण पत्र (Residence Certificate)
- विकलांग पेंशन (Disability Pension)
- जन्म प्रमाण पत्र (Birth Certificate)
- बिजली कनेक्शन (Electricity Connection)
- आयुष्मान कार्ड (Ayushman Card)
- ड्राइविंग लाइसेंस (Driving License)
- प्रधानमंत्री आवास योजना (PM Housing Scheme)
- किसान क्रेडिट कार्ड (Kisan Credit Card)
- वृद्धावस्था पेंशन (Old Age Pension)
- पुलिस वेरिफिकेशन (Police Verification)
- किसान सम्मान निधि (PM Kisan Scheme)

## Data Characteristics

- **Realistic Names**: All names are in Hindi (Devanagari script) representing typical Chhattisgarh citizen names
- **Cross-References**: Some names appear in multiple datasets (e.g., death records and ration cards) to enable cross-database analysis
- **Geographic Coverage**: Data covers major districts of Chhattisgarh including Raipur, Bilaspur, Durg, and Rajnandgaon
- **Temporal Range**: Records span from 2015 to 2023
- **Status Variety**: Grievances and applications have varied statuses (pending, resolved, approved, rejected)
- **Hindi Content**: Grievances and rejection reasons are in Hindi to test NLP capabilities
- **Department Diversity**: 14 different government departments represented

## Usage

These CSV files can be loaded into the backend application for demo purposes. They provide realistic test data for:
- Cross-database anomaly detection
- Grievance classification and routing
- Application outcome prediction
- Natural language processing of Hindi text
- Data quality analysis
