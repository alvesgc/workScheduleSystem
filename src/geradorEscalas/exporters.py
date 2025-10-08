import pandas as pd
from calendar import monthrange, weekday
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def exportar_para_excel(dados_escala, ano, mes, caminho_arquivo):
    """
    Converte os dados da escala para um formato de grade e salva como um arquivo Excel.
    """
    meses_nomes = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    mes_nome = meses_nomes[mes - 1]
    num_dias = monthrange(ano, mes)[1]

    colunas_dias = [str(i) for i in range(1, num_dias + 1)]
    dados_para_df = []

    for matricula, info in dados_escala.items():
        linha = {"Colaborador": info.get("nome", matricula)}
        for dia_num_str in colunas_dias:
            linha[dia_num_str] = ""  # Inicializa a célula do dia como vazia

        for turno in info.get("dias", []):
            dia = turno.get("dia")
            tipo_turno = turno.get("turno")
            if dia and 1 <= dia <= num_dias:
                linha[str(dia)] = tipo_turno

        dados_para_df.append(linha)

    df = pd.DataFrame(dados_para_df)
    df.set_index("Colaborador", inplace=True)

    # Salva o DataFrame no arquivo Excel
    df.to_excel(caminho_arquivo, sheet_name=f"Escala {mes_nome} {ano}")


def exportar_para_pdf(dados_escala, ano, mes, caminho_arquivo):
    """
    Gera uma tabela formatada da escala e a salva em um arquivo PDF.
    """
    meses_nomes = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    mes_nome = meses_nomes[mes - 1]
    num_dias = monthrange(ano, mes)[1]

    # Preparação dos dados para a tabela do ReportLab
    cabecalho = ["Colaborador"] + [str(i) for i in range(1, num_dias + 1)]
    dados_tabela = [cabecalho]

    for matricula, info in dados_escala.items():
        linha = [info.get("nome", matricula)]
        dias_trabalho = {turno["dia"]: turno["turno"] for turno in info.get("dias", [])}
        for dia_num in range(1, num_dias + 1):
            linha.append(
                dias_trabalho.get(dia_num, "")
            )  # Adiciona o tipo de turno ou vazio
        dados_tabela.append(linha)

    # Criação do documento PDF em modo paisagem
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=landscape(letter))

    # Estilização da tabela
    style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#4A4A4A"),
            ),  # Fundo do cabeçalho
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Fonte do cabeçalho
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Colore as colunas de fim de semana
    for dia in range(1, num_dias + 1):
        if weekday(ano, mes, dia) >= 5:  # 5=Sábado, 6=Domingo
            style.add("BACKGROUND", (dia, 0), (dia, -1), colors.HexColor("#3A3A3A"))

    # Cria a tabela e aplica o estilo
    tabela = Table(dados_tabela)
    tabela.setStyle(style)

    # Constrói o PDF
    elementos = [tabela]
    doc.build(elementos)
