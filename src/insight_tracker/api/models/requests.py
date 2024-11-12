from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ApiKeyRequest:
    email: str

@dataclass
class CompanyInsightRequest:
    company_name: str
    industry: str
    language: str = "en"
    scrape_employees: bool = False

@dataclass
class CompanyInsightByUrlRequest:
    company_url: str
    language: str = "en"
    scrape_employees: bool = False

@dataclass
class ProfileInsightRequest:
    full_name: str
    company_name: str
    language: str = "en"

@dataclass
class OutreachEmailRequest:
    profile: Dict[str, str]
    sender_info: Optional[Dict[str, str]] = None
    language: str = "en"
    proposal_url: Optional[str] = None 