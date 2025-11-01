from module.source import ETToday
from langchain.prompts import PromptTemplate
from LLM.prompt import prompt_news
from langchain.chains import LLMChain

prompt_template = PromptTemplate.from_template(prompt_news)

if __name__ == "__main__":
    news = ETToday()
    news.output(scroll_count=3)
    print("執行完成!")
