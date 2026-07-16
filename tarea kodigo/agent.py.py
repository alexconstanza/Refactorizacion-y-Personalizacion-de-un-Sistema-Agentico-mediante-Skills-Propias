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