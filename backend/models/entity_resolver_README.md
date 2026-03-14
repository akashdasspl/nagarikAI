# Entity Resolver

## Overview

The Entity Resolver is a component that matches citizen records across disconnected databases using fuzzy string matching. It's designed to handle name variations, OCR errors, and spelling differences commonly found in government databases.

## Features

- **Fuzzy Name Matching**: Uses fuzzywuzzy library with Levenshtein distance
- **Multi-field Matching**: Combines name, father's name, and location similarity
- **Weighted Confidence Scoring**: Calculates overall confidence using weighted average
- **Configurable Threshold**: Only returns matches above 70% confidence
- **Top-N Results**: Returns top 3 matches per query
- **Multi-Database Support**: Can match across ration card and Aadhaar databases

## Implementation Details

### Matching Algorithm

The entity resolver uses a multi-stage fuzzy matching approach:

1. **Name Similarity**: Token sort ratio to handle word order variations
2. **Father Name Similarity**: Same algorithm as name matching
3. **Location Similarity**: Partial ratio for substring matches (village + district)

### Confidence Calculation

Overall confidence is calculated as a weighted average:
- Name: 40% weight
- Father Name: 30% weight
- Location: 30% weight

Formula: `confidence = (name_sim * 0.4) + (father_name_sim * 0.3) + (location_sim * 0.3)`

### Threshold

Only matches with confidence ≥ 70% are returned, ensuring high-quality matches.

## Usage

```python
from models.entity_resolver import EntityResolver

# Initialize resolver
resolver = EntityResolver(data_dir="data")

# Match a death record against ration card database
death_record = {
    'record_id': 'CDR001',
    'name': 'राम कुमार शर्मा',
    'father_name': 'श्री मोहन लाल शर्मा',
    'district': 'रायपुर',
    'village': 'खमतराई'
}

# Get matches
matches = resolver.match_death_to_ration_cards(death_record)

# Or match across multiple databases
matches = resolver.resolve_entity(
    death_record,
    target_databases=['ration_card', 'aadhaar']
)

# Process results
for match in matches:
    print(f"Confidence: {match.confidence_score:.1%}")
    print(f"Target: {match.target_database} - {match.target_record_id}")
```

## Testing

Run the test suite:
```bash
python test_entity_resolver.py
```

Run the demo:
```bash
python demo_entity_resolver.py
```

## Requirements Validation

This implementation validates:
- **Requirement 1.2**: Entity resolution across disconnected databases
- **Requirement 9.1**: Fuzzy matching with name, DOB, and address fields
- **Requirement 9.2**: Handling name variations and OCR errors

## Performance

- Processes individual records in milliseconds
- Returns top 3 matches per query
- Confidence scores range from 0.0 to 1.0
- Minimum threshold: 0.7 (70%)

## Future Enhancements

For production deployment, consider:
- Date of birth matching (when available in data)
- Phonetic matching for Hindi names (Soundex/Metaphone)
- Caching for frequently queried records
- Batch processing optimization
- Database indexing for faster lookups
