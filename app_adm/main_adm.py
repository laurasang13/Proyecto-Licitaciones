# app/main.py
from fastapi import FastAPI
from .api_adm import router
from fastapi.middleware.cors import CORSMiddleware #Compartición de recursos entre dominios distintos

#Crea una instancia de FastAPI
app = FastAPI(
    title="API de Pliegos Administrativos",
    description="Genera pliegos Administrativos a partir de respuestas usando Gemini.",
    version="1.0.0"
)

# Permitir CORS si lo usarás desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Dominios permitidos
    allow_credentials=True, #Permite incluir cookies o autenticación
    allow_methods=["*"], #Métodos HTTP permitidos
    allow_headers=["*"], #Qué cabeceras están permitidas en la petición
)
# ¡¡Comentar que en desarrollo se permite usar *, sin embargo, en producción se recomienda especificar los dominios permitidos para mayor seguridad!!
app.include_router(router)
