import yaml
from autogen import ConversableAgent
from config.groq_wrapper import run_groq_chat
from config.llm import llm_config_groq

with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)

agentErrX = ConversableAgent(
    name="agentErrX",
    system_message=SYSTEM_MESSAGES["agentExplainr"],
    llm_config=llm_config_groq,  # importante
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "").endswith("🛑")
)