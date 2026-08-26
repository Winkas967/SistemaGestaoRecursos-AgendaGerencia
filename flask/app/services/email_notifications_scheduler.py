import os
import threading
from time import sleep

from services.email_notifications_service import EmailNotificationsService


_scheduler_lock = threading.Lock()
_scheduler_started = False


# Inicia uma única rotina de avisos por processo da aplicação
def start_email_notifications_scheduler(app):
    global _scheduler_started
    enabled = str(os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true")).lower() in {
        "1", "true", "sim", "on"
    }
    if not enabled:
        return

    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    interval = max(300, int(os.getenv("EMAIL_NOTIFICATIONS_INTERVAL_SECONDS", "3600")))

    def worker():
        while True:
            try:
                result = EmailNotificationsService.send_due_notifications()
                app.logger.info("Verificação de avisos de documentação concluída: %s", result)
            except Exception:
                app.logger.exception("Falha ao verificar avisos de documentação.")
            sleep(interval)

    threading.Thread(
        target=worker,
        name="document-email-notifications",
        daemon=True,
    ).start()
