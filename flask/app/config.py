import os

#contem as configuracoes gerais da aplicacao
class Config:
    #define a chave usada para proteger a sessao
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    #define o tamanho maximo dos arquivos enviados
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    
    #impede o js de acessar o cookie da sessao
    SESSION_COOKIE_HTTPONLY = True
    
    #reduz o envio de cookie em requisicoes externas
    SESSION_COOKIE_SAMESITE = "Lax"
    
    #ativa cookie seguro quando o servidor usa HTTPS
    SESSION_COOKIE_SECURE = os.getenv(
        "SESSION_COOKIE_SECURE",
        "false",
    ).lower() in {"1", "true", "sim", "on"}
    
    #define a pasta externa usada para armazenar arquivos
    UPLOAD_ROOT = os.getenv("UPLOAD_ROOT")