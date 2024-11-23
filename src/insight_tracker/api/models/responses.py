from dataclasses import dataclass, field
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
    area: Optional[str] = None
    relevance_score: Optional[int] = None
    description: Optional[str] = None
    evidence: Optional[List[str]] = field(default_factory=list)
    target_company_alignment: Optional[str] = None
    my_company_alignment: Optional[str] = None
    score_explanation: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExpertiseMatch':
        return cls(**data)

@dataclass
class DecisionMakerAnalysis:
    influence_level: Optional[str] = None
    influence_evidence: Optional[List[str]] = field(default_factory=list)
    budget_control: Optional[str] = None
    budget_evidence: Optional[List[str]] = field(default_factory=list)
    decision_areas: Optional[List[str]] = field(default_factory=list)
    stakeholder_relationships: Optional[List[str]] = field(default_factory=list)
    analysis_summary: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionMakerAnalysis':
        return cls(**data)

@dataclass
class CompanyAlignment:
    area: Optional[str] = None
    strength: Optional[int] = None
    description: Optional[str] = None
    evidence: Optional[List[str]] = field(default_factory=list)
    impact_potential: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyAlignment':
        return cls(**data)

@dataclass
class EngagementOpportunity:
    opportunity_description: Optional[str] = None
    rationale: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngagementOpportunity':
        return cls(**data)

@dataclass
class GrowthPotential:
    opportunity_area: Optional[str] = None
    analysis: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrowthPotential':
        return cls(**data)

@dataclass
class CulturalAlignment:
    cultural_aspect: Optional[str] = None
    evidence: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CulturalAlignment':
        return cls(**data)

@dataclass
class PotentialChallenge:
    challenge_description: Optional[str] = None
    impact_assessment: Optional[str] = None
    mitigation_strategy: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PotentialChallenge':
        return cls(**data)

@dataclass
class NextStep:
    step_description: Optional[str] = None
    rationale: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NextStep':
        return cls(**data)

@dataclass
class RecommendedApproach:
    approach_description: Optional[str] = None
    rationale: Optional[str] = None
    expected_outcomes: Optional[List[str]] = field(default_factory=list)
    resources_required: Optional[List[str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecommendedApproach':
        return cls(**data)

@dataclass
class ProfileFitEvaluation:
    fit_score: Optional[int] = None
    fit_summary: Optional[str] = None
    key_insights: Optional[List[str]] = field(default_factory=list)
    expertise_matches: Optional[List[ExpertiseMatch]] = field(default_factory=list)
    decision_maker_analysis: Optional[DecisionMakerAnalysis] = None
    business_model_fit: Optional[int] = None
    business_model_analysis: Optional[str] = None
    market_synergy: Optional[int] = None
    market_synergy_explanation: Optional[str] = None
    company_alignments: Optional[List[CompanyAlignment]] = field(default_factory=list)
    engagement_opportunities: Optional[List[EngagementOpportunity]] = field(default_factory=list)
    growth_potential: Optional[List[GrowthPotential]] = field(default_factory=list)
    cultural_alignment: Optional[List[CulturalAlignment]] = field(default_factory=list)
    potential_challenges: Optional[List[PotentialChallenge]] = field(default_factory=list)
    risk_analysis: Optional[str] = None
    recommended_approach: Optional[RecommendedApproach] = None
    priority_level: Optional[str] = None
    priority_justification: Optional[str] = None
    next_steps: Optional[List[NextStep]] = field(default_factory=list)
    competitive_analysis: Optional[str] = None
    long_term_potential: Optional[str] = None
    resource_implications: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileFitEvaluation':
        return cls(
            fit_score=data.get('fit_score'),
            fit_summary=data.get('fit_summary'),
            key_insights=data.get('key_insights', []),
            expertise_matches=[ExpertiseMatch.from_dict(em) for em in data.get('expertise_matches', [])],
            decision_maker_analysis=DecisionMakerAnalysis.from_dict(data.get('decision_maker_analysis', {})),
            business_model_fit=data.get('business_model_fit'),
            business_model_analysis=data.get('business_model_analysis'),
            market_synergy=data.get('market_synergy'),
            market_synergy_explanation=data.get('market_synergy_explanation'),
            company_alignments=[CompanyAlignment.from_dict(ca) for ca in data.get('company_alignments', [])],
            engagement_opportunities=[EngagementOpportunity.from_dict(eo) for eo in data.get('engagement_opportunities', [])],
            growth_potential=[GrowthPotential.from_dict(gp) for gp in data.get('growth_potential', [])],
            cultural_alignment=[CulturalAlignment.from_dict(ca) for ca in data.get('cultural_alignment', [])],
            potential_challenges=[PotentialChallenge.from_dict(pc) for pc in data.get('potential_challenges', [])],
            risk_analysis=data.get('risk_analysis'),
            recommended_approach=RecommendedApproach.from_dict(data.get('recommended_approach', {})),
            priority_level=data.get('priority_level'),
            priority_justification=data.get('priority_justification'),
            next_steps=[NextStep.from_dict(ns) for ns in data.get('next_steps', [])],
            competitive_analysis=data.get('competitive_analysis'),
            long_term_potential=data.get('long_term_potential'),
            resource_implications=data.get('resource_implications')
        )

@dataclass
class ProfileCompanyFitResponse:
    evaluation: ProfileFitEvaluation
    total_tokens: int
    status_code: int = 200

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileCompanyFitResponse':
        return cls(
            evaluation=ProfileFitEvaluation.from_dict(data['evaluation']),
            total_tokens=data['total_tokens'],
            status_code=data.get('status_code', 200)
        )

@dataclass
class OutreachResponse:
    email: str
    total_tokens: int
    status_code: int = 200

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutreachResponse':
        # Extract email from the nested structure
        if 'outreach_data' in data:
            email = data['outreach_data']['email']
        else:
            email = data.get('email', '')  # Fallback for backward compatibility
            
        return cls(
            email=email,
            total_tokens=data.get('total_tokens', 0),
            status_code=data.get('status_code', 200)
        )

@dataclass
class MeetingAgendaItem:
    title: str
    duration: str
    description: Optional[str] = None
    objectives: Optional[List[str]] = field(default_factory=list)

@dataclass
class MeetingPreparation:
    meeting_objectives: List[str]
    key_talking_points: List[str]
    prepared_questions: List[str]
    risk_factors: List[str]
    success_metrics: List[str]
    next_steps: List[str]
    follow_up_items: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeetingPreparation':
        return cls(
            meeting_objectives=data.get('meeting_objectives', []),
            key_talking_points=data.get('key_talking_points', []),
            prepared_questions=data.get('prepared_questions', []),
            risk_factors=data.get('risk_factors', []),
            success_metrics=data.get('success_metrics', []),
            next_steps=data.get('next_steps', []),
            follow_up_items=data.get('follow_up_items', [])
        )

@dataclass
class MeetingResponse:
    meeting_preparation: MeetingPreparation
    total_tokens: int
    status_code: int = 200

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeetingResponse':
        # First create the MeetingPreparation instance
        meeting_preparation = MeetingPreparation.from_dict(data['meeting_preparation'])
        
        # Then create the MeetingResponse with the proper structure
        return cls(
            meeting_preparation=meeting_preparation,
            total_tokens=data['total_tokens'],
            status_code=data.get('status_code', 200)
        )