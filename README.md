# ⚡ CaloriasPro60Hz ⚡

[![Banner o Screenshot Principal de la App](https://github.com/HectorLep/CaloriasPro60Hz/raw/master/assets/interfaz.png)](https://github.com/HectorLep/CaloriasPro60Hz/raw/master/assets/interfaz.png)
> Una aplicación de escritorio para Linux y Windows, construida en Python, para el seguimiento integral de tu salud y nutrición.

---

## 📝 Descripción del Proyecto

**CaloriasPro60Hz** es una aplicación de escritorio multiplataforma (Linux/Windows) desarrollada en Python como proyecto para la asignatura `Diseño de Software` en la `Universidad Catolica de Temuco`.

A diferencia de las soluciones web, esta aplicación se ejecuta de forma nativa en tu sistema operativo, ofreciendo una experiencia rápida y fluida. El objetivo es proporcionar una herramienta robusta y centralizada para que los usuarios puedan monitorear su ingesta calórica, medir su pulso, y calcular métricas de salud clave como el IMC y la TMB, todo desde una única interfaz gráfica.

---

## ✨ Características Principales (Features)

CaloriasPro60Hz está organizado en módulos para una gestión completa de tu salud:

* **🍎 Gestión de Alimentos y Base de Datos**
    * **Registro Diario:** Añade alimentos a tu consumo del día, calculando calorías por porción o por cada 100gr.
    * **Base de Datos Personalizable:** Agrega nuevos alimentos a la base de datos de la aplicación para usarlos en futuros registros.

* **❤️ Módulo de Salud Centralizado**
    * **Calculadoras de Salud:** Mide tu IMC (Índice de Masa Corporal) y TMB (Tasa Metabólica Basal) de forma instantánea.
    * **Seguimiento de Hidratación:** Registra los vasos de agua tomados, con una meta diaria recomendada según tu peso.
    * **Progreso Visual:** Una barra de progreso te muestra en tiempo real cuántas calorías has consumido de tu meta diaria.
    * **Actualización de Peso:** Registra tu peso actual para mantener tus cálculos y progreso siempre al día.
    * **🤖 Asistente IA Integrado:** Recibe consejos, análisis y respuestas de un asistente inteligente para ayudarte a alcanzar tus metas de salud.

* **📊 Gráficos y Estadísticas de Progreso**
    * Visualiza tu consumo de calorías, agua y la frecuencia de alimentos consumidos.
    * Filtra las vistas por día, semana o mes para entender tus hábitos a lo largo del tiempo.

* **📖 Historial de Consumo Detallado**
    * Revisa todos los alimentos que has consumido en el pasado.
    * Filtra tu historial por fechas específicas para encontrar un registro fácilmente.

* **🍽️ Creador de Menús**
    * Planifica tus comidas y dietas con antelación creando menús personalizados para la semana.

* **⚙️ Configuración y Gestión de Cuenta**
    * **Perfil de Usuario:** Visualiza y actualiza tu información personal como estatura, edad, nivel de actividad y metas calóricas.
    * **Recordatorios Personalizables:** Configura notificaciones para recordar actualizar tu peso, con frecuencias diarias, semanales, etc.
    * **Seguridad y Privacidad:** Cambia tu contraseña, cierra la sesión de forma segura o elimina tu cuenta y todos tus datos permanentemente.

---

## 🛠️ Tecnologías Utilizadas (Tech Stack)

* **Lenguaje:** `Python 3.10+`
* **Interfaz Gráfica (GUI):** `PyQt6`
* **Librerías Clave:**
    * `PyQt6-Charts` para la generación de gráficos y estadísticas.
    * `google-genai` para la integración con el Asistente IA.
    * `FastAPI` y `uvicorn` para servir el modelo de IA de forma local.
    * `NumPy` para cálculos numéricos y manipulación de datos.
    * `python-dotenv` para la gestión de variables de entorno (como API Keys).

---

## 🚀 Cómo Empezar (Getting Started)

Sigue estos pasos para instalar y ejecutar el proyecto en un entorno local.

### Prerrequisitos

* Python 3.10 o superior
* pip (El gestor de paquetes de Python)
* Git

### Instalación

1.  **Clona el repositorio:**
    ````bash
    git clone [https://github.com/HectorLep/CaloriasPro60Hz.git](https://github.com/HectorLep/CaloriasPro60Hz.git)
    ````
2.  **Navega al directorio del proyecto:**
    ````bash
    cd CaloriasPro60Hz
    ````
3.  **Crea y activa un entorno virtual (Recomendado):**
    * En **Linux / macOS**:
        ````bash
        python3 -m venv venv
        source venv/bin/activate
        ````
    * En **Windows**:
        ````bash
        python -m venv venv
        .\venv\Scripts\activate
        ````
4.  **Instala las dependencias del proyecto:**
    *(Asegúrate de tener un archivo `requirements.txt` en tu repositorio)*
    ````bash
    pip install -r requirements.txt
    ````
5.  **Ejecuta la aplicación:**
    ````bash
    python main.py
    ````

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 👤 Autores

* **Hector** - [@HectorLep](https://github.com/HectorLep)
* **Maximiliano** - [@Mxtsi7](https://github.com/Mxtsi7)
* **Agustin** - [@sonickiller39](https://github.com/sonickiller39)
* **Christoper** - [@Insert-name-115](https://github.com/Insert-name-115)
* **Javier** - [@javierrrp](https://github.com/javierrrp)
