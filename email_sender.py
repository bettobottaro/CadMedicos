import smtplib
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Tuple


class EmailSender:
    """Envio de e-mails pelo Gmail usando STARTTLS na porta 587."""

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USE_SSL = False
    REQUIRES_AUTH = True

    # Use "password" para autenticação com senha de app.
    # Use "oauth2" somente se o OAuth estiver configurado.
    AUTH_METHOD = "password"

    OAUTH_CREDENTIALS_FILE = ""
    OAUTH_TOKEN_FILE = ""

    def __init__(self, sender_email: str, sender_password: str = ""):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def _get_oauth_token(self):
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
        except ImportError:
            raise RuntimeError(
                "Dependências OAuth2 ausentes. Instale: "
                "google-auth==2.22.0 google-auth-oauthlib==1.0.0"
            )

        scopes = ["https://mail.google.com/"]

        token_file = (
            os.path.abspath(os.path.expanduser(self.OAUTH_TOKEN_FILE))
            if self.OAUTH_TOKEN_FILE
            else ""
        )

        credentials_file = (
            os.path.abspath(os.path.expanduser(self.OAUTH_CREDENTIALS_FILE))
            if self.OAUTH_CREDENTIALS_FILE
            else ""
        )

        creds = None

        if token_file and os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    token_file,
                    scopes
                )
            except Exception:
                creds = None

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            if not credentials_file or not os.path.exists(credentials_file):
                raise RuntimeError(
                    "Arquivo de credenciais OAuth2 não encontrado. "
                    "Configure o arquivo credentials.json."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                scopes
            )

            creds = flow.run_local_server(
                port=0,
                open_browser=True
            )

        if token_file:
            folder = os.path.dirname(token_file)

            if folder:
                os.makedirs(folder, exist_ok=True)

            with open(token_file, "w", encoding="utf-8") as token:
                token.write(creds.to_json())

        return creds.token

    def _oauth2_auth(self, server):
        token = self._get_oauth_token()

        auth_string = (
            "user={0}\x01auth=Bearer {1}\x01\x01"
            .format(self.sender_email, token)
        )

        auth_bytes = auth_string.encode("utf-8")
        encoded = base64.b64encode(auth_bytes).decode("ascii")

        code, response = server.docmd(
            "AUTH",
            "XOAUTH2 " + encoded
        )

        if code != 235:
            raise smtplib.SMTPAuthenticationError(
                code,
                response
            )

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachments: List[str] = None
    ) -> Tuple[bool, str]:

        try:
            message = MIMEMultipart()

            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject

            message.attach(
                MIMEText(body, "plain", "utf-8")
            )

            if attachments:
                for file_path in attachments:
                    if not os.path.exists(file_path):
                        return (
                            False,
                            "Arquivo não encontrado: {}".format(file_path)
                        )

                    self._attach_file(
                        message,
                        file_path
                    )

            # Porta 587: conexão SMTP normal, seguida de STARTTLS.
            # Não usar SMTP_SSL nesta configuração.
            with smtplib.SMTP(
                self.SMTP_SERVER,
                self.SMTP_PORT,
                timeout=30
            ) as server:

                server.ehlo()
                server.starttls()
                server.ehlo()

                if self.REQUIRES_AUTH:
                    if str(self.AUTH_METHOD).lower() == "oauth2":
                        self._oauth2_auth(server)
                    else:
                        server.login(
                            self.sender_email,
                            self.sender_password
                        )

                server.send_message(message)

            return True, "E-mail enviado com sucesso!"

        except smtplib.SMTPAuthenticationError as error:
            return (
                False,
                "Erro de autenticação SMTP: {}".format(error)
            )

        except smtplib.SMTPException as error:
            return (
                False,
                "Erro SMTP ao enviar e-mail: {}".format(error)
            )

        except Exception as error:
            return (
                False,
                "Erro inesperado: {}".format(error)
            )

    @staticmethod
    def _attach_file(
        message: MIMEMultipart,
        file_path: str
    ):
        with open(file_path, "rb") as attachment:
            part = MIMEBase(
                "application",
                "octet-stream"
            )

            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        filename = os.path.basename(file_path)

        part.add_header(
            "Content-Disposition",
            "attachment; filename={}".format(filename)
        )

        message.attach(part)