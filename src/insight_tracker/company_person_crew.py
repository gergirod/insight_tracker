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
from crewai_tools import ScrapeWebsiteTool

from dotenv import load_dotenv

load_dotenv()

# Uncomment the following line to use an example of a custom tool
# from insight_tracker.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool


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
	def company_person_detail_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['company_person_detail_scraper'],
			tools = [ScrapeWebsiteTool()],
			#llm = self.llm(),
			verbose=True
		)
	
	@agent
	def email_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['email_writer'],
			allow_delegation=False,
			verbose=True,
		)


	@task
	def company_person_detail_scraping_task(self) -> Task:
		return Task(
			config=self.tasks_config['company_person_detail_scraping_task'],
			agent=self.company_person_detail_scraper()
		)
	
	@task
	def write_invitation_email_task_three(self) -> Task:
		return Task(
			config=self.tasks_config['write_invitation_email_task_three'],
			agent = self.email_writer(),
			context = [self.company_person_detail_scraping_task()]
		)
	
	
	@crew
	def company_person_crew(self) -> Crew:
		"""Creates the CompanyInsightTracker crew"""
		return Crew(
			agents=[self.company_person_detail_scraper()], # Automatically created by the @agent decorator
			tasks=[self.company_person_detail_scraping_task()], # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)