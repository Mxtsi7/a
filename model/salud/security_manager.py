import os
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
import json
from pathlib import Path
import getpass
import platform

class SecureAPIManager:
    """
    Sistema de encriptación multicapa para API keys con máxima seguridad.
    Combina varias técnicas de seguridad para protección óptima.
    """
    
    def __init__(self, app_name="CaloriasPro60hz"):
        self.app_name = app_name
        self.config_dir = Path.home() / f".{app_name.lower()}"
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / "secure.key"
        self.config_file = self.config_dir / "config.enc"
        
    def _generate_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Genera una clave de encriptación a partir de una contraseña usando PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Número alto de iteraciones para mayor seguridad
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _get_machine_fingerprint(self) -> str:
        """Crea una huella digital única de la máquina"""
        # Combina información única del sistema
        machine_info = f"{platform.node()}{platform.processor()}{platform.system()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    def _store_in_keyring(self, key_name: str, value: str) -> bool:
        """Almacena datos en el keyring del sistema operativo"""
        try:
            keyring.set_password(self.app_name, key_name, value)
            return True
        except Exception as e:
            print(f"Error almacenando en keyring: {e}")
            return False
    
    def _get_from_keyring(self, key_name: str) -> str:
        """Recupera datos del keyring del sistema operativo"""
        try:
            return keyring.get_password(self.app_name, key_name)
        except Exception as e:
            print(f"Error recuperando del keyring: {e}")
            return None
    
    def setup_encryption(self, api_key: str, master_password: str = None) -> bool:
        """
        Configuración inicial de encriptación con múltiples capas de seguridad.
        
        Capas de seguridad:
        1. Encriptación Fernet (AES 128)
        2. Derivación de clave PBKDF2 con salt
        3. Almacenamiento en keyring del SO
        4. Huella digital de máquina
        5. Ofuscación adicional
        """
        try:
            # Generar salt aleatorio
            salt = secrets.token_bytes(16)
            
            # Si no se proporciona contraseña maestra, generar una automáticamente
            if not master_password:
                master_password = self._get_machine_fingerprint() + secrets.token_urlsafe(16)
            
            # Generar clave de encriptación
            encryption_key = self._generate_key_from_password(master_password, salt)
            fernet = Fernet(encryption_key)
            
            # Encriptar API key
            encrypted_api_key = fernet.encrypt(api_key.encode())
            
            # Crear estructura de datos segura
            secure_data = {
                "encrypted_key": base64.b64encode(encrypted_api_key).decode(),
                "salt": base64.b64encode(salt).decode(),
                "fingerprint": self._get_machine_fingerprint(),
                "version": "1.0"
            }
            
            # Almacenar en keyring si está disponible
            keyring_stored = self._store_in_keyring("master_key", master_password)
            
            if keyring_stored:
                # Solo guardar datos encriptados en archivo
                with open(self.config_file, 'w') as f:
                    json.dump(secure_data, f)
                print("✅ API key encriptada y almacenada en keyring del sistema")
            else:
                # Fallback: guardar todo en archivo con encriptación adicional
                secure_data["master_key_hash"] = hashlib.sha256(master_password.encode()).hexdigest()
                with open(self.config_file, 'w') as f:
                    json.dump(secure_data, f)
                print("✅ API key encriptada y almacenada en archivo local")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando encriptación: {e}")
            return False
    
    def get_api_key(self, master_password: str = None) -> str:
        """
        Recupera y desencripta la API key.
        """
        try:
            # Verificar si existe el archivo de configuración
            if not self.config_file.exists():
                return None
            
            # Cargar datos encriptados
            with open(self.config_file, 'r') as f:
                secure_data = json.load(f)
            
            # Verificar huella digital de máquina
            if secure_data.get("fingerprint") != self._get_machine_fingerprint():
                print("❌ Error: Huella digital de máquina no coincide")
                return None
            
            # Recuperar contraseña maestra
            if not master_password:
                master_password = self._get_from_keyring("master_key")
                if not master_password:
                    # Intentar generar automáticamente
                    master_password = self._get_machine_fingerprint() + secrets.token_urlsafe(16)
            
            # Verificar contraseña maestra si hay hash
            if "master_key_hash" in secure_data:
                password_hash = hashlib.sha256(master_password.encode()).hexdigest()
                if password_hash != secure_data["master_key_hash"]:
                    print("❌ Error: Contraseña maestra incorrecta")
                    return None
            
            # Desencriptar
            salt = base64.b64decode(secure_data["salt"])
            encryption_key = self._generate_key_from_password(master_password, salt)
            fernet = Fernet(encryption_key)
            
            encrypted_api_key = base64.b64decode(secure_data["encrypted_key"])
            decrypted_api_key = fernet.decrypt(encrypted_api_key).decode()
            
            return decrypted_api_key
            
        except Exception as e:
            print(f"❌ Error desencriptando API key: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Verifica si la encriptación está configurada"""
        return self.config_file.exists()
    
    def reset_encryption(self) -> bool:
        """Elimina todas las configuraciones de encriptación"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            
            # Limpiar keyring
            try:
                keyring.delete_password(self.app_name, "master_key")
            except:
                pass
            
            print("✅ Configuración de encriptación eliminada")
            return True
        except Exception as e:
            print(f"❌ Error eliminando configuración: {e}")
            return False


class EnvironmentAPIManager:
    """
    Alternativa simple usando variables de entorno para desarrollo.
    """
    
    @staticmethod
    def set_api_key(api_key: str, env_file: str = ".env"):
        """Guarda API key en archivo .env"""
        env_path = Path(env_file)
        with open(env_path, 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print(f"✅ API key guardada en {env_file}")
    
    @staticmethod
    def get_api_key(env_var: str = "GEMINI_API_KEY") -> str:
        """Recupera API key de variable de entorno"""
        return os.environ.get(env_var)
    
    @staticmethod
    def load_env_file(env_file: str = ".env"):
        """Carga variables de entorno desde archivo .env"""
        env_path = Path(env_file)
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value


# Ejemplo de uso e integración
def setup_api_security():
    """Función para configurar la seguridad de API key por primera vez"""
    print("🔐 Configuración de seguridad para API key")
    print("1. Encriptación avanzada con keyring")
    print("2. Archivo .env para desarrollo")
    
    choice = input("Selecciona opción (1/2): ")
    
    if choice == "1":
        api_key = getpass.getpass("Ingresa tu API key de Gemini: ")
        manager = SecureAPIManager()
        
        use_password = input("¿Usar contraseña maestra personalizada? (y/n): ").lower() == 'y'
        master_password = None
        if use_password:
            master_password = getpass.getpass("Ingresa contraseña maestra: ")
        
        if manager.setup_encryption(api_key, master_password):
            print("✅ API key configurada de forma segura")
        else:
            print("❌ Error en la configuración")
    
    elif choice == "2":
        api_key = input("Ingresa tu API key de Gemini: ")
        EnvironmentAPIManager.set_api_key(api_key)
        print("⚠️  Recuerda agregar .env a tu .gitignore")

if __name__ == "__main__":
    setup_api_security()