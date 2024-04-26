import http.client
import json
import configparser
import os
# 取得當前檔案的目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

# 連接 config.ini 檔案的完整路徑
config_file_path = os.path.join(current_dir, 'config.ini')

# Config Parser
config = configparser.ConfigParser()
config.read(config_file_path)


def azure_computer_vision(image_path):
    # 設定你的訂閱金鑰
    subscription_key = config["AzureCustomVision"]["SUBSCRIPTION_KEY"]
    region = config["AzureCustomVision"]["REGION"]
    headers = {
        # 設定請求標頭
        'Prediction-key': subscription_key,
        'Content-Type': 'application/octet-stream',  # 設定內容類型為二進位流
    }

    # 設定圖片的URL
    image_url = config["AzureCustomVision"]["IMAGE_URL"]

    # 讀取圖片並設定為請求的主體
    with open(image_path, 'rb') as image_file:
        body = image_file.read()

    try:
        # 連接到Custom Vision服務
        conn = http.client.HTTPSConnection(
            # 換成您的regin
            f"{region}.api.cognitive.microsoft.com")
        # 發送POST請求
        conn.request("POST", image_url, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        # 解析JSON
        par_data = json.loads(data.decode('utf-8'))

        # 取出第二個tagName
        second_tag_name = par_data['predictions'][1]['tagName']

        return second_tag_name
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
