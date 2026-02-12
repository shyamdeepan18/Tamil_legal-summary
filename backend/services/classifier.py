"""
Document Classifier - Classifies legal documents by type
"""

import re
from typing import Dict, List, Any


class DocumentClassifier:
    """Classifies Tamil legal documents"""
    
    # Supported document types with keywords
    SUPPORTED_DOCS = {
        "sale_deed": {
            "tamil_names": ["விற்பனை பத்திரம்", "வில்பத்திரம்"],
            "english_names": ["sale deed", "conveyance deed"],
            "keywords": ["விற்பனையாளர்", "வாங்குபவர்", "சர்வே", "நிலம்", "seller", "purchaser", "survey", "land"]
        },
        "agreement_to_sell": {
            "tamil_names": ["ஒப்பந்தம்", "உடன்படிக்கை"],
            "english_names": ["agreement to sell", "agreement"],
            "keywords": ["முன்பணம்", "advance", "terms", "conditions", "ஒப்பந்தம்"]
        },
        "encumbrance_certificate": {
            "tamil_names": ["சுமையில்லா சான்றிதழ்", "பாரமில்லா சான்றிதழ்"],
            "english_names": ["encumbrance certificate", "ec"],
            "keywords": ["sub registrar", "registration district", "பதிவாளர்"]
        },
        "power_of_attorney": {
            "tamil_names": ["அதிகாரப் பத்திரம்", "பவர் ஆஃப் அட்டார்னி"],
            "english_names": ["power of attorney", "poa"],
            "keywords": ["attorney", "represent", "அதிகாரம்"]
        },
        "court_order": {
            "tamil_names": ["நீதிமன்ற உத்தரவு"],
            "english_names": ["court order", "judgment", "decree"],
            "keywords": ["hon'ble", "petitioner", "respondent", "case no", "நீதிமன்றம்"]
        },
        "loan_agreement": {
            "tamil_names": ["கடன் ஒப்பந்தம்"],
            "english_names": ["loan agreement", "mortgage deed"],
            "keywords": ["loan amount", "emi", "interest rate", "repayment", "கடன்"]
        },
        "lease_deed": {
            "tamil_names": ["குத்தகை பத்திரம்"],
            "english_names": ["lease deed", "rental agreement"],
            "keywords": ["lease period", "rent", "lessee", "lessor", "குத்தகை"]
        },
        "property_tax": {
            "tamil_names": ["சொத்து வரி"],
            "english_names": ["property tax", "tax receipt"],
            "keywords": ["assessment", "tax", "municipal", "corporation", "வரி"]
        }
    }
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify document based on content
        
        Returns:
            {
                "type": str,
                "confidence": "high" | "medium" | "low",
                "method": "header" | "keywords" | "llm"
            }
        """
        text_lower = text.lower()
        
        # Method 1: Header detection (fastest)
        first_page = text[:1000].lower()
        
        for doc_type, config in self.SUPPORTED_DOCS.items():
            for name in config['tamil_names'] + config['english_names']:
                if name.lower() in first_page:
                    return {
                        "type": doc_type,
                        "confidence": "high",
                        "method": "header"
                    }
        
        # Method 2: Keyword scoring
        scores = {}
        for doc_type, config in self.SUPPORTED_DOCS.items():
            score = 0
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    score += 1
            scores[doc_type] = score
        
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] >= 3:
                return {
                    "type": best_match,
                    "confidence": "medium",
                    "method": "keywords",
                    "score": scores[best_match]
                }
        
        # If no match found
        return {
            "type": "unsupported",
            "confidence": "low",
            "method": "none"
        }
    
    def get_document_info(self, doc_type: str) -> Dict[str, Any]:
        """Get information about a document type"""
        if doc_type in self.SUPPORTED_DOCS:
            return self.SUPPORTED_DOCS[doc_type]
        return {}
