import yaml
from autogen import UserProxyAgent, GroupChat, GroupChatManager
from agents.agentErrX import agentErrX
from agents.agentWapSendr import agentWapSendr
from agents.agentExplainr import agentExplainr
from agents.agentGraphor import agentGraphor
from agents.agentRAG3DSanalyzer import agentRAG3DSanalyzer
from config.llm import llm_config_groq
from vector_store import build_vector_store, retrieve_similar, is_index_built

class CustomGroupChatManager(GroupChatManager):
    def select_speaker(self, last_message, groupchat):
        content = last_message.get("content", "").strip()
        sender = last_message.get("name")
        print(f"[DEBUG] Último mensaje de {sender}: {content}")

        if sender == "Dispatcher":
            if content == "agentErrX":
                return "agentErrX"
            elif content == "agentExplainr":
                return "agentExplainr"
            elif content == "agentGraphor":
                return "agentGraphor"
            elif content == "agentWapSendr":
                return "agentWapSendr"
            elif content == "agentRAG3DSanalyzer":
                return "agentRAG3DSanalyzer"
            return None  # Evita que Dispatcher hable

        # Aquí el chequeo clave para llamar a agentWapSendr solo si error es crítico
        if sender == "agentErrX":
            # Puedes afinar este filtro con tu criterio o con expresiones regulares
            keywords_criticos = ["error crítico", "fallo grave", "error 500", "caída", "excepción crítica", "urgente"]
            if any(k in content.lower() for k in keywords_criticos):
                print("[DEBUG] Error crítico detectado. Llamando a agentWapSendr...")
                return "agentWapSendr"
            else:
                return None  # No sigue la cadena, termina aquí
            
        if sender in ["agentErrX", "agentExplainr", "agentGraphor", "agentWapSendr", "agentRAG3DSanalyzer"]:
            return None  # Responder solo una vez

        return super().select_speaker(last_message, groupchat)

    def is_termination_msg(self, message):
        content = message.get("content", "").strip().lower()
        if content == "" or \
           "no hay más consultas" in content or \
           "listo para intervenir" in content or \
           "no hay más preguntas" in content or \
           "flujo terminado" in content:
            return True
        return super().is_termination_msg(message)

    def run(self, *args, **kwargs):
        # Evita limpiar mensajes para mantener contexto
        if hasattr(self.groupchat, "messages") and self.groupchat.messages is not None:
            pass  # No limpiar nada aquí
        return super().run(*args, **kwargs)

with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)
    
dispatcher = UserProxyAgent(
    name="Dispatcher",
    human_input_mode="ALWAYS",
    system_message=SYSTEM_MESSAGES["dispatcher"],   
    llm_config=llm_config_groq,
    code_execution_config={"use_docker": False}
)

group_chat = GroupChat(
    agents=[dispatcher, agentErrX, agentExplainr, agentGraphor, agentWapSendr, agentRAG3DSanalyzer],
    messages=[],
    max_round=2,  # solo una interacción controlada
    speaker_selection_method="auto",
    select_speaker_auto_llm_config=llm_config_groq
)

if not is_index_built():
    print("No se encontró índice, construyendo vector store...")
    build_vector_store()


manager = CustomGroupChatManager(groupchat=group_chat)

print("💬 MCP Activo. Escribe tu consulta (escribe 'salir' para terminar):\n")

while True:
    query = input("👤 Tú: ")
    if query.strip().lower() == "salir":
        print("Sesión finalizada.")
        break

    dispatcher.initiate_chat(manager, message=query)

    #Dejar que el manager corra el flujo conversacional
    manager.run()

    # Mostrar respuesta
    print("\n Respuesta:")
    for msg in group_chat.messages:
        sender = msg.get("name") or msg.get("role") or msg.get("sender", "Unknown")
        content = msg.get("content", "").strip()
        if content:
            print(f"{sender}: {content}")
    print("-" * 60)

#### .\venv\Scripts\Activate.ps1 ..python main.py
# terminar rag gcp .. solucionando chromadb
# falta que por medio de IA se asistan entre ellos, siempre vuelvan a dispatcher y el llame a otro si es necesario
# dockerizar
# agregar potencia de arquitectura..  logs, db vetor, etc..
# generar diagrama de mi arquitectura mcp
###