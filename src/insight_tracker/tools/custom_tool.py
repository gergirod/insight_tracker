from typing import Any
from crewai_tools import BaseTool
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()



class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, you agent will need this information to use it."
    )

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
    
class CrawlingCustomTool(BaseTool) :
    name: str = "crawling tool"
    description : str = (
        "this tool is mean to be used to crawl and return a max of 7 subpages and a minimun of 3."
    )

    def _run(self, argument : str) -> Any:
        app = FirecrawlApp()
        crawl_result = app.crawl_url(argument,
                                    {'crawlerOptions':
                                      {'includes': ['/personas/*'], 'max_depth': 1}
                                      })

        return crawl_result
    
class ScrapingCustomTool(BaseTool) :
    name : str = "scraping tool"
    description : str = ('this tool is mean to be use to scrate a url')

    def _run(self, argument : str) -> Any:
        app = FirecrawlApp()
        content = app.scrape_url(argument)

        return content
