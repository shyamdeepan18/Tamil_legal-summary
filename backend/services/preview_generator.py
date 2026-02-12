"""
Preview Generator - Creates free preview before payment
"""

import re
from typing import Dict, Any


class PreviewGenerator:
    """Generates document preview using only OCR metadata and regex"""
    
    def generate(
        self,
        upload_id: str,
        ocr_result: Dict[str, Any],
        classification: Dict[str, Any],
        page_count: int,
        file_size: int
    ) -> Dict[str, Any]:
        """
        Generate preview using:
        - OCR metadata (already done)
        - Keyword detection (regex)
        - Basic pattern matching
        
        Total cost: ₹0
        Processing time: <2 seconds
        """
        text = ocr_result['full_text']
        
        # Quick entity detection
        has_property = bool(re.search(r'சர்வே|survey no|plot', text, re.I))
        has_parties = bool(re.search(r'விற்பனையாளர்|வாங்குபவர்|seller|purchaser', text, re.I))
        has_financial = bool(re.search(r'ரூ|₹|rs\.?\s*\d+', text, re.I))
        has_signatures = bool(re.search(r'கையொப்பம்|signature|witnessed', text, re.I))
        
        # Detect potential issues (keyword-based)
        has_court_ref = bool(re.search(r'வழக்கு|court case|litigation', text, re.I))
        has_encumbrance = bool(re.search(r'அடமானம்|mortgage|encumbrance', text, re.I))
        
        # Estimate processing time based on page count
        estimated_time = min(25 + (page_count * 2), 60)  # 25s base + 2s per page, max 60s
        
        return {
            "doc_type": classification['type'],
            "doc_type_tamil": self._get_tamil_name(classification['type']),
            "quality_score": ocr_result['overall_confidence'],
            "page_count": page_count,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "language": ocr_result['detected_language'],
            "estimated_time": estimated_time,
            "detected_elements": {
                "property_details": has_property,
                "party_information": has_parties,
                "financial_terms": has_financial,
                "signatures": has_signatures
            },
            "potential_flags": {
                "court_references": has_court_ref,
                "encumbrance_mentions": has_encumbrance
            },
            "preview_message": self._generate_preview_message(
                has_property, has_parties, has_financial, has_court_ref
            )
        }
    
    def _get_tamil_name(self, doc_type: str) -> str:
        """Get Tamil name for document type"""
        tamil_names = {
            "sale_deed": "விற்பனை பத்திரம்",
            "agreement_to_sell": "ஒப்பந்தம்",
            "encumbrance_certificate": "சுமையில்லா சான்றிதழ்",
            "power_of_attorney": "அதிகாரப் பத்திரம்",
            "court_order": "நீதிமன்ற உத்தரவு",
            "loan_agreement": "கடன் ஒப்பந்தம்",
            "lease_deed": "குத்தகை பத்திரம்",
            "property_tax": "சொத்து வரி"
        }
        return tamil_names.get(doc_type, "")
    
    def _generate_preview_message(
        self,
        has_property: bool,
        has_parties: bool,
        has_financial: bool,
        has_court_ref: bool
    ) -> str:
        """Generate user-friendly preview message"""
        if has_court_ref:
            return "⚠️ Possible court reference found - detailed analysis recommended"
        elif has_property and has_parties and has_financial:
            return "✅ Document appears complete with all key elements"
        elif not has_property:
            return "⚠️ Property details may be missing - review needed"
        else:
            return "✓ Document ready for analysis"
