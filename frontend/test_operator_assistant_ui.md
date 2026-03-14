# CSC Operator Assistant UI - Manual Test Plan

## Test Scenario 1: Real-Time Validation

### Steps:
1. Navigate to "CSC Operator Assistant" tab
2. Start typing in "Applicant Name" field
3. Enter age below minimum (e.g., 15)
4. Enter high income (e.g., 500000)
5. Leave documents unchecked

### Expected Results:
- ✓ Validation indicator appears: "⟳ Validating in real-time..."
- ✓ Risk score updates automatically after 800ms
- ✓ Fields with issues show red border
- ✓ Warning indicators appear below problematic fields
- ✓ Risk score card shows appropriate color (red/orange/green)
- ✓ Validation issues list appears with severity badges
- ✓ Corrective guidance shows in both Hindi and English

## Test Scenario 2: Field Error Highlighting

### Steps:
1. Fill form with invalid data:
   - Age: 15 (below minimum)
   - Income: 500000 (above threshold)
   - Leave required documents unchecked
2. Observe field highlighting

### Expected Results:
- ✓ Age field has red border and error indicator
- ✓ Income field has red border and error indicator
- ✓ Document checkboxes section shows in validation issues
- ✓ Each problematic field listed in validation issues
- ✓ Field names match between form and issue cards

## Test Scenario 3: Risk Score Color Coding

### Test Cases:

**Low Risk (< 40%):**
- Fill all fields correctly
- Check all required documents
- Expected: Green risk score, "LOW RISK" label

**Medium Risk (40-69%):**
- Fill most fields correctly
- Missing 1-2 documents
- Expected: Orange risk score, "MEDIUM RISK" label

**High Risk (≥ 70%):**
- Age below minimum
- Income above threshold
- Missing multiple documents
- Expected: Red risk score, "HIGH RISK" label

## Test Scenario 4: Bilingual Guidance

### Steps:
1. Create validation issues (e.g., age below minimum)
2. Check corrective guidance section

### Expected Results:
- ✓ Each guidance item has priority badge
- ✓ English guidance clearly labeled
- ✓ Hindi guidance clearly labeled (हिंदी:)
- ✓ Suggested action separated and clear
- ✓ Guidance items sorted by priority

## Test Scenario 5: Form Submission

### Steps:
1. Fill complete form with valid data
2. Click "Validate Application" button
3. Observe results

### Expected Results:
- ✓ Button shows "Validating..." during submission
- ✓ Results appear within 3 seconds
- ✓ If valid: Green success box appears
- ✓ If invalid: Issues and guidance displayed
- ✓ Risk score matches validation results

## Test Scenario 6: Empty State

### Steps:
1. Load page without filling form
2. Observe right column

### Expected Results:
- ✓ Placeholder message displayed
- ✓ Icon (📋) visible
- ✓ Helpful text: "Fill in the application details..."
- ✓ No error messages or empty lists

## Test Scenario 7: Responsive Layout

### Steps:
1. Resize browser window
2. Test on different screen sizes

### Expected Results:
- ✓ Two-column layout on desktop
- ✓ Form and results side-by-side
- ✓ Proper spacing and alignment
- ✓ No horizontal scrolling
- ✓ All elements visible and accessible

## Test Scenario 8: Real-Time Updates

### Steps:
1. Enter invalid age (e.g., 15)
2. Wait for validation
3. Correct age to valid value (e.g., 45)
4. Wait for validation

### Expected Results:
- ✓ Risk score increases with invalid age
- ✓ Age field shows red border
- ✓ Issue appears in validation list
- ✓ After correction: risk score decreases
- ✓ Red border removed from age field
- ✓ Issue removed from validation list
- ✓ Smooth transition animations

## Test Scenario 9: Multiple Issues

### Steps:
1. Create multiple validation issues:
   - Missing name
   - Invalid age
   - High income
   - No documents
2. Observe issue display

### Expected Results:
- ✓ All issues listed separately
- ✓ Each issue has severity badge
- ✓ Issues sorted by severity
- ✓ Total count shown: "Validation Issues (4)"
- ✓ Each issue shows impact on risk
- ✓ Guidance provided for each issue

## Test Scenario 10: Success State

### Steps:
1. Fill form with completely valid data:
   - Name: "Rajesh Kumar"
   - Age: 45
   - Income: 50000
   - All required documents checked
2. Wait for validation

### Expected Results:
- ✓ Risk score: 0% (green)
- ✓ Success box appears
- ✓ "✓ Application Ready" heading
- ✓ "No validation issues found" message
- ✓ No issue cards displayed
- ✓ No guidance cards displayed

## Performance Tests

### Test 1: Debouncing
- Type rapidly in multiple fields
- Expected: Only one API call after 800ms of inactivity

### Test 2: Response Time
- Submit form
- Expected: Results within 3 seconds (Requirement 6.5)

### Test 3: Visual Feedback
- Make changes to form
- Expected: Immediate visual feedback (< 100ms)

## Accessibility Tests

### Test 1: Keyboard Navigation
- Tab through all form fields
- Expected: Logical tab order, all fields accessible

### Test 2: Screen Reader
- Use screen reader on form
- Expected: Labels read correctly, error states announced

### Test 3: Color Contrast
- Check color contrast ratios
- Expected: All text meets WCAG AA standards

## Browser Compatibility

Test on:
- ✓ Chrome (latest)
- ✓ Firefox (latest)
- ✓ Edge (latest)
- ✓ Safari (latest)

## API Integration Tests

### Test 1: Valid Request
- Fill form and submit
- Expected: 200 response, validation object returned

### Test 2: Network Error
- Disconnect network and submit
- Expected: Error handled gracefully, user notified

### Test 3: Invalid Response
- Mock invalid API response
- Expected: Error caught, no UI crash

## Notes

- All tests should be performed with backend server running
- Check browser console for any errors
- Verify network requests in DevTools
- Test with different scheme types
- Verify Hindi text displays correctly
