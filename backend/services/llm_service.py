"""
LLM Service - Document summarization with COST-EFFECTIVE options
Supports: Google Gemini Flash (FREE), Groq (FREE), OpenAI (PAID)
"""

from typing import Dict, List, Any, Optional
import asyncio
import os

from config import settings


class LLMService:
    """LLM-based document summarization with multiple providers"""
    
    def __init__(self):
        """Initialize LLM client based on available API keys"""
        self.provider = self._detect_provider()
        self._init_client()
    
    def _detect_provider(self) -> str:
        """Detect which LLM provider to use based on available API keys"""
        # Priority: Gemini (free) > Groq (free) > OpenAI (paid)
        if os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("GROQ_API_KEY"):
            return "groq"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        else:
            return "none"
    
    def _init_client(self):
        """Initialize the appropriate client"""
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai.GenerativeModel('gemini-1.5-flash')
            self.model_name = "gemini-1.5-flash"
        
        elif self.provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model_name = "llama-3.1-70b-versatile"
        
        elif self.provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model_name = "gpt-4o-mini"
        
        else:
            self.client = None
            self.model_name = "none"
    
    async def generate_summary(
        self,
        ocr_text: str,
        doc_type: str,
        red_flags: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary using available LLM provider
        
        Returns:
            {
                "summary": str,
                "confidence": "high" | "medium" | "low",
                "model": str,
                "tokens_used": int,
                "cost": float
            }
        """
        if self.provider == "none":
            return self._generate_fallback_summary(ocr_text, doc_type, red_flags)
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(ocr_text, doc_type, red_flags)
        
        try:
            if self.provider == "gemini":
                return await self._generate_with_gemini(system_prompt, user_prompt)
            elif self.provider == "groq":
                return await self._generate_with_groq(system_prompt, user_prompt)
            elif self.provider == "openai":
                return await self._generate_with_openai(system_prompt, user_prompt)
        
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_fallback_summary(ocr_text, doc_type, red_flags)
    
    async def _generate_with_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate with Google Gemini Flash (FREE - 15 requests/min, 1M tokens/day)"""
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = await asyncio.to_thread(
            self.client.generate_content,
            full_prompt
        )
        
        summary = response.text
        # Gemini doesn't provide token count in free tier
        tokens_used = len(summary.split()) * 1.3  # Rough estimate
        
        confidence = self._assess_confidence(summary, user_prompt)
        
        return {
            "summary": summary,
            "confidence": confidence,
            "model": self.model_name,
            "tokens_used": int(tokens_used),
            "cost": 0.0,  # FREE!
            "provider": "gemini"
        }
    
    async def _generate_with_groq(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate with Groq (FREE - very fast, 30 req/min)"""
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        summary = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        confidence = self._assess_confidence(summary, user_prompt)
        
        return {
            "summary": summary,
            "confidence": confidence,
            "model": self.model_name,
            "tokens_used": tokens_used,
            "cost": 0.0,  # FREE!
            "provider": "groq"
        }
    
    async def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate with OpenAI GPT-4o-mini (PAID - ~₹0.15 per doc)"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=30
        )
        
        summary = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Calculate cost (GPT-4o-mini: $0.15/1M input, $0.60/1M output)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost_usd = (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000)
        cost_inr = cost_usd * 83  # Approximate USD to INR
        
        confidence = self._assess_confidence(summary, user_prompt)
        
        return {
            "summary": summary,
            "confidence": confidence,
            "model": self.model_name,
            "tokens_used": tokens_used,
            "cost": cost_inr,
            "provider": "openai"
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return """You are an expert Tamil legal document analyzer for Indian users. Your goal is to extract key information accurately and present it in simple Tamil + English mixed format.

CRITICAL RULES:
1. NEVER make assumptions about missing information
2. NEVER provide legal advice or opinions
3. NEVER say "this document is safe" or "you should buy"
4. If information is not mentioned, explicitly state "குறிப்பிடப்படவில்லை / Not mentioned"
5. Use simple language - target audience is common people, not lawyers
6. Mix Tamil and English naturally (how people actually speak)
7. Be precise with numbers, dates, names
8. Flag inconsistencies if found

OUTPUT LANGUAGE:
- Use Tamil script for Tamil words
- Use English for: amounts (₹50,000), dates (15/03/2023), technical terms
- Natural mixing: "விற்பனையாளர் Mr. Kumar has agreed to sell..."
"""
    
    def _get_user_prompt(
        self,
        ocr_text: str,
        doc_type: str,
        red_flags: List[Dict[str, Any]]
    ) -> str:
        """Get user prompt with document-specific instructions"""
        
        doc_instructions = self._get_doc_type_instructions(doc_type)
        red_flags_text = self._format_red_flags(red_flags)
        
        return f"""DOCUMENT TYPE: {doc_type}

DOCUMENT TEXT:
{ocr_text[:8000]}  

{doc_instructions}

RED FLAGS DETECTED:
{red_flags_text}

Please provide a comprehensive summary following the structure above. Remember:
- Use Tamil + English mixed naturally
- State "Not mentioned" for missing info
- Be precise with numbers and dates
- No legal advice or recommendations
- Confidence level: Indicate if any section had poor OCR quality
"""
    
    def _get_doc_type_instructions(self, doc_type: str) -> str:
        """Get document-type-specific extraction instructions"""
        
        instructions = {
            "sale_deed": """
EXTRACT FOR SALE DEED:

1. பத்திர விவரங்கள் / Document Details:
   - Document type, Registration date and number, Sub-registrar office, Document value

2. விற்பனையாளர் / Seller Details:
   - Full name (exactly as written), Father's/Husband's name, Address, Age

3. வாங்குபவர் / Purchaser Details:
   - Full name, Father's/Husband's name, Address, Age

4. சொத்து விவரம் / Property Details:
   - Survey number, Plot/door number, Village/Town/City, Taluk and District
   - Total extent (acres/cents/sq.ft), Boundaries (N/S/E/W), Current usage

5. நிதி விவரங்கள் / Financial Terms:
   - Total sale consideration, Advance paid, Balance payment, Payment mode/date

6. முக்கிய விதிமுறைகள் / Important Clauses:
   - Possession date, Tax payment responsibility, Encumbrance status, Warranties

7. கையொப்பங்கள் / Signatures:
   - Seller/Purchaser/Witness signatures count and names

8. Missing Information: List all missing standard elements
""",
            "agreement_to_sell": """
EXTRACT FOR AGREEMENT:

1. ஒப்பந்த விவரங்கள் / Agreement Details
2. Parties (seller/buyer details)
3. Property Details
4. நிதி விதிமுறைகள் / Financial Terms (price, advance, balance schedule)
5. கால அட்டவணை / Timeline (sale deed date, possession date)
6. நிபந்தனைகள் / Conditions
7. Missing Information
""",
            "encumbrance_certificate": """
EXTRACT FOR EC:

1. சான்றிதழ் விவரங்கள் / Certificate Details
2. சொத்து விவரம் / Property Details
3. பதிவுகள் / Registrations Found (or NIL)
4. முக்கியமான குறிப்புகள் / Important Notes
5. Missing Information
"""
        }
        
        return instructions.get(doc_type, "Extract all key information from the document.")
    
    def _format_red_flags(self, red_flags: List[Dict[str, Any]]) -> str:
        """Format red flags for LLM context"""
        if not red_flags:
            return "None detected in automated scan"
        
        formatted = "The following patterns were detected:\n"
        for flag in red_flags:
            formatted += f"- {flag['explanation_english']}: {flag['context'][:100]}...\n"
        
        return formatted
    
    def _assess_confidence(self, summary: str, ocr_text: str) -> str:
        """Assess confidence in the summary"""
        # Check for "not mentioned" frequency
        not_mentioned_count = summary.lower().count("not mentioned") + \
                             summary.lower().count("குறிப்பிடப்படவில்லை")
        
        # Check summary completeness
        key_sections = ["விற்பனையாளர்", "வாங்குபவர்", "சொத்து", "தொகை"]
        sections_present = sum(1 for section in key_sections if section in summary)
        
        if not_mentioned_count > 5:
            return "low"
        elif sections_present >= 3 and not_mentioned_count <= 2:
            return "high"
        else:
            return "medium"
    
    def _generate_fallback_summary(
        self,
        ocr_text: str,
        doc_type: str,
        red_flags: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic summary without LLM (fallback)"""
        
        summary = f"""# {doc_type.upper()} SUMMARY

⚠️ Automated summary (LLM unavailable)

## Document Type
{doc_type}

## Red Flags
{len(red_flags)} issues detected

## Full Text Preview
{ocr_text[:500]}...

Please contact support for detailed analysis.
"""
        
        return {
            "summary": summary,
            "confidence": "low",
            "model": "fallback",
            "tokens_used": 0,
            "cost": 0.0,
            "provider": "fallback"
        }
