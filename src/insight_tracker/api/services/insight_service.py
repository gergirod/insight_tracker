from typing import Optional, Dict, Any, List
from ..client.insight_client import InsightApiClient
from ..exceptions.api_exceptions import ApiError
from ..models.responses import ProfileInsightResponse, CompanyInsightResponse, EmailResponse, ProfessionalProfile, Company, ProfileCompanyFitResponse, OutreachResponse, MeetingResponse, MeetingPreparation

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
            
            # Extract the company data from the response
            company_data = response.get('company', {})
            
            # Create a Company instance from the company data
            company = Company(**company_data)  # Convert dict to Company data class
            
            # Return the CompanyInsightResponse with the Company instance
            return CompanyInsightResponse(
                company=company,
                total_tokens=response.get('total_tokens', 0),
                status_code=response.get('status_code', 200),
                employee_links=response.get('employee_links', [])
            )
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

            # Extract the company data from the response
            company_data = response.get('company', {})
            
            # Create a Company instance from the company data
            company = Company(**company_data)  # Convert
            return CompanyInsightResponse(
                company=company,
                total_tokens=response.get('total_tokens', 0),
                status_code=response.get('status_code', 200),
                employee_links=response.get('employee_links', [])
            )
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
        profile: Dict[str, Any],
        company: Dict[str, Any],
        sender_info: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """Generate personalized outreach email"""
        try:
            response = await self.api_client.generate_outreach_email(
                profile=profile,
                company=company,
                sender_info=sender_info,
                language=language
            )
            # Return just the email string
            return response.email
        except ApiError as e:
            print(f"Debug - API Error in generate_outreach_email: {str(e)}")
            raise
        except Exception as e:
            print(f"Debug - Unexpected error in generate_outreach_email: {str(e)}")
            raise

    async def evaluate_profile_fit(
        self,
        profile: Dict[str, Any],
        company: Dict[str, Any],
        language: str = "en"
    ) -> ProfileCompanyFitResponse:
        """Evaluate profile fit"""
        try:
            # Add debug logging
            print("Debug - Sending profile data:", profile)
            print("Debug - Sending company data:", company)
            
            response = await self.api_client.evaluate_profile_fit(
                profile=profile,
                company=company,
                language=language
            )
            return response
        except ApiError as e:
            print(f"Debug - API Error in evaluate_profile_fit: {str(e)}")
            print(f"Debug - Request details: {e.response.text if hasattr(e, 'response') else 'No response details'}")
            raise
        except Exception as e:
            print(f"Debug - Unexpected error in evaluate_profile_fit: {str(e)}")
            raise

    async def prepare_meeting(
        self,
        profile: Dict[str, Any],
        company: Dict[str, Any],
        language: str = "en"
    ) -> MeetingPreparation:
        """Prepare meeting strategy"""
        try:
            response = await self.api_client.prepare_meeting(
                profile=profile,
                company=company,
                language=language
            )
            # Return just the meeting preparation data
            return response.meeting_preparation
        except ApiError as e:
            print(f"Debug - API Error in prepare_meeting: {str(e)}")
            raise
        except Exception as e:
            print(f"Debug - Unexpected error in prepare_meeting: {str(e)}")
            raise