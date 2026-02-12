"""
Red Flags Detection Service
Scans documents for concerning patterns across 5 categories
"""

import re
from typing import Dict, List, Any


class RedFlagsDetector:
    """Detects red flags in legal documents"""
    
    # Red flag patterns organized by category
    RED_FLAG_PATTERNS = {
        "legal_issues": {
            "severity": "high",
            "patterns": [
                {
                    "name": "court_case",
                    "tamil": ["வழக்கு எண்", "நீதிமன்ற", "வழக்கு", "தீர்ப்பு"],
                    "english": ["case no", "court case", "litigation", "suit", "petition"],
                    "explanation_tamil": "நீதிமன்ற வழக்கு குறிப்பிடப்பட்டுள்ளது",
                    "explanation_english": "Court case reference found",
                    "action": "Verify if case is resolved before proceeding"
                },
                {
                    "name": "stay_order",
                    "tamil": ["தடை உத்தரவு", "நிறுத்தம்"],
                    "english": ["stay order", "injunction", "restraining order"],
                    "explanation_tamil": "தடை உத்தரவு இருக்கலாம்",
                    "explanation_english": "Stay/injunction order may exist",
                    "action": "Critical - Consult lawyer immediately"
                },
                {
                    "name": "dispute",
                    "tamil": ["சர்ச்சை", "பிரச்சினை", "மோதல்"],
                    "english": ["dispute", "contested", "conflict"],
                    "explanation_tamil": "சொத்து சர்ச்சை குறிப்பிடப்பட்டுள்ளது",
                    "explanation_english": "Property dispute mentioned",
                    "action": "Investigate nature of dispute"
                }
            ]
        },
        "financial_issues": {
            "severity": "high",
            "patterns": [
                {
                    "name": "pending_payment",
                    "tamil": ["நிலுவை", "மீதித் தொகை", "மீதி பணம்"],
                    "english": ["balance payment", "pending amount", "remaining"],
                    "explanation_tamil": "நிலுவை தொகை இருக்கிறது",
                    "explanation_english": "Pending payment obligation exists",
                    "action": "Clarify payment terms and schedule"
                },
                {
                    "name": "installment",
                    "tamil": ["தவணை", "தவணை முறை"],
                    "english": ["installment", "emi", "periodic payment"],
                    "explanation_tamil": "தவணை முறை பணம் செலுத்துதல்",
                    "explanation_english": "Installment payment structure",
                    "action": "Review payment schedule carefully"
                },
                {
                    "name": "loan",
                    "tamil": ["கடன்", "கடன் தொகை"],
                    "english": ["loan", "borrowed", "debt"],
                    "explanation_tamil": "கடன் குறிப்பிடப்பட்டுள்ளது",
                    "explanation_english": "Loan mentioned in document",
                    "action": "Check if loan is cleared"
                }
            ]
        },
        "encumbrance": {
            "severity": "high",
            "patterns": [
                {
                    "name": "mortgage",
                    "tamil": ["அடமானம்", "அடமான பத்திரம்"],
                    "english": ["mortgage", "mortgaged", "hypothecated"],
                    "explanation_tamil": "சொத்து அடமானம் வைக்கப்பட்டுள்ளது",
                    "explanation_english": "Property is mortgaged",
                    "action": "Verify mortgage clearance certificate"
                },
                {
                    "name": "lien",
                    "tamil": ["உரிமைக் கோரல்"],
                    "english": ["lien", "charge", "encumbrance"],
                    "explanation_tamil": "சொத்தின் மீது உரிமைக் கோரல் உள்ளது",
                    "explanation_english": "Lien/charge exists on property",
                    "action": "Obtain encumbrance certificate"
                }
            ]
        },
        "ownership_issues": {
            "severity": "medium",
            "patterns": [
                {
                    "name": "multiple_owners",
                    "tamil": ["பல உரிமையாளர்கள்", "அனைவரும் விற்பனையாளர்"],
                    "english": ["multiple sellers", "joint owners", "co-owners"],
                    "explanation_tamil": "பல விற்பனையாளர்கள்",
                    "explanation_english": "Multiple sellers/owners involved",
                    "action": "Ensure all owners have signed"
                },
                {
                    "name": "inheritance",
                    "tamil": ["வாரிசு", "பங்கு", "பிரிவினை"],
                    "english": ["inheritance", "partition", "succession"],
                    "explanation_tamil": "வாரிசு சொத்து பிரிவினை",
                    "explanation_english": "Inherited property / partition",
                    "action": "Verify legal heir certificates"
                },
                {
                    "name": "poa_sale",
                    "tamil": ["அதிகார பத்திரம் மூலம்", "பவர் ஆஃப் அட்டார்னி"],
                    "english": ["power of attorney", "poa holder", "attorney"],
                    "explanation_tamil": "அதிகார பத்திரம் மூலம் விற்பனை",
                    "explanation_english": "Sale through Power of Attorney",
                    "action": "Verify POA validity and scope"
                }
            ]
        },
        "documentation": {
            "severity": "medium",
            "patterns": [
                {
                    "name": "missing_signatures",
                    "tamil": ["கையொப்பம் இல்லை", "சாட்சி கையொப்பம் இல்லை"],
                    "english": ["unsigned", "signature pending", "not witnessed"],
                    "explanation_tamil": "கையொப்பம் / சாட்சி இல்லை",
                    "explanation_english": "Signature/witness missing",
                    "action": "Ensure all parties sign before registration"
                },
                {
                    "name": "unregistered",
                    "tamil": ["பதிவு செய்யப்படவில்லை", "பதிவு நிலுவை"],
                    "english": ["unregistered", "registration pending"],
                    "explanation_tamil": "பதிவு செய்யப்படவில்லை",
                    "explanation_english": "Document not registered",
                    "action": "Registration is mandatory for validity"
                },
                {
                    "name": "conditional",
                    "tamil": ["நிபந்தனை", "கட்டுப்பாடு"],
                    "english": ["subject to", "conditional", "contingent"],
                    "explanation_tamil": "நிபந்தனைகள் உள்ளன",
                    "explanation_english": "Conditional terms present",
                    "action": "Review all conditions carefully"
                }
            ]
        }
    }
    
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scan document for red flag patterns
        
        Returns list of found flags with context
        """
        found_flags = []
        text_lower = text.lower()
        
        for category, config in self.RED_FLAG_PATTERNS.items():
            for pattern in config['patterns']:
                # Check Tamil keywords
                for keyword in pattern['tamil']:
                    if keyword in text_lower:
                        context = self._extract_context(text, keyword, chars=80)
                        found_flags.append({
                            "category": category,
                            "name": pattern['name'],
                            "severity": config['severity'],
                            "keyword_matched": keyword,
                            "context": context,
                            "explanation_tamil": pattern['explanation_tamil'],
                            "explanation_english": pattern['explanation_english'],
                            "action": pattern['action']
                        })
                        break  # One match per pattern is enough
                
                # Check English keywords (if not already matched)
                if not any(f['name'] == pattern['name'] for f in found_flags):
                    for keyword in pattern['english']:
                        if keyword in text_lower:
                            context = self._extract_context(text, keyword, chars=80)
                            found_flags.append({
                                "category": category,
                                "name": pattern['name'],
                                "severity": config['severity'],
                                "keyword_matched": keyword,
                                "context": context,
                                "explanation_tamil": pattern['explanation_tamil'],
                                "explanation_english": pattern['explanation_english'],
                                "action": pattern['action']
                            })
                            break
        
        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        found_flags.sort(key=lambda x: severity_order[x['severity']])
        
        return found_flags
    
    def _extract_context(self, text: str, keyword: str, chars: int = 80) -> str:
        """Extract surrounding context for better understanding"""
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        
        index = text_lower.find(keyword_lower)
        if index == -1:
            return ""
        
        start = max(0, index - chars)
        end = min(len(text), index + len(keyword) + chars)
        
        context = text[start:end]
        
        # Trim to sentence boundaries
        sentences = context.split('.')
        if len(sentences) > 1:
            context = sentences[0] + '...'
        
        return context.strip()
    
    def get_summary(self, flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of red flags"""
        high_priority = [f for f in flags if f['severity'] == 'high']
        medium_priority = [f for f in flags if f['severity'] == 'medium']
        
        return {
            "total_flags": len(flags),
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "categories_affected": list(set(f['category'] for f in flags)),
            "critical_actions_required": len(high_priority) > 0
        }
