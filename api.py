from flask import Flask
from flask_cors import CORS
from module.source import ETToday
from LLM.llm import gemini

from langchain.chains import LLMChain
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['GET'])
def curl():
    news = ETToday()
    news.output(scroll_count=3,chain=gemini)
    return 'curl finished...'

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")