import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sib_api_v3_sdk.models import SendSmtpEmail
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)


load_dotenv()

API_KEY      = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME  = os.getenv("SENDER_NAME")
TO_EMAIL     = os.getenv("EMAIL_TO")
TO_NAME      = os.getenv("EMAIL_TO_NAME")

def send_via_brevo(html_content: str, subject: str):
    """
    Envia um e-mail com o conteúdo HTML fornecido.
    """
    # Configura a API do Brevo
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = SendSmtpEmail(
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        to=[{"email": TO_EMAIL, "name": TO_NAME}],
        subject=subject,
        html_content=html_content
    )

    try:
        # Envia o e-mail
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("E-mail enviado com sucesso:", api_response)
    except ApiException as e:
        logger.exception("Erro ao enviar e-mail:", e, exc_info=False)