# 🤖 Sistema Agéntico Orientado a Skills (Habilidades)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/architecture-Clean--Skills-orange.svg)](#-propuesta-de-refactorización-y-arquitectura)

Este repositorio presenta un caso práctico de **Refactorización y Personalización de un Sistema Agéntico**, migrando de un enfoque tradicional basado en "monolitos de prompts" hacia un paradigma moderno de desarrollo de agentes de software basado en **Skills (Habilidades) Redirigibles** en Python.

---

## 📌 Contexto y Problemática: El "Monolito" Original

Heredamos un script clásico de procesamiento de datos: un archivo único, altamente acoplado, encargado de extraer texto de PDFs, interactuar mediante prompts fijos con un LLM para clasificar la información y guardar un reporte final.

### 🚨 Principales Fallos del Diseño Monolítico:
1. **Acoplamiento de Proveedor (Vendor Lock-in):** Las llamadas directas a las APIs de los LLM están incrustadas ("hardcoded") en la lógica del negocio. Cambiar de proveedor (ej. de OpenAI a Anthropic o un modelo local) requiere modificar todo el flujo.
2. **Falta de Estado y Memoria:** El agente carece de la habilidad de recordar interacciones previas de forma limpia o mantener configuraciones de sesión sin recurrir a variables globales propensas a errores.
3. **Imposibilidad de Extensión:** Si decidimos añadir capacidades como "búsqueda web" o "ejecución segura de código", nos vemos forzados a alterar el flujo de ejecución principal mediante estructuras condicionales (`if/else`) interminables y difíciles de mantener.

---

## 🏗️ Propuesta de Refactorización y Arquitectura

Para solucionar estas limitaciones, se ha diseñado un sistema modular estructurado en **tres capas limpias y desacopladas**:

```
 ┌─────────────────────────────────────────────────────────┐
 │            Capa 1: Core LLM (config.py)                 │
 │   - Abstracción de Proveedor e Inferencia del LLM       │
 └────────────────────────────┬────────────────────────────┘
                              ▼
 ┌─────────────────────────────────────────────────────────┐
 │            Capa 3: Agente (agent.py)                    │
 │   - Orquesta flujos, historial de conversación y memoria │
 └────────────────────────────┬────────────────────────────┘
                              ▼  (Registro Dinámico)
 ┌─────────────────────────────────────────────────────────┐
 │            Capa 2: Sistema de Skills (skills.py)        │
 │   - Módulos independientes y autocontenidos            │
 │   - Auto-descriptivos mediante JSON Schema              │
 └─────────────────────────────────────────────────────────┘
```

1. **Capa de Configuración e Inferencia (Core LLM):** Abstrae al proveedor del modelo para permitir intercambiar motores de inferencia sin alterar el comportamiento de negocio.
2. **Capa de Skills (Habilidades):** Módulos independientes, autocontenidos y auto-documentados que el agente puede registrar y ejecutar dinámicamente bajo demanda.
3. **Capa de Agente:** Coordina el flujo de ejecución, mantiene el historial de conversación (memoria) y decide inteligentemente qué skill invocar.

---

## 🛠️ Estructura del Proyecto

El código se organiza en archivos especializados y limpios:

```bash
.
├── config.py  # Capa 1: Proveedor e interfaz de inferencia LLM
├── skills.py  # Capa 2: Definición de Skills base y específicas (WebSearch, CodeExecutor)
├── agent.py   # Capa 3: Orquestación del Agente, gestión de memoria y ruteo
└── main.py    # Punto de entrada / Orquestador y pruebas de concepto
```

---

## 💻 Implementación de la Refactorización

### 📦 Capa 1: Configuración y Cliente LLM (`config.py`)
Gestiona la conexión y encapsula las llamadas al LLM de forma abstracta.

```python
import os
from typing import List, Dict, Any

class LLMProvider:
    """Abstracción para el motor de inferencia del LLM."""
    def __init__(self, model: str = "gpt-4o-mini"):
        # En producción, se cargaría desde variables de entorno (.env)
        self.api_key = os.getenv("OPENAI_API_KEY", "tu-api-key-aqui")
        self.model = model

    def generate(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> Any:
        """Simulación de llamada a la API con soporte para Tool Calling."""
        # Nota de diseño: En una implementación real con la librería 'openai' instalada:
        # from openai import OpenAI
        # client = OpenAI(api_key=self.api_key)
        # response = client.chat.completions.create(model=self.model, messages=messages, tools=tools)
        # return response.choices[0].message
        
        # Simulación de respuesta para fines demostrativos sin dependencias externas obligatorias
        print(f"--- [Invocando LLM: {self.model}] ---")
        return {
            "role": "assistant",
            "content": "Pensando en la mejor respuesta...",
            "tool_calls": None
        }
```

### 🎯 Capa 2: Diseño del Sistema de Skills (`skills.py`)
Un Skill es una unidad de comportamiento autocontenida que obliga a documentar la funcionalidad mediante un JSON Schema para que el LLM entienda cómo usarla vía *Function Calling*.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSkill(ABC):
    """Clase abstracta para definir Habilidades (Skills) del Agente."""
    
    @property
    @abstractmethod
    def definition(self) -> Dict[str, Any]:
        """Devuelve la definición de la herramienta en formato JSON Schema para el LLM."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Ejecuta la lógica de negocio de la skill."""
        pass


# --- IMPLEMENTACIÓN DE SKILLS ESPECÍFICAS ---

class WebSearchSkill(BaseSkill):
    """Skill para simular búsquedas de información actualizada."""
    
    @property
    def definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Busca información actualizada en la web sobre un tema específico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "El término o pregunta a buscar."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

    def execute(self, query: str) -> str:
        # Aquí iría la integración con APIs como Tavily, Serper, etc.
        print(f"[Skill - WebSearch] Buscando en la red: '{query}'")
        return f"Resultados para '{query}': La tecnología o evento consultado está operando bajo estándares óptimos en 2026."


class CodeExecutorSkill(BaseSkill):
    """Skill para ejecutar pequeños scripts de forma segura (ej. cálculos matemáticos complejos)."""

    @property
    def definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "execute_code",
                "description": "Ejecuta expresiones matemáticas complejas utilizando Python de manera segura.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "La expresión matemática a evaluar. Ej: '2 * 3.1416 * 5'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }

    def execute(self, expression: str) -> str:
        print(f"[Skill - CodeExecutor] Evaluando expresión: '{expression}'")
        try:
            # Uso controlado de eval para evaluación matemática básica
            allowed_chars = set("0123456789+-*/(). ")
            if not all(char in allowed_chars for char in expression):
                return "Error: Caracteres no permitidos detectados por razones de seguridad."
            result = eval(expression)
            return f"Resultado de la evaluación: {result}"
        except Exception as e:
            return f"Error al ejecutar la expresión: {str(e)}"
```

### 🧠 Capa 3: El Agente Personalizado (`agent.py`)
El agente coordina su memoria (historial), sus directrices principales (system prompt) y las habilidades registradas de forma dinámica.

```python
from typing import List, Dict, Any
from config import LLMProvider
from skills import BaseSkill

class CustomAgent:
    """Agente con soporte para carga dinámica de Skills y gestión de estado."""
    def __init__(self, name: str, instructions: str, llm_provider: LLMProvider):
        self.name = name
        self.instructions = instructions
        self.llm = llm_provider
        self.skills: Dict[str, BaseSkill] = {}
        self.memory: List[Dict[str, str]] = [
            {"role": "system", "content": instructions}
        ]

    def register_skill(self, skill: BaseSkill):
        """Registra dinámicamente una nueva habilidad en el inventario del agente."""
        skill_name = skill.definition["function"]["name"]
        self.skills[skill_name] = skill
        print(f"[{self.name}] Skill registrada con éxito: {skill_name}")

    def _get_tools_definitions(self) -> List[Dict[str, Any]]:
        """Compila las definiciones de todas las skills registradas."""
        return [skill.definition for skill in self.skills.values()]

    def run(self, user_message: str) -> str:
        """Ciclo de razonamiento y ejecución del agente (Reasoning-Action Loop)."""
        self.memory.append({"role": "user", "content": user_message})
        
        tools = self._get_tools_definitions()
        
        # Primera llamada al LLM para evaluar la intención y determinar si requiere herramientas
        response = self.llm.generate(messages=self.memory, tools=tools if tools else None)
        
        # En una integración real con OpenAI API:
        # Se verifica si 'response.tool_calls' no es nulo y se ejecuta recursivamente.
        # A continuación, simulamos la decisión de usar una herramienta si la consulta lo amerita.
        
        if "buscar" in user_message.lower() and "web_search" in self.skills:
            # Simulación de ruteo automático a la Skill de Búsqueda
            search_skill = self.skills["web_search"]
            result = search_skill.execute(query=user_message)
            self.memory.append({"role": "assistant", "content": f"He usado la herramienta de búsqueda. {result}"})
            return f"[{self.name}]: {result}"
            
        elif "calcular" in user_message.lower() and "execute_code" in self.skills:
            # Simulación de ruteo automático a la Skill de Ejecución de Código
            code_skill = self.skills["execute_code"]
            # Extraemos una operación simple para el ejemplo
            result = code_skill.execute(expression="2 * 3.1416 * 10")
            self.memory.append({"role": "assistant", "content": f"He calculado la expresión. {result}"})
            return f"[{self.name}]: {result}"

        # Respuesta conversacional por defecto
        reply = "Entendido. No he necesitado utilizar herramientas externas para responder a tu solicitud."
        self.memory.append({"role": "assistant", "content": reply})
        return f"[{self.name}]: {reply}"
```

### 🚀 Ejecución e Integración (`main.py`)
El punto de entrada unifica la configuración de las capas, registra dinámicamente las habilidades en el agente y ejecuta las pruebas de comportamiento.

```python
from config import LLMProvider
from skills import WebSearchSkill, CodeExecutorSkill
from agent import CustomAgent

def main():
    print("=== Inicializando Sistema Agéntico de Pruebas ===")
    
    # 1. Inicializar Proveedor LLM
    llm = LLMProvider(model="gpt-4o-mini")
    
    # 2. Configurar el Agente Personalizado con directrices claras
    agent_instructions = (
        "Eres un Asistente Técnico Avanzado para infraestructuras críticas. "
        "Usa herramientas solo cuando sea estrictamente necesario para dar respuestas precisas."
    )
    support_agent = CustomAgent(
        name="TechOps-Agent",
        instructions=agent_instructions,
        llm_provider=llm
    )
    
    # 3. Registrar de forma dinámica las Skills diseñadas
    support_agent.register_skill(WebSearchSkill())
    support_agent.register_skill(CodeExecutorSkill())
    
    print("\n--- Inicio de Interacción ---")
    
    # Prueba 1: Solicitar información externa (Activa WebSearchSkill)
    print("\nUser: Por favor, busca el estado actual de los enlaces de fibra en Centroamérica.")
    response_1 = support_agent.run("buscar el estado de los enlaces de fibra")
    print(response_1)
    
    # Prueba 2: Solicitar un cálculo complejo (Activa CodeExecutorSkill)
    print("\nUser: Necesito calcular la circunferencia de un nodo con radio de 10 metros.")
    response_2 = support_agent.run("calcular la circunferencia")
    print(response_2)

if __name__ == "__main__":
    main()
```

---

## 📈 Criterios de Diseño de Software Aplicados

El diseño final cumple estrictamente con principios fundamentales de ingeniería de software:

* **Principio de Responsabilidad Única (Single Responsibility Principle - SRP):** Cada clase `Skill` tiene una única razón para cambiar (ej. actualizar una API de búsqueda externa o cambiar las políticas de seguridad de ejecución de código).
* **Principio de Abierto/Cerrado (Open/Closed Principle - OCP):** Puedes añadir capacidades infinitas (acceso a bases de datos, APIs de monitoreo de red, Slack, etc.) heredando de la interfaz base `BaseSkill` y registrándola con `register_skill()`, sin necesidad de alterar la lógica central del `CustomAgent`.
* **Desacoplamiento de la Plataforma:** El agente se desliga de una arquitectura rígida. Toda la abstracción técnica de integración, tokens y manejo del LLM se encapsula en la clase `LLMProvider`.

---

## ⚙️ Guía de Uso Rápido

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/nombre-repositorio.git
   cd nombre-repositorio
   ```

2. **Ejecutar el sistema de pruebas:**
   ```bash
   python main.py
   ```
