from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class ErrorResponse:
    error: str
    status_code: int

@dataclass
class ProfessionalProfile:
    full_name: str
    current_job_title: Optional[str] = None
    current_company: Optional[str] = None
    current_company_url: Optional[str] = None
    professional_background: Optional[str] = None
    past_jobs: Optional[str] = None
    key_achievements: Optional[str] = None
    contact: Optional[str] = None
    linkedin_url: Optional[str] = None

@dataclass
class Company:
    company_name: str
    company_website: Optional[str] = None
    company_linkedin: Optional[str] = None
    company_summary: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_services: Optional[List[str]] = None
    company_industries: Optional[List[str]] = None
    company_awards_recognitions: Optional[List[str]] = None
    company_clients_partners: Optional[List[str]] = None
    company_founded_year: Optional[int] = None
    company_headquarters: Optional[str] = None
    company_culture: Optional[List[str]] = None
    company_recent_updates: Optional[List[str]] = None

@dataclass
class CompanyInsightResponse:
    company: Company
    total_tokens: int
    status_code: int = 200
    employee_links: Optional[List[str]] = None

@dataclass
class ProfileInsightResponse:
    profile: ProfessionalProfile
    total_tokens: int
    status_code: Optional[int] = 200

@dataclass
class Profile:
    full_name: str
    current_job_title: Optional[str] = None
    professional_background: Optional[str] = None
    past_jobs: Optional[str] = None
    key_achievements: Optional[str] = None
    contact: Optional[str] = None
    linkedin_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Profile':
        return cls(**data)

@dataclass
class EmailResponse:
    email: str
    subject: Optional[str] = None
    total_tokens: Optional[int] = None
    status_code: Optional[int] = 200

    def __post_init__(self):
        """Ensure email content exists"""
        if not self.email:
            self.email = "No email content generated"

@dataclass
class ExpertiseMatch:
    expertise_area: str
    match_score: int

@dataclass
class DecisionMakerAnalysis:
    is_decision_maker: bool
    influence_level: int

@dataclass
class CompanyAlignment:
    alignment_area: str
    alignment_score: int

@dataclass
class ProfileFitEvaluation:
    fit_score: int
    fit_summary: str
    key_insights: List[str]
    expertise_matches: List[ExpertiseMatch]
    decision_maker_analysis: DecisionMakerAnalysis
    business_model_fit: int
    business_model_analysis: str
    market_synergy: int
    market_synergy_explanation: str
    company_alignments: List[CompanyAlignment]
    engagement_opportunities: List[Dict[str, str]]
    growth_potential: List[Dict[str, str]]
    cultural_alignment: List[Dict[str, str]]
    potential_challenges: List[Dict[str, Any]]
    risk_analysis: str
    recommended_approach: Dict[str, Any]
    priority_level: str
    priority_justification: str
    next_steps: List[Dict[str, str]]
    competitive_analysis: str
    long_term_potential: str
    resource_implications: str

@dataclass
class ProfileCompanyFitResponse:
    evaluation: ProfileFitEvaluation
    total_tokens: int
    status_code: int = 200