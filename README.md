# 🤖 CreditBot - Asistente de Validación de Crédito con LangGraph

Este proyecto implementa un asistente inteligente de evaluación crediticia utilizando [LangGraph](https://docs.langchain.com/langgraph/), una extensión de LangChain para flujos de conversación, y modelos de lenguaje de OpenAI (`gpt-4o`).

El bot evalúa si un usuario cumple las condiciones necesarias para recibir un crédito, basado en múltiples políticas de negocio y criterios como edad, ingresos, score crediticio y justificación del préstamo.

---

## 🚀 Requisitos

- Python 3.10 o superior
- [LangChain CLI](https://docs.langchain.com/langchain/cli/get_started/) con entorno in-memory
- OpenAI API Key

---

## 🧰 Instalación

```bash
# Clona el repositorio
git clone https://github.com/tuusuario/credit-bot.git
cd credit-bot

# Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala dependencias
pip install langchain langgraph langchain-openai python-dotenv
pip install -U langchain-cli[inmem]

# Crea un archivo .env para tus variables de entorno
OPENAI_API_KEY=tu_clave_de_api
````
---

## 🧩 ¿Por qué usar LangGraph?
LangGraph te permite representar flujos de decisión con control total sobre la lógica, ideal para sistemas basados en reglas como este. Además, permite escalar fácilmente a múltiples criterios o integrar nueva lógica de negocio.

## 📌 To Do
 Integración con FastAPI para exponer un endpoint.
 Soporte para historiales de múltiples usuarios.
 Persistencia de decisiones para auditoría.