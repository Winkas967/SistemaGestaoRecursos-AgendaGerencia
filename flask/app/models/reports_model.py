from database.connection import get_db_connection

#contem as consultas usadas nos relatorios
class ReportModel:
    
    #agrupa as reservas pelo nome do recurso
    @staticmethod
    def get_reservations_by_resource():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                           SELECT
                                r.nome AS label,
                                COUNT(rv.id) AS valor
                            FROM reservas rv
                            INNER JOIN recursos r
                                ON r.id = rv.recurso_id
                            WHERE rv.status <> 'cancelado'
                            GROUP BY
                                r.id,
                                r.nome
                            ORDER BY valor DESC
                           """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas por setor
    @staticmethod
    def get_reservations_by_sector():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            COALESCE(s.nome, 'Sem setor') AS label,
                            COUNT(rv.id) AS valor
                        FROM reservas rv
                        LEFT JOIN setores s
                            ON s.id = rv.setor_id
                        WHERE rv.status <> 'cancelado'
                        GROUP BY
                            s.id,
                            s.nome
                        ORDER BY valor DESC
                           """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas por status
    @staticmethod
    def get_reservations_by_status():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            rv.status AS label,
                            COUNT(rv.id) AS valor
                        FROM reservas rv
                        GROUP BY rv.status
                        ORDER BY valor DESC
                                """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas pelo responsavel
    @staticmethod
    def get_reservations_by_responsible():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            COALESCE(
                                NULLIF(rv.responsavel, ''),
                                u.usuario,
                                'Não informado'
                            ) AS label,
                            COUNT(rv.id) AS valor
                        FROM reservas rv
                        LEFT JOIN usuarios u
                            ON u.id = rv.usuario_id
                        WHERE rv.status <> 'cancelado'
                        GROUP BY label
                        ORDER BY valor DESC
                           """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close
                
                
    #agrupa as reservas pela hora de inicio
    @staticmethod
    def get_reservation_by_hour():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            TIME_FORMAT(
                                rv.hora_inicio,
                                '%H:00'
                            ) AS label,
                            COUNT(rv.id) AS valor
                        FROM reservas rv
                        WHERE rv.status <> 'cancelado'
                        GROUP BY HOUR(rv.hora_inicio)
                        ORDER BY HOUR(rv.hora_inicio)
                           """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agora as reservas pela data
    @staticmethod
    def get_reservations_by_period():
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            DATE_FORMAT(
                                rv.data_reserva,
                                '%d/%m/%Y'
                            ) AS label,
                            COUNT(rv.id) AS valor
                        FROM reservas rv
                        WHERE rv.status <> 'cancelado'
                        GROUP BY rv.data_reserva
                        ORDER BY rv.data_reserva
                           """)
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()