# app/admin_models.py
from pydantic import BaseModel
from typing import Optional, List


class EntidadContratante(BaseModel):
    nombre: str
    domicilio: str
    tipo: str
    cif: str


class ObjetoContrato(BaseModel):
    descripcion: str
    tipo: str
    lugar: str
    division: bool
    presupuestos: str
    financiacion: Optional[str] = None


class ProcedimientoContratacion(BaseModel):
    tipo: str
    tramitacion: str
    regulacion: str


class Garantias(BaseModel):
    garantia_definitiva: bool
    porcentaje_definitiva: Optional[float] = None
    garantia_complementaria: Optional[str] = None


class Requisitos(BaseModel):
    solvencia_economica: str
    solvencia_tecnica: str
    medios: Optional[str] = None


class PresentacionOfertas(BaseModel):
    plazo: str
    lugar: str
    forma: str
    criterios: List[str]


class Datos(BaseModel):
    entidad: EntidadContratante
    objeto_contrato: str
    objeto: ObjetoContrato
    procedimiento: ProcedimientoContratacion
    garantias: Garantias
    requisitos: Requisitos
    presentacion: PresentacionOfertas
