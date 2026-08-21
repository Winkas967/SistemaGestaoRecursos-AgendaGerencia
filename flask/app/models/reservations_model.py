from database.connection import get_db_connection

#representa uma reserva retornada pelo banco
class Reservation:
    def __init__(
        self,
        recurso_id,
        data_reserva,
        hora_inicio,
        id=None,
        usuario_id=None,
        setor_id=None,
        responsavel=None,
        motivo=None,
        data_volta=None,
        hora_fim=None,
        observacao=None,
        viagem=False,
        status="reservado",
        criado_em=None,
        atualizado_em=None,
        recurso_nome=None,
        usuario_nome=None,
        setor_nome=None
    ):
        self.id = id
        self.recurso_id = recurso_id
        self.recurso_nome = recurso_nome
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.setor_id = setor_id
        self.setor_nome = setor_nome
        self.responsavel = responsavel
        self.motivo = motivo
        self.data_reserva = data_reserva
        self.data_volta = data_volta
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.observacao = observacao
        self.viagem = viagem
        self.status = status
        self.criado_em = criado_em
        self.atualizado_em = atualizado_em
        
    #cenverte em dicionario
    def to_dict(self):
        return {
            "id": self.id,
            "recurso_id": self.recurso_id,
            "recurso_nome": self.recurso_nome,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario_nome,
            "setor_id": self.setor_id,
            "setor_nome": self.setor_nome,
            "responsavel": self.responsavel,
            "motivo": self.motivo,
            "data_reserva": (
                str(self.data_reserva)
                if self.data_reserva
                else None
            ),
            "data_volta": (
                str(self.data_volta)
                if self.data_volta
                else None
            ),
            "hora_inicio": (
                str(self.hora_inicio)
                if self.hora_inicio
                else None
            ),
            "hora_fim": (
                str(self.hora_fim)
                if self.hora_fim
                else None
            ),
            "observacao": self.observacao,
            "viagem": self.viagem,
            "status": self.status,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }
        
#contem as consultas da tabela reservas
class ReservationModel:
    #busca pelo id
    @staticmethod
    def get_by_id(reservation_id):
        connection = None   
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT
                                rv.id,
                                rv.recurso_id,
                                r.nome AS recurso_nome,
                                rv.usuario_id,
                                u.usuario AS usuario_nome,
                                rv.setor_id,
                                s.nome AS setor_nome,
                                rv.responsavel,
                                rv.motivo,
                                rv.data_reserva,
                                rv.data_volta,
                                rv.hora_inicio,
                                rv.hora_fim,
                                rv.observacao,
                                rv.viagem,
                                rv.status,
                                rv.criado_em,
                                rv.atualizado_em
                            FROM reservas rv
                            INNER JOIN recursos r
                                ON r.id = rv.recurso_id
                            LEFT JOIN usuarios u
                                ON u.id = rv.usuario_id
                            LEFT JOIN setores s
                                ON s.id = rv.setor_id
                            WHERE rv.id = %s
                            LIMIT 1
                           """, (reservation_id,),
                        )
            
            record = cursor.fetchone()
            
            return Reservation(**record) if record else None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #lista as reservas de um recurso
    @staticmethod
    def get_by_resource(resource_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT
                                rv.id,
                                rv.recurso_id,
                                r.nome AS recurso_nome,
                                rv.usuario_id,
                                u.usuario AS usuario_nome,
                                rv.setor_id,
                                s.nome AS setor_nome,
                                rv.responsavel,
                                rv.motivo,
                                rv.data_reserva,
                                rv.data_volta,
                                rv.hora_inicio,
                                rv.hora_fim,
                                rv.observacao,
                                rv.viagem,
                                rv.status,
                                rv.criado_em,
                                rv.atualizado_em
                            FROM reservas rv
                            INNER JOIN recursos r
                                ON r.id = rv.recurso_id
                            LEFT JOIN usuarios u
                                ON u.id = rv.usuario_id
                            LEFT JOIN setores s
                                ON s.id = rv.setor_id
                            WHERE rv.recurso_id = %s
                            AND rv.status NOT IN ('cancelado')
                            ORDER BY rv.data_reserva, rv.hora_inicio
                            """, (resource_id,),
            )
        
            return [
                Reservation(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #cadastra uma nova reserva
    @staticmethod
    def create(reservation):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        INSERT INTO reservas (
                            recurso_id,
                            usuario_id,
                            setor_id,
                            responsavel,
                            motivo,
                            data_reserva,
                            data_volta,
                            hora_inicio,
                            hora_fim,
                            observacao,
                            viagem,
                            status
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            reservation.recurso_id,
                            reservation.usuario_id,
                            reservation.setor_id,
                            reservation.responsavel,
                            reservation.motivo,
                            reservation.data_reserva,
                            reservation.data_volta,
                            reservation.hora_inicio,
                            reservation.hora_fim,
                            reservation.observacao,
                            reservation.viagem,
                            reservation.status,
                        ),
                )
            
            reservation_id = cursor.lastrowid
            connection.commit()
            
            return reservation_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #verifica conflito entre reservas do mesmo recurso
    @staticmethod
    def has_conflict(
        resource_id,
        start_date,
        end_date,
        start_time,
        end_time,
        ignored_reservation_id=None,
    ):
        
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                            SELECT rv.id
                            FROM reservas rv
                            WHERE rv.recurso_id = %s
                            AND rv.status NOT IN (
                                'cancelado',
                                'devolvido'
                            )
                            AND TIMESTAMP(
                                rv.data_reserva,
                                rv.hora_inicio
                            ) < TIMESTAMP(%s, %s)
                            AND TIMESTAMP(
                                COALESCE(
                                    rv.data_volta,
                                    rv.data_reserva
                                ),
                                COALESCE(
                                    rv.hora_fim,
                                    '23:59:59'
                                )
                            ) > TIMESTAMP(%s, %s)
                            AND (
                                %s IS NULL
                                OR rv.id <> %s
                            )
                            LIMIT 1
                            """,
                            (
                                resource_id,
                                end_date,
                                end_time,
                                start_date,
                                start_time,
                                ignored_reservation_id,
                                ignored_reservation_id,
                            ),
            )
            
            return cursor.fetchone() is not None
        
        finally:
            if cursor: 
                cursor.close()
            
            if connection:
                connection.close()
            
            
    #lista as reservas exibidas na pagina inicial
    @staticmethod
    def get_for_home(user_id=None):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            query = """
                SELECT
                    rv.id,
                    rv.recurso_id,
                    r.nome AS recurso_nome,
                    rv.usuario_id,
                    u.usuario AS usuario_nome,
                    rv.setor_id,
                    s.nome AS setor_nome,
                    rv.responsavel,
                    rv.motivo,
                    rv.data_reserva,
                    rv.data_volta,
                    rv.hora_inicio,
                    rv.hora_fim,
                    rv.observacao,
                    rv.viagem,
                    rv.status,
                    rv.criado_em,
                    rv.atualizado_em
                FROM reservas rv
                INNER JOIN recursos r
                    ON r.id = rv.recurso_id
                LEFT JOIN usuarios u
                    ON u.id = rv.usuario_id
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
            """
            
            parameters = ()
            
            #filtra pelo usuario quando ele nao for admin
            if user_id is not None:
                query += """
                    AND rv.usuario_id = %s
                """
                
                
                parameters = (user_id,)
                
            query += """
                ORDER BY
                    rv.data_reserva DESC,
                    rv.hora_inicio DESC
            """
            
            cursor.execute(query, parameters)
            
            return [
                Reservation(**record)
                for record in cursor.fetchall()
            ]
            
        finally:
            if cursor:
                cursor.close()
            
            if connection:
                connection.close()
                
    #marca como reserva devolvida
    @staticmethod
    def mark_as_returned(reservation_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        UPDATE reservas
                        SET
                            status = 'devolvido',
                            atualizado_em = CURRENT_TIMESTAMP
                        WHERE id = %s
                        AND status IN ('reservado', 'em_uso')
                           """, (reservation_id,))
            
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