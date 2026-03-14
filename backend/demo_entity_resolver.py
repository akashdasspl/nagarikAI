"""
Demo script showing entity resolver in action
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.entity_resolver import EntityResolver


def main():
    print("=" * 70)
    print("NagarikAI Entity Resolver Demo")
    print("Matching Death Records to Ration Card and Aadhaar Databases")
    print("=" * 70)
    
    resolver = EntityResolver(data_dir="data")
    
    # Load some sample death records
    death_records = resolver.load_csv_data("civil_death_records.csv")
    
    # Demo with first 5 death records
    for i, death_record in enumerate(death_records[:5], 1):
        print(f"\n{'=' * 70}")
        print(f"Death Record #{i}")
        print(f"{'=' * 70}")
        print(f"Record ID: {death_record['record_id']}")
        print(f"Name: {death_record['name']}")
        print(f"Father: {death_record['father_name']}")
        print(f"Location: {death_record['village']}, {death_record['district']}")
        print(f"Date of Death: {death_record['date_of_death']}")
        
        # Find matches across both databases
        matches = resolver.resolve_entity(
            death_record,
            target_databases=['ration_card', 'aadhaar']
        )
        
        if matches:
            print(f"\n✓ Found {len(matches)} potential matches (confidence > 70%):")
            for j, match in enumerate(matches, 1):
                print(f"\n  Match {j}:")
                print(f"    Database: {match.target_database}")
                print(f"    Record ID: {match.target_record_id}")
                print(f"    Confidence: {match.confidence_score:.1%}")
                print(f"    Name Similarity: {match.field_similarities['name']:.1%}")
                print(f"    Father Name Similarity: {match.field_similarities['father_name']:.1%}")
                print(f"    Location Similarity: {match.field_similarities['location']:.1%}")
                print(f"    Matched Name: {match.matched_fields['name'][1]}")
        else:
            print(f"\n✗ No matches found above 70% confidence threshold")
    
    print(f"\n{'=' * 70}")
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
