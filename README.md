# 行銷企劃助手

##### 使用技術

1. Line Bot
2. Flask
3. Azure computer vision
4. LLM

##### 專案說明

使用者透過 Line 上傳圖片，即可得到該商品的企劃案。

##### 業務流程

1. 用戶使用 Line 上傳圖片
2. 後端收到圖片儲存在本地，`main.py`會呼叫`azure_computer_vision.py`並將圖片位置做為參數帶入
3. `azure_computer_vision.py` 呼叫 Azure Custom Vision 的 model 分析圖片
4. 分析結果傳入 LLM
5. 最後生成文案
