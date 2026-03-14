"""
Debug script to test entity resolver with CDR001
"""
from models.entity_resolver import EntityResolver

# Initialize resolver with correct data directory
resolver = EntityResolver(data_dir="data")

# Test death record (CDR001)
death_record = {
    'record_id': 'CDR001',
    'name': 'राम कुमार शर्मा',
    'father_name': 'श्री मोहन लाल शर्मा',
    'date_of_death': '2023-03-15',
    'age': 67,
    'gender': 'M',
    'district': 'रायपुर',
    'village': 'खमतराई'
}

print("Testing Entity Resolver with CDR001")
print("=" * 60)
print(f"Death Record: {death_record['name']}")
print(f"Father: {death_record['father_name']}")
print(f"Location: {death_record['village']}, {death_record['district']}")
print()

# Test name similarity
print("Testing name similarity:")
name1 = 'राम कुमार शर्मा'
name2 = 'राम कुमार शर्मा'
similarity = resolver.calculate_name_similarity(name1, name2)
print(f"  '{name1}' vs '{name2}': {similarity:.2f}")
print()

# Test with ration card matching
print("Matching against ration cards:")
matches = resolver.match_death_to_ration_cards(death_record)
print(f"Found {len(matches)} matches")
for i, match in enumerate(matches, 1):
    print(f"\nMatch {i}:")
    print(f"  Target ID: {match.target_record_id}")
    print(f"  Confidence: {match.confidence_score:.2%}")
    print(f"  Matched fields:")
    for field, (source, target) in match.matched_fields.items():
        print(f"    {field}: '{source}' -> '{target}'")
    print(f"  Field similarities:")
    for field, score in match.field_similarities.items():
        print(f"    {field}: {score:.2f}")

# Test with aadhaar matching
print("\n" + "=" * 60)
print("Matching against Aadhaar records:")
matches = resolver.match_death_to_aadhaar(death_record)
print(f"Found {len(matches)} matches")
for i, match in enumerate(matches, 1):
    print(f"\nMatch {i}:")
    print(f"  Target ID: {match.target_record_id}")
    print(f"  Confidence: {match.confidence_score:.2%}")
    print(f"  Matched fields:")
    for field, (source, target) in match.matched_fields.items():
        print(f"    {field}: '{source}' -> '{target}'")

# Test full resolve_entity
print("\n" + "=" * 60)
print("Full entity resolution:")
all_matches = resolver.resolve_entity(death_record, ['ration_card', 'aadhaar'])
print(f"Total matches found: {len(all_matches)}")
for i, match in enumerate(all_matches, 1):
    print(f"\nMatch {i}:")
    print(f"  Database: {match.target_database}")
    print(f"  Target ID: {match.target_record_id}")
    print(f"  Confidence: {match.confidence_score:.2%}")
