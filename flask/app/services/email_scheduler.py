import threading

from services.email_notifications import enviar_avisos_documentos_vencimento


INTERVALO_VERIFICACAO_SEGUNDOS = 60 * 60
_agendador_iniciado = False
_trava_agendador = threading.Lock()


def iniciar_agendador_email(app):
    global _agendador_iniciado

    with _trava_agendador:
        if _agendador_iniciado:
            return
        _agendador_iniciado = True

    def executar():
        while True:
            try:
                with app.app_context():
                    enviar_avisos_documentos_vencimento()
            except Exception:
                app.logger.exception("Falha ao verificar avisos de vencimento por e-mail.")

            threading.Event().wait(INTERVALO_VERIFICACAO_SEGUNDOS)

    thread = threading.Thread(
        target=executar,
        name="avisos-documentacao-email",
        daemon=True,
    )
    thread.start()
