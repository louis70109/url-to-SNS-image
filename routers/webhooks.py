import os
from typing import List, Optional
import requests
import tempfile

from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw 
from fastapi import APIRouter, HTTPException, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent, TextSendMessage
from pydantic import BaseModel

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

router = APIRouter(
    prefix="/webhooks",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)


class Line(BaseModel):
    destination: str
    events: List[Optional[None]]


@router.post("/line")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print(event.message.text)
    # if match URL
    url = event.message.text
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.select("img")    
    first_img = results[0]['src']
    print("!!!!!!!!!!!!!!!!!!!!!!")
    i = requests.get(url=results[0]['src'])
    image_content = b''
    for chunk in i.iter_content():
      image_content += chunk
    print('Image into binary')
    temp = tempfile.NamedTemporaryFile(suffix='.jpg')
    img_file_tmp_name = ''
    try:
        
        temp.write(image_content)
        img_file_tmp_name = temp.name
        temp.seek(0)
        print('Temp file path create success.')
    except:
        temp.close()
        print('Temp path create fail.')
    
    my_image = Image.open(img_file_tmp_name)
    title_font = ImageFont.truetype('zh-black.ttf', 200)
    title_text = '123'
    image_editable = ImageDraw.Draw(my_image)
    image_editable.text((15,15), title_text, (237, 230, 211), font=title_font)
    print('Draw image success.')
    # my_image.save("result.jpg")
    # Save as a binary file to LINE Bot
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
