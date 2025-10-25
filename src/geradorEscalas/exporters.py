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
    Image,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date, datetime
import os
from .utils import resource_path


def exportar_para_excel(dados_escala, ano, mes, caminho_arquivo):
    """Gera uma planilha Excel com a escala, incluindo dados do colaborador, dias da semana e motivos de afastamento."""
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

    MOTIVO_ABBREV = {
        "ATESTADO": "AT",
        "ATESTADO ACOMP.": "AF",
        "FÉRIAS": "FE",
        "FERIAS": "FE",
        "LICENÇA MATERNIDADE": "LM",
        "LICENCA MATERNIDADE": "LM",
        "HORA EXTRA": "HE",
    }

    dias_semana_abrev = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

    # --- Preparação dos dados ---
    # Define os nomes exatos das colunas como aparecerão no Excel
    colunas_info = ["Nome", "Cargo", "Matrícula", "Conselho", "Setor"]
    colunas_dias_num = [str(i) for i in range(1, num_dias + 1)]
    colunas_finais = colunas_info + colunas_dias_num

    dados_para_df = []  # Agora conterá APENAS os dados dos colaboradores

    # --- Linha EXTRA para os dias da semana (será adicionada depois) ---
    linha_dias_semana = {col: "" for col in colunas_info}  # Células vazias no início
    for dia_num in range(1, num_dias + 1):
        dia_semana_num = weekday(ano, mes, dia_num)
        linha_dias_semana[str(dia_num)] = dias_semana_abrev[dia_semana_num]
    # Converte para DataFrame para inserir depois
    df_dias_semana = pd.DataFrame([linha_dias_semana])

    # --- Linhas dos Colaboradores ---
    colaboradores_ordenados = sorted(
        dados_escala.items(), key=lambda item: item[1].get("nome", "")
    )

    for matricula, info in colaboradores_ordenados:
        linha_colab = {
            "Nome": info.get("nome", matricula),
            "Cargo": info.get("cargo", ""),
            "Matrícula": str(matricula),
            "Conselho": str(info.get("conselho", "")),
            "Setor": info.get("setor", ""),
        }

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

                    turno_info = dias_trabalho.get(dia_num)
                    if turno_info:
                        motivo = turno_info.get("afastamento_motivo")
                        print(motivo)
                        if motivo:
                            valor_celula = MOTIVO_ABBREV.get(
                                motivo.upper(), motivo[:2].upper()
                            )
                        else:
                            valor_celula = "X"

            linha_colab[dia_num_str] = valor_celula

        dados_para_df.append(linha_colab)

    # --- Criação do DataFrame Principal (só com dados dos colaboradores) ---
    df_principal = pd.DataFrame(
        dados_para_df, columns=colunas_finais
    )  # Garante a ordem

    # --- Exportação para Excel usando XlsxWriter para inserir a linha extra ---
    try:
        # Cria o objeto writer
        writer = pd.ExcelWriter(caminho_arquivo, engine="xlsxwriter")

        # Escreve o DataFrame principal, INCLUINDO o cabeçalho padrão
        df_principal.to_excel(
            writer,
            sheet_name=f"Escala {mes_nome} {ano}",
            index=False,
            header=True,
            startrow=1,
        )  # Começa na linha 1 (abaixo do cabeçalho)

        # Escreve a linha dos dias da semana ACIMA dos dados, na linha 2 (índice 1 no excel)
        df_dias_semana.to_excel(
            writer,
            sheet_name=f"Escala {mes_nome} {ano}",
            index=False,
            header=False,
            startrow=2,
        )

        # (Opcional) Ajustar largura das colunas - pode precisar de ajustes finos
        workbook = writer.book
        worksheet = writer.sheets[f"Escala {mes_nome} {ano}"]
        worksheet.set_column("A:A", 30)  # Nome
        worksheet.set_column("B:B", 20)  # Cargo
        worksheet.set_column("C:C", 10)  # Matrícula
        worksheet.set_column("D:D", 10)  # Conselho
        worksheet.set_column("E:E", 20)  # Setor
        worksheet.set_column("F:AJ", 4)  # Colunas dos dias (ajuste F:AJ conforme o mês)

        # Salva o arquivo Excel
        writer.close()  # Use close() em vez de save() para xlsxwriter

        print(f"Planilha Excel gerada com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao gerar a planilha Excel: {e}")


def _draw_header(canvas, doc, mes_nome, ano, logo_path):
    """Desenha o cabeçalho com logo e título diretamente no canvas."""
    canvas.saveState()

    page_width, page_height = landscape(letter)
    usable_width = page_width - doc.leftMargin - doc.rightMargin

    # Configuração do Logo - dimensões ainda maiores
    logo_img_obj = None
    logo_max_width = 3.0 * inch  # Aumentado de 2.5 para 3.0
    logo_max_height = 1.2 * inch  # Aumentado de 1.0 para 1.2
    logo_width = 0
    logo_height = 0
    spacing = 0.3 * inch

    # Carrega a logo com alta qualidade
    if logo_path and os.path.exists(logo_path):
        try:
            # Usa preserveAspectRatio para manter qualidade
            from reportlab.lib.utils import ImageReader

            img_reader = ImageReader(logo_path)
            img_width, img_height = img_reader.getSize()

            # Calcula proporção para manter aspecto
            aspect = img_width / float(img_height)

            # Ajusta dimensões mantendo aspecto (prioriza altura para melhor visibilidade)
            if aspect > (logo_max_width / logo_max_height):
                # Imagem mais larga - limita pela largura
                logo_width = logo_max_width
                logo_height = logo_max_width / aspect
            else:
                # Imagem mais alta - limita pela altura
                logo_height = logo_max_height
                logo_width = logo_max_height * aspect

            # Cria o objeto Image com as dimensões calculadas
            logo_img_obj = Image(logo_path, width=logo_width, height=logo_height)

            print(
                f'✓ Logo carregada: {logo_width:.2f}" x {logo_height:.2f}" (original: {img_width}x{img_height}px)'
            )
        except Exception as e:
            print(f"✗ Erro ao carregar logo: {e}")
            logo_img_obj = None
            logo_width = 0
            logo_height = 0

    # Configuração do Título - alinhamento e tamanho
    styles = getSampleStyleSheet()
    style_titulo_header = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Heading1"],
        fontSize=20,  # Aumentado de 18 para 20
        textColor=colors.black,
        alignment=TA_LEFT,
        fontName="Helvetica-Bold",
        leading=24,  # Aumentado de 22 para 24
    )

    titulo_html = f'ESCALA <font color="red">UMPA STA. LUZIA</font> - {mes_nome} {ano}'
    title_paragraph = Paragraph(titulo_html, style_titulo_header)

    # Calcula largura disponível para o título
    if logo_img_obj:
        available_width_for_title = usable_width - logo_width - spacing
    else:
        available_width_for_title = usable_width
        spacing = 0

    # Wrap do título
    title_w, title_h = title_paragraph.wrapOn(
        canvas, available_width_for_title, 1 * inch
    )

    # Validação de dimensões
    if not title_w or title_w <= 0:
        title_w = available_width_for_title
    if not title_h or title_h <= 0:
        title_h = 0.3 * inch

    # Calcula altura máxima do header
    max_h = max(logo_height, title_h) if logo_img_obj else title_h

    # Posição Y - CORRIGIDO: desenha DENTRO da margem superior
    # O topo da página é page_height
    # Queremos que o header fique logo abaixo do topo, ANTES do conteúdo
    header_top_y = page_height - 0.3 * inch  # Começa 0.3" abaixo do topo
    header_bottom_y = header_top_y - max_h  # Base do header

    # Centraliza horizontalmente
    if logo_img_obj:
        total_content_width = logo_width + spacing + title_w
    else:
        total_content_width = title_w

    start_x = doc.leftMargin + (usable_width - total_content_width) / 2.0
    current_x = start_x

    # Desenha Logo (alinhado na base com o título)
    if logo_img_obj and logo_width > 0:
        # Alinha pela base (bottom) em vez de centralizar verticalmente
        logo_y = header_bottom_y
        try:
            logo_img_obj.drawOn(canvas, current_x, logo_y)
            current_x += logo_width + spacing
        except Exception as e:
            print(f"✗ Erro ao desenhar logo: {e}")

    # Desenha Título (alinhado na base com a logo)
    title_y = header_bottom_y
    try:
        title_paragraph.drawOn(canvas, current_x, title_y)
    except Exception as e:
        print(f"✗ Erro ao desenhar título: {e}")

    # Linha Separadora (logo abaixo do header)
    line_y = header_bottom_y - 0.1 * inch
    canvas.setStrokeColor(colors.HexColor("#C6E0B4"))
    canvas.setLineWidth(0.8)
    canvas.line(doc.leftMargin, line_y, page_width - doc.rightMargin, line_y)

    canvas.restoreState()


def _draw_footer(canvas, doc, gerado_por_usuario=None):
    """Desenha o rodapé com legenda e info de geração."""
    canvas.saveState()

    page_width = landscape(letter)[0]
    usable_width = page_width - doc.leftMargin - doc.rightMargin

    # Legenda
    data = [
        ["LEGENDA", "F", "FOLGA", "HE", "HORA EXTRA", "FE", "FÉRIAS"],
        ["", "AT", "ATESTADO", "AF", "AFASTADO INSS.", "LM", "LICENÇA MATERNIDADE"],
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
    legend_table.setStyle(
        TableStyle(
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
    )

    legend_width = sum(col_widths)
    start_x_legend = doc.leftMargin + (usable_width - legend_width) / 2.0
    legend_table.wrapOn(canvas, doc.width, doc.bottomMargin)
    legend_table.drawOn(canvas, start_x_legend, 0.55 * inch)

    # Informações de Geração
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#666666"))

    now = datetime.now()
    data_hora_geracao = now.strftime("%d/%m/%Y às %H:%M:%S")

    # Esquerda: Desenvolvido por
    canvas.drawString(doc.leftMargin, 0.3 * inch, "Desenvolvido por NetCode")

    # Centro: Data/Hora
    center_x = doc.leftMargin + (usable_width / 2.0)
    canvas.drawCentredString(center_x, 0.3 * inch, f"Impresso em: {data_hora_geracao}")

    # Direita: Usuário
    texto_usuario = f"Gerado por: {gerado_por_usuario if gerado_por_usuario else 'Usuário Desconhecido'}"
    canvas.drawRightString(page_width - doc.rightMargin, 0.3 * inch, texto_usuario)

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


def exportar_para_pdf(
    dados_escala,
    ano,
    mes,
    caminho_arquivo,
    ordenar_por="setor",
    gerado_por_usuario=None,
):
    """Gera múltiplas tabelas (uma por setor), com espaçamento,
    e garante que não quebrem entre páginas, colorindo afastamentos em blocos."""

    # Busca a logo em múltiplos caminhos
    possible_logo_paths = [
        resource_path(os.path.join("src", "geradorEscalas", "assets", "logoPDF.png")),
        os.path.join("src", "geradorEscalas", "assets", "logoPDF.png"),
        os.path.join("assets", "logoPDF.png"),
        os.path.join("geradorEscalas", "assets", "logoPDF.png"),
        "logoPDF.png",
    ]

    logo_path = None
    for path in possible_logo_paths:
        if os.path.exists(path):
            logo_path = path
            print(f"✓ Logo encontrada: {path}")
            break

    if not logo_path:
        print("⚠ Logo não encontrada - PDF será gerado sem logo")
        print(f"  Diretório atual: {os.getcwd()}")

    # Configurações
    if ordenar_por == "cargo":
        primary_group_key = "cargo"
        secondary_info_key = "setor"
        primary_group_label = "CARGO"
        secondary_column_header = "SETOR"
    else:
        primary_group_key = "setor"
        secondary_info_key = "cargo"
        primary_group_label = "SETOR"
        secondary_column_header = "CARGO"

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

    MOTIVO_ABBREV = {
        "ATESTADO": "AT",
        "AFASTADO INSS.": "AF",
        "AFASTADO INSS": "AF",
        "FÉRIAS": "FE",
        "FERIAS": "FE",
        "LICENÇA MATERNIDADE": "LM",
        "LICENCA MATERNIDADE": "LM",
        "HORA EXTRA": "HE",
        "FOLGA": "F",
    }

    MOTIVO_COLORS = {
        "ATESTADO": colors.red,
        "AFASTADO INSS.": colors.HexColor("#00B050"),
        "AFASTADO INSS": colors.HexColor("#00B050"),
        "ATESTADO ACOMP.": colors.HexColor("#00B050"),
        "ATESTADO ACOMP": colors.HexColor("#00B050"),
        "FÉRIAS": colors.HexColor("#ED7D31"),
        "FERIAS": colors.HexColor("#ED7D31"),
        "LICENÇA MATERNIDADE": colors.HexColor("#7030A0"),
        "LICENCA MATERNIDADE": colors.HexColor("#7030A0"),
        "HORA EXTRA": colors.HexColor("#00B0F0"),
        "FOLGA": colors.yellow,
        "_DEFAULT_": colors.lightgrey,
    }

    TAMANHO_BLOCO_IDEAL = 5

    # Agrupa os dados
    grupos_primarios = {}
    for matricula, info in dados_escala.items():
        grupo_primario_val = info.get(
            primary_group_key, f"{primary_group_label} NÃO DEFINIDO"
        ).upper()
        escala_tipo = info.get("escala", "N/A").upper()
        tipo_turno_bruto = info.get("Tipo_turno", "")

        if tipo_turno_bruto:
            tipo_turno_limpo = tipo_turno_bruto.split(" ")[0].upper()
            escala_nome_grupo = f"{escala_tipo} - {tipo_turno_limpo}"
        else:
            escala_nome_grupo = escala_tipo

        if grupo_primario_val not in grupos_primarios:
            grupos_primarios[grupo_primario_val] = {}
        if escala_nome_grupo not in grupos_primarios[grupo_primario_val]:
            grupos_primarios[grupo_primario_val][escala_nome_grupo] = []
        grupos_primarios[grupo_primario_val][escala_nome_grupo].append(
            (matricula, info)
        )

    # Configuração do documento - margem superior ajustada para logo maior
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=landscape(letter),
        topMargin=1.6 * inch,  # Aumentada para acomodar logo maior (1.2" + espaços)
        bottomMargin=1.2 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )
    elementos = []

    # Estilos
    styles = getSampleStyleSheet()
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

    # Cabeçalhos das tabelas
    cabecalho_dias = ["NOME", secondary_column_header, "MATRÍCULA", "CONSELHO"] + [
        str(i) for i in range(1, num_dias + 1)
    ]
    cabecalho_semana = ["", "", "", ""]
    for dia_num in range(1, num_dias + 1):
        dia_semana_num = weekday(ano, mes, dia_num)
        cabecalho_semana.append(dias_semana_abrev[dia_semana_num])

    # Larguras das colunas
    largura_col_nome = 2.0 * inch
    largura_secondary_col = 1.2 * inch
    largura_matricula = 0.7 * inch
    largura_conselho = 0.7 * inch
    largura_disponivel = (
        landscape(letter)[0]
        - largura_col_nome
        - largura_secondary_col
        - largura_matricula
        - largura_conselho
        - 1 * inch
    )
    largura_col_dia = largura_disponivel / num_dias
    larguras_colunas = [
        largura_col_nome,
        largura_secondary_col,
        largura_matricula,
        largura_conselho,
    ] + ([largura_col_dia] * num_dias)
    colunas_totais = len(larguras_colunas)

    # Estilos base da tabela
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

    # Constrói as tabelas (mantém o resto do código original)
    for grupo_primario_nome, escalas_do_grupo in sorted(grupos_primarios.items()):
        dados_para_esta_tabela = [cabecalho_dias, cabecalho_semana]
        estilos_para_esta_tabela = list(estilos_base) + list(estilos_fds_cabecalho)
        row_index = 2

        for i, (escala_nome_grupo, colaboradores_do_grupo) in enumerate(
            sorted(escalas_do_grupo.items())
        ):
            titulo_setor_cell = ""
            if i == 0:
                titulo_setor_cell = Paragraph(grupo_primario_nome, style_setor_row)
            titulo_escala_cell = Paragraph(escala_nome_grupo.upper(), style_escala_row)
            linha_titulo = [titulo_setor_cell, "", "", "", titulo_escala_cell] + [
                ""
            ] * (colunas_totais - 5)
            dados_para_esta_tabela.append(linha_titulo)

            cor_fundo_titulo = (
                colors.HexColor("#C6E0B4") if i == 0 else colors.HexColor("#E2EFD9")
            )
            if i == 0:
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
                secondary_info_val = info.get(secondary_info_key, "")
                conselho_real = info.get("conselho", "")

                linha_colab = [
                    Paragraph(nome_colab, style_cell_wrap_left),
                    Paragraph(secondary_info_val, style_cell_wrap_center),
                    str(matricula),
                    str(conselho_real),
                ]

                dias_trabalho = {turno["dia"]: turno for turno in info.get("dias", [])}
                escala_data_base = info.get("escala_data_base")
                afastamento_inicio = info.get("afastamento_inicio")
                afastamento_fim = info.get("afastamento_fim")
                afastamento_motivo_geral = info.get("afastamento_motivo")

                cor_afastamento = None
                motivo_abbrev = ""
                if afastamento_motivo_geral:
                    motivo_upper = afastamento_motivo_geral.upper().strip()
                    cor_afastamento = MOTIVO_COLORS.get(
                        motivo_upper, MOTIVO_COLORS["_DEFAULT_"]
                    )
                    motivo_abbrev = MOTIVO_ABBREV.get(
                        motivo_upper, motivo_upper[:2].upper()
                    )

                dias_afastamento = set()
                if (
                    afastamento_inicio
                    and afastamento_fim
                    and isinstance(afastamento_inicio, date)
                    and isinstance(afastamento_fim, date)
                ):
                    primeiro_dia_mes = date(ano, mes, 1)
                    ultimo_dia_mes = date(ano, mes, num_dias)

                    if (
                        afastamento_inicio <= ultimo_dia_mes
                        and afastamento_fim >= primeiro_dia_mes
                    ):
                        data_inicio_no_mes = max(afastamento_inicio, primeiro_dia_mes)
                        data_fim_no_mes = min(afastamento_fim, ultimo_dia_mes)
                        for dia_num in range(
                            data_inicio_no_mes.day, data_fim_no_mes.day + 1
                        ):
                            dias_afastamento.add(dia_num)

                for dia_num in range(1, num_dias + 1):
                    valor_celula_str = ""
                    if dia_num in dias_afastamento:
                        valor_celula_str = ""
                    else:
                        try:
                            data_do_dia = date(ano, mes, dia_num)
                            if not escala_data_base or data_do_dia >= escala_data_base:
                                valor_celula_str = "F"
                                if dia_num in dias_trabalho:
                                    valor_celula_str = "X"
                        except ValueError:
                            valor_celula_str = ""
                    linha_colab.append(valor_celula_str)

                dados_para_esta_tabela.append(linha_colab)

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

                if dias_afastamento and cor_afastamento:
                    dias_ordenados = sorted(dias_afastamento)
                    i = 0
                    while i < len(dias_ordenados):
                        dias_restantes = len(dias_ordenados) - i
                        tamanho_bloco = min(TAMANHO_BLOCO_IDEAL, dias_restantes)
                        if (
                            dias_restantes - tamanho_bloco > 0
                            and dias_restantes - tamanho_bloco < 3
                        ):
                            tamanho_bloco = dias_restantes // 2

                        primeiro_dia_bloco = dias_ordenados[i]
                        ultimo_dia_bloco = dias_ordenados[i + tamanho_bloco - 1]
                        start_col = primeiro_dia_bloco + 3
                        end_col = ultimo_dia_bloco + 3

                        estilos_para_esta_tabela.append(
                            ("SPAN", (start_col, row_index), (end_col, row_index))
                        )
                        estilos_para_esta_tabela.append(
                            (
                                "BACKGROUND",
                                (start_col, row_index),
                                (end_col, row_index),
                                cor_afastamento,
                            )
                        )
                        estilos_para_esta_tabela.append(
                            (
                                "ALIGN",
                                (start_col, row_index),
                                (end_col, row_index),
                                "CENTER",
                            )
                        )
                        estilos_para_esta_tabela.append(
                            (
                                "FONTNAME",
                                (start_col, row_index),
                                (end_col, row_index),
                                "Helvetica-Bold",
                            )
                        )
                        estilos_para_esta_tabela.append(
                            (
                                "FONTSIZE",
                                (start_col, row_index),
                                (end_col, row_index),
                                8,
                            )
                        )

                        if cor_afastamento in [colors.red, colors.HexColor("#7030A0")]:
                            estilos_para_esta_tabela.append(
                                (
                                    "TEXTCOLOR",
                                    (start_col, row_index),
                                    (end_col, row_index),
                                    colors.white,
                                )
                            )

                        linha_colab[start_col] = motivo_abbrev
                        i += tamanho_bloco

                for dia_num in range(1, num_dias + 1):
                    if (
                        weekday(ano, mes, dia_num) >= 5
                        and dia_num not in dias_afastamento
                    ):
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

        tabela_grupo_primario = Table(
            dados_para_esta_tabela, colWidths=larguras_colunas
        )
        tabela_grupo_primario.setStyle(TableStyle(estilos_para_esta_tabela))
        bloco_para_manter_junto = [tabela_grupo_primario, Spacer(1, 0.2 * inch)]
        elementos.append(KeepTogether(bloco_para_manter_junto))

    # Função de template para header e footer
    def draw_page_template(canvas, doc):
        _draw_header(canvas, doc, mes_nome, ano, logo_path)
        _draw_footer(canvas, doc, gerado_por_usuario)

    # Constrói o documento
    doc.build(
        elementos, onFirstPage=draw_page_template, onLaterPages=draw_page_template
    )
    print(f"✓ PDF gerado com sucesso: {caminho_arquivo}")
