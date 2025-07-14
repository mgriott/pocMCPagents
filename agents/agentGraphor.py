import yaml 
from autogen import ConversableAgent
from config.groq_wrapper import run_groq_chat
from config.llm import llm_config_groq

# Carga el contexto del archivo YAML
with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)


def reply(agent, messages, sender, config):
    return True, run_groq_chat(agent.system_message, messages[-1]["content"]) # run_groq_chat llama a un modelo de lenguaje (LLM) alojado en Groq

# Agente configurado para usar LLM
agentGraphor = ConversableAgent(
    name="agentGraphor",
    system_message=SYSTEM_MESSAGES["agentGraphor"],
    llm_config=llm_config_groq,
    code_execution_config=False,
    human_input_mode="NEVER",  #Permite que el agente responda automáticamente
    is_termination_msg=lambda x: x.get("content", "").strip().lower() in ["flujo terminado.", "flujo terminado"]
)

#agentGraphor implementa su lógica de respuesta use IA generativa
agentGraphor.reply = reply 
