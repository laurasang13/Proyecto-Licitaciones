from .core_adm import generar_pliego_administrativo
from .model_adm import Datos
from fastapi import APIRouter
from .LiciZen_adm import Datos  


router = APIRouter()


# 📄 Pliego administrativo
@router.post("/administrativo")
async def generar_administrativo(datos: Datos):
    print("Datos:", datos)
    resultado = await generar_pliego_administrativo(datos)
    return resultado

from .model_adm import Datos as DatosSimple

@router.post("/administrativo_simple")
async def generar_basico(datos: DatosSimple):
    print(datos)
    return {"mensaje": "Recibido correctamente", "objeto": datos.objeto_contrato}
