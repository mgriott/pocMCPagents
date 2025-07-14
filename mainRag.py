import os
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
        #IA llama a la IA para decidir el agente que debe hablar según contexto
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

def preprocess_log_for_display(log_lines):
    return "\n".join(f"- {line}" for line in log_lines if line.strip())

def check_and_reindex_if_new_logs():
    import os
    import pickle

    logs_dir = "inputRag"
    current_logs = sorted(f for f in os.listdir(logs_dir) if f.endswith(".log"))

    if not os.path.exists("doc_store.pkl"):
        print("doc_store.pkl no existe. Reindexando...")
        build_vector_store()
        return

    with open("doc_store.pkl", "rb") as f:
        existing_docs = pickle.load(f)

    # Si hay logs nuevos (nombres distintos) o más líneas que antes, se reindexa
    existing_texts = set(existing_docs)
    all_lines = []
    for log_file in current_logs:
        with open(os.path.join(logs_dir, log_file), "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            all_lines.extend(lines)

    new_texts = set(all_lines)
    if not new_texts.issubset(existing_texts):
        print("Nuevos logs detectados. Reconstruyendo índice FAISS...")
        build_vector_store()
    else:
        print("No se detectan nuevos logs. Índice actual es válido.")


#recupera contexto para agente dispatcher
with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)
    
# Region #IA Mi bloque de código
dispatcher = UserProxyAgent( #Agente Dispatcher
    name="Dispatcher",
    human_input_mode="ALWAYS",
    system_message=SYSTEM_MESSAGES["dispatcher"],   
    llm_config=llm_config_groq,
    code_execution_config={"use_docker": False}
)

# se indica que la selección automática usa inteligencia para decidir quién responde
group_chat = GroupChat(
    agents=[dispatcher, agentErrX, agentExplainr, agentGraphor, agentWapSendr, agentRAG3DSanalyzer],
    messages=[],
    max_round=2,  # solo una interacción controlada
    speaker_selection_method="auto",
    select_speaker_auto_llm_config=llm_config_groq
)
# endregion

check_and_reindex_if_new_logs()

if not is_index_built():
    print("No se encontró índice, construyendo vector store...")
    build_vector_store()
else:
    print("Índice existente en Pesos semanticos. Continuando...")

manager = CustomGroupChatManager(groupchat=group_chat)


while True:
    query = input("👤 Tú: ").strip().lower()
    
    if query in ["salir", "exit", "quit"]:
        try:
            from agents import agentErrX, agentWapSendr, agentExplainr, agentGraphor, agentRAG3DSanalyzer
            agentWapSendr.shutdown()

            group_chat.messages.clear()
            print("Sesión finalizada correctamente.")
            os._exit(0) 

        except Exception as e:
            print(f"Error al apagar agentes: {e}")
    

    # Recuperar contexto antes de enviar al agente
    docs = retrieve_similar(query)
    contexto = preprocess_log_for_display(docs)
    if contexto.strip():
        query_con_contexto = f"Contexto del log:\n{contexto}\n\n Pregunta:\n{query}"
    else:
        query_con_contexto = query

    #query_con_contexto = f"Pregunta:\n{query}"

    dispatcher.initiate_chat(manager, message=query_con_contexto)
    manager.run()

    # Mostrar respuesta
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
# agregar arquitectura..  logs, db vetor, etc..
# generar diagrama de mi arquitectura mcp
###