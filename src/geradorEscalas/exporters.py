import pandas as pd
from calendar import monthrange, weekday
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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

        dias_trabalho = {turno["dia"]: turno for turno in info.get("dias", [])}
        escala_data_base = info.get("escala_data_base")

        for dia_num in range(1, num_dias + 1):
            dia_num_str = str(dia_num)
            valor_celula = ""

            try:
                data_do_dia = datetime(ano, mes, dia_num).date()
            except ValueError:
                data_do_dia = None

            if data_do_dia:
                if not escala_data_base or data_do_dia >= escala_data_base:
                    valor_celula = "F"

                    if dia_num in dias_trabalho:
                        turno_info = dias_trabalho[dia_num]
                        tipo_turno = turno_info.get("turno", "X").upper()
                        esta_afastado = turno_info.get("em_afastamento", False)
                        valor_celula = (
                            f"{tipo_turno}(A)" if esta_afastado else tipo_turno
                        )

            linha[dia_num_str] = valor_celula

        dados_para_df.append(linha)

    df = pd.DataFrame(dados_para_df)

    colunas_ordenadas = ["Colaborador"] + colunas_dias
    df = df.reindex(columns=colunas_ordenadas)
    df.set_index("Colaborador", inplace=True)
    df.to_excel(caminho_arquivo, sheet_name=f"Escala {mes_nome} {ano}")


def _draw_footer(canvas, doc):
    """
    Desenha o rodapé com a legenda colorida e as informações de impressão,
    CENTRALIZANDO ambos dentro das margens da página.
    """
    canvas.saveState()

    # 1. Definição da Legenda (como antes)
    data = [
        ["LEGENDA", "F", "FOLGA", "HE", "HORA EXTRA", "FE", "FÉRIAS"],
        ["", "AT", "ATESTADO", "AF", "ATESTADO INSS.", "LM", "LICENÇA MATERNIDADE"],
    ]
    col_widths = [
        0.9 * inch,
        0.4 * inch,
        1.2 * inch,
        0.4 * inch,
        1.3 * inch,
        0.4 * inch,
        1.5 * inch,
    ]
    legend_table = Table(data, colWidths=col_widths)

    style = TableStyle(
        [
            ("SPAN", (0, 0), (0, 1)),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 1), "CENTER"),
            ("FONTNAME", (0, 0), (0, 1), "Helvetica-Bold"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (1, 0), (1, 1), "CENTER"),
            ("ALIGN", (3, 0), (3, 1), "CENTER"),
            ("ALIGN", (5, 0), (5, 1), "CENTER"),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
            ("FONTNAME", (3, 0), (3, 0), "Helvetica-Bold"),
            ("FONTNAME", (5, 0), (5, 0), "Helvetica-Bold"),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            ("FONTNAME", (3, 1), (3, 1), "Helvetica-Bold"),
            ("FONTNAME", (5, 1), (5, 1), "Helvetica-Bold"),
            ("ALIGN", (2, 0), (2, 1), "LEFT"),
            ("ALIGN", (4, 0), (4, 1), "LEFT"),
            ("ALIGN", (6, 0), (6, 1), "LEFT"),
            ("LEFTPADDING", (2, 0), (2, 1), 5),
            ("LEFTPADDING", (4, 0), (4, 1), 5),
            ("LEFTPADDING", (6, 0), (6, 1), 5),
            ("BACKGROUND", (1, 0), (1, 0), colors.yellow),
            ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#00B0F0")),
            ("BACKGROUND", (5, 0), (5, 0), colors.HexColor("#ED7D31")),
            ("BACKGROUND", (1, 1), (1, 1), colors.red),
            ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#00B050")),
            ("BACKGROUND", (5, 1), (5, 1), colors.HexColor("#7030A0")),
        ]
    )
    legend_table.setStyle(style)

    # --- CORREÇÃO DO ALINHAMENTO DA LEGENDA ---
    # Calcula a largura total da tabela da legenda
    legend_width = sum(col_widths)
    # Calcula a largura útil da página
    page_width = landscape(letter)[0]
    usable_width = page_width - doc.leftMargin - doc.rightMargin
    # Calcula a posição X inicial para centralizar a legenda
    start_x_legend = doc.leftMargin + (usable_width - legend_width) / 2.0

    # Desenha a tabela da legenda na posição X calculada
    legend_table.wrapOn(canvas, doc.width, doc.bottomMargin)
    # Usa start_x_legend em vez de doc.leftMargin
    legend_table.drawOn(canvas, start_x_legend, 0.4 * inch)
    # --- FIM DA CORREÇÃO ---

    # 2. Desenha o texto "Desenvolvido por" centralizado ENTRE as margens (como antes)
    canvas.setFont("Helvetica", 8)
    now = datetime.now()
    data_hora_geracao = now.strftime("%d/%m/%Y às %H:%M:%S")
    texto_footer = f"Desenvolvido por NetCode | Impresso em: {data_hora_geracao}"

    # O cálculo do centro para o texto já estava correto
    center_x_text = doc.leftMargin + (usable_width / 2.0)
    canvas.drawCentredString(center_x_text, 0.25 * inch, texto_footer)

    canvas.restoreState()


def _determinar_sequencia(info_colab):
    """Determina a sequência PAR/ÍMPAR."""
    dias_trabalho = info_colab.get("dias", [])
    if not dias_trabalho:
        return 2
    primeiro_dia = dias_trabalho[0].get("dia")
    if primeiro_dia:
        if primeiro_dia % 2 == 1:
            return 1  # ÍMPAR
        else:
            return 0  # PAR
    return 2


def exportar_para_pdf(dados_escala, ano, mes, caminho_arquivo):
    """Gera múltiplas tabelas (uma por setor), com espaçamento,
    e garante que não quebrem entre páginas."""
    meses_nomes = [
        "JANEIRO",
        "FEVEREIRO",
        "MARÇO",
        "ABRIL",
        "MAIO",
        "JUNHO",
        "JULHO",
        "AGOSTO",
        "SETEMBRO",
        "OUTUBRO",
        "NOVEMBRO",
        "DEZEMBRO",
    ]
    mes_nome = meses_nomes[mes - 1]
    num_dias = monthrange(ano, mes)[1]
    dias_semana_abrev = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

    # --- MUDANÇA: Dicionário de Mapeamento de Motivos ---
    MOTIVO_ABBREV = {
        "ATESTADO": "AT",
        "AFASTADO INSS.": "AF",
        "FÉRIAS": "FE",
        "FERIAS": "FE",  # Variação comum
        "LICENÇA MATERNIDADE": "LM",
        "LICENCA MATERNIDADE": "LM",  # Variação comum
        "HORA EXTRA": "HE",
        "FOLGA": "F",
    }
    # --- FIM DA MUDANÇA ---

    # --- Agrupamento Aninhado (Setor > Escala/Turno) ---
    grupos_de_setor = {}
    for matricula, info in dados_escala.items():
        setor_grupo = info.get("setor", "SETOR NÃO DEFINIDO").upper()
        escala_tipo = info.get("escala", "N/A").upper()
        tipo_turno_bruto = info.get("Tipo_turno", "")
        escala_nome_grupo = ""

        if tipo_turno_bruto:
            tipo_turno_limpo = tipo_turno_bruto.split(" ")[0].upper()
            escala_nome_grupo = f"{escala_tipo} - {tipo_turno_limpo}"
        else:
            escala_nome_grupo = escala_tipo

        if setor_grupo not in grupos_de_setor:
            grupos_de_setor[setor_grupo] = {}
        if escala_nome_grupo not in grupos_de_setor[setor_grupo]:
            grupos_de_setor[setor_grupo][escala_nome_grupo] = []
        grupos_de_setor[setor_grupo][escala_nome_grupo].append((matricula, info))

    # --- Criação do Documento ---
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=landscape(letter),
        topMargin=0.5 * inch,
        bottomMargin=1.0 * inch,  # Aumenta a margem inferior para caber a legenda
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )
    elementos = []

    # --- Estilos de Parágrafo ---
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    style_setor_row = ParagraphStyle(
        "SetorTitle",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        alignment=TA_LEFT,
    )
    style_escala_row = ParagraphStyle(
        "EscalaTitle",
        parent=styles["Normal"],
        fontSize=8,
        fontName="Helvetica-Bold",
        textColor=colors.black,
        alignment=TA_RIGHT,
    )
    style_cell_wrap_left = ParagraphStyle(
        "CellWrapLeft", fontSize=7, fontName="Helvetica", alignment=TA_LEFT
    )
    style_cell_wrap_center = ParagraphStyle(
        "CellWrapCenter", fontSize=7, fontName="Helvetica", alignment=TA_CENTER
    )

    # --- Título Principal ---
    titulo_html = f'ESCALA <font color="red">UMPA STA. LUZIA</font> - {mes_nome} {ano}'
    elementos.append(Paragraph(titulo_html, style_titulo))
    elementos.append(Spacer(1, 0.1 * inch))

    # --- Definições Globais da Tabela ---
    cabecalho_dias = ["NOME", "CARGO", "MATRÍCULA", "CONSELHO"] + [
        str(i) for i in range(1, num_dias + 1)
    ]
    cabecalho_semana = ["", "", "", ""]
    for dia_num in range(1, num_dias + 1):
        dia_semana_num = weekday(ano, mes, dia_num)
        cabecalho_semana.append(dias_semana_abrev[dia_semana_num])

    largura_col_nome = 2.0 * inch
    largura_cargo = 1.2 * inch
    largura_matricula = 0.7 * inch
    largura_conselho = 0.7 * inch

    largura_disponivel = (
        landscape(letter)[0]
        - largura_col_nome
        - largura_cargo
        - largura_matricula
        - largura_conselho
        - 1 * inch
    )
    largura_col_dia = largura_disponivel / num_dias
    larguras_colunas = [
        largura_col_nome,
        largura_cargo,
        largura_matricula,
        largura_conselho,
    ] + ([largura_col_dia] * num_dias)

    colunas_totais = len(larguras_colunas)

    # --- Estilos de Base ---
    estilos_base = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C6E0B4")),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#E2EFD9")),
        ("VALIGN", (0, 1), (-1, 1), "MIDDLE"),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.black),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, 1), 7),
        ("ALIGN", (0, 1), (-1, 1), "CENTER"),
        ("VALIGN", (0, 2), (-1, -1), "MIDDLE"),
        ("FONTNAME", (2, 2), (-1, -1), "Helvetica"),
        ("FONTSIZE", (2, 2), (-1, -1), 7),
        ("ALIGN", (2, 2), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("LINEBELOW", (0, 1), (-1, 1), 1, colors.black),
    ]

    estilos_fds_cabecalho = []
    for dia_num in range(1, num_dias + 1):
        if weekday(ano, mes, dia_num) >= 5:
            col_index = dia_num + 3
            estilos_fds_cabecalho.append(
                (
                    "BACKGROUND",
                    (col_index, 0),
                    (col_index, 1),
                    colors.HexColor("#E7E6E6"),
                )
            )

    # --- Loop para criar uma tabela por setor ---
    for setor_nome, escalas_do_setor in sorted(grupos_de_setor.items()):

        dados_para_esta_tabela = [cabecalho_dias, cabecalho_semana]
        estilos_para_esta_tabela = list(estilos_base) + list(estilos_fds_cabecalho)
        row_index = 2

        for i, (escala_nome_grupo, colaboradores_do_grupo) in enumerate(
            sorted(escalas_do_setor.items())
        ):

            titulo_setor_cell = ""
            if i == 0:
                titulo_setor_cell = Paragraph(setor_nome, style_setor_row)

            titulo_escala_cell = Paragraph(escala_nome_grupo.upper(), style_escala_row)

            linha_titulo = [titulo_setor_cell, "", "", "", titulo_escala_cell] + [
                ""
            ] * (colunas_totais - 5)
            dados_para_esta_tabela.append(linha_titulo)

            cor_fundo_titulo = (
                colors.HexColor("#C6E0B4") if i == 0 else colors.HexColor("#E2EFD9")
            )

            if i == 0:  # Adiciona espaço ANTES do primeiro título (Setor)
                estilos_para_esta_tabela.append(
                    ("TOPPADDING", (0, row_index), (-1, row_index), 8)
                )

            estilos_para_esta_tabela.append(("SPAN", (0, row_index), (3, row_index)))
            estilos_para_esta_tabela.append(("SPAN", (4, row_index), (-1, row_index)))
            estilos_para_esta_tabela.append(
                ("BACKGROUND", (0, row_index), (-1, row_index), cor_fundo_titulo)
            )
            estilos_para_esta_tabela.append(
                ("LEFTPADDING", (0, row_index), (0, row_index), 10)
            )
            estilos_para_esta_tabela.append(
                ("RIGHTPADDING", (4, row_index), (4, row_index), 10)
            )
            estilos_para_esta_tabela.append(
                ("VALIGN", (0, row_index), (-1, row_index), "MIDDLE")
            )
            estilos_para_esta_tabela.append(
                ("NOSPLIT", (0, row_index), (-1, row_index + 1))
            )
            row_index += 1

            dados_ordenados_grupo = []
            for matricula, info in colaboradores_do_grupo:
                sequencia = _determinar_sequencia(info)
                dados_ordenados_grupo.append((matricula, info, sequencia))
            dados_ordenados_grupo.sort(key=lambda x: (x[2], x[1].get("nome", "")))

            is_even_row = False
            for matricula, info, _ in dados_ordenados_grupo:
                nome_colab = info.get("nome", matricula)
                cargo_real = info.get("cargo", "")
                conselho_real = info.get("conselho", "")

                linha_colab = [
                    Paragraph(nome_colab, style_cell_wrap_left),
                    Paragraph(cargo_real, style_cell_wrap_center),
                    str(matricula),
                    str(conselho_real),
                ]

                dias_trabalho = {turno["dia"]: turno for turno in info.get("dias", [])}
                escala_data_base = info.get("escala_data_base")

                # --- MUDANÇA: LÓGICA DE PREENCHIMENTO DA CÉLULA ---
                for dia_num in range(1, num_dias + 1):
                    valor_celula_str = ""
                    try:
                        data_do_dia = datetime(ano, mes, dia_num).date()
                    except ValueError:
                        data_do_dia = None

                    if data_do_dia:
                        if not escala_data_base or data_do_dia >= escala_data_base:
                            valor_celula_str = "F"  # Padrão é Folga

                            turno_info = dias_trabalho.get(dia_num)
                            
                            if turno_info:
                                motivo = turno_info.get("afastamento_motivo")
                                if motivo:
                                    valor_celula_str = MOTIVO_ABBREV.get(motivo.upper(), motivo[:2].upper())
                                else:
                                    # Se não, é um dia de trabalho normal
                                    tipo_turno = turno_info.get("turno", "X").upper()
                                    valor_celula_str = tipo_turno

                    linha_colab.append(valor_celula_str)
                # --- FIM DA MUDANÇA ---

                dados_para_esta_tabela.append(linha_colab)

                # Estilos da Linha de Dados
                cor_fundo_zebra = (
                    colors.HexColor("#F2F2F2") if is_even_row else colors.white
                )
                estilos_para_esta_tabela.append(
                    ("BACKGROUND", (0, row_index), (-1, row_index), cor_fundo_zebra)
                )
                estilos_para_esta_tabela.append(
                    ("TOPPADDING", (0, row_index), (-1, row_index), 3)
                )
                estilos_para_esta_tabela.append(
                    ("BOTTOMPADDING", (0, row_index), (-1, row_index), 3)
                )

                for dia_num in range(1, num_dias + 1):
                    if weekday(ano, mes, dia_num) >= 5:
                        col_index = dia_num + 3
                        estilos_para_esta_tabela.append(
                            (
                                "BACKGROUND",
                                (col_index, row_index),
                                (col_index, row_index),
                                colors.HexColor("#E7E6E6"),
                            )
                        )

                is_even_row = not is_even_row
                row_index += 1

        # Cria e aplica estilos para a tabela do setor
        tabela_setor = Table(dados_para_esta_tabela, colWidths=larguras_colunas)
        tabela_setor.setStyle(TableStyle(estilos_para_esta_tabela))

        # Adiciona a Tabela e o Espaçador ao PDF
        bloco_para_manter_junto = [
            tabela_setor,
            Spacer(1, 0.2 * inch),  # Espaçador ENTRE setores
        ]
        elementos.append(KeepTogether(bloco_para_manter_junto))

    # --- FIM DO LOOP POR SETORES ---

    # Constrói o PDF
    doc.build(elementos, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
