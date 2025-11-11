from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY
import requests
from bs4 import BeautifulSoup
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import ResumeanalyserException
log = CustomLogger().get_logger(__name__)
import sys
import re
import json

class JobLoader:
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm()
        log.info("JobLoader initialized with LLM")
        self.parser=JsonOutputParser(pydantic_object=JobDescription)########
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)######
        self.prompt = PROMPT_REGISTRY["job_description"]#####

    def url_extractor(self, text: str) -> str:
        pattern = r'(https?://\S+)'
        match = re.search(pattern, text)
        if match:
            url = match.group(1)
            log.info("URL extracted successfully", url=url)
            return url
        else:
            log.error("No URL found in the provided text")
            return None

    def load_job_url(self, url: str) -> str:
        try:
            html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            log.info("Job url loaded successfully", url=url)
            return text
        except Exception as e:
            log.error("Failed to load job description", url=url, error=str(e))
            raise ResumeanalyserException("Failed to load job description", sys) from e

    def extract_job_details(self, job_text: str) -> str:
        chain = self.prompt | self.llm | self.fixing_parser

        try:
            response = chain.invoke({
                "job_text":job_text,
                "format_instructions": self.parser.get_format_instructions(),
            })
            log.info("Job details extracted successfully")

            if hasattr(response, 'dict'):
                response_dict = response.dict()
            elif hasattr(response, '__dict__'):
                response_dict = response.__dict__
            else:
                response_dict = response

            log.info("Job extraction successful", keys=list(response_dict.keys()) if isinstance(response_dict, dict) else 'Not a dict')
            
            return json.dumps(response_dict)
        except Exception as e:
            log.error("Failed to extract job details", error=str(e))
            raise ResumeanalyserException("Failed to extract job details", sys) from e


if __name__ == "__main__":
    job_loader = JobLoader()
    url = input("Paste job link: ")
    url=job_loader.url_extractor(url)
    if url is None:
        print("No valid URL found.")
        sys.exit(1)
    else:
        job_text = job_loader.load_job_url(url)
        job_details = job_loader.extract_job_details(job_text)
        print(job_details)
        print(type(job_details))