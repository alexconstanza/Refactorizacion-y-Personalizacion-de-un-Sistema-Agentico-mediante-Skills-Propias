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