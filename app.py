import time
import logging
import os
from uuid import uuid4
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# 设置日志记录
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Azure 密钥和终结点
key = 'key'
endpoint = 'endpoint'
# 你的Bot Token
token = 'token'

# 创建Computer Vision客户端
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

async def start(update: Update, context: CallbackContext) -> None:
  await update.message.reply_text('欢迎使用OCR Bot，请上传一张图片。')

async def handle_image(update: Update, context: CallbackContext) -> None:
  message = await update.message.reply_text('正在识别图片，请稍等...')

  # 生成唯一的文件名
  file_id = str(uuid4())
  file_path = f"{file_id}.jpg"

  # 获取图片
  photo_file = await update.message.photo[-1].get_file()
  await photo_file.download_to_drive(file_path)

  # 调用Azure OCR
  with open(file_path, 'rb') as image_stream:
    read_response = computervision_client.read_in_stream(image_stream, raw=True)

  read_operation_location = read_response.headers["Operation-Location"]
  operation_id = read_operation_location.split("/")[-1]

  while True:
    read_result = computervision_client.get_read_result(operation_id)
    if read_result.status not in ['notStarted', 'running']:
      break
    time.sleep(1)

  if read_result.status == OperationStatusCodes.succeeded:
    text_results = []
    for text_result in read_result.analyze_result.read_results:
      for line in text_result.lines:
        text_results.append(line.text)
    await update.message.reply_text('识别结果:\n' + '\n'.join(text_results))
  else:
    await update.message.reply_text('识别失败，请重试。')

  # 删除临时图片文件
  os.remove(file_path)

  # 删除 "正在识别图片，请稍等..." 信息
  await message.delete()

def main() -> None:

  application = Application.builder().token(token).build()

  application.add_handler(CommandHandler('start', start))
  application.add_handler(MessageHandler(filters.PHOTO, handle_image))

  application.run_polling()

if __name__ == '__main__':
  main()
