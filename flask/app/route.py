from flask import redirect, url_for

from controllers import main

# Importar os controllers registra as rotas no blueprint principal.
from controllers import auth_controller
from controllers import agenda_controller
from controllers import equipment_controller
from controllers import home_controller
from controllers import report_controller
from controllers import reservation_controller
from controllers import user_controller


@main.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="img/unimed3.png"))
