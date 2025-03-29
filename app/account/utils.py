import json
import re
from datetime import datetime

import openai
from django.conf import settings

def normalize_date(date_string):
    try:
        return datetime.strptime(date_string, "%d.%m.%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_string


def send_to_openai(front_image_base64, back_image_base64):
    """ Отправляет изображения паспорта в OpenAI и получает JSON-ответ на русском языке """
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = [
            {"role": "system",
             "content": "Ты OCR-специалист. Проанализируй текст на изображениях паспорта и верни только JSON."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image_base64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image_base64}"}},
                {"type": "text",
                 "text": (
                     'Распознай паспорт, только кириллицу и числа. Верни **чистый JSON**, строго в таком формате: '
                     '{"inn": "", "first_name": "", "last_name": "", "patronymic": "", '
                     '"gender": "", "date_of_birth": "", "passport_number": ""}. '
                     'Не добавляй никакой другой текст, кроме JSON!'
                 )}
            ]}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        result_text = response.choices[0].message.content.strip()

        # Удаляем возможные текстовые обёртки вокруг JSON
        result_text = re.sub(r"^```json\n|\n```$", "", result_text).strip()

        # Проверяем, является ли ответ валидным JSON
        if result_text.startswith("{") and result_text.endswith("}"):
            extracted_data = json.loads(result_text)

            extracted_data["first_name"] = extracted_data["first_name"].capitalize()
            extracted_data["last_name"] = extracted_data["last_name"].capitalize()
            extracted_data["patronymic"] = extracted_data["patronymic"].capitalize()

            if extracted_data.get("gender") in ["М", "Э"]:
                extracted_data["gender"] = "male"
            elif extracted_data.get("gender") in ["Ж", "А"]:
                extracted_data["gender"] = "female"
            else:
                extracted_data["gender"] = ""

            extracted_data["date_of_birth"] = normalize_date(extracted_data.get("date_of_birth", ""))

            return extracted_data

        return {"error": "OpenAI не вернул JSON. Ответ: " + result_text}

    except json.JSONDecodeError:
        return {"error": "Ошибка декодирования JSON от OpenAI."}
    except openai.OpenAIError as e:
        return {"error": f"Ошибка OpenAI: {str(e)}"}
    except Exception as e:
        return {"error": f"Неизвестная ошибка: {str(e)}"}
