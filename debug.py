from google import genai
from google.genai import types
import os
from config import TOKEN
os.environ['GEMINI_API_KEY'] = TOKEN

prompt_config = types.GenerateContentConfig(
    system_instruction=["""你是一位新聞記者
    你的任務是將接受到的文字以簡短5句中文描述
    你將會接收到一段文字, 該段文字會被涵蓋在html的tag之中, 
    看到<text>代表句子的開始,看到</text>代表句子的結束
    請勿回答5句中文描述以外的資訊
    不要有1.2.3.4 之類的條列式回答
    """]
)



# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="<text>罕見西南氣流造成高雄茂林及桃源地區顯著降雨，總計近2500毫米，創近年非颱風劇烈降雨紀錄，可能持續到周一白天。</text>",config=prompt_config
)
print(response.text)