from database.connection import get_db_connection

#contem as consultas usadas nos relatorios
class ReportModel:
    
    #mostra os filtros usados nas consultas dos relatorios
    @staticmethod
    def build_filters(
        start_date=None,
        end_date=None,
        sector=None
    ):
        conditions = []
        parameters = []
        
        if start_date:
            conditions.append(
                "rv.data_reserva >= %s"
            )
            parameters.append(start_date)
            
        if end_date:
            conditions.append(
                "rv.data_reserva <= %s"
            )
            parameters.append(end_date)
            
        if sector:
            conditions.append(
                "LOWER(COALESCE(s.nome, '')) LIKE LOWER(%s)"
            )
            parameters.append(
                f"%{sector}%"
            )
            
        if not conditions:
            return "", ()
        
        sql = " AND " + " AND ".join(
            conditions
        )
        
        return sql, tuple(parameters)
    #agrupa as reservas pelo nome do recurso
    @staticmethod
    def get_reservations_by_resource(
        start_date=None,
        end_date=None,
        sector=None,
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector,
                )
            )

            query = f"""
                SELECT
                    r.nome AS label,
                    COUNT(rv.id) AS valor
                FROM reservas rv
                INNER JOIN recursos r
                    ON r.id = rv.recurso_id
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
                {filter_sql}
                GROUP BY
                    r.id,
                    r.nome
                ORDER BY valor DESC
            """

            cursor.execute(
                query,
                parameters,
            )
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas por setor
    @staticmethod
    def get_reservations_by_sector(
        start_date=None,
        end_date=None,
        sector=None
    ):
        
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector
                )
            )
            
            query = f"""
                SELECT
                    COALESCE(
                        s.nome,
                        'Sem setor'
                    ) AS label,
                    COUNT(rv.id) AS valor
                FROM reservas rv
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
                {filter_sql}
                GROUP BY
                    s.id,
                    s.nome
                ORDER BY valor DESC
            """

            cursor.execute(
                query,
                parameters,
            )
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas por status
    @staticmethod
    def get_reservations_by_status(
        start_date=None,
        end_date=None,
        sector=None,
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector
                )
            )
            
            query = f"""
                SELECT
                    rv.status AS label,
                    COUNT(rv.id) AS valor
                FROM reservas rv
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE 1 = 1
                {filter_sql}
                GROUP BY rv.status
                ORDER BY valor DESC
            """

            cursor.execute(
                query,
                parameters,
            )

            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas pelo responsavel
    @staticmethod
    def get_reservations_by_responsible(
        start_date=None,
        end_date=None,
        sector=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector
                )
            )
            
            query = f"""
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
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
                {filter_sql}
                GROUP BY label
                ORDER BY valor DESC
            """

            cursor.execute(
                query,
                parameters,
            )
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agrupa as reservas pela hora de inicio
    @staticmethod
    def get_reservation_by_hour(
        start_date=None,
        end_date=None,
        sector=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector,
                )
            )

            query = f"""
                SELECT
                    TIME_FORMAT(
                        rv.hora_inicio,
                        '%%H:00'
                    ) AS label,
                    COUNT(rv.id) AS valor
                FROM reservas rv
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
                {filter_sql}
                GROUP BY HOUR(rv.hora_inicio)
                ORDER BY HOUR(rv.hora_inicio)
            """

            cursor.execute(
                query,
                parameters,
            )
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #agora as reservas pela data
    @staticmethod
    def get_reservations_by_period(
        start_date=None,
        end_date=None,
        sector=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector,
                )
            )

            query = f"""
                SELECT
                    DATE_FORMAT(
                        rv.data_reserva,
                        '%%d/%%m/%%Y'
                    ) AS label,
                    COUNT(rv.id) AS valor
                FROM reservas rv
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE rv.status <> 'cancelado'
                {filter_sql}
                GROUP BY rv.data_reserva
                ORDER BY rv.data_reserva
            """

            cursor.execute(
                query,
                parameters,
            )
            
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
                
    #calcula os numeros gerais dos relatorios
    @staticmethod
    def get_summary(
        start_date=None,
        end_date=None,
        sector=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            filter_sql, parameters = (
                    ReportModel.build_filters(
                        start_date=start_date,
                        end_date=end_date,
                        sector=sector,
                    )
                )

            query = f"""
                    SELECT
                        SUM(
                            rv.status <> 'cancelado'
                        ) AS total,

                        SUM(
                            rv.status = 'reservado'
                        ) AS reservados,

                        SUM(
                            rv.status = 'em_uso'
                        ) AS em_uso,

                        SUM(
                            rv.status = 'devolvido'
                        ) AS devolvidos,

                        SUM(
                            rv.status = 'cancelado'
                        ) AS cancelados,

                        SUM(
                            rv.viagem = TRUE
                            AND rv.status <> 'cancelado'
                        ) AS viagens,

                        SUM(
                            rv.status IN (
                                'reservado',
                                'em_uso'
                            )
                            AND TIMESTAMP(
                                COALESCE(
                                    rv.data_volta,
                                    rv.data_reserva
                                ),
                                COALESCE(
                                    rv.hora_fim,
                                    '23:59:59'
                                )
                            ) < CURRENT_TIMESTAMP
                        ) AS atrasados,

                        COUNT(
                            DISTINCT CASE
                                WHEN rv.status <> 'cancelado'
                                THEN rv.data_reserva
                            END
                        ) AS dias_com_uso

                    FROM reservas rv
                    LEFT JOIN setores s
                        ON s.id = rv.setor_id
                    WHERE 1 = 1
                    {filter_sql}
                """

            cursor.execute(
                    query,
                    parameters,
                )

            
            return cursor.fetchone()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #busca as reservas detalhadas ao relatorio
    @staticmethod
    def get_reservation_details(
        start_date=None,
        end_date=None,
        sector=None,
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            #prepara os filtros da consulta
            filter_sql, parameters = (
                ReportModel.build_filters(
                    start_date=start_date,
                    end_date=end_date,
                    sector=sector
                )
            )
            
            # Monta a consulta das reservas
            query = f"""
                SELECT
                    rv.id,
                    DATE_FORMAT(
                        rv.data_reserva,
                        '%%d/%%m/%%Y'
                    ) AS data_reserva,
                    DATE_FORMAT(
                        rv.data_volta,
                        '%%d/%%m/%%Y'
                    ) AS data_volta,
                    TIME_FORMAT(
                        rv.hora_inicio,
                        '%%H:%%i'
                    ) AS hora_inicio,
                    TIME_FORMAT(
                        rv.hora_fim,
                        '%%H:%%i'
                    ) AS hora_fim,
                    r.nome AS recurso,
                    COALESCE(
                        NULLIF(rv.responsavel, ''),
                        u.usuario,
                        'Não informado'
                    ) AS responsavel,
                    COALESCE(
                        s.nome,
                        'Sem setor'
                    ) AS setor,
                    rv.motivo,
                    rv.observacao,
                    CASE
                        WHEN rv.viagem = TRUE
                        THEN 'Sim'
                        ELSE 'Não'
                    END AS viagem,
                    rv.status
                FROM reservas rv
                INNER JOIN recursos r
                    ON r.id = rv.recurso_id
                LEFT JOIN usuarios u
                    ON u.id = rv.usuario_id
                LEFT JOIN setores s
                    ON s.id = rv.setor_id
                WHERE 1 = 1
                {filter_sql}
                ORDER BY
                    rv.data_reserva DESC,
                    rv.hora_inicio DESC
            """

            # Executa a consulta
            cursor.execute(
                query,
                parameters,
            )


            #retorna todas as reservas
            return cursor.fetchall()
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
            