import yaml
import os
from autogen import ConversableAgent
from twilio.rest import Client
from config.groq_wrapper import run_groq_chat
from config.llm import llm_config_groq

# Leer el system_message desde YAML
with open("config/system_messages.yaml", "r", encoding="utf-8") as f:
    SYSTEM_MESSAGES = yaml.safe_load(f)

# Función para enviar WhatsApp con Twilio
def enviar_whatsapp(mensaje):
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        message = client.messages.create(
            body=mensaje,
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=os.getenv("DEST_WHATSAPP_NUMBER")
        )
        print(f"WhatsApp enviado. SID: {message.sid}")
        return "WhatsApp enviado correctamente."
    except Exception as e:
        print(f"Error al enviar WhatsApp: {e}")
        return f"Error al enviar WhatsApp: {e}"

# Función de respuesta personalizada del agente
def wap_reply(agent, messages, sender, config):
    user_input = messages[-1]["content"]

    # Prompt para que el LLM decida si enviar alerta o no
    decision_prompt = f"""Eres un agente que decide si se debe enviar una alerta urgente por WhatsApp según el siguiente mensaje del usuario: "{user_input}"
    Si el contenido representa un evento crítico (como errores 500, fallos en producción, amenazas, caídas de servicios, error critico, enviar, wasap), responde solo con la palabra: ENVIAR
    Si el contenido no amerita alerta (ej. cosas menores, warnings sin impacto, ideas generales), responde solo con la palabra: IGNORAR
    IMPORTANTE: Responde solo con ENVIAR o IGNORAR. No agregues explicaciones."""

    #IA Evaluación del modelo (solo devuelve 1 valor)
    decision = run_groq_chat(decision_prompt, user_input)
    decision = decision.strip().upper()

    if "IGNORAR" in decision:
        return True, "El agente determinó que no es necesario enviar WhatsApp."

    mensaje_alerta = (
        "Esto es una alerta automática detectada por IA. "
        "Se recomienda revisar lo siguiente:\n\n"
        f"{user_input}"
    )
    resultado = enviar_whatsapp(mensaje_alerta)
    return True, resultado

# Crear agente
agentWapSendr = ConversableAgent(
    name="agentWapSendr",
    system_message=SYSTEM_MESSAGES["agentWapSendr"],
    llm_config=llm_config_groq,
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "").endswith("🛑")
)

def trigger_whatsapp(sender):
    # Accede al último mensaje que recibió este agente
    last_msg = agentWapSendr.chat_messages.get(sender, [])[-1].get("content", "").lower()
    return any(k in last_msg for k in ["whatsapp", "avisar", "enviar"])

def shutdown():
    agentWapSendr.whatsapp_client.close()

#IA Esto hace que el agente “escuche” mensajes y aplique IA para decidir acciones.
agentWapSendr.register_reply(
    trigger=trigger_whatsapp,
    reply_func=wap_reply,
    config=llm_config_groq
)