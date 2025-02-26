import requests
import json
from typing import Optional, Dict, Any, List, Union, AsyncGenerator, Tuple
from ..exceptions.api_exceptions import ApiError
from ..models.responses import (
    OutreachResponse,
    ProfileCompanyFitResponse,
    MeetingResponse
)
import streamlit as st
from sseclient import SSEClient  # Add this import at the top
import aiohttp  # Add this import

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

    async def _make_strategy_request(
        self,
        action: str,
        profile: Optional[Dict[str, Any]] = None,
        company: Optional[Dict[str, Any]] = None,
        targetCompany: Optional[Dict[str, Any]] = None,
        language: str = "en",
        sender_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a strategy request to the API"""
        endpoint = "/api/generateProfileCompanyInteractionStrategy"
        
        data = {
            "action": action,
            "profile": profile,
            "myCompany": company,
            "target_company": targetCompany,
            "language": language
        }
        
        if sender_info:
            data["sender_info"] = sender_info
            
        # Add debug logging
        print(f"Debug - Making request to {endpoint}")
        print(f"Debug - Request data: {json.dumps(data, indent=2)}")
        
        try:
            response = await self.post(endpoint, data)
            return response
        except Exception as e:
            print(f"Debug - Error in _make_strategy_request: {str(e)}")
            raise

    async def generate_outreach_email(
        self,
        profile: Dict[str, Any],
        company: Dict[str, Any],
        sender_info: Dict[str, Any],
        language: str = "en"
    ) -> OutreachResponse:
        """Generate an outreach email"""
        response = await self._make_strategy_request(
            action="outreach",
            profile=profile,
            company=company,
            language=language,
            sender_info=sender_info
        )
        
        if response.get('action') == 'outreach' and 'outreach_data' in response:
            # Create a dictionary with the expected structure
            email_data = {
                'email': response['outreach_data']['email'],
                'total_tokens': response['total_tokens'],
                'status_code': response.get('status_code', 200)
            }
            return OutreachResponse.from_dict(email_data)
        raise ApiError("Invalid response format or missing outreach data", status_code=500)

    async def evaluate_profile_fit(
        self,
        profile: Optional[Dict[str, Any]] = None,
        company: Optional[Dict[str, Any]] = None,
        targetCompany: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> ProfileCompanyFitResponse:
        print(f"Debug - Sending target company data: {targetCompany}")
        try:
            response = await self._make_strategy_request(
                action="evaluation",
                profile=profile,
                company=company,
                targetCompany=targetCompany,
                language=language
            )
            
            # Add debug logging
            print("Debug - Response from server:", response)
            
            if response.get('action') == 'evaluation' and 'evaluation_data' in response:
                return ProfileCompanyFitResponse.from_dict({
                    'evaluation': response['evaluation_data']['evaluation'],
                    'total_tokens': response['total_tokens']
                })
            raise ApiError("Invalid response format or missing evaluation data", status_code=500)
        except Exception as e:
            print(f"Debug - Error in evaluate_profile_fit: {str(e)}")
            print(f"Debug - Request data: action=evaluation, profile={profile}, company={company}")
            raise

    async def prepare_meeting(
        self,
        profile: Dict[str, Any],
        company: Dict[str, Any],
        language: str = "en"
    ) -> MeetingResponse:
        """Prepare meeting strategy"""
        response = await self._make_strategy_request(
            action="meeting",
            profile=profile,
            company=company,
            language=language
        )
        
        if response.get('action') == 'meeting' and 'meeting_data' in response:
            print(response)
            print(type(response))
            # Create the response data structure
            meeting_data = {
                'meeting_preparation': response['meeting_data']['meeting_preparation'],
                'total_tokens': response['total_tokens'],
                'status_code': response.get('status_code', 200)
            }

            return MeetingResponse.from_dict(meeting_data)
        raise ApiError("Invalid response format or missing meeting data", status_code=500)

    def stream_with_ui_updates(
        self,
        response: requests.Response,
    ):
        """Handle streaming responses"""
        try:
            print("DEBUG: Starting stream processing")
            for line in response.iter_lines():
                print(f"DEBUG: Raw line received: {line}")
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        print(f"DEBUG: Parsed data: {data}")
                        
                        # Update UI based on data type
                        if "status" in data:
                            print(f"DEBUG: Status update: {data['status']}")
                        if "intermediate_result" in data:
                            print(f"DEBUG: Intermediate result: {data['intermediate_result']}")
                        
                        yield data
                    except json.JSONDecodeError as e:
                        print(f"DEBUG: JSON decode error: {e} for line: {line}")
                    
        except Exception as e:
            print(f"Debug - Streaming Error: {str(e)}")
            # Print the full response content to see what we got
            print(f"DEBUG: Full response content: {response.content}")
            raise ApiError(str(e))

    def get_profile_insight_stream(
        self,
        full_name: str,
        company_name: str,
        language: str = "en"
    ):
        """Get streaming profile insights"""
        print("\n=== Starting Profile Stream ===")
        endpoint = "/api/v2/profile_insight/stream"
        data = {
            "profile": full_name,
            "company": company_name,
            "language": language
        }
        
        url = f"{self.base_url}{endpoint}"
        try:
            print("Debug - Getting profile insight stream 1")
            
            response = requests.post(
                url, 
                json=data,
                stream=True,
                verify=False,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.api_key,
                    'X-OpenAI-API-Key': self.openai_api_key
                }
            )
            
            print(f"Debug - Response status: {response.status_code}")
            
            # Process the response line by line
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    print(f"Debug - Raw line: {line_text}")
                    
                    if line_text.startswith('data: '):
                        event_data = json.loads(line_text[6:])
                        print(f"Debug - Event: {event_data}")
                        yield event_data
                        
        except Exception as e:
            print(f"Debug - Error in stream: {str(e)}")
            raise ApiError(str(e))

    def get_company_insight_stream(
        self,
        company_name: str,
        industry: str,
        language: str = "en"
    ):
        """Get streaming company insights"""
        print("\n=== Starting Company Stream ===")
        endpoint = "/api/v2/company_insight/stream"
        data = {
            "company": company_name,
            "industry": industry,
            "language": language
        }
        
        url = f"{self.base_url}{endpoint}"
        try:
            print("Debug - Getting company insight stream")
            
            response = requests.post(
                url, 
                json=data,
                stream=True,
                verify=False,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.api_key,
                    'X-OpenAI-API-Key': self.openai_api_key
                }
            )
            
            print(f"Debug - Response status: {response.status_code}")
            
            # Process the response line by line
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    print(f"Debug - Raw line: {line_text}")
                    
                    if line_text.startswith('data: '):
                        event_data = json.loads(line_text[6:])
                        print(f"Debug - Event: {event_data}")
                        yield event_data
                        
        except Exception as e:
            print(f"Debug - Error in stream: {str(e)}")
            raise ApiError(str(e))