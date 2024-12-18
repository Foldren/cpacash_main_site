from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from os import path
from sqlalchemy import select
from sqladmin import Admin
from starlette.exceptions import HTTPException
from admin import ProductAdmin, CategoryAdmin, authentication_backend, TagAdmin
from database import engine, async_session
from models import Category, Product, Tag
from routers import registration, exchange_prize

app = FastAPI()
app.include_router(registration.router)
app.include_router(exchange_prize.router)

# Подключаем статику
this_directory = path.dirname(__file__)
app.mount("/source/static", StaticFiles(directory=path.join(this_directory, "static")), name="static")
templates = Jinja2Templates(directory=path.join(this_directory, "templates"))

# Подключаем админку
admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    base_url="/admin-dy73HPyTU1UR_R5",
    title="CpacashAdmin",
)

admin.add_view(CategoryAdmin)
admin.add_view(TagAdmin)
admin.add_view(ProductAdmin)


# При первом запуске
# @app.on_event("startup")
# async def create_db_engine():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(404) # Вывод при ошибке 404
async def http_exception_404(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error_404.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/prize-shop")
async def prize_shop(request: Request, category: str = ""):
    async with async_session() as session:
        categories_obj = await session.execute(select(Category))
        products_obj = await session.execute(select(Product))
        tags_obj = await session.execute(select(Tag))
        categories = categories_obj.scalars().all()
        products = products_obj.scalars().all()
        tags = tags_obj.scalars().all()

    return templates.TemplateResponse(
        name="prize_shop.html",
        context={
            "request": request,
            "categories": categories,
            "tags": tags,
            "products": products,
            "category_index": category
        }
    )


@app.get("/page-success")
async def page_success(request: Request, event: str):
    data: dict = {
        'prize': {
            'header': 'Ура!<br>Мы получили твою заявку',
            'text': 'Скоро мы свяжемся и подтвердим доступ.<br>После этого ты сможешь зайти в личный кабинет.',
            },
        'reg': {
            'header': 'Мы получили твою заявку',
            'text': 'Скоро мы свяжемся с тобой и расскажем, как действовать дальше.',
        },
    }

    return templates.TemplateResponse(
        name="page_success.html",
        context={
            "request": request,
            "header": data[event]['header'],
            "text": data[event]['text'],
        }
    )


@app.get("/contacts")
async def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

@app.get("/registration")
async def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})
