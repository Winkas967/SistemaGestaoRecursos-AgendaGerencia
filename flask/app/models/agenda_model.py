from datetime import date, timedelta

from database.connection import get_db_connection

#representa um compromisso retornado pelo banco
class AgendaAppointment:
    def __init__(
        self,
        titulo,
        data,
        hora_inicio,
        id=None,
        hora_fim=None,
        responsavel=None,
        local=None,
        descricao=None,
        status="agendado",
        criado_por_id=None,
        criado_em=None,
        atualizado_em=None
    ):
        
        self.id = id
        self.titulo = titulo
        self.data = data
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.responsavel = responsavel
        self.local = local
        self.descricao = descricao
        self.status = status
        self.criado_em = criado_em
        self.criado_por_id = criado_por_id
        self.atualizado_em = atualizado_em
        
        
    #converte o compromisso para o formato utilizado pelo js
    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "data": str(self.data) if self.data else None,
            "horaInicio": (
                str(self.hora_inicio)[:5]
                if self.hora_inicio
                else None
            ),
            "horaFim": (
                str(self.hora_fim)[:5]
                if self.hora_fim
                else None
            ),
            "responsavel": self.responsavel,
            "local": self.local,
            "descricao": self.descricao,
            "status": self.status,
            "criadoPorId": self.criado_por_id,
            "criadoEm": self.criado_em,
            "atualizadoEm": self.atualizado_em
        }
        
#contem as consultas da tabela agenda_compromissos
class AgendaModel:
    
    #lista os compromissos; sem ano/mes retorna todos (usado pela exportacao em
    #pdf e por quem precisa do conjunto completo), com ano/mes retorna somente o
    #periodo informado — usado pela agenda (calendario), que busca so o mes visivel
    #calcula o intervalo de datas exibido na grade do calendario para um mes
    #(inclui os dias esmaecidos do mes anterior/seguinte que preenchem a grade),
    #replicando o calculo feito no front (renderCalendar)
    @staticmethod
    def _calendar_grid_range(year, month):
        first_of_month = date(year, month, 1)
        #getDay() do JS: domingo=0..sabado=6; date.weekday() do Python: segunda=0..domingo=6
        start_weekday = (first_of_month.weekday() + 1) % 7
        range_start = first_of_month - timedelta(days=start_weekday)

        next_month_first = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        days_in_month = (next_month_first - first_of_month).days

        cells_count = -(-(start_weekday + days_in_month) // 7) * 7
        range_end = range_start + timedelta(days=cells_count - 1)

        return range_start, range_end

    @staticmethod
    def get_all(year=None, month=None):
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            where_sql = ""
            parameters = []

            if year and month:
                range_start, range_end = AgendaModel._calendar_grid_range(year, month)
                where_sql = "WHERE data BETWEEN %s AND %s"
                parameters = [range_start, range_end]

            cursor.execute(f"""
                        SELECT
                            id,
                            titulo,
                            data,
                            hora_inicio,
                            hora_fim,
                            responsavel,
                            local,
                            descricao,
                            status,
                            criado_por_id,
                            criado_em,
                            atualizado_em
                        FROM agenda_compromissos
                        {where_sql}
                        ORDER BY data, hora_inicio, id
                           """, tuple(parameters))

            return [
                AgendaAppointment(**record)
                for record in cursor.fetchall()
            ]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    #lista os responsaveis distintos ja usados em compromissos — independente do
    #mes visivel, usada para preencher o filtro sem que as opcoes mudem conforme
    #o usuario navega pelo calendario
    @staticmethod
    def get_distinct_responsaveis():
        connection = None
        cursor = None

        try:
            connection, cursor = get_db_connection()

            cursor.execute("""
                SELECT DISTINCT responsavel
                FROM agenda_compromissos
                WHERE responsavel IS NOT NULL AND responsavel <> ''
                ORDER BY responsavel
            """)

            return [row["responsavel"] for row in cursor.fetchall()]

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

    #busca um compromisso pelo ID
    @staticmethod
    def get_by_id(appointment_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                        SELECT
                            id,
                            titulo,
                            data,
                            hora_inicio,
                            hora_fim,
                            responsavel,
                            local,
                            descricao,
                            status,
                            criado_por_id,
                            criado_em,
                            atualizado_em
                        FROM agenda_compromissos
                        WHERE id = %s
                        LIMIT 1
                           """, (appointment_id,))
            
            record = cursor.fetchone()
            
            return (
                AgendaAppointment(**record)
                if record
                else None
            )
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    
    #cadastra um compromisso
    @staticmethod
    def create(appointment):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                INSERT INTO agenda_compromissos (
                    titulo,
                    data,
                    hora_inicio,
                    hora_fim,
                    responsavel,
                    local,
                    descricao,
                    status,
                    criado_por_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                appointment.titulo,
                appointment.data,
                appointment.hora_inicio,
                appointment.hora_fim,
                appointment.responsavel,
                appointment.local,
                appointment.descricao,
                appointment.status,
                appointment.criado_por_id,
            ))
            
            appointment_id = cursor.lastrowid
            connection.commit()
            
            return appointment_id
        
        except Exception:
            if connection:
                connection.rollback()
                
            raise
            
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    #atualiza um compromisso
    @staticmethod
    def update(appointment):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE agenda_compromissos
                SET
                    titulo = %s,
                    data = %s,
                    hora_inicio = %s,
                    hora_fim = %s,
                    responsavel = %s,
                    local = %s,
                    descricao = %s,
                    status = %s
                WHERE id = %s
            """, (
                appointment.titulo,
                appointment.data,
                appointment.hora_inicio,
                appointment.hora_fim,
                appointment.responsavel,
                appointment.local,
                appointment.descricao,
                appointment.status,
                appointment.id,
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
                
    #atualiza somente o status
    @staticmethod
    def update_status(appointment_id, status):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                UPDATE agenda_compromissos
                SET status = %s
                WHERE id = %s
            """, (
                status,
                appointment_id,
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
                
                
                
    #verifica se existe outro compromisso no mesmo periodo
    @staticmethod
    def has_conflict(
        appointment_date,
        start_time,
        end_time,
        ignored_id=None
    ):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            query = """
                SELECT id
                FROM agenda_compromissos
                WHERE data = %s
                AND status <> 'cancelado'
                AND hora_inicio < %s
                AND COALESCE(hora_fim, hora_inicio) > %s
            """
            
            parameters = [
                appointment_date,
                end_time,
                start_time
            ]
            
            if ignored_id is not None:
                query += " AND id <> %s"
                parameters.append(ignored_id)
                
            query += " LIMIT 1"
            
            cursor.execute(
                query,
                tuple(parameters)
            )
            
            return cursor.fetchone() is not None
        
        finally:
            if cursor:
                cursor.close()
                
            if connection:
                connection.close()
                
    
    #exclui um compromisso
    @staticmethod
    def delete(appointment_id):
        connection = None
        cursor = None
        
        try:
            connection, cursor = get_db_connection()
            
            cursor.execute("""
                DELETE FROM agenda_compromissos
                WHERE id = %s
            """, (appointment_id,))
            
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