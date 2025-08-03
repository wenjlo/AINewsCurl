from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp
from google import genai
from google.genai import types
from config import TOKEN
import os
os.environ['GEMINI_API_KEY'] = TOKEN

def LargeLanguageModel(path):

    model = LlamaCpp(
        model_path=path,
        n_gpu_layers=0,
        n_batch=256,
        n_ctx=2048,
        f16_kv=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        verbose=True
    )
    return model

def gemini(context):
    prompt_config = types.GenerateContentConfig(
        system_instruction=["""你是一位新聞記者
        你的任務是將接受到的文字以簡短5句中文描述
        你將會接收到一段文字, 該段文字會被涵蓋在html的tag之中, 
        看到<text>代表句子的開始,看到</text>代表句子的結束
        請勿回答5句中文描述以外的資訊
        不要有1.2.3.4 之類的條列式回答
        """]
    )

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"<text>{context}</text>",
        config=prompt_config
    )
    return  response