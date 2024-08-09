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
from langchain_groq import ChatGroq


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
class CompanyInsightTrackerCrew():
	"""InsightTracker crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def company_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['company_linkedin_researcher'],
			tools = [tavily_tool],
			verbose=True
		)
	
	@agent
	def company_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_website_researcher'],
			tools = [ScrapeWebsiteTool()],
			verbose=True,
		)
	
	@agent
	def company_employee_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_employee_scraper'],
			tools = [ScrapingCustomTool()],
			verbose=True,
		)
	
	@agent
	def company_employee_insight_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_employee_insight_scraper'],
			tools = [ScrapingCustomTool()],
			verbose=True,
		)
	

	@task
	def company_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_linkedin_research_task'],
			agent=self.company_researcher()
		)
	
	@task
	def company_website_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_website_research_task'],
			agent=self.company_scraper()
		)
	
	@task
	def company_people_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_people_research_task'],
			agent=self.company_employee_scraper()
		)

	
	
	@crew
	def company_crew(self) -> Crew:
		"""Creates the CompanyInsightTracker crew"""
		return Crew(
			agents=[self.company_researcher(), self.company_scraper(), self.company_employee_scraper()], # Automatically created by the @agent decorator
			tasks=[self.company_research_task(), self.company_website_research_task(), self.company_people_research_task()], # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)