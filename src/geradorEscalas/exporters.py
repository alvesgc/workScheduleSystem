import pandas as pd
from calendar import monthrange, weekday
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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


def _draw_footer(canvas, doc):
    """
    Função chamada pelo ReportLab para desenhar o rodapé em cada página.
    """
    canvas.saveState()
    canvas.setFont("Helvetica", 8)

    now = datetime.now()
    data_hora_geracao = now.strftime("%d/%m/%Y às %H:%M:%S")

    texto_footer = f"Desenvolvido por NetCode | Impresso em: {data_hora_geracao}"

    canvas.drawCentredString(landscape(letter)[0] / 2.0, 0.5 * inch, texto_footer)

    canvas.restoreState()


def _determinar_sequencia(info_colab):
    """
    Determina se o colaborador está em sequência PAR ou ÍMPAR baseado nos dias de trabalho.
    Retorna 0 para PAR, 1 para ÍMPAR, 2 para outros casos (diarista, etc).
    """
    dias_trabalho = info_colab.get("dias", [])
    if not dias_trabalho:
        return 2

    # Pega o primeiro dia de trabalho
    primeiro_dia = dias_trabalho[0].get("dia")

    if primeiro_dia:
        # Se o primeiro dia é ímpar, está em sequência ÍMPAR
        # Se o primeiro dia é par, está em sequência PAR
        if primeiro_dia % 2 == 1:
            return 1  # ÍMPAR
        else:
            return 0  # PAR

    return 2  # Outros casos


def exportar_para_pdf(dados_escala, ano, mes, caminho_arquivo):
    """Gera uma tabela formatada da escala e a salva em um arquivo PDF profissional,
    agrupando colaboradores por tipo de escala."""
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

    # Mapeamento dos dias da semana
    dias_semana_abrev = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]

    # --- MUDANÇA 1: Agrupamento dos dados ---
    # Em vez de uma lista, criamos um dicionário de grupos
    grupos_de_escala = {}
    for matricula, info in dados_escala.items():
        # Usamos 'info.get("escala")' como a chave do grupo
        escala_nome = info.get("escala", "Sem Escala Definida")
        if escala_nome not in grupos_de_escala:
            grupos_de_escala[escala_nome] = []
        grupos_de_escala[escala_nome].append((matricula, info))

    # --- Criação do Documento (mesmo de antes) ---
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=landscape(letter),
        topMargin=0.5 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )
    elementos = []

    # --- Estilos (mesmo de antes) ---
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
    style_info = ParagraphStyle(
        "InfoStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=3,
        alignment=TA_LEFT,
        fontName="Helvetica",
    )
    
    # --- Título Principal (mesmo de antes) ---
    titulo_html = f'ESCALA <font color="red">UMPA STA. LUZIA</font> - {mes_nome} {ano}'
    elementos.append(Paragraph(titulo_html, style_titulo))
    elementos.append(Spacer(1, 0.1 * inch)) # Adiciona um espaço

    # --- MUDANÇA 2: Definição dos Cabeçalhos (seguindo a imagem) ---
    # Ordem: NOME, SETOR, MATRÍCULA (diferente do seu código original)
    
    # Linha 1: Números dos dias
    cabecalho_dias = ["NOME", "SETOR", "MATRÍCULA"] + [str(i) for i in range(1, num_dias + 1)] + [""]

    # Linha 2: Dias da semana abreviados
    cabecalho_semana = ["", "", ""]  # Células vazias para NOME, SETOR, MATRÍCULA
    for dia_num in range(1, num_dias + 1):
        dia_semana_num = weekday(ano, mes, dia_num)
        cabecalho_semana.append(dias_semana_abrev[dia_semana_num])
    cabecalho_semana.append("")  # Coluna extra vazia

    # --- MUDANÇA 3: Definição das Larguras (seguindo a imagem) ---
    largura_col_nome = 2.2 * inch
    largura_setor = 1.2 * inch
    largura_matricula = 0.8 * inch
    largura_disponivel = (
        landscape(letter)[0]
        - largura_col_nome
        - largura_setor
        - largura_matricula
        - 1 * inch # Margens + coluna extra
    )
    largura_col_dia = largura_disponivel / (num_dias + 1)

    # Nova ordem de larguras
    larguras_colunas = [largura_col_nome, largura_setor, largura_matricula] + [
        largura_col_dia
    ] * (num_dias + 1)


    # --- MUDANÇA 4: Loop principal para criar blocos ---
    
    # Ordena os grupos pelo nome da escala (ex: "DIURNO" antes de "NOTURNO")
    for escala_nome, colaboradores_do_grupo in sorted(grupos_de_escala.items()):
        
        # Adiciona os títulos do bloco (ESCALA e FUNÇÃO)
        elementos.append(Paragraph(f"<b>ESCALA:</b> {escala_nome.upper()}", style_info))
        elementos.append(Paragraph(f"<b>FUNÇÃO:</b> ASG", style_info))
        elementos.append(Spacer(1, 0.1 * inch))

        # --- Ordenação interna do grupo (PAR/ÍMPAR, igual ao seu código) ---
        dados_ordenados_grupo = []
        for matricula, info in colaboradores_do_grupo:
            sequencia = _determinar_sequencia(info)
            dados_ordenados_grupo.append((matricula, info, sequencia))
        
        # Ordena por sequência (0=PAR, 1=ÍMPAR, 2=Outros) e depois por nome
        dados_ordenados_grupo.sort(key=lambda x: (x[2], x[1].get("nome", "")))

        # --- Preparação dos dados da tabela para ESTE GRUPP ---
        dados_tabela_grupo = [cabecalho_dias, cabecalho_semana]

        for matricula, info, _ in dados_ordenados_grupo:
            
            # --- REQUISITO 1: USA O SETOR REAL ---
            setor_real = info.get("setor", "") # Pega o setor real
            
            # Nova ordem da linha: NOME, SETOR, MATRÍCULA
            linha = [
                info.get("nome", matricula),
                setor_real, # <--- Corrigido
                str(matricula),
            ]

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

            linha.append("")  # Coluna extra vazia
            dados_tabela_grupo.append(linha)

        # Cria o objeto Tabela para este grupo
        tabela_grupo = Table(dados_tabela_grupo, colWidths=larguras_colunas)

        # --- MUDANÇA 5: Estilização (cores e alinhamento ajustados) ---
        style = TableStyle(
            [
                # Cabeçalho (Linha 0) - Cor VERDE (para bater com a imagem)
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C6E0B4")), # Verde
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black), # Texto preto
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                
                # Dias da Semana (Linha 1) - Cor VERDE CLARO
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#E2EFD9")), # Verde claro
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.black),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, 1), 7),
                ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                ("VALIGN", (0, 1), (-1, 1), "MIDDLE"),
                
                # Corpo da tabela (Linhas 2+)
                ("FONTNAME", (0, 2), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 2), (-1, -1), 7),
                
                # --- Ajuste de Alinhamento (NOME, SETOR, MATRÍCULA) ---
                ("ALIGN", (0, 2), (0, -1), "LEFT"),    # NOME à esquerda
                ("ALIGN", (1, 2), (1, -1), "CENTER"),  # SETOR centralizado
                ("ALIGN", (2, 2), (2, -1), "CENTER"),  # MATRÍCULA centralizada
                ("ALIGN", (3, 2), (-1, -1), "CENTER"),  # Dias centralizados
                
                ("VALIGN", (0, 2), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("LINEBELOW", (0, 1), (-1, 1), 1, colors.black),
                
                # Padding (mesmo de antes)
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )

        # Cores de fundo alternadas (efeito zebra)
        for i in range(2, len(dados_tabela_grupo)):
            if i % 2 == 0:
                style.add("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F2F2F2"))
            else:
                style.add("BACKGROUND", (0, i), (-1, i), colors.white)

        # Destaque para finais de semana (Sábado ou Domingo)
        for dia_num in range(1, num_dias + 1):
            if weekday(ano, mes, dia_num) >= 5:
                # +3 colunas de offset: NOME, SETOR, MATRÍCULA
                # (Índice 0, 1, 2). O Dia 1 está no índice 3.
                col_index = dia_num + 2 
                style.add(
                    "BACKGROUND",
                    (col_index, 0),
                    (col_index, -1),
                    colors.HexColor("#E7E6E6"),
                )

        tabela_grupo.setStyle(style)

        # Adiciona a tabela do grupo e um espaço
        elementos.append(tabela_grupo)
        elementos.append(Spacer(1, 0.2 * inch))

    # --- Fim do Loop de Blocos ---

    # Constrói o PDF
    doc.build(elementos, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
