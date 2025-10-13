from datetime import date, datetime, timedelta
from calendar import monthrange, weekday
from . import database as db


class GeradorEscalaEngine:
    def __init__(self, ano, mes):
        self.ano = int(ano)
        self.mes = int(mes)
        self.escala_gerada = {}

    def _gerar_ciclo(self, data_base, horas_trabalho, horas_folga):
        """
        Calcula e retorna uma lista de objetos datetime completos para cada início de turno
        dentro do mês e ano selecionados.
        """
        inicios_de_turno = []
        intervalo = timedelta(hours=(horas_trabalho + horas_folga))

        try:
            # Assume que o turno base começa às 07:00.
            data_atual = datetime.combine(
                date.fromisoformat(str(data_base)), datetime.min.time().replace(hour=7)
            )
        except (ValueError, TypeError):
            return []

        # Avança a data até o período de geração
        limite_inferior = datetime(self.ano, self.mes, 1) - (
            intervalo * 5
        )  # Buffer de 5 ciclos
        while data_atual < limite_inferior:
            data_atual += intervalo

        # Gera os turnos que caem dentro do mês
        try:
            proximo_mes = self.mes + 1
            proximo_ano = self.ano
            if proximo_mes > 12:
                proximo_mes = 1
                proximo_ano += 1
            limite_superior = datetime(proximo_ano, proximo_mes, 1)
        except ValueError:  # Lida com meses que não têm dia 31, etc.
            limite_superior = datetime(
                self.ano, self.mes, monthrange(self.ano, self.mes)[1]
            ) + timedelta(days=1)

        while data_atual < limite_superior:
            if data_atual.year == self.ano and data_atual.month == self.mes:
                inicios_de_turno.append(data_atual)
            data_atual += intervalo

        return inicios_de_turno

    # --- Métodos Específicos para Cada Tipo de Escala ---

    def _calcular_escala_12x36(self, colaborador):
        data_base = colaborador.get("escala_data_base")
        if not data_base:
            return []
        turnos = []
        for dt in self._gerar_ciclo(data_base, 12, 36):
            turnos.append({"dia": dt.day, "turno": "X"})  # <-- Simplificado para "X"
        return turnos

    def _calcular_escala_24x72(self, colaborador):
        data_base = colaborador.get("escala_data_base")
        if not data_base:
            return []
        turnos = []
        for dt in self._gerar_ciclo(data_base, 24, 72):
            turnos.append({"dia": dt.day, "turno": "X"})  # <-- Simplificado para "X"
        return turnos

    def _calcular_escala_24x120(self, colaborador):
        """
        Calcula a escala 24x120 com a lógica de alternância de ciclos (par/ímpar).
        """
        data_base_original = colaborador.get("escala_data_base")
        sequencia_anterior = colaborador.get("escala_sequencia_atual", "IMPAR")
        matricula = colaborador.get("matricula")
        if not data_base_original or not matricula:
            return []

        # --- LÓGICA CORRIGIDA ---
        # Determina a sequência para o mês atual, invertendo a anterior
        sequencia_deste_mes = "PAR" if sequencia_anterior == "IMPAR" else "IMPAR"

        # Define a data de início do ciclo para este mês.
        # Se a regra for PAR, o ciclo começa 24h depois da data base original.
        data_base_para_este_mes = data_base_original
        if sequencia_deste_mes == "PAR":
            data_base_para_este_mes_dt = datetime.combine(
                data_base_original, datetime.min.time()
            ) + timedelta(hours=24)
            data_base_para_este_mes = data_base_para_este_mes_dt.date()

        # Gera o ciclo usando a data base correta (original para ÍMPAR, ajustada para PAR)
        turnos_formatados = []
        for dt_inicio_turno in self._gerar_ciclo(data_base_para_este_mes, 24, 120):
            turnos_formatados.append({"dia": dt_inicio_turno.day, "turno": "X"})

        # Atualiza o estado no banco para a próxima geração
        db.update_sequencia_colaborador(matricula, sequencia_deste_mes)

        return turnos_formatados

    def _calcular_diarista(self, colaborador):
        turnos_formatados = []
        num_dias = monthrange(self.ano, self.mes)[1]
        for dia in range(1, num_dias + 1):
            if weekday(self.ano, self.mes, dia) < 5:
                turnos_formatados.append(
                    {"dia": dia, "turno": "X"}
                )  # <-- Simplificado para "X"
        return turnos_formatados

    # --- Método Principal (O Roteador) ---
    def executar(self, colaboradores_filtrados):
        """
        Gera a escala para os colaboradores filtrados e adiciona uma flag
        nos turnos que caem em períodos de afastamento.
        """
        primeiro_dia_mes = date(self.ano, self.mes, 1)
        ultimo_dia_mes = date(self.ano, self.mes, monthrange(self.ano, self.mes)[1])

        for colab in colaboradores_filtrados:
            matricula = colab.get("matricula")
            tipo_escala = colab.get("escala")

            dias_de_trabalho_calculados = []

            # --- ROTEADOR DE ESCALAS (sem alterações) ---
            if tipo_escala == "12x36":
                dias_de_trabalho_calculados = self._calcular_escala_12x36(colab)
            elif tipo_escala == "24x72":
                dias_de_trabalho_calculados = self._calcular_escala_24x72(colab)
            elif tipo_escala == "24x120":
                dias_de_trabalho_calculados = self._calcular_escala_24x120(colab)
            elif tipo_escala == "Diarista":
                dias_de_trabalho_calculados = self._calcular_diarista(colab)

            # --- NOVA LÓGICA DE VERIFICAÇÃO DE AFASTAMENTO ---
            inicio_afast = colab.get("afastamento_inicio")
            fim_afast = colab.get("afastamento_fim")

            dias_de_trabalho_final = []
            for turno in dias_de_trabalho_calculados:
                dia_do_turno = turno["dia"]
                data_do_turno = date(self.ano, self.mes, dia_do_turno)

                # Adiciona a nova flag 'em_afastamento'
                turno["em_afastamento"] = False
                if inicio_afast and fim_afast:
                    if inicio_afast <= data_do_turno <= fim_afast:
                        turno["em_afastamento"] = True

                dias_de_trabalho_final.append(turno)

            self.escala_gerada[matricula] = {
                "nome": colab.get("nome"),
                "dias": dias_de_trabalho_final,
            }

        return self.escala_gerada
