from database.connection import get_db_connection



#representa uma ata retornada pelo banco
class Minute:
    def __init__(
        self,
        numero_ata,
        data_reuniao,
        tipo_ata_id,
        pauta,
        participantes,
        id=None,
        arquivo_id=None,
        criado_por_id=None,
        criado_em=None,
        atualizado_em=None,
        tipo_ata_nome=None,
        nome_original=None,
        nome_armazenado=None,
        caminho_relativo=None,
        mime_type=None,
        tamanho_bytes=None,
    ):
        self.id = id
        self.numero_ata = numero_ata
        self.data_reuniao = data_reuniao
        self.tipo_ata_id = tipo_ata_id
        self.tipo_ata_nome = tipo_ata_nome
        self.pauta = pauta
        self.participantes = participantes
        self.arquivo_id = arquivo_id
        self.nome_original = nome_original
        self.nome_armazenado = nome_armazenado
        self.caminho_relativo = caminho_relativo
        self.mime_type = mime_type
        self.tamanho_bytes = tamanho_bytes
        self.criado_por_id = criado_por_id
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        
        
#contem as consultas da tabela atas_reuniao
class MinuteModel:
    
    #monta o trecho FROM/JOIN/WHERE reutilizado pela listagem e pela contagem,
    #aplicando os filtros de ano/tipo/busca (paginacao no servidor)
    @staticmethod
    def _build_list_filter(year=None, type_id=None, search=None):
        where_clauses = []
        parameters = []

        if year:
            where_clauses.append("YEAR(ar.data_reuniao) = %s")
            parameters.append(year)

        if type_id:
            where_clauses.append("ar.tipo_ata_id = %s")
            parameters.append(type_id)

        if search:
            where_clauses.append("""(
                ar.numero_ata LIKE %s
                OR ta.nome LIKE %s
                OR ar.pauta LIKE %s
                OR ar.participantes LIKE %s
                OR a.nome_original LIKE %s
            )""")
            termo = f"%{search}%"
            parameters.extend([termo, termo, termo, termo, termo])

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        base_query = f"""
            FROM atas_reuniao ar
            INNER JOIN tipos_ata ta
                ON ta.id = ar.tipo_ata_id
            LEFT JOIN arquivos a
                ON a.id = ar.arquivo_id
            {where_sql}
        """

        return base_query, parameters


    #lista as atas com filtros de ano/tipo/busca, ordenacao e paginacao no servidor
    @staticmethod
    def get_all(year=None, type_id=None, search=None, order="recentes", limit=None, offset=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = MinuteModel._build_list_filter(year, type_id, search)

            direcao = "ASC" if order == "antigas" else "DESC"

            select_query = f"""
                SELECT
                    ar.id,
                    ar.numero_ata,
                    ar.data_reuniao,
                    ar.tipo_ata_id,
                    ta.nome AS tipo_ata_nome,
                    ar.pauta,
                    ar.participantes,
                    ar.arquivo_id,
                    ar.criado_por_id,
                    ar.criado_em,
                    ar.atualizado_em,
                    a.nome_original,
                    a.nome_armazenado,
                    a.caminho_relativo,
                    a.mime_type,
                    a.tamanho_bytes
                {base_query}
                ORDER BY ar.data_reuniao {direcao}, ar.id {direcao}
            """

            query_parameters = list(parameters)

            if limit is not None:
                select_query += " LIMIT %s OFFSET %s"
                query_parameters.extend([limit, offset or 0])

            cursor.execute(select_query, tuple(query_parameters))

            return [
                Minute(**record)
                for record in cursor.fetchall()
            ]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #conta quantas atas atendem aos mesmos filtros de get_all, para a paginacao
    @staticmethod
    def count_all(year=None, type_id=None, search=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            base_query, parameters = MinuteModel._build_list_filter(year, type_id, search)

            cursor.execute(f"SELECT COUNT(*) AS total {base_query}", tuple(parameters))

            return cursor.fetchone()["total"]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()


    #retorna os agregados globais (anos existentes, total e ultima atualizacao),
    #independentes dos filtros/paginacao — usados no cabecalho da tela de atas
    @staticmethod
    def get_global_stats():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT DISTINCT YEAR(data_reuniao) AS ano
                FROM atas_reuniao
                WHERE data_reuniao IS NOT NULL
                ORDER BY ano
            """)
            anos = [row["ano"] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    MAX(GREATEST(COALESCE(atualizado_em, criado_em), COALESCE(criado_em, atualizado_em))) AS ultima_atualizacao
                FROM atas_reuniao
            """)
            resumo = cursor.fetchone()

            return {
                "anos": anos,
                "total": resumo["total"] if resumo else 0,
                "ultima_atualizacao": resumo["ultima_atualizacao"] if resumo else None,
            }

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
                
    #busca uma ata pelo id
    @staticmethod
    def get_by_id(minute_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    ar.id,
                    ar.numero_ata,
                    ar.data_reuniao,
                    ar.tipo_ata_id,
                    ta.nome AS tipo_ata_nome,
                    ar.pauta,
                    ar.participantes,
                    ar.arquivo_id,
                    ar.criado_por_id,
                    ar.criado_em,
                    ar.atualizado_em,
                    a.nome_original,
                    a.nome_armazenado,
                    a.caminho_relativo,
                    a.mime_type,
                    a.tamanho_bytes
                FROM atas_reuniao ar
                INNER JOIN tipos_ata ta
                    ON ta.id = ar.tipo_ata_id
                LEFT JOIN arquivos a
                    ON a.id = ar.arquivo_id
                WHERE ar.id = %s
                LIMIT 1
            """, (minute_id,))
            
            record = cursor.fetchone()
            
            return Minute(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca um tipo de ata pelo nome
    @staticmethod
    def get_type_by_name(type_name):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    nome,
                    ativo
                FROM tipos_ata
                WHERE nome = %s
                AND ativo = TRUE
                LIMIT 1
            """, (type_name,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #cadastra uma ata
    @staticmethod
    def create(minute):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO atas_reuniao (
                    numero_ata,
                    data_reuniao,
                    tipo_ata_id,
                    pauta,
                    participantes,
                    arquivo_id,
                    criado_por_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                minute.numero_ata,
                minute.data_reuniao,
                minute.tipo_ata_id,
                minute.pauta,
                minute.participantes,
                minute.arquivo_id,
                minute.criado_por_id,
            ))
    
            minute_id = cursor.lastrowid
            connection.commit()
            
            return minute_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #exclui uma ata
    @staticmethod
    def delete(minute_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                DELETE FROM atas_reuniao
                WHERE id = %s
            """, (minute_id,))
            
            deleted = cursor.rowcount > 0
            connection.commit()
            
            return deleted
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
                