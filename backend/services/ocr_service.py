"""
OCR Service - Integrates Tamil OCR processing
This is a placeholder that will integrate with your existing Tamil OCR code
"""

import re
from typing import Dict, List, Any
import PyPDF2
import io


class OCRService:
    """OCR processing service for Tamil and English documents"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.ocr_model = None
        try:
            from ocr_tamil.ocr import OCR
            # Initialize with detect=True for full pipeline, details=2 for confidence
            # enable_cuda=False for Mac compatibility unless GPU confirmed
            self.ocr_model = OCR(detect=True, details=2, enable_cuda=False)
            print("✅ Tamil OCR Model initialized successfully")
        except ImportError as e:
            print(f"⚠️ Tamil OCR module not found: {e}. Using fallback.")
        except Exception as e:
            print(f"⚠️ Tamil OCR init failed: {e}. Using fallback.")

    def detect_language(self, pdf_path: str) -> Dict[str, Any]:
        """
        Detect language of the document
        
        Returns:
            {
                "language": "tamil_primary" | "tamil_english_mixed" | "english_primary" | "unknown",
                "tamil_ratio": float,
                "english_ratio": float
            }
        """
        # Extract sample text from first 2 pages + random middle page
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Sample pages
            sample_pages = [0, 1]
            if total_pages > 3:
                sample_pages.append(total_pages // 2)
            
            sample_text = ""
            for page_num in sample_pages:
                if page_num < total_pages:
                    sample_text += pdf_reader.pages[page_num].extract_text() or ""
        
        # Count character types
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', sample_text))
        english_chars = len(re.findall(r'[a-zA-Z]', sample_text))
        total_chars = len(sample_text.strip())
        
        if total_chars == 0:
            return {"language": "unknown", "tamil_ratio": 0, "english_ratio": 0}
        
        tamil_ratio = tamil_chars / total_chars
        english_ratio = english_chars / total_chars
        
        # Classify
        if tamil_ratio > 0.4:
            language = "tamil_primary"
        elif tamil_ratio > 0.15:
            language = "tamil_english_mixed"
        elif english_ratio > 0.7:
            language = "english_primary"
        else:
            language = "unknown"
        
        return {
            "language": language,
            "tamil_ratio": tamil_ratio,
            "english_ratio": english_ratio
        }

    async def process_document(self, pdf_path: str, language: str) -> Dict[str, Any]:
        """
        Process document with OCR using ocr_tamil library
        """
        import time
        from pdf2image import convert_from_path
        import numpy as np

        start_time = time.time()
        
        full_text = ""
        page_wise = []
        overall_confidences = []

        if self.ocr_model:
            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                # Convert PIL images to numpy arrays
                np_images = [np.array(img) for img in images]
                
                # Predict
                # predict handles list of images
                # Output format with details=2: list of (text, conf, bbox) lists per image
                # Wait, ocr.predict(list) returns list of results.
                # structure: [ [(text, conf, bbox), ...], [(text, conf, bbox), ...] ]
                
                # Running prediction
                predictions = self.ocr_model.predict(np_images)
                
                for i, page_result in enumerate(predictions):
                    page_text = ""
                    page_confs = []
                    
                    # page_result is a list of tuples (text, conf, bbox) or (text, conf) depending on implementation details
                    # If details=2 and bbox available
                    
                    for item in page_result:
                        # Unpack based on length to be safe
                        if len(item) >= 2:
                            text = item[0]
                            conf = item[1]
                            # bbox = item[2] if len(item) > 2 else None
                            
                            page_text += text + " "
                            page_confs.append(float(conf))
                    
                    avg_page_conf = sum(page_confs) / len(page_confs) if page_confs else 0.0
                    overall_confidences.extend(page_confs)
                    
                    page_wise.append({
                        "page": i + 1,
                        "text": page_text.strip(),
                        "confidence": avg_page_conf
                    })
                    
                    full_text += page_text + "\n"
                    
            except Exception as e:
                print(f"❌ Custom OCR failed: {e}. Falling back to text extraction.")
                # Fallback logic below (same as original placeholder)
                return await self._fallback_extraction(pdf_path, language, start_time)

        else:
             return await self._fallback_extraction(pdf_path, language, start_time)

        # Post-processing cleanup
        full_text = self._cleanup_text(full_text)
        
        processing_time = time.time() - start_time
        final_confidence = sum(overall_confidences) / len(overall_confidences) if overall_confidences else 0.0
        
        return {
            "full_text": full_text,
            "page_wise": page_wise,
            "overall_confidence": final_confidence,
            "processing_time": processing_time,
            "detected_language": language
        }

    async def _fallback_extraction(self, pdf_path, language, start_time):
        """Fallback to simple text extraction"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_wise = []
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text() or ""
                full_text += text + "\n"
                page_wise.append({
                    "page": page_num + 1,
                    "text": text,
                    "confidence": 0.60 # Low confidence for fallback
                })
        
        full_text = self._cleanup_text(full_text)
        return {
            "full_text": full_text,
            "page_wise": page_wise,
            "overall_confidence": 0.60,
            "processing_time": time.time() - start_time,
            "detected_language": language
        }
    
    def _cleanup_text(self, text: str) -> str:
        """
        Post-processing cleanup of OCR text
        - Remove headers/footers
        - Remove page numbers
        - Normalize Unicode
        - Fix common OCR errors
        """
        # Remove common headers/footers
        text = re.sub(r'பக்கம்\s*\d+', '', text)
        text = re.sub(r'Page\s*\d+\s*of\s*\d+', '', text, flags=re.IGNORECASE)
        
        # Remove standalone page numbers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove duplicate spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove duplicate newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def check_quality(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check OCR quality
        
        Returns:
            {
                "pass": bool,
                "reason": str (if failed),
                "quality_score": float
            }
        """
        text = ocr_result["full_text"]
        confidence = ocr_result["overall_confidence"]
        
        # Metric 1: Minimum text length
        if len(text) < 200:
            return {
                "pass": False,
                "reason": "insufficient_text",
                "quality_score": 0.0
            }
        
        # Metric 2: Confidence threshold
        if confidence < 0.70:
            return {
                "pass": False,
                "reason": "low_confidence",
                "quality_score": confidence
            }
        
        # Metric 3: Noise ratio
        special_chars = len(re.findall(r'[^a-zA-Z0-9\u0B80-\u0BFF\s.,;:!?()\-]', text))
        noise_ratio = special_chars / len(text) if len(text) > 0 else 1.0
        
        if noise_ratio > 0.3:
            return {
                "pass": False,
                "reason": "high_noise",
                "quality_score": 1.0 - noise_ratio
            }
        
        # Metric 4: Sentence continuity
        sentences = re.split(r'[.!?।]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 5:
            return {
                "pass": False,
                "reason": "fragmented_text",
                "quality_score": len(sentences) / 5.0
            }
        
        return {
            "pass": True,
            "quality_score": confidence
        }
