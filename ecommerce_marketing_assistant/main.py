import sys
import configparser


from azure_computer_vision import azure_computer_vision
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import datetime

import os
import tempfile
from flask import Flask, request, abort
import linebot.v3.messaging
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.messaging.models.show_loading_animation_request import ShowLoadingAnimationRequest
from linebot.v3.messaging.rest import ApiException


# 取得當前檔案的目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

# 連接 config.ini 檔案的完整路徑
config_file_path = os.path.join(current_dir, 'config.ini')

# Config Parser
config = configparser.ConfigParser()
config.read(config_file_path)


# 將本地檔案辨識
UPLOAD_FOLDER = config['Local']['dir_file']


app = Flask(__name__)

# 設定 Line channel access token和 secret
channel_access_token = config['Line']['CHANNEL_ACCESS_TOKEN']
channel_secret = config['Line']['CHANNEL_SECRET']
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=ImageMessageContent)
def message_image(event):
    with ApiClient(configuration) as api_client:
        # ---Line 前端加載動畫 start---
        api_instance = linebot.v3.messaging.MessagingApi(api_client)
        show_loading_animation_request = linebot.v3.messaging.ShowLoadingAnimationRequest(
            chatId=event.source.user_id, loadingSeconds=5)
        api_response = api_instance.show_loading_animation(
            show_loading_animation_request)
        print("The response of MessagingApi->show_loading_animation:\n")
        print(api_response)
        # ---Line 前端加載動畫 end---
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(
            message_id=event.message.id
        )
        with tempfile.NamedTemporaryFile(
            dir=UPLOAD_FOLDER, prefix="", delete=False
        ) as tf:
            tf.write(message_content)
            tempfile_path = tf.name

    original_file_name = os.path.basename(tempfile_path)
    os.rename(
        UPLOAD_FOLDER + "/" + original_file_name,
        UPLOAD_FOLDER + "/" + "output.jpg",
    )
    result = azure_computer_vision(UPLOAD_FOLDER+'output.jpg')

    # 獲取當前日期時間
    current_datetime = datetime.datetime.now()

    # 從當前日期時間中獲取年份
    current_year = current_datetime.year

    # Chat LLM
    llm = ChatOllama(model='yabi/breeze-7b-instruct-v1_0_q6_k')
    prompt = ChatPromptTemplate.from_template(
        "你是一位行銷經理，請給我一份完整詳細的 {year} {topic} 企劃案")
    chain = prompt | llm | StrOutputParser()
    print(chain.invoke({"topic": result, "year": current_year}))

    with ApiClient(configuration) as api_client:
        # ---Line 前端加載動畫 start---
        api_instance = linebot.v3.messaging.MessagingApi(api_client)
        show_loading_animation_request = linebot.v3.messaging.ShowLoadingAnimationRequest(
            chatId=event.source.user_id, loadingSeconds=5)
        api_response = api_instance.show_loading_animation(
            show_loading_animation_request)
        print("The response of MessagingApi->show_loading_animation:\n")
        print(api_response)
        # ---Line 前端加載動畫 end---
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=chain.invoke(
                    {"topic": result, "year": current_year}))],
            )
        )


# file path
url = config["Deploy"]["WEBSITE"] + "/static/" + "output.jpg"


if __name__ == "__main__":
    app.run()
