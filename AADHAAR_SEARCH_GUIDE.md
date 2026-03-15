# Aadhaar-Based Beneficiary Search Guide

## Overview
The Beneficiary Discovery Engine now supports two search modes:
1. **Death Record Search** - Find beneficiaries based on death certificates (widow pension, dependent support)
2. **Aadhaar Search** - Find scheme eligibility for a person using their Aadhaar number

## How to Use Aadhaar Search

### Step 1: Navigate to Beneficiary Discovery
- Go to http://localhost:3001
- Click on "Beneficiary Discovery Engine" in the navigation

### Step 2: Switch to Aadhaar Search Mode
- Click the "🆔 Aadhaar Search" button at the top of the form
- The form will change to show a single Aadhaar number input field

### Step 3: Enter Aadhaar Number
- Enter a 12-digit Aadhaar number
- The system will automatically validate the format

### Step 4: Search
- Click "Search by Aadhaar" button
- The system will:
  1. Find the person in the Aadhaar database
  2. Match them with their family in the Ration Card database
  3. Check eligibility for various welfare schemes
  4. Return results with confidence scores

## Test Aadhaar Numbers

| Aadhaar Number | Name | Age | Eligible Schemes |
|----------------|------|-----|------------------|
| 234567890123 | राम कुमार शर्मा | 69 | Old Age Pension, BPL Card |
| 345678901234 | सुनीता देवी पटेल | 65 | Old Age Pension, Widow Pension (if applicable) |
| 456789012345 | राजेश कुमार | 54 | BPL Card (if applicable) |

## What the System Checks

1. **Old Age Pension**: Person is 60+ years old
2. **Widow Pension**: Female, 18+ years (suggests checking if spouse is deceased)
3. **BPL Card**: Family has BPL ration card
4. **Disability Pension**: Would require disability certificate (not checked in Aadhaar search)

## Results Display

Results show:
- Person's name and Aadhaar number
- Eligible schemes with reasoning
- Confidence score (based on name and location matching)
- Contact information (Aadhaar ID and address)

## Differences from Death Record Search

| Feature | Death Record Search | Aadhaar Search |
|---------|-------------------|----------------|
| Input | Death certificate details | Aadhaar number only |
| Purpose | Find newly eligible beneficiaries | Check existing person's eligibility |
| Output | Spouse/dependents of deceased | Person themselves |
| Use Case | Proactive outreach | Direct eligibility check |
