import json
import re

import openai
from django.conf import settings


def send_to_openai(front_image_base64, back_image_base64):
    """ Отправляет изображения паспорта в OpenAI и получает JSON-ответ """
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = [
            {"role": "system",
             "content": "Ты опытный OCR-специалист. Проанализируй изображения паспорта и верни чистый JSON без форматирования."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image_base64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image_base64}"}},
                {"type": "text",
                 "text": 'Распознай паспорт и верни **чистый JSON, без форматирования, без пояснений**, строго: '
                         '{"inn": "", "first_name": "", "last_name": "", "patronymic": "", '
                         '"gender": "", "birthdate": "", "passport_number": ""}. '
                         '❗ Не добавляй ничего перед и после JSON. Просто JSON.'}
            ]}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        result_text = response.choices[0].message.content.strip()

        result_text = re.sub(r"^```json\n|\n```$", "", result_text).strip()

        # Проверяем, начинается ли ответ с "{" и заканчивается "}"
        if result_text.startswith("{") and result_text.endswith("}"):
            return json.loads(result_text)  # Парсим в словарь Python

        return {"error": "OpenAI не вернул JSON. Ответ: " + result_text}

    except json.JSONDecodeError:
        return {"error": "Ошибка декодирования JSON от OpenAI."}
    except openai.OpenAIError as e:
        return {"error": f"Ошибка OpenAI: {str(e)}"}
    except Exception as e:
        return {"error": f"Неизвестная ошибка: {str(e)}"}
