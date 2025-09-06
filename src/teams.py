#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only

import os, sys, time
import requests, base64
import json

GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/chats"
headers = { "Authorization": "", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)" }

ACCOUNT_SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TWILIO_PHONE = '+1XXXXXXXXXX'
TO_PHONE = '+1XXXXXXXXXX'

def get_teams_chats():
    response = requests.get(GRAPH_API_URL, headers=headers)
    if response.status_code == 200:
        chats = response.json()
        if chats.get("value"):
            return chats["value"]
        else:
            print("No chats found.")
            return []
    else:
        raise Exception(f"Error fetching chats: {response.status_code}\nResponse: {response.text}")
        return []

def get_chat_messages(chat_id, limit=5):
    url = f"https://graph.microsoft.com/v1.0/me/chats/{chat_id}/messages?$top={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        raise Exception(f"Error fetching messages for chat {chat_id}: {response.status_code}\nResponse: {response.text}")
        return []

def send_sms(message):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"
    auth = (ACCOUNT_SID, AUTH_TOKEN)
    data = { "From": TWILIO_PHONE, "To": TO_PHONE, "Body": message }
    response = requests.post(url, data=data, auth=auth)
    if response.status_code == 201:
        print(f"SMS SID: {response.json()['sid']}")
    else:
        print(f"Failed to send SMS: {response.status_code}")
        print(f"Response: {response.text}")
    return

def notify_tmux():
    sys.stdout.write('\a')
    sys.stdout.flush()
    return

def check_for_new_messages():
    notify_tmux()
    chats = get_teams_chats()
    if not chats:
        return
    last_message_ids = {}
    while True:
        for chat in chats:
            chat_id = chat['id']
            messages = get_chat_messages(chat_id)
            if messages:
                latest_message_id = messages[0]['id']
                if chat_id not in last_message_ids:
                    last_message_ids[chat_id] = latest_message_id
                    continue
                if latest_message_id != last_message_ids[chat_id]:
                    notify_tmux()
                    #print(f"Message: {messages[0]}")
                    #print(f"Chat: {chat['id']}")
                    print(f"{messages[0]['from']['user']['displayName']}:{messages[0]['body']['content']}")
                    last_message_ids[chat_id] = latest_message_id
                    if 'systemEventMessage' in messages[0]['body']['content']:
                        continue
                    # if condition below allows you to skip your own messages
                    if messages[0]['from']['user']['displayName'] == 'YOUR_OWN_NAME':
                        continue
                    # if condition below allows you to skip specific chats
                    if 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' in chat['id']:
                        continue
                    # skip meeting messages
                    if 'meeting' in chat['id']:
                        continue
                    # send sms
                    send_sms(f"{messages[0]['from']['user']['displayName']}:{messages[0]['body']['content']}")
                    continue
        time.sleep(120)
    return

if __name__ == "__main__":
    os.chdir('/tmp')
    while True:
        try:
            with open('/tmp/graph' , 'r') as f:
                access_token = f.read()
                if len(access_token) < 100:
                    print(f'access token is too small, {len(access_token)} bytes')
                    break
                headers['Authorization'] = f'Bearer {access_token.rstrip()}'
            check_for_new_messages()
        except Exception as e:
            if not 'Bad Gateway' in str(e) and not 'Service Unavailable' in str(e) and not 'Failed to execute backend' in str(e):
                print(e)
            pass
        time.sleep(5)
