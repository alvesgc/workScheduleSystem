from datetime import date, datetime, timedelta
from calendar import monthrange, weekday
from . import database as db


class GeradorEscalaEngine:
    def __init__(self, ano, mes):
        self.ano = int(ano)
        self.mes = int(mes)
        self.escala_gerada = {}
        self.colaboradores = []

    def _calcular_ciclo_par_impar(
        self, data_base, ano_referencia, mes_referencia, horas_trabalho, horas_folga
    ):
        """
        Calcula se o colaborador está em ciclo PAR ou ÍMPAR no mês de referência.

        Lógica:
        - Conta quantos CICLOS COMPLETOS se passaram desde a data base até o início do mês
        - Se número de ciclos é PAR (0, 2, 4...) → ciclo ÍMPAR (começa na data base original)
        - Se número de ciclos é ÍMPAR (1, 3, 5...) → ciclo PAR (começa 24h depois)

        Returns:
            tuple: (é_ciclo_par, data_inicio_ajustada)
        """
        try:
            data_base_obj = date.fromisoformat(str(data_base))
        except (ValueError, TypeError):
            return False, data_base

        # Data de referência: primeiro dia do mês que queremos calcular
        primeiro_dia_mes = date(ano_referencia, mes_referencia, 1)

        # Calcula a diferença em dias
        dias_desde_base = (primeiro_dia_mes - data_base_obj).days

        # Duração de um ciclo completo em dias
        horas_ciclo = horas_trabalho + horas_folga
        dias_ciclo = horas_ciclo / 24

        # Quantos ciclos completos se passaram
        ciclos_completos = int(dias_desde_base / dias_ciclo)

        # Se o número de ciclos completos é ÍMPAR, estamos no ciclo PAR
        # Se o número de ciclos completos é PAR, estamos no ciclo ÍMPAR
        e_ciclo_par = ciclos_completos % 2 == 1

        # Ajusta a data base se for ciclo PAR (adiciona 24h)
        if e_ciclo_par:
            data_inicio_ajustada = data_base_obj + timedelta(days=1)
        else:
            data_inicio_ajustada = data_base_obj

        return e_ciclo_par, data_inicio_ajustada

    def _gerar_ciclo(self, data_base, horas_trabalho, horas_folga):
        """
        Calcula e retorna uma lista de objetos datetime completos para cada início de turno
        dentro do mês e ano selecionados.
        """
        inicios_de_turno = []
        intervalo = timedelta(hours=(horas_trabalho + horas_folga))

        try:
            data_base_obj = date.fromisoformat(str(data_base))
            # Assume que o turno base começa às 07:00.
            data_atual = datetime.combine(
                data_base_obj, datetime.min.time().replace(hour=7)
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
        except ValueError:
            limite_superior = datetime(
                self.ano, self.mes, monthrange(self.ano, self.mes)[1]
            ) + timedelta(days=1)

        # Loop principal
        while data_atual < limite_superior:
            # Verifica se o turno está no mês correto
            if data_atual.year == self.ano and data_atual.month == self.mes:
                inicios_de_turno.append(data_atual)

            # Incrementa sempre
            data_atual += intervalo

        return inicios_de_turno

    # --- Métodos Específicos para Cada Tipo de Escala ---

    def _calcular_escala_12x36(self, colaborador):
        """
        Calcula escala 12x36 com lógica automática de par/ímpar.
        """
        data_base = colaborador.get("escala_data_base")
        matricula = colaborador.get("matricula")
        if not data_base:
            return []

        # Calcula se está em ciclo par ou ímpar
        e_ciclo_par, data_base_ajustada = self._calcular_ciclo_par_impar(
            data_base, self.ano, self.mes, 12, 36
        )

        # Gera os turnos usando a data base ajustada
        turnos = []
        for dt in self._gerar_ciclo(data_base_ajustada, 12, 36):
            turnos.append({"dia": dt.day, "turno": "X"})

        # Atualiza sequência no banco para referência
        sequencia = "PAR" if e_ciclo_par else "IMPAR"
        if matricula:
            db.update_sequencia_colaborador(matricula, sequencia)

        return turnos

    def _calcular_escala_24x72(self, colaborador):
        """
        Calcula escala 24x72 com lógica automática de par/ímpar.
        """
        data_base = colaborador.get("escala_data_base")
        matricula = colaborador.get("matricula")
        if not data_base:
            return []

        # Calcula se está em ciclo par ou ímpar
        e_ciclo_par, data_base_ajustada = self._calcular_ciclo_par_impar(
            data_base, self.ano, self.mes, 24, 72
        )

        # Gera os turnos usando a data base ajustada
        turnos = []
        for dt in self._gerar_ciclo(data_base_ajustada, 24, 72):
            turnos.append({"dia": dt.day, "turno": "X"})

        # Atualiza sequência no banco para referência
        sequencia = "PAR" if e_ciclo_par else "IMPAR"
        if matricula:
            db.update_sequencia_colaborador(matricula, sequencia)

        return turnos

    def _calcular_escala_24x120(self, colaborador):
        """
        Calcula escala 24x120 com lógica automática de par/ímpar.
        Nesta escala, o colaborador trabalha em meses alternados.
        """
        data_base = colaborador.get("escala_data_base")
        matricula = colaborador.get("matricula")
        if not data_base:
            return []

        try:
            data_base_obj = date.fromisoformat(str(data_base))
        except (ValueError, TypeError):
            return []

        # Calcula quantos meses se passaram desde a data base
        primeiro_dia_mes = date(self.ano, self.mes, 1)
        meses_desde_base = (primeiro_dia_mes.year - data_base_obj.year) * 12 + (
            primeiro_dia_mes.month - data_base_obj.month
        )

        # Verifica se trabalha neste mês (alternância mensal)
        trabalha_neste_mes = meses_desde_base % 2 == 0

        if not trabalha_neste_mes:
            # Está em mês de folga
            sequencia = "FOLGA_MES"
            if matricula:
                db.update_sequencia_colaborador(matricula, sequencia)
            return []

        # Calcula se está em ciclo par ou ímpar DENTRO do mês de trabalho
        e_ciclo_par, data_base_ajustada = self._calcular_ciclo_par_impar(
            data_base, self.ano, self.mes, 24, 120
        )

        # Gera os turnos usando a data base ajustada
        turnos = []
        for dt in self._gerar_ciclo(data_base_ajustada, 24, 120):
            turnos.append({"dia": dt.day, "turno": "X"})

        # Atualiza sequência no banco
        sequencia = f"TRABALHA_{'PAR' if e_ciclo_par else 'IMPAR'}"
        if matricula:
            db.update_sequencia_colaborador(matricula, sequencia)

        return turnos

    def _calcular_diarista(self, colaborador):
        """
        Calcula escala de diarista (segunda a sexta).
        """
        turnos_formatados = []
        num_dias = monthrange(self.ano, self.mes)[1]
        for dia in range(1, num_dias + 1):
            if weekday(self.ano, self.mes, dia) < 5:  # 0-4 = Seg-Sex
                turnos_formatados.append({"dia": dia, "turno": "X"})
        return turnos_formatados

    # --- Método Principal (O Roteador) ---
    def executar(self, colaboradores_filtrados):
        """
        Gera a escala para os colaboradores filtrados e adiciona uma flag
        nos turnos que caem em períodos de afastamento.
        """
        self.colaboradores = colaboradores_filtrados
        primeiro_dia_mes = date(self.ano, self.mes, 1)
        ultimo_dia_mes = date(self.ano, self.mes, monthrange(self.ano, self.mes)[1])

        for colab in colaboradores_filtrados:
            matricula = colab.get("matricula")
            tipo_escala = colab.get("escala")

            dias_de_trabalho_calculados = []

            # Roteador de escalas
            if tipo_escala == "12x36":
                dias_de_trabalho_calculados = self._calcular_escala_12x36(colab)
            elif tipo_escala == "24x72":
                dias_de_trabalho_calculados = self._calcular_escala_24x72(colab)
            elif tipo_escala == "24x120":
                dias_de_trabalho_calculados = self._calcular_escala_24x120(colab)
            elif tipo_escala == "Diarista":
                dias_de_trabalho_calculados = self._calcular_diarista(colab)

            # Verifica afastamento
            inicio_afast = colab.get("afastamento_inicio")
            fim_afast = colab.get("afastamento_fim")

            dias_de_trabalho_final = []
            for turno in dias_de_trabalho_calculados:
                dia_do_turno = turno["dia"]
                data_do_turno = date(self.ano, self.mes, dia_do_turno)

                # Adiciona flag de afastamento
                turno["em_afastamento"] = False
                if inicio_afast and fim_afast:
                    if inicio_afast <= data_do_turno <= fim_afast:
                        turno["em_afastamento"] = True

                dias_de_trabalho_final.append(turno)

            self.escala_gerada[matricula] = {
                "nome": colab.get("nome"),
                "escala": tipo_escala,
                "dias": dias_de_trabalho_final,
                "escala_data_base": colab.get("escala_data_base")
            }

        return self.escala_gerada
