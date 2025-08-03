from langchain.chains.question_answering.map_reduce_prompt import messages
from module.source import ETToday
from LLM.llm import LargeLanguageModel,gemini
from langchain.prompts import PromptTemplate
from LLM.prompt import prompt_news
from langchain.chains import LLMChain

prompt_template = PromptTemplate.from_template(prompt_news)
# llm_model = LargeLanguageModel("./LLM/models/Breeze-7B-Instruct-64k-v0.1-Q5_K_M.gguf")
# chain = LLMChain(llm=llm_model,prompt=prompt_template,verbose=False)

if __name__=="__main__":
    news = ETToday()
    news.output(gemini)
