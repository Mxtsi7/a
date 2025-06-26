import os
from datetime import datetime, date, timedelta
from typing import Optional
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator, computed_field
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. Configuración (Inspirado en tu ApiConfig) ---

class Settings:
    # URL de la base de datos (usamos SQLite por simplicidad)
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL') or 'sqlite:///./app.db'
    
    # Configuración de JWT
    JWT_SECRET_KEY: str = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60 # Equivalente a 1 hora

settings = Settings()

# --- 2. Modelos de Base de Datos SQLAlchemy (Tu Models.py adaptado) ---

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(80), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    genero = Column(String(10), nullable=False)
    peso = Column(Float, nullable=False)
    altura = Column(Integer, nullable=False)
    meta_calorias = Column(Integer, nullable=False)
    nivel_actividad = Column(String(15), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    registro = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calcular_edad(self) -> int:
        """Calcula la edad actual a partir de la fecha de nacimiento."""
        today = date.today()
        edad_calculada = today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return edad_calculada


# --- Configuración de la Base de Datos ---

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} # Necesario para SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. Esquemas Pydantic (Tu validacion.py adaptado) ---

class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=80)
    genero: str
    peso: float = Field(..., gt=30, le=300)
    altura: int = Field(..., gt=100, le=250)
    meta_calorias: int = Field(..., gt=1000, le=5000)
    nivel_actividad: str
    fecha_nacimiento: date

    @field_validator('genero')
    @classmethod
    def genero_valido(cls, v):
        if v not in ['Masculino', 'Femenino']:
            raise ValueError("El genero debe ser 'Masculino' o 'Femenino'")
        return v

    @field_validator('nivel_actividad')
    @classmethod
    def nivel_actividad_valido(cls, v):
        if v not in ['Sedentario', 'Ligero', 'Moderado', 'Intenso']:
            raise ValueError("El nivel de actividad no es válido")
        return v
        
    @field_validator('fecha_nacimiento')
    @classmethod
    def validar_edad(cls, v):
        today = date.today()
        edad = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if not (13 <= edad <= 120):
            raise ValueError(f'La edad debe estar entre 13 y 120 años. Edad calculada: {edad} años')
        return v

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class UsuarioLogin(BaseModel):
    nombre_usuario: str
    password: str

# CORREGIDO: Esquema para mostrar datos públicos del usuario
class UsuarioPublic(BaseModel):
    id: int
    nombre_usuario: str
    genero: str
    peso: float
    altura: int
    meta_calorias: int
    nivel_actividad: str
    fecha_nacimiento: date
    registro: datetime
    
    # NUEVO: Campo calculado para la edad usando computed_field
    @computed_field
    @property
    def edad(self) -> int:
        """Calcula la edad actual a partir de la fecha de nacimiento."""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    class Config:
        from_attributes = True  # Reemplaza orm_mode en Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

# --- 4. Lógica de Autenticación y JWT ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# --- 5. Creación de la Aplicación y Endpoints ---

app = FastAPI(
    title="API de Registro y Nutrición",
    description="Una API para gestionar el registro y login de usuarios.",
    version="1.0.0"
)

@app.post("/register/", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos.
    - Valida que el nombre de usuario no exista.
    - Hashea la contraseña antes de guardarla.
    """
    db_user = db.query(Usuario).filter(Usuario.nombre_usuario == usuario.nombre_usuario).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado."
        )
    
    hashed_password = generate_password_hash(usuario.password)
    nuevo_usuario = Usuario(
        nombre_usuario=usuario.nombre_usuario,
        password_hash=hashed_password,
        genero=usuario.genero,
        peso=usuario.peso,
        altura=usuario.altura,
        meta_calorias=usuario.meta_calorias,
        nivel_actividad=usuario.nivel_actividad,
        fecha_nacimiento=usuario.fecha_nacimiento
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


@app.post("/login/", response_model=Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica a un usuario y retorna un token JWT.
    Utiliza `OAuth2PasswordRequestForm` para que puedas usar el formulario de "Authorize"
    en la documentación de Swagger UI.
    - **username**: corresponde a `nombre_usuario`.
    - **password**: corresponde a la contraseña.
    """
    user = db.query(Usuario).filter(Usuario.nombre_usuario == form_data.username).first()
    
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": user.nombre_usuario}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=UsuarioPublic, tags=["Users"])
def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Endpoint protegido que devuelve los datos del usuario autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    if user is None:
        raise credentials_exception
    return user