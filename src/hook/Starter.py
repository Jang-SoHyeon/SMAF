import logging
import requests
from fastapi import APIRouter
from src.hook.Summary import ConversationSummary
from fastapi.responses import JSONResponse
import dotenv
import os
import json
import random

dotenv.load_dotenv('.env')
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


class Starter:
    router = APIRouter()

    @staticmethod
    @router.post("/conversation/start/f")
    def conversation_starter_f():
        result = ConversationSummary().completion_executor()
        if result.get('status_code') == 2000:
            questions = ["안녕 너는 무슨 대화를 좋아해?","요즘 관심사가 뭐야?","너가 좋아하는게 뭔지 궁금해","배 안고파? 너는 뭐 먹고싶어?"]
            random_number = random.randint(0, 3)
            return JSONResponse({"result": questions[random_number], "response_code": 200})
        else:
            return JSONResponse({"result": Starter().execute_f(), "response_code": 200})

    def __init__(self):
        self._host = 'https://clovastudio.stream.ntruss.com'
        starter_api_key = os.getenv('sliding_api_key')
        starter_api_key_primary_val = os.getenv('sliding_api_key_primary_val')
        starter_request_id = os.getenv('starter_request_id')
        self._api_key = starter_api_key
        self._api_key_primary_val = starter_api_key_primary_val
        self._request_id = starter_request_id

    @staticmethod
    def save_summary():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'userInformation.txt')
        try:
            with open(file_path, 'r', encoding='utf-8') as infile:
                line = infile.read()
            if line:
                preset_text = [{
                    "role": "system",
                    "content": "당신은 공감과 이해를 잘해주는 친구입니다.\n질문 패턴과 사용자의 정보를 참고하여 사용자에게 질문합니다.\n###질문 패턴###\r\n- 항상 반말로 질문한다.\r\n- 짧게 질문한다.\r\n- 사용자의 의견을 존중하고 공감합니다.\n- 사용자의 감정을 고려하여 말합니다.\n- 착하고 친절한 말투로 말한다.\n###\n질문 패턴과 사용자의 정보를 참고하여 사용자에게 질문합니다.\n\n사용자 정보 :\r\n곧 결혼식을 앞두고 있다.\r\n다이어트를 하고 있다.\r\n살이 잘 빠지지 않아 힘들어 한다.\n\n결혼 준비는 잘 돼가?\n###\n질문 패턴과 사용자의 정보를 참고하여 사용자에게 질문합니다. \n\n- 다이어트를 하려고 했으나, 건강에 좋지 않다는 조언을 듣고 포기함\n\n\n다이어트 힘들지 않아?"
                },
                    {"role": "user",
                     "content": line}]
                return preset_text
        except Exception as e:
            logging.warning("txt file save error", e)

    def execute_f(self):
        preset_text = Starter().save_summary()
        request_data = {
            'messages': preset_text,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 322,
            'temperature': 0.5,
            'repeatPenalty': 7.1,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        final_answer = ""
        with requests.post(self._host + '/testapp/v1/tasks/pxzv15fo/chat-completions',
                           headers=headers, json=request_data, stream=True) as r:
            r.raise_for_status()
            longest_line = ""
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        event_data = json.loads(decoded_line[len("data:"):])
                        message_content = event_data.get("message", {}).get("content", "")
                        if len(message_content) > len(longest_line):
                            longest_line = message_content
                    final_answer = longest_line
            logging.warning(final_answer)
            return final_answer
