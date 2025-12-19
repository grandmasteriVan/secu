from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from app import schemas, models, security
from app.services.pdf_service import create_certificate

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/download/test")
async def download_test_cert(user: models.User = Depends(security.get_current_user)):
    """
    Генерує тестовий сертифікат для поточного користувача
    """
    # 1. Формуємо назву файлу (унікальну)
    filename = f"cert_{user.id}_test.pdf"
    
    # 2. Викликаємо генератор (ім'я юзера з БД або заглушка)
    display_name = user.full_name if user.full_name else user.email.split('@')[0]
    course_title = "Основи кібергігієни" # Тут можна брати реальний курс
    
    file_path = create_certificate(
        user_name=display_name,
        course_name=course_title,
        output_filename=filename
    )
    
    # 3. Віддаємо файл браузеру
    return FileResponse(
        path=file_path, 
        filename=f"Certificate_{display_name}.pdf", 
        media_type='application/pdf'
    )