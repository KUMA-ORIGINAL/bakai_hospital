import json
import logging
import re

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

logger.info("Инициализация клиента OpenAI")
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def send_to_openai(front_image_base64, back_image_base64):
    """
    Отправка изображений паспорта в OpenAI для извлечения данных.
    """
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты профессиональный OCR-специалист.\n"
                    "Твоя задача:\n"
                    "1. Проанализировать фотографии паспорта (переднюю и заднюю стороны).\n"
                    "2. Вернуть ТОЛЬКО строго JSON без комментариев.\n"
                    "\n"
                    "Извлеки следующие поля:\n"
                    "- inn: Персональный номер/personal number (если нет — пустая строка \"\")\n"
                    "- first_name: Имя (только кириллица, заглавными буквами)\n"
                    "- last_name: Фамилия (только кириллица, заглавными буквами)\n"
                    "- patronymic: Отчество (если нет — пустая строка \"\")\n"
                    "- gender: 'М' для мужчин, 'Ж' для женщин\n"
                    "- date_of_birth: Дата рождения в формате 'DD-MM-YYYY'\n"
                    "- passport_number: Номер паспорта или ID-карты\n"
                    "\n"
                    "Требования:\n"
                    "- Использовать только кириллицу.\n"
                    "- Все ФИО — заглавными буквами (например: «ИВАНОВ»).\n"
                    "- Строго форматировать дату.\n"
                    "- Если данных нет — пустая строка.\n"
                    "- Никаких лишних текстов и пояснений."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image_base64}"}},
                    {"type": "text",
                     "text": "Распознай текст и верни данные в формате JSON."}
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

        result_text = re.sub(r"^```json\s*|\s*```$", "", result_text.strip())

        if result_text.startswith("{") and result_text.endswith("}"):
            extracted_data = json.loads(result_text)

            for field in ["first_name", "last_name", "patronymic"]:
                if extracted_data.get(field):
                    extracted_data[field] = extracted_data[field].capitalize()

            gender = extracted_data.get("gender", "").upper()
            if gender in ["М", "Э"]:
                extracted_data["gender"] = "male"
            elif gender in ["Ж", "А"]:
                extracted_data["gender"] = "female"
            else:
                extracted_data["gender"] = ""

            return extracted_data

        return {"error": f"OpenAI не вернул JSON. Ответ: {result_text}"}

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {str(e)}")
        return {"error": "Ошибка декодирования JSON от OpenAI."}
    except openai.OpenAIError as e:
        logger.error(f"Ошибка OpenAI: {str(e)}")
        return {"error": f"Ошибка OpenAI: {str(e)}"}
    except Exception as e:
        logger.exception("Неизвестная ошибка при работе send_to_openai")
        return {"error": f"Неизвестная ошибка: {str(e)}"}
