from typing import Optional, Dict, Any, List
from ..client.insight_client import InsightApiClient
from ..exceptions.api_exceptions import ApiError
from ..models.responses import ProfileInsightResponse, CompanyInsightResponse, EmailResponse, ProfessionalProfile

class InsightService:
    def __init__(self, api_client: InsightApiClient):
        self.api_client = api_client

    async def generate_api_key(self, email: str) -> str:
        """Generate new API key"""
        try:
            return await self.api_client.generate_api_key(email)
        except ApiError as e:
            raise

    async def get_company_analysis(
        self,
        company_name: str,
        industry: str,
        language: str = "en",
        scrape_employees: bool = False
    ) -> CompanyInsightResponse:
        """Get company analysis"""
        try:
            response = await self.api_client.get_company_insight(
                company_name=company_name,
                industry=industry,
                language=language,
                scrape_employees=scrape_employees
            )
            return CompanyInsightResponse(**response)
        except ApiError as e:
            raise

    async def get_company_analysis_by_url(
        self,
        company_url: str,
        language: str = "en",
        scrape_employees: bool = False
    ) -> CompanyInsightResponse:
        """Get company analysis by URL"""
        try:
            response = await self.api_client.get_company_insight_by_url(
                company_url=company_url,
                language=language,
                scrape_employees=scrape_employees
            )
            return CompanyInsightResponse(**response)
        except ApiError as e:
            raise

    async def get_profile_analysis(
        self,
        full_name: str,
        company_name: str,
        language: str = "en"
    ) -> ProfileInsightResponse:
        """Get profile analysis"""
        try:
            response = await self.api_client.get_profile_insight(
                full_name=full_name,
                company_name=company_name,
                language=language
            )
            
            # Convert the profile dict to ProfessionalProfile object
            profile_data = response.get('profile', {})
            profile = ProfessionalProfile(**profile_data)
            
            # Create ProfileInsightResponse with ProfessionalProfile object
            return ProfileInsightResponse(
                profile=profile,  # Now passing a ProfessionalProfile object
                total_tokens=response.get('total_tokens', 0),
                status_code=response.get('status_code', 200)
            )
        except ApiError as e:
            print(f"Debug - API Error in get_profile_analysis: {str(e)}")
            raise
        except Exception as e:
            print(f"Debug - Unexpected error in get_profile_analysis: {str(e)}")
            raise

    async def generate_outreach_email(
        self,
        profile_data: Dict[str, Any],
        sender_info: Optional[Dict[str, Any]] = None,
        language: str = "en",
        proposal_url: Optional[str] = None
    ) -> EmailResponse:
        """Generate outreach email"""
        try:
            print("Debug - Profile Data:", profile_data)
            print("Debug - Sender Info:", sender_info)
            
            response = await self.api_client.get_outreach_email(
                profile=profile_data,
                sender_info=sender_info,
                language=language,
                proposal_url=proposal_url
            )
            print("Debug - Email Response:", response)
            return EmailResponse(**response)
        except ApiError as e:
            print("Debug - API Error:", str(e))
            raise
        except Exception as e:
            print("Debug - Unexpected Error:", str(e))
            raise