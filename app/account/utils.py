import json
import logging
import re
from datetime import datetime

import openai
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_date(date_string):
    try:
        return datetime.strptime(date_string, "%d.%m.%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_string


def send_to_openai(front_image_base64, back_image_base64):
    try:
        logger.info("Инициализация клиента OpenAI")
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        messages = [
            {
                "role": "system",
                "content": (
                    "Ты профессиональный OCR-специалист.\n"
                    "Твоя задача: точно анализировать изображения паспорта (переднюю и заднюю стороны) "
                    "и вернуть только нужные данные в формате чистого JSON без каких-либо пояснений."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image_base64}"}},
                    {"type": "text",
                     "text": (
                         "Распознай текст на паспорте.\n"
                         "Извлеки строго следующие данные:\n"
                         "- inn — ИНН (если есть, иначе \"\")\n"
                         "- first_name — Имя (предпочтительно кириллицей, если доступно)\n"
                         "- last_name — Фамилия (предпочтительно кириллицей, если доступно)\n"
                         "- patronymic — Отчество (если есть, иначе \"\")\n"
                         "- gender — Пол (М или Ж)\n"
                         "- date_of_birth — Дата рождения в формате YYYY-MM-DD\n"
                         "- passport_number — Номер паспорта или ID-карты\n\n"
                         "Важно:\n"
                         "- Используй только кириллицу.\n"
                         "- Формат даты строго YYYY-MM-DD.\n"
                         "- Пол указывай одной буквой: 'М' (мужской) или 'Ж' (женский).\n"
                         "- Если данных нет, оставляй пустую строку \"\".\n"
                         "- Никаких лишних слов, описаний или пояснений — только JSON, ровно по шаблону."
                     )}
                ]
            }
        ]

        logger.info("Отправка запроса в OpenAI")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        result_text = response.choices[0].message.content.strip()
        logger.info(f"Ответ от OpenAI: {result_text}")

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

            # extracted_data["date_of_birth"] = normalize_date(extracted_data.get("date_of_birth", ""))

            return extracted_data

        return {"error": "OpenAI не вернул JSON. Ответ: " + result_text}

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {str(e)}")
        return {"error": "Ошибка декодирования JSON от OpenAI."}
    except openai.OpenAIError as e:
        logger.error(f"Ошибка OpenAI: {str(e)}")
        return {"error": f"Ошибка OpenAI: {str(e)}"}
    except Exception as e:
        logger.exception("Неизвестная ошибка при работе send_to_openai")
        return {"error": f"Неизвестная ошибка: {str(e)}"}
