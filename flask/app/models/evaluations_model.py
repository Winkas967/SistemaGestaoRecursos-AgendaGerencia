from database.connection import get_db_connection

#representa uma avaliacao vinculada a um prestador
class Evaluation:
    def __init__(
        self,
        prestador_id,
        ano_referencia,
        iniciado_por_id=None,
        id=None,
        etapa_atual="termo_adesao",
        status="em_andamento",
        iniciado_em=None,
        concluido_em=None,
        atualizado_em=None,
    ):
        self.id = id
        self.prestador_id = prestador_id
        self.ano_referencia = ano_referencia
        self.etapa_atual = etapa_atual
        self.status = status
        self.iniciado_por_id = iniciado_por_id
        self.iniciado_em = iniciado_em
        self.concluido_em = concluido_em
        self.atualizado_em = atualizado_em
        

#contem as consultas da tabela de avaliações
class EvaluationModel:
    
    #lista todas as avaliacoes com os dados do prestador
    @staticmethod
    def get_all():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    av.id,
                    av.prestador_id,
                    av.ano_referencia,
                    p.nome AS prestador_nome,
                    p.categoria_id,
                    cp.nome AS categoria_nome,
                    cp.slug AS categoria_slug,
                    av.etapa_atual,
                    av.status,
                    av.iniciado_por_id,
                    av.iniciado_em,
                    av.concluido_em,
                    av.atualizado_em
                FROM avaliacoes_prestador av
                INNER JOIN prestadores p
                    ON p.id = av.prestador_id
                INNER JOIN categorias_prestador cp
                    ON cp.id = p.categoria_id
                ORDER BY
                    COALESCE(av.atualizado_em, av.iniciado_em) DESC,
                    av.id DESC
            """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca uma avaliacao pelo identificador
    @staticmethod
    def get_by_id(evaluation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    av.id,
                    av.prestador_id,
                    av.ano_referencia,
                    p.nome AS prestador_nome,
                    p.categoria_id,
                    cp.nome AS categoria_nome,
                    cp.slug AS categoria_slug,
                    av.etapa_atual,
                    av.status,
                    av.iniciado_por_id,
                    av.iniciado_em,
                    av.concluido_em,
                    av.atualizado_em
                FROM avaliacoes_prestador av
                INNER JOIN prestadores p
                    ON p.id = av.prestador_id
                INNER JOIN categorias_prestador cp
                    ON cp.id = p.categoria_id
                WHERE av.id = %s
            """, (evaluation_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #busca a avaliacao em andamento de um prestador
    @staticmethod
    def get_active_by_provider(provider_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                SELECT
                    id,
                    prestador_id,
                    ano_referencia,
                    etapa_atual,
                    status,
                    iniciado_por_id,
                    iniciado_em,
                    concluido_em,
                    atualizado_em
                FROM avaliacoes_prestador
                WHERE prestador_id = %s
                  AND status = 'em_andamento'
                ORDER BY id DESC
                LIMIT 1
            """, (provider_id,))
            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #cria uma avaliacao
    @staticmethod
    def create(evaluation):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO avaliacoes_prestador (
                    prestador_id,
                    ano_referencia,
                    etapa_atual,
                    status,
                    iniciado_por_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                evaluation.prestador_id,
                evaluation.ano_referencia,
                evaluation.etapa_atual,
                evaluation.status,
                evaluation.iniciado_por_id,
            ))
            
            evaluation_id = cursor.lastrowid
            connection.commit()
            
            return evaluation_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
                
                
    #atualiza a etapa atual de uma avaliacao
    @staticmethod
    def update_stage(evaluation_id, stage):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
            UPDATE avaliacoes_prestador
            SET etapa_atual = %s
            WHERE id = %s
              AND status = 'em_andamento'
            """, (
            stage,
            evaluation_id,
            ))

            updated = cursor.rowcount > 0
            connection.commit()
        
            return updated
    
        except Exception:
            if connection:
                connection.rollback()
                
            raise
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
