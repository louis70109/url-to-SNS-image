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
    print('Get og:title content')
    og_title = soup.find("meta", property="og:title").get('content') or 'Just Sharing'
    print(og_title)
    print('!!!!!!!!!!!!!!!!!!!')
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
    title_font = ImageFont.truetype('zh-black.ttf', 50)
    title_text = og_title
    
    

    print('Check and crop image size.')
    original_w = my_image.size[0]
    original_h = my_image.size[1]
    print('file size:')
    print(original_h)
    print(original_w)
    if original_w <= 1080 and original_h <= 1920:
        # if little than IG size
        if original_w <= original_h:
            x = 540-(original_w/2)
            y = 960-(original_h/2)
            resize_flag = 1
        else:
            x = 960-(original_w/2)
            y = 540-(original_h/2)
            resize_flag = 11
        # (540-x/2, 960-y/2)
        
        print('111111')
    elif original_w <= 1080 and original_h > 1920:
        # if only heigh more than IG heigh
        if original_w <= original_h:
            x = 540-(original_w/2)
            y = (original_h/2)-960
            resize_flag = 2
        else:
            x = 960-(original_w/2)
            y = (original_h/2)-540
            resize_flag = 22
        # (540-(x/2), (y/2)-960)
        print('2222222')
    elif original_w > 1080 and original_h > 1920:
        # if only width more tha IG width
        if original_w <= original_h:
            x = (original_w/2)-540
            y = 960-(original_h/2)
            resize_flag = 3
        else:
            x = (original_w/2)-960
            y = 540-(original_h/2)
            resize_flag = 33
        # ((x/2)-540, 960-(y/2))
        print('3333333')
    else:
        # if width and height more than IG size.
        if original_w <= original_h:
            x = (original_w/2)-540
            y = (original_h/2)-960
            resize_flag = 4
        else:
            x = (original_w/2)-960
            y = (original_h/2)-540
            resize_flag = 44
        # 可能需要遞迴處理過大問題的判斷式
        # ((x/2)-540, (y/2)-960)
        print('4444444')
    

    print('Resize done.')
    resize_image = my_image.resize((int(float(x)), int(float(y))), Image.ANTIALIAS)
    
    # Put size into this line
    new_image = Image.new('RGB',(1080, 1920), (250,250,250))
    image1 = Image.open('white_ig.png') # Change to no background PNG

    new_image.paste(image1,(0,0))
    new_image.paste(resize_image,(200,720))
    new_image.save("merged_image.jpg","JPEG")
    print("Get url image and change to IG size.")

    print('start drawing.')
    # 做完之後需要畫上 OG title
    # final_image = Image.open("merged_image.jpg")
    # image_editable = ImageDraw.Draw(final_image)
    # if resize_flag == 1:
    #     image_editable.text((540+20,960+20), title_text, (237, 230, 211), font=title_font)
    # elif resize_flag == 11:
    #     image_editable.text((960+20,540+20), title_text, (237, 230, 211), font=title_font)
    print('Draw image success.')

    # my_image.save("result.jpg")
    # Save as a binary file to LINE Bot
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
