from azure_computer_vision import azure_computer_vision
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import datetime

# 將本地檔案辨識
image_path = '/Users/ahern/Documents/Python/openAI/Ecommerce_marketing_assistant/ecommerce_marketing_assistant/static/output.jpg'
result = azure_computer_vision(image_path)

# 獲取當前日期時間
current_datetime = datetime.datetime.now()

# 從當前日期時間中獲取年份
current_year = current_datetime.year


llm = ChatOllama(model='yabi/breeze-7b-instruct-v1_0_q6_k')
prompt = ChatPromptTemplate.from_template(
    "你是一位行銷經理，請給我一份完整詳細的 {year} {topic} 企劃案")
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"topic": result, "year": current_year}))
