import base64
from telethon import TelegramClient, events
from openai import OpenAI
from keys import Key, System

client = OpenAI(api_key=Key.gpt_token)

telethon_client = TelegramClient('Arc', Key.api_id, Key.api_hash)
telethon_client.start()

@telethon_client.on(events.NewMessage)
async def handle_new_message(event):
    bot_user_id = Key.ai_id

    if event.sender_id == bot_user_id:
        return

    if event.photo:
        path = await telethon_client.download_media(event.photo)
        with open(path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        message_content = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }

        if event.message.text:
            message_content["content"].append(event.message.text)

    else:
        message_content = {"role": "user", "content": event.message.text}



    recent_history = await telethon_client.get_messages(event.chat_id, limit=None)


    history = [
        {"role": "system", "content": System.sys1},
        {"role": "system", "content": System.sys2},
        {"role": "system", "content": System.sys3}
    ]

    for msg in reversed(recent_history):
        if msg.id != event.message.id:

            if msg.photo:
                path = await telethon_client.download_media(msg.photo)
                with open(path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                image_message_content = [{
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }]
                history.append({
                    "role": "user" if msg.sender_id == event.sender_id else "assistant",
                    "content": image_message_content  
                })
            else:

                history.append({
                    "role": "user" if msg.sender_id == event.sender_id else "assistant",
                    "content": msg.text or ""  
                })


    history.append(message_content)



    print("Message history for GPT:")
    for msg in history:
        print(f"Role: {msg['role']}, Content: {msg['content']}")

        

    completion = client.chat.completions.create(
        #model="gpt-4-vision-preview",
        model="gpt-4-1106-preview",
        messages=history,
        max_tokens=4096
    )


    response_content = completion.choices[0].message.content
    # Since we're only dealing with text responses at the moment, just send back the content
    await event.respond(response_content)

print("Server Started")
telethon_client.run_until_disconnected()
