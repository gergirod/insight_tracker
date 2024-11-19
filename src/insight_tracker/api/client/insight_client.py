import requests
import json
from typing import Optional, Dict, Any, List
from ..exceptions.api_exceptions import ApiError

# Optional: Add logging for better debugging
import logging
logger = logging.getLogger(__name__)

class InsightApiClient:
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        openai_api_key: str,
        verify_ssl: bool = True
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.openai_api_key = openai_api_key
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        logger.debug(f"Initializing InsightApiClient with base_url: {base_url}")
        
        # Set up headers according to API spec
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'X-OpenAI-API-Key': self.openai_api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    async def generate_api_key(self, email: str) -> str:
        """Generate new API key"""
        endpoint = "/api/generateApiKey"
        data = {"email": email}
        return await self.post(endpoint, data)

    async def get_company_insight(
        self,
        company_name: str,
        industry: str,
        language: str = "en",
        scrape_employees: bool = False
    ) -> Dict[str, Any]:
        """Get company insights"""
        endpoint = "/api/getCompanyInsight"
        params = {
            "companyName": company_name,
            "industry": industry,
            "language": language,
            "scrapeEmployees": scrape_employees
        }
        return await self.get(endpoint, params)

    async def get_company_insight_by_url(
        self,
        company_url: str,
        language: str = "en",
        scrape_employees: bool = False
    ) -> Dict[str, Any]:
        """Get company insights by URL"""
        endpoint = "/api/getCompanyInsightByUrl"
        params = {
            "companyUrl": company_url,
            "language": language,
            "scrapeEmployees": scrape_employees
        }
        return await self.get(endpoint, params)

    async def get_profile_insight(
        self,
        full_name: str,
        company_name: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get profile insights"""
        endpoint = "/api/getProfileInsight"
        print(f"Debug - Full Name: {full_name}, Company Name: {company_name}")
        params = {
            "fullName": full_name,
            "companyName": company_name,
            "language": language
        }
        return await self.get(endpoint, params)

    async def get_outreach_email(
        self,
        profile: Dict[str, Any],
        sender_info: Optional[Dict[str, Any]] = None,
        language: str = "en",
        proposal_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate outreach email"""
        endpoint = "/api/getOutreachEmail"
        params = {
            "profile": json.dumps(profile),  # Convert dict to JSON string
            "language": language
        }
        
        if sender_info:
            params["senderInfo"] = json.dumps(sender_info)
        if proposal_url:
            params["proposalUrl"] = proposal_url
            
        return await self.get(endpoint, params)

    async def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            print(f"Debug - GET Request URL: {response.url}")
            print(f"Debug - Response Status: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print(f"Debug - Auth Error Response: {response.text}")
                raise ApiError(
                    f"Authentication failed: {response.text}",
                    status_code=response.status_code
                )
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Debug - Request Error: {str(e)}")
            raise ApiError(str(e))

    async def post(self, endpoint: str, data: dict) -> dict:
        """Make POST request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data)
            print(f"Debug - POST Request URL: {response.url}")
            print(f"Debug - Response Status: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print(f"Debug - Auth Error Response: {response.text}")
                raise ApiError(
                    f"Authentication failed: {response.text}",
                    status_code=response.status_code
                )
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Debug - Request Error: {str(e)}")
            raise ApiError(str(e))

    async def evaluate_profile_fit(
        self,
        profile: Dict[str, Any],
        company: Dict[str, Any],
        language: str = "en"
    ) -> Dict[str, Any]:
        """Evaluate profile fit for company"""
        endpoint = "/api/getProfileCompanyFitAnalysis"
        payload = {
            "profile": profile,
            "myCompany": company,
            "language": language
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=payload, headers=headers)
            print(f"Debug - POST Request URL: {response.url}")
            print(f"Debug - Response Status: {response.status_code}")
            
            if response.status_code in [401, 403]:
                print(f"Debug - Auth Error Response: {response.text}")
                raise ApiError(
                    f"Authentication failed: {response.text}",
                    status_code=response.status_code
                )
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Debug - Request Error: {str(e)}")
            raise ApiError(str(e))