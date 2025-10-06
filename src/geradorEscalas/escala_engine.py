from datetime import date, timedelta
from . import database as db

class GeradorEscalaEngine:
    def __init__(self, ano, mes):
        self.ano = int(ano)
        self.mes = int(mes)
        self.escala_gerada = {} # Dicionário para guardar a escala final

    def _gerar_ciclo(self, data_base, horas_trabalho, horas_folga):
        """
        Calcula as datas de um ciclo de trabalho/folga para o mês/ano selecionado.
        Esta é uma função genérica que servirá para 12x36, 24x72, etc.
        """
        dias_de_trabalho = []
        
        # Define o intervalo total de um ciclo (ex: 24h trabalho + 72h folga = 96h)
        intervalo = timedelta(hours=(horas_trabalho + horas_folga))
        data_atual = date.fromisoformat(str(data_base))

        # Avança a data base até que ela esteja próxima ou dentro do período que queremos gerar
        while data_atual.year < self.ano or (data_atual.year == self.ano and data_atual.month < self.mes):
            data_atual += intervalo
        
        # Gera os dias de trabalho para o mês corrente
        while data_atual.year == self.ano and data_atual.month == self.mes:
            dias_de_trabalho.append(data_atual.day)
            data_atual += intervalo
        
        return dias_de_trabalho

    def _calcular_escala_24x72(self, colaborador):
        """Chama o gerador de ciclo com os parâmetros da escala 24x72."""
        data_base = colaborador.get('escala_data_base')
        if not data_base:
            print(f"AVISO: Colaborador {colaborador.get('nome')} não possui data base para a escala.")
            return []
        
        return self._gerar_ciclo(data_base, 24, 72)

    def executar(self):
        """
        Método principal que busca os colaboradores e direciona para o cálculo correto.
        """
        colaboradores = db.get_all_active_collaborators() # Precisamos criar esta função
        
        for colab in colaboradores:
            matricula = colab.get('matricula')
            tipo_escala = colab.get('escala')
            
            dias_de_trabalho = []

            # --- ROTEADOR DE ESCALAS ---
            if tipo_escala == '24x72':
                dias_de_trabalho = self._calcular_escala_24x72(colab)
            # Futuramente, adicionaremos:
            # elif tipo_escala == '12x36':
            #     dias_de_trabalho = self._calcular_escala_12x36(colab)
            
            self.escala_gerada[matricula] = {
                'nome': colab.get('nome'),
                'dias': dias_de_trabalho
            }
        
        return self.escala_gerada