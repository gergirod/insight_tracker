from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_anthropic import ChatAnthropic
from langchain.tools.tavily_search import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from crewai_tools import FirecrawlScrapeWebsiteTool
from crewai_tools import ScrapeWebsiteTool
from crewai_tools import FileReadTool
from typing import Union, List, Tuple, Dict
from langchain_core.agents import AgentFinish
import json
import streamlit as st
from pydantic import BaseModel, Field
from insight_tracker.tools.custom_tool import CrawlingCustomTool, ScrapingCustomTool
from typing import List, Optional
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

# Uncomment the following line to use an example of a custom tool
# from insight_tracker.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)

class ProfessionalProfile(BaseModel):
	first_name: Optional[str] = Field(
		..., description="The first name of the profile"
	)
	last_name: Optional[str] = Field(
		None, description="The last name of the profile"
	)
	company: Optional[str] =  Field(
		None, description="the current company of the profile"
	)
	profesional_background: Optional[str] = Field(
		None, description="the professional background of the profile"
	)
	key_achievements: Optional[str] = Field(
		None, description="key achievements of the profile"
	)
	email_address: Optional[str] = Field(
		None, description="The email address of the profile"
	)
	linkedin_url: Optional[str] = Field(
		None, description="The LinkedIn profile URL of the profile"
	)
	   

@CrewBase
class CompanyPersonInsightTrackerCrew():
	"""InsightTracker crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# def llm(self):
	# 	llm = ChatAnthropic(model_name="claude-3-sonnet-20240229", max_tokens=4096, temperature=0.0)
	# 	# llm = ChatGroq(model="llama3-70b-8192")
	# 	# llm = ChatGroq(model="mixtral-8x7b-32768")
	# 	# llm = ChatGoogleGenerativeAI(google_api_key=os.getenv("GOOGLE_API_KEY"))
	# 	return llm

	@agent
	def company_person_employee_insight_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_person_employee_insight_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True
		)
	
	@agent
	def company_person_employee_detail_insight_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_person_employee_detail_insight_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True
		)
	

	@task
	def company_persons_scraping_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_persons_scraping_task'],
			agent=self.company_person_employee_insight_scraper()
		)
	
	@task
	def company_persons_detail_scraping_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_persons_detail_scraping_task'],
			agent=self.company_person_employee_insight_scraper()
		)
	
	@task
	def write_invitation_email_task(self) -> Task:
		return Task(
			config=self.tasks_config['write_invitation_email_task'],
			agent = self.email_writer()
		)
	
	
	@crew
	def company_person_crew(self) -> Crew:
		"""Creates the CompanyInsightTracker crew"""
		return Crew(
			agents=[self.company_person_employee_insight_scraper(), self.company_person_employee_detail_insight_scraper()], # Automatically created by the @agent decorator
			tasks=[self.company_persons_scraping_task(), self.company_persons_detail_scraping_task()], # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			planning=True,
			planning_llm=ChatOpenAI(model="gpt-4o")
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)