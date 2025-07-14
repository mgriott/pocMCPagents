import yaml
from autogen import ConversableAgent
from config.groq_wrapper import run_groq_chat
from config.llm import llm_config_groq

with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)

def reply(agent, messages, sender, config):
    return True, run_groq_chat(agent.system_message, messages[-1]["content"])

agentRAG3DSanalyzer = ConversableAgent(
    name="agentRAG3DSanalyzer",
    system_message=SYSTEM_MESSAGES["agentRAG3DSanalyzer"],
    llm_config=llm_config_groq,
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "").strip().lower() in [
        "flujo terminado.", "flujo terminado", "evento cerrado", "finalizo"
    ]
)
