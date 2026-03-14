"""
Entity Resolver for matching records across disconnected databases
Validates: Requirements 1.2, 9.1, 9.2
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import csv
import os


@dataclass
class MatchResult:
    """Result of entity matching operation"""
    source_record_id: str
    target_record_id: str
    target_database: str  # 'civil_death', 'ration_card', 'aadhaar'
    confidence_score: float
    field_similarities: Dict[str, float]  # Per-field similarity scores
    matched_fields: Dict[str, Tuple[Any, Any]]  # (source_value, target_value)


class EntityResolver:
    """
    Entity resolver for matching citizen records across disconnected databases
    Uses fuzzy matching with tolerance for OCR errors and name variations
    """
    
    def __init__(self, data_dir: str = "backend/data"):
        """Initialize entity resolver with data directory"""
        self.data_dir = data_dir
        self.name_weight = 0.4
        self.father_name_weight = 0.3
        self.location_weight = 0.3
        self.min_confidence_threshold = 0.7
        
    def load_csv_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load CSV data from file"""
        filepath = os.path.join(self.data_dir, filename)
        records = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        
        return records
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names using fuzzy matching
        Returns score between 0 and 1
        """
        if not name1 or not name2:
            return 0.0
        
        # Normalize names (strip whitespace, lowercase)
        name1 = name1.strip().lower()
        name2 = name2.strip().lower()
        
        # Use token sort ratio to handle word order variations
        similarity = fuzz.token_sort_ratio(name1, name2)
        
        # Convert from 0-100 scale to 0-1 scale
        return similarity / 100.0
    
    def calculate_location_similarity(self, loc1: str, loc2: str) -> float:
        """
        Calculate similarity between two location strings
        Returns score between 0 and 1
        """
        if not loc1 or not loc2:
            return 0.0
        
        loc1 = loc1.strip().lower()
        loc2 = loc2.strip().lower()
        
        # Exact match gets full score
        if loc1 == loc2:
            return 1.0
        
        # Use partial ratio for substring matches
        similarity = fuzz.partial_ratio(loc1, loc2)
        
        return similarity / 100.0
    
    def calculate_confidence(
        self,
        field_similarities: Dict[str, float]
    ) -> float:
        """
        Calculate overall match confidence from field-level similarities
        Weighted average: name (0.4), father_name (0.3), location (0.3)
        """
        name_sim = field_similarities.get('name', 0.0)
        father_name_sim = field_similarities.get('father_name', 0.0)
        location_sim = field_similarities.get('location', 0.0)
        
        confidence = (
            name_sim * self.name_weight +
            father_name_sim * self.father_name_weight +
            location_sim * self.location_weight
        )
        
        return confidence
    
    def match_death_to_ration_cards(
        self,
        death_record: Dict[str, Any]
    ) -> List[MatchResult]:
        """
        Match a death record against ration card database
        Returns top 3 matches with confidence > 70%
        """
        # Load ration card records
        ration_records = self.load_csv_data("ration_card_records.csv")
        
        matches = []
        
        for ration_record in ration_records:
            # Calculate field similarities
            name_similarity = self.calculate_name_similarity(
                death_record.get('name', ''),
                ration_record.get('head_of_family', '')
            )
            
            father_name_similarity = self.calculate_name_similarity(
                death_record.get('father_name', ''),
                ration_record.get('father_name', '')
            )
            
            # Match on village and district
            death_location = f"{death_record.get('village', '')} {death_record.get('district', '')}"
            ration_location = f"{ration_record.get('village', '')} {ration_record.get('district', '')}"
            location_similarity = self.calculate_location_similarity(
                death_location,
                ration_location
            )
            
            field_similarities = {
                'name': name_similarity,
                'father_name': father_name_similarity,
                'location': location_similarity
            }
            
            # Calculate overall confidence
            confidence = self.calculate_confidence(field_similarities)
            
            # Only include matches above threshold
            if confidence >= self.min_confidence_threshold:
                match_result = MatchResult(
                    source_record_id=death_record.get('record_id', ''),
                    target_record_id=ration_record.get('card_number', ''),
                    target_database='ration_card',
                    confidence_score=confidence,
                    field_similarities=field_similarities,
                    matched_fields={
                        'name': (death_record.get('name', ''), ration_record.get('head_of_family', '')),
                        'father_name': (death_record.get('father_name', ''), ration_record.get('father_name', '')),
                        'village': (death_record.get('village', ''), ration_record.get('village', '')),
                        'district': (death_record.get('district', ''), ration_record.get('district', ''))
                    }
                )
                matches.append(match_result)
        
        # Sort by confidence score (descending) and return top 3
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches[:3]
    
    def match_death_to_aadhaar(
        self,
        death_record: Dict[str, Any]
    ) -> List[MatchResult]:
        """
        Match a death record against Aadhaar database
        Returns top 3 matches with confidence > 70%
        """
        # Load Aadhaar records
        aadhaar_records = self.load_csv_data("aadhaar_records.csv")
        
        matches = []
        
        for aadhaar_record in aadhaar_records:
            # Calculate field similarities
            name_similarity = self.calculate_name_similarity(
                death_record.get('name', ''),
                aadhaar_record.get('name', '')
            )
            
            father_name_similarity = self.calculate_name_similarity(
                death_record.get('father_name', ''),
                aadhaar_record.get('father_name', '')
            )
            
            # Match on village and district
            death_location = f"{death_record.get('village', '')} {death_record.get('district', '')}"
            aadhaar_location = f"{aadhaar_record.get('village', '')} {aadhaar_record.get('district', '')}"
            location_similarity = self.calculate_location_similarity(
                death_location,
                aadhaar_location
            )
            
            field_similarities = {
                'name': name_similarity,
                'father_name': father_name_similarity,
                'location': location_similarity
            }
            
            # Calculate overall confidence
            confidence = self.calculate_confidence(field_similarities)
            
            # Only include matches above threshold
            if confidence >= self.min_confidence_threshold:
                match_result = MatchResult(
                    source_record_id=death_record.get('record_id', ''),
                    target_record_id=aadhaar_record.get('aadhaar_number', ''),
                    target_database='aadhaar',
                    confidence_score=confidence,
                    field_similarities=field_similarities,
                    matched_fields={
                        'name': (death_record.get('name', ''), aadhaar_record.get('name', '')),
                        'father_name': (death_record.get('father_name', ''), aadhaar_record.get('father_name', '')),
                        'village': (death_record.get('village', ''), aadhaar_record.get('village', '')),
                        'district': (death_record.get('district', ''), aadhaar_record.get('district', ''))
                    }
                )
                matches.append(match_result)
        
        # Sort by confidence score (descending) and return top 3
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches[:3]
    
    def resolve_entity(
        self,
        source_record: Dict[str, Any],
        target_databases: List[str]
    ) -> List[MatchResult]:
        """
        Match a source record against target databases
        Returns ranked list of potential matches with confidence scores
        """
        all_matches = []
        
        for database in target_databases:
            if database == 'ration_card':
                matches = self.match_death_to_ration_cards(source_record)
                all_matches.extend(matches)
            elif database == 'aadhaar':
                matches = self.match_death_to_aadhaar(source_record)
                all_matches.extend(matches)
        
        # Sort all matches by confidence score (descending)
        all_matches.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return all_matches
