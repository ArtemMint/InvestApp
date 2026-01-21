from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import crud
from app.schemas.item import ItemCreate

router = APIRouter()
# Compute project root reliably using parents so this works from nested modules
# For a file at app/api/v1/endpoints/item.py, parents[4] -> project root (/code)
project_root = Path(__file__).resolve().parents[4]
templates_dir = project_root / "frontend" / "templates"
# Fallback: if frontend/templates doesn't exist, fall back to app/templates
if not templates_dir.exists():
    templates_dir = Path(__file__).resolve().parents[3] / "templates"

templates = Jinja2Templates(directory=str(templates_dir))

# Сторінка перегляду та форми
@router.get("/ui", response_class=HTMLResponse)
async def read_items_ui(request: Request, db: Session = Depends(get_db)):
    items = crud.item.get_items(db)
    return templates.TemplateResponse("items.html", {"request": request, "items": items})

# Обробка форми (використовуємо Form замість JSON для звичайних HTML форм)
@router.post("/ui")
async def create_item_ui(
    title: str = Form(...),
    description: str = Form(None),
    media_url: str = Form(None),
    db: Session = Depends(get_db)
):
    item_in = ItemCreate(title=title, description=description, media_url=media_url)
    crud.item.create_item(db=db, item_in=item_in)
    # Після додавання повертаємо користувача на сторінку списку
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/items/ui", status_code=303)
