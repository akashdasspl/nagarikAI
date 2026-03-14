"""
Unit tests for Entity Resolver
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entity_resolver import EntityResolver, MatchResult


def test_entity_resolver_basic():
    """Test basic entity resolution functionality"""
    resolver = EntityResolver(data_dir="data")
    
    # Test with a death record that should match ration card
    death_record = {
        'record_id': 'CDR001',
        'name': 'राम कुमार शर्मा',
        'father_name': 'श्री मोहन लाल शर्मा',
        'district': 'रायपुर',
        'village': 'खमतराई'
    }
    
    # Match against ration card database
    matches = resolver.match_death_to_ration_cards(death_record)
    
    print(f"\n=== Test: Basic Entity Resolution ===")
    print(f"Death Record: {death_record['name']} from {death_record['village']}, {death_record['district']}")
    print(f"Found {len(matches)} matches above 70% confidence threshold\n")
    
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"  Ration Card: {match.target_record_id}")
        print(f"  Confidence: {match.confidence_score:.2%}")
        print(f"  Name Match: {match.field_similarities['name']:.2%}")
        print(f"  Father Name Match: {match.field_similarities['father_name']:.2%}")
        print(f"  Location Match: {match.field_similarities['location']:.2%}")
        print(f"  Matched Name: {match.matched_fields['name'][1]}")
        print()
    
    # Verify we got matches
    assert len(matches) > 0, "Should find at least one match"
    
    # Verify top match has high confidence
    if matches:
        assert matches[0].confidence_score >= 0.7, "Top match should have confidence >= 70%"
        print(f"✓ Top match confidence: {matches[0].confidence_score:.2%} (>= 70%)")
    
    # Verify matches are sorted by confidence
    for i in range(len(matches) - 1):
        assert matches[i].confidence_score >= matches[i+1].confidence_score, \
            "Matches should be sorted by confidence (descending)"
    print(f"✓ Matches are sorted by confidence score")
    
    # Verify we return at most 3 matches
    assert len(matches) <= 3, "Should return at most 3 matches"
    print(f"✓ Returned {len(matches)} matches (max 3)")


def test_confidence_calculation():
    """Test confidence score calculation"""
    resolver = EntityResolver()
    
    print(f"\n=== Test: Confidence Calculation ===")
    
    # Test with perfect match
    field_similarities = {
        'name': 1.0,
        'father_name': 1.0,
        'location': 1.0
    }
    confidence = resolver.calculate_confidence(field_similarities)
    print(f"Perfect match confidence: {confidence:.2%}")
    assert confidence == 1.0, "Perfect match should have 100% confidence"
    print(f"✓ Perfect match = 100%")
    
    # Test with weighted average
    field_similarities = {
        'name': 0.8,  # weight 0.4
        'father_name': 0.6,  # weight 0.3
        'location': 0.9  # weight 0.3
    }
    expected = 0.8 * 0.4 + 0.6 * 0.3 + 0.9 * 0.3
    confidence = resolver.calculate_confidence(field_similarities)
    print(f"Weighted average confidence: {confidence:.2%} (expected: {expected:.2%})")
    assert abs(confidence - expected) < 0.001, "Should calculate weighted average correctly"
    print(f"✓ Weighted average calculated correctly")


def test_name_similarity():
    """Test name similarity calculation"""
    resolver = EntityResolver()
    
    print(f"\n=== Test: Name Similarity ===")
    
    # Test exact match
    sim = resolver.calculate_name_similarity("राम कुमार शर्मा", "राम कुमार शर्मा")
    print(f"Exact match: {sim:.2%}")
    assert sim == 1.0, "Exact match should be 100%"
    print(f"✓ Exact match = 100%")
    
    # Test case insensitivity and whitespace
    sim = resolver.calculate_name_similarity("राम कुमार शर्मा", "  राम कुमार शर्मा  ")
    print(f"With whitespace: {sim:.2%}")
    assert sim == 1.0, "Should handle whitespace"
    print(f"✓ Handles whitespace correctly")
    
    # Test word order variation
    sim = resolver.calculate_name_similarity("राम कुमार शर्मा", "शर्मा राम कुमार")
    print(f"Word order variation: {sim:.2%}")
    assert sim >= 0.7, "Should handle word order variations"
    print(f"✓ Handles word order variations")
    
    # Test partial match
    sim = resolver.calculate_name_similarity("राम कुमार", "राम कुमार शर्मा")
    print(f"Partial match: {sim:.2%}")
    assert sim > 0.5, "Partial match should have reasonable similarity"
    print(f"✓ Partial match has reasonable similarity")
    
    # Test no match
    sim = resolver.calculate_name_similarity("राम कुमार", "सीता देवी")
    print(f"No match: {sim:.2%}")
    assert sim < 0.5, "Different names should have low similarity"
    print(f"✓ Different names have low similarity")


def test_resolve_entity_multiple_databases():
    """Test resolving entity across multiple databases"""
    resolver = EntityResolver(data_dir="data")
    
    print(f"\n=== Test: Multi-Database Resolution ===")
    
    death_record = {
        'record_id': 'CDR001',
        'name': 'राम कुमार शर्मा',
        'father_name': 'श्री मोहन लाल शर्मा',
        'district': 'रायपुर',
        'village': 'खमतराई'
    }
    
    # Resolve across both databases
    matches = resolver.resolve_entity(
        death_record,
        target_databases=['ration_card', 'aadhaar']
    )
    
    print(f"Death Record: {death_record['name']}")
    print(f"Found {len(matches)} total matches across all databases\n")
    
    for i, match in enumerate(matches, 1):
        print(f"Match {i}:")
        print(f"  Database: {match.target_database}")
        print(f"  Record ID: {match.target_record_id}")
        print(f"  Confidence: {match.confidence_score:.2%}")
        print()
    
    # Verify matches are sorted by confidence across all databases
    for i in range(len(matches) - 1):
        assert matches[i].confidence_score >= matches[i+1].confidence_score, \
            "All matches should be sorted by confidence"
    print(f"✓ Matches sorted by confidence across all databases")


if __name__ == "__main__":
    print("=" * 60)
    print("Entity Resolver Test Suite")
    print("=" * 60)
    
    try:
        test_confidence_calculation()
        test_name_similarity()
        test_entity_resolver_basic()
        test_resolve_entity_multiple_databases()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
