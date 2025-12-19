from fastapi import APIRouter, Depends, HTTPException
from app import schemas, security, config
import google.generativeai as genai

router = APIRouter(prefix="/secubot", tags=["AI Chat"])

# Налаштування Gemini
# Переконайтесь, що в .env є змінна GOOGLE_API_KEY
try:
    genai.configure(api_key=config.settings.OPENAI_API_KEY) # Використовуємо ту ж змінну з конфігу, щоб не ламати структуру, але туди треба вставити ключ від Google
except Exception as e:
    print(f"Error configuring Gemini: {e}")

@router.post("/message", response_model=schemas.ChatResponse)
async def chat_with_ai(msg: schemas.ChatMessage, user=Depends(security.get_current_user)):
    # Демо-режим
    if config.settings.OPENAI_API_KEY == "demo" or not config.settings.OPENAI_API_KEY:
        return {"reply": f"Це демо режим SecuBot (Gemini). Я отримав ваше питання: {msg.text}"}

    try:
        # Використовуємо модель Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Створюємо промпт з контекстом
        prompt = f"Ти експерт з кібербезпеки SecuBot. Відповідай коротко, українською мовою. Питання користувача: {msg.text}"
        
        # Асинхронний виклик (generate_content_async)
        response = await model.generate_content_async(prompt)
        
        return {"reply": response.text}
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {"reply": "Вибачте, сервіс тимчасово недоступний або ключ API невірний."}