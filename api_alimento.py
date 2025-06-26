import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# --- Configuración Inicial ---
load_dotenv()
app = FastAPI(
    title="API Persistente de Alimentos",
    description="Gestiona alimentos personalizados y el registro de consumo diario de forma persistente.",
    version="4.0.0"
)

# --- Constantes ---
DB_FILE = "alimentos_app.db" # Renombramos para mayor claridad
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")  
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

# --- Lógica de Base de Datos del Servidor ---
def init_db():
    """Inicializa ambas tablas en la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabla para alimentos personalizados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alimentos_personalizados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        calorias_100gr REAL,
        calorias_porcion REAL
    )
    """)
    # ¡NUEVO! Tabla para el consumo diario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consumo_diario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        cantidad REAL NOT NULL,
        total_cal REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# ... (Las funciones buscar_alimento_local y buscar_calorias_edamam no cambian) ...
def buscar_alimento_local(nombre: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alimentos_personalizados WHERE LOWER(nombre) = ?", (nombre.lower(),))
    alimento = cursor.fetchone()
    conn.close()
    return dict(alimento) if alimento else None

def buscar_calorias_edamam(nombre: str) -> Optional[dict]:
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {"ingr": nombre, "app_id": EDAMAM_APP_ID, "app_key": EDAMAM_APP_KEY}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("parsed"):
            food = data["parsed"][0]["food"]
            nutrients = food.get("nutrients", {})
            return { "nombre": food.get("label", nombre), "calorias_100gr": nutrients.get("ENERC_KCAL", 0), "calorias_porcion": None }
    except requests.RequestException:
        return None
    return None

# --- Modelos Pydantic (No cambian) ---
class AlimentoCreado(BaseModel):
    nombre: str
    calorias_100gr: Optional[float] = None
    calorias_porcion: Optional[float] = None

class AlimentoRespuesta(BaseModel):
    nombre: str
    calorias_100gr: Optional[float] = None
    calorias_porcion: Optional[float] = None
    fuente: str

class ConsumoRegistrado(BaseModel):
    nombre: str
    fecha: str
    hora: str
    cantidad: float
    total_cal: float

class RegistroRequest(BaseModel):
    consumo: ConsumoRegistrado

# --- Endpoints de la API ---

@app.on_event("startup")
async def startup_event():
    init_db()

# ... (Endpoints /alimentos y /consultar-alimento no cambian) ...
@app.post("/alimentos", status_code=201)
def agregar_alimento_personalizado(alimento: AlimentoCreado):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alimentos_personalizados (nombre, calorias_100gr, calorias_porcion) VALUES (?, ?, ?)",
                       (alimento.nombre, alimento.calorias_100gr, alimento.calorias_porcion))
        conn.commit()
        conn.close()
        return {"mensaje": f"Alimento '{alimento.nombre}' guardado con éxito."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail=f"El alimento '{alimento.nombre}' ya existe.")

@app.get("/alimentos", response_model=List[AlimentoCreado])
def obtener_alimentos_personalizados():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, calorias_100gr, calorias_porcion FROM alimentos_personalizados ORDER BY nombre")
    alimentos = cursor.fetchall()
    conn.close()
    return [dict(row) for row in alimentos]

@app.post("/consultar-alimento", response_model=AlimentoRespuesta)
def consultar_alimento(alimento: AlimentoCreado):
    local_food = buscar_alimento_local(alimento.nombre)
    if local_food:
        local_food['fuente'] = 'local'
        return local_food
    external_food = buscar_calorias_edamam(alimento.nombre)
    if external_food:
        external_food['fuente'] = 'externa'
        return external_food
    raise HTTPException(status_code=404, detail=f"No se encontró información para '{alimento.nombre}'.")


# --- ¡ENDPOINT MODIFICADO! ---
@app.post("/registrar-consumo")
def registrar_consumo(req: RegistroRequest):
    """Registra un nuevo consumo en la base de datos persistente."""
    consumo = req.consumo
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO consumo_diario (nombre, fecha, hora, cantidad, total_cal) VALUES (?, ?, ?, ?, ?)",
        (consumo.nombre, consumo.fecha, consumo.hora, consumo.cantidad, consumo.total_cal)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Consumo registrado exitosamente en la base de datos."}

# --- ¡ENDPOINT MODIFICADO! ---
@app.get("/resumen-diario/{fecha_str}")
def obtener_resumen_diario(fecha_str: str):
    """Obtiene el resumen de un día específico desde la base de datos persistente."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consumo_diario WHERE fecha = ?", (fecha_str,))
    consumos_del_dia = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not consumos_del_dia:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros para la fecha {fecha_str}")
        
    total_calorias = sum(c["total_cal"] for c in consumos_del_dia)
    return {"fecha": fecha_str, "resumen_total": {"calorias": round(total_calorias, 2)}, "consumos": consumos_del_dia}

@app.get("/historial")
def obtener_historial_completo(fecha_desde: str, fecha_hasta: str):
    """
    Devuelve todos los registros de consumo entre dos fechas (formato YYYY-MM-DD).
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # La consulta busca en la tabla de consumo y filtra por el rango de fechas.
    query = """
        SELECT nombre, fecha, hora, cantidad, total_cal 
        FROM consumo_diario 
        WHERE fecha BETWEEN ? AND ?
        ORDER BY fecha DESC, hora DESC
    """
    
    cursor.execute(query, (fecha_desde, fecha_hasta))
    registros = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not registros:
        # Es mejor devolver una lista vacía que un error 404 en este caso.
        return []
        
    return registros
@app.get("/")
def root():
    return {"mensaje": "API Persistente de Alimentos está en línea y funcionando."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)