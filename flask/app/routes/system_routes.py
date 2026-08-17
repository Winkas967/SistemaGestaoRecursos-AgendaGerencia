from flask import Blueprint, jsonify

#importa a conexao mariaDB
from database.connection import get_db_connection

#cria o grupo de rotas do sistema
system_bp = Blueprint(
    "system",
    __name__,
)

#verifica se a aplicacao e o banco estao funcionando
@system_bp.route("/health", methods=["GET"])
def health():
    connection = None
    cursor = None
    
    try:
        #abre a conexao
        connection, cursor = get_db_connection()
        
        #executa uma consulta simples
        cursor.execute("SELECT 1 AS database_ok")
        
        #busca o resultado da consulta
        result = cursor.fetchone()
        
        #retorna o estado saudavel
        return jsonify({
            "status": "ok",
            "database": result["database_ok"] == 1,
        }),200
    
    except Exception:
        #retorna indisponivel sem expor o erro interno
        return jsonify({
            "status": "error",
            "database": False,
        }), 503
        
    finally:
        if cursor:
            cursor.close()
            
        if connection:
            connection.close()