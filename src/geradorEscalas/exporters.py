import pandas as pd
from calendar import monthrange, weekday
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime


def exportar_para_excel(dados_escala, ano, mes, caminho_arquivo):
    """Converte os dados da escala para um formato de grade e salva como um arquivo Excel."""
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
            linha[dia_num_str] = ""

        for turno in info.get("dias", []):
            dia = turno.get("dia")
            tipo_turno = turno.get("turno", "").upper()
            esta_afastado = turno.get("em_afastamento", False)
            valor_celula = f"{tipo_turno}(A)" if esta_afastado else tipo_turno

            if dia and 1 <= dia <= num_dias:
                linha[str(dia)] = valor_celula

        dados_para_df.append(linha)

    df = pd.DataFrame(dados_para_df)
    df.set_index("Colaborador", inplace=True)

    df.to_excel(caminho_arquivo, sheet_name=f"Escala {mes_nome} {ano}")

# --- 2. NOVA FUNÇÃO PARA DESENHAR O RODAPÉ ---
def _draw_footer(canvas, doc):
    """
    Função chamada pelo ReportLab para desenhar o rodapé em cada página.
    """
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    
    # Pega a data e hora atuais
    now = datetime.now()
    data_hora_geracao = now.strftime("%d/%m/%Y às %H:%M:%S")
    
    # Texto do rodapé
    texto_footer = f"Desenvolvido por NetCode | Impresso em: {data_hora_geracao}"
    
    # Desenha o texto centralizado na margem inferior
    canvas.drawCentredString(landscape(letter)[0] / 2.0, 0.5 * inch, texto_footer)
    
    canvas.restoreState()
    
def exportar_para_pdf(dados_escala, ano, mes, caminho_arquivo):
    """Gera uma tabela formatada da escala e a salva em um arquivo PDF profissional."""
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

    # --- Preparação dos Dados ---
    cabecalho = ["Colaborador"] + [str(i) for i in range(1, num_dias + 1)]
    dados_tabela = [cabecalho]

    for matricula, info in dados_escala.items():
        linha = [info.get("nome", matricula)]
        dias_trabalho = {turno["dia"]: turno for turno in info.get("dias", [])}
        for dia_num in range(1, num_dias + 1):
            turno_info = dias_trabalho.get(dia_num)
            if turno_info:
                tipo_turno = turno_info.get("turno", "").upper()
                esta_afastado = turno_info.get("em_afastamento", False)
                valor_celula = f"{tipo_turno}(A)" if esta_afastado else tipo_turno
                linha.append(valor_celula)
            else:
                linha.append("")
        dados_tabela.append(linha)

    # --- 3. CRIAÇÃO DO DOCUMENTO COM O RODAPÉ ---
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=landscape(letter))
    
    elementos = []
    
    styles = getSampleStyleSheet()
    style_titulo = styles['h1']
    style_titulo.alignment = 1
    
    elementos.append(Paragraph(f"Escala de Trabalho - {mes_nome.capitalize()} / {ano}", style_titulo))
    elementos.append(Spacer(1, 0.25 * inch))

    # Estilos de parágrafo para o título
    styles = getSampleStyleSheet()
    style_titulo = styles["h1"]
    style_titulo.alignment = 1  # Centralizado

    # Largura das colunas (uma para o nome, as outras para os dias)
    largura_col_nome = 2.5 * inch
    largura_col_dia = (landscape(letter)[0] - largura_col_nome - inch) / num_dias
    larguras_colunas = [largura_col_nome] + [largura_col_dia] * num_dias

    # Cria a tabela com as larguras definidas
    tabela = Table(dados_tabela, colWidths=larguras_colunas)

    # --- Estilização Avançada da Tabela ---
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B2B2B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]
    )

    # Cores de fundo alternadas (efeito zebra)
    for i, row in enumerate(dados_tabela):
        if i % 2 == 0 and i > 0:  # i > 0 para não colorir o cabeçalho
            style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F0F0F0"))

    # Destaque para as colunas de fim de semana
    # for dia in range(1, num_dias + 1):
    #     if weekday(ano, mes, dia) >= 5:  # 5=Sábado, 6=Domingo
    #         style.add("BACKGROUND", (dia, 0), (dia, -1), colors.HexColor("#E0E0E0"))

    tabela.setStyle(style)

    # --- Constrói o PDF ---
    elementos = []
    elementos.append(
        Paragraph(f"Escala de Trabalho - {mes_nome.capitalize()} / {ano}", style_titulo)
    )
    elementos.append(Spacer(1, 0.25 * inch))
    elementos.append(tabela)

    doc.build(elementos, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
