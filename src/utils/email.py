import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_summary_email(start_dt,duration_seconds,captured: list[dict],errors):
    """
    Envia um e-mail com:
     - Data/hora de início
     - Tempo total de execução
     - Lista de IDs capturados
     - Erros encontrados
    """
    # Formata data de início
    run_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    # Formata duração em HH:MM:SS
    hrs, rem = divmod(duration_seconds, 3600)
    mins, secs = divmod(rem, 60)
    duration_str = f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}"

    # Monta o corpo do e-mail
    body_lines = [
        f"📅 Data de início do scraping: {run_dt_str}",
        f"🕒 Tempo total de execução: {duration_str}",
        "",
        "✅ IDs capturados:"
    ]
    if captured:
        for p in captured:
            body_lines.append(
                f"  • {p['id']} — {p['name']} ({p['exam_date']})"
            )
    else:
        body_lines.append("  (nenhum paciente)")

    body_lines += ["", "⚠️ Erros encontrados:"]
    if errors:
        body_lines += [f"  • {err}" for err in errors]
    else:
        body_lines.append("  (não houve erros)")

    content = "\n".join(body_lines)

    # Carrega configurações SMTP do .env
    host      = os.getenv("SMTP_HOST")
    port      = int(os.getenv("SMTP_PORT", 587))
    user      = os.getenv("SMTP_USER")
    pwd       = os.getenv("SMTP_PASS")
    from_addr = os.getenv("EMAIL_FROM")
    to_addrs  = os.getenv("EMAIL_TO", "").split(",")

    msg = EmailMessage()
    msg["From"]    = from_addr
    msg["To"]      = ", ".join(to_addrs)
    msg["Subject"] = os.getenv("EMAIL_SUBJECT", "[Scraping] Resumo de Execução")
    msg.set_content(content)

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, pwd)
        smtp.send_message(msg)
