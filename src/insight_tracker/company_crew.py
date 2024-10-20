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
from crewai_tools import SeleniumScrapingTool
from langchain_openai import ChatOpenAI


from dotenv import load_dotenv

load_dotenv()

# Uncomment the following line to use an example of a custom tool
# from insight_tracker.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search)

class Company(BaseModel):
    company_name: Optional[str] = Field(
        ..., description="the name of the company"
    )
    company_website: Optional[str] =  Field(
        None, description="the website of the company"
    )
    company_summary: Optional[str] = Field(
        None, description="the summary of the company"
    )
    company_industry: Optional[str] = Field(
        None, description="the industry of the company"
    )
    company_services: Optional[str] = Field(
        None, description="the services of the company"
    )
    company_industries: Optional[str] = Field(
        None, description="the industries of the company"
    )
    company_awards_recognitions: Optional[str] = Field(
        None, description="the awards and recognitions of the company"
    )
    company_clients_partners: Optional[str] = Field(
        None, description="the clients and partners of the company"
    )
    search_date: Optional[str] = Field(
        None, description="The date of the search"
    )

class Employess(BaseModel):
	employee_list : Optional[List[str]]
	   

@CrewBase
class CompanyInsightTrackerCrew():
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
	def company_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['company_linkedin_researcher'],
			tools = [tavily_tool],
			#llm = self.llm(),
			verbose=True
		)
	
	@agent
	def company_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_website_researcher'],
			tools = [ScrapeWebsiteTool()],
			#llm = self.llm(),
			verbose=True,
		)
	
	@agent
	def company_data_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_data_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True,
		)
	
	@agent
	def company_employee_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_employee_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True,
		)
	
	@agent
	def company_employee_insight_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_employee_insight_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True,
		)
	
	@agent
	def email_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['email_writer'],
			allow_delegation=False,
			verbose=True,
		)
	
	@agent
	def company_person_employee_detail_insight_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_person_employee_detail_insight_scraper'],
			tools = [ScrapingCustomTool()],
			#llm = self.llm(),
			verbose=True
		)
	

	@agent
	def data_formater(self) -> Agent:
		return Agent(
			config=self.agents_config['data_formater'],
			#llm = self.llm(),
			verbose=True
		)
	

	@task
	def company_linkedin_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_linkedin_research_task'],
			agent=self.company_researcher()
		)
	
	@task
	def company_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_research_task'],
			agent=self.company_data_scraper(),
			output_pydantic=Company	
		)
	
	@task
	def company_website_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_website_research_task'],
			agent=self.company_scraper(),
		)
	
	@task
	def company_people_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_people_research_task'],
			agent=self.company_employee_scraper(),
			context=[self.company_website_research_task()]
			)
	
	def company_persons_detail_scraping_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_persons_detail_scraping_task'],
			agent=self.company_person_employee_detail_insight_scraper(),
			context= [self.company_people_research_task()]
		)
	
	
	@task
	def data_format_task(self) -> Task:
		return Task(
			config=self.tasks_config['data_format_task'],
			agent=self.data_formater(),
			context = [self.company_people_research_task()],
			output_pydantic=Employess

		)

	
	
	@crew
	def company_crew(self) -> Crew:
		"""Creates the CompanyInsightTracker crew"""
		return Crew(
			agents=[self.company_researcher(), self.company_scraper(),self.company_data_scraper(), self.company_employee_scraper(), self.data_formater()], # Automatically created by the @agent decorator
			tasks=[self.company_linkedin_research_task(), self.company_website_research_task(), self.company_research_task(), self.company_people_research_task(), self.data_format_task()], # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)