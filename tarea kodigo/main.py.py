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