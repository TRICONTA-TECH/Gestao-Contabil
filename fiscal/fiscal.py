import pandas as pd
import streamlit as st
import unicodedata
import altair as alt
import datetime as dt
import locale

st.set_page_config(page_title="Setor Fiscal", layout="wide")

# obtem mês e ano atual
data_atual = dt.datetime.now()
mes_nome = data_atual.strftime("%B de %Y")

# localiza para português se disponível
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    mes_nome = data_atual.strftime("%B de %Y")
except locale.Error:
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_nome = f"{meses_pt[data_atual.month]} de {data_atual.year}"

st.write(f"# Relatório Setor Fiscal - {mes_nome}")

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip().lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto


etapas_dlf = {
    "dlf 1": ("DLF 1ª - Recebimento de Informações Fiscais", 25.0),
    "dlf 2": ("DLF 2ª - Escrituração e apuração", 50.0),
    "dlf 3": ("DLF 3ª - Revisão E Conferência", 75.0),
    "dlf 4": ("DLF 4ª - Envio Dos Impostos", 100.0),
    "dlf 5": ("DLF 5ª - Dossiê", 100.0),
    "dlf - escrituracao concluida": ("DLF - Escrituração Concluída", 100.0)
}

etapa_para_pct = {v[0]: v[1] for v in etapas_dlf.values()}

uploaded_file = st.file_uploader("Envie a planilha Excel (gestta.busca).", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Por favor, carregue a planilha para gerar o relatório.")
    st.stop()

df_original = pd.read_excel(uploaded_file)
if not df_original.empty:
    df = df_original.copy()

    df["Nome_norm"] = df["Nome"].apply(normalizar_texto)
    df["Cliente"] = df["Cliente"].astype(str).str.strip()
    df["Responsável"] = df["Responsável"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str)

    def identificar_etapa(nome_norm):
        for chave, (etapa_completa, pct) in etapas_dlf.items():
            if chave in nome_norm:
                return etapa_completa
        return None

    df["Etapa DLF"] = df["Nome_norm"].apply(identificar_etapa)

    df_parcelamentos = df[df["Nome_norm"].str.contains("parcelamento", na=False)].copy()
    df_outros = df[~df["Nome_norm"].str.contains("parcelamento", na=False)].copy()

    df_outros["Progresso_Etapa"] = df_outros["Etapa DLF"].map(etapa_para_pct).fillna(0)

    df_outros["Progresso Final (%)"] = df_outros["Progresso_Etapa"]


    df_parcelamentos['Status_norm'] = df_parcelamentos['Status'].astype(str).str.strip().str.upper()
    status_contagem_parc = df_parcelamentos['Status_norm'].value_counts().reset_index()
    status_contagem_parc.columns = ['Status', 'Quantidade']

    parc_concluidos = status_contagem_parc.loc[
        status_contagem_parc['Status'].isin(['CONCLUIDO', 'DESCONSIDERADO']), 'Quantidade'
    ].sum()

    total_tarefas_dlf = len(df_outros)
    total_tarefas_parcelamento = len(df_parcelamentos)

    def verificar_repeticoes(df):
        df_unique = df[["Cliente", "CNPJ/CPF", "Etapa DLF"]].dropna(subset=["Etapa DLF"])
        df_grouped = df_unique.groupby(["Cliente", "CNPJ/CPF"])["Etapa DLF"].nunique().reset_index()
        repetidos = df_grouped[df_grouped["Etapa DLF"] > 1]
        return len(repetidos), repetidos

    num_repetidos, df_repetidos = verificar_repeticoes(df_outros)

    total_tarefas_geral = total_tarefas_dlf + total_tarefas_parcelamento - num_repetidos

    progresso_real_dlf = df_outros["Progresso Final (%)"].sum()
    progresso_real_parcelamentos = parc_concluidos * 100
    total_progresso_real = progresso_real_dlf + progresso_real_parcelamentos
    total_progresso_potencial = total_tarefas_geral * 100 if total_tarefas_geral > 0 else 0
    progresso_geral_final = (
        (total_progresso_real / total_progresso_potencial) * 100
        if total_progresso_potencial > 0
        else 0
    )

    # trata 'DESCONSIDERADO' também como concluído para esta análise
    df_responsavel = df.groupby("Responsável").agg(
        
        Tarefas_Concluidas=('Status', lambda x: x.astype(str).str.strip().str.upper().isin(['CONCLUIDO', 'DESCONSIDERADO']).sum()),
        
        Total_Tarefas=('Status', 'size')
        
    ).reset_index()


    # considera apenas Status == 'ABERTO' como tarefas em aberto (case-insensitive)
    abertas_dlf = df_outros[df_outros["Status"].astype(str).str.strip().str.upper() == "ABERTO"].copy()
    abertas_parc = df_parcelamentos[df_parcelamentos["Status"].astype(str).str.strip().str.upper() == "ABERTO"].copy()

    # conta clientes únicos por responsável entre as tarefas em aberto (Cliente + CNPJ/CPF)
    abertas_dlf['Cliente_Unico'] = abertas_dlf['Cliente'].astype(str).str.strip() + '_' + abertas_dlf['CNPJ/CPF'].astype(str).str.strip()
    abertas_parc['Cliente_Unico'] = abertas_parc['Cliente'].astype(str).str.strip() + '_' + abertas_parc['CNPJ/CPF'].astype(str).str.strip()

    contagem_abertas_dlf = abertas_dlf.drop_duplicates(subset=['Cliente_Unico', 'Responsável']).groupby('Responsável')['Cliente_Unico'].nunique()
    contagem_abertas_parc = abertas_parc.drop_duplicates(subset=['Cliente_Unico', 'Responsável']).groupby('Responsável')['Cliente_Unico'].nunique()

    df_tarefas_abertas = (
        contagem_abertas_dlf.add(contagem_abertas_parc, fill_value=0)
        .astype(int)
        .reset_index()
    )
    df_tarefas_abertas.columns = ["Responsável", "Tarefas Abertas"]

    st.write("## Análise por Responsável")

    st.write("#### Tarefas Concluídas (DLFs)")
    st.dataframe(df_responsavel.sort_values(by="Tarefas_Concluidas", ascending=False), use_container_width=True)

    grafico_responsavel = (
        alt.Chart(df_responsavel)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("Tarefas_Concluidas:Q", title="Total de Tarefas Concluídas"),
            y=alt.Y("Responsável:N", sort="-x", title="Responsável"),
            color=alt.Color("Tarefas_Concluidas:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["Responsável", "Tarefas_Concluidas", "Total_Tarefas"]
        )
        .properties(title="Tarefas Concluídas por Responsável")
    )
    st.altair_chart(grafico_responsavel, use_container_width=True)

    st.write("#### Total de Tarefas em Aberto")
    st.dataframe(df_tarefas_abertas.sort_values(by="Tarefas Abertas", ascending=False), use_container_width=True)

    grafico_abertas = (
        alt.Chart(df_tarefas_abertas)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="salmon")
        .encode(
            x=alt.X("Tarefas Abertas:Q", title="Quantidade de Tarefas Abertas"),
            y=alt.Y("Responsável:N", sort="-x", title="Responsável"),
            tooltip=["Responsável", "Tarefas Abertas"]
        )
        .properties(title="Tarefas em Aberto por Responsável")
    )
    st.altair_chart(grafico_abertas, use_container_width=True)

    st.write("---")
    st.write("## Análise de Parcelamentos")

    col1, col2 = st.columns([2, 1])

    with col1:
        grafico_status = (
            alt.Chart(status_contagem_parc)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("Status:N", title="Status", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Quantidade:Q", title="Quantidade"),
                color=alt.Color("Status:N", scale=alt.Scale(domain=["CONCLUIDO", "ABERTO", "DESCONSIDERADO"], range=["#1f77b4", "salmon", "pink"]), legend=None),
                tooltip=["Status", "Quantidade"]
            )
            .properties(title="Status dos Parcelamentos")
        )
        st.altair_chart(grafico_status, use_container_width=True)

    with col2:
        porcentagem_concluidos = (
            (parc_concluidos / total_tarefas_parcelamento) * 100
            if total_tarefas_parcelamento > 0
            else 0
        )
        st.metric("Total de Parcelamentos", total_tarefas_parcelamento)
        st.metric("Percentual de Concluídos", f"{porcentagem_concluidos:.2f}%")

    st.write("### Parcelamentos em Aberto")
    parcelamentos_abertos = df_parcelamentos[df_parcelamentos["Status"].str.upper() == "ABERTO"]
    st.dataframe(
        parcelamentos_abertos[["Cliente", "Responsável", "Status"]].sort_values(by=["Responsável", "Cliente"]),
        use_container_width=True
    )

    st.write("---")
    st.write("## Andamentos de Cliente por Etapas")
    st.markdown("Considera a porcentagem de progresso dos DLFs por cliente. Se um cliente possui filiais (mesmo nome, CNPJ/CPF diferentes), a média entre filiais é exibida.")


    df_outros['Cliente_clean'] = df_outros['Cliente'].astype(str).str.strip()
    df_outros['CNPJ_clean'] = df_outros['CNPJ/CPF'].astype(str).str.strip()
    df_outros['Cliente_Branch'] = df_outros['Cliente_clean'] + '_' + df_outros['CNPJ_clean']

    etapa_ordem = {
        "DLF 1ª - Recebimento de Informações Fiscais": 1,
        "DLF 2ª - Escrituração e apuração": 2,
        "DLF 3ª - Revisão E Conferência": 3,
        "DLF 4ª - Envio Dos Impostos": 4
    }
    etapa_pct = {
        "DLF 1ª - Recebimento de Informações Fiscais": 25.0,
        "DLF 2ª - Escrituração e apuração": 50.0,
        "DLF 3ª - Revisão E Conferência": 75.0,
        "DLF 4ª - Envio Dos Impostos": 100.0
    }

    # calcula progresso por filial (Cliente_Branch)
    def calcular_progresso_filial(g):
        etapas = g['Etapa DLF'].dropna().unique().tolist()
        # se houver DLF 4, considera 100%
        if any(e == "DLF 4ª - Envio Dos Impostos" for e in etapas):
            return 100.0
        # escolhe a etapa de maior ordem conhecida
        melhor = None
        melhor_ordem = 0
        for e in etapas:
            if e in etapa_ordem and etapa_ordem[e] > melhor_ordem:
                melhor_ordem = etapa_ordem[e]
                melhor = e
        if melhor:
            return etapa_pct.get(melhor, 0.0)
        return 0.0

    df_branch = (
        df_outros.groupby('Cliente_Branch').apply(calcular_progresso_filial).reset_index(name='Progresso_Branch')
    )
    # extrai nome do cliente (antes do underscore) para agregar filiais
    # extrai o nome do cliente de forma segura (separa na última ocorrência do underscore)
    df_branch['Cliente'] = df_branch['Cliente_Branch'].apply(lambda x: x.rsplit('_', 1)[0])

    # média de progresso entre filiais por cliente
    df_progresso_cliente = (
        df_branch.groupby('Cliente')['Progresso_Branch'].mean().reset_index()
    )
    df_progresso_cliente.rename(columns={'Progresso_Branch': 'Progresso (%)'}, inplace=True)
    df_progresso_cliente['Progresso (%)'] = df_progresso_cliente['Progresso (%)'].round(2)

    st.dataframe(df_progresso_cliente.sort_values(by='Progresso (%)', ascending=False), use_container_width=True)

    st.write("### Quantidade de DLFs por Etapa (Visão Geral)")
   
    etapas_principais = [
        "DLF 1ª - Recebimento de Informações Fiscais",
        "DLF 2ª - Escrituração e apuração",
        "DLF 3ª - Revisão E Conferência",
        "DLF 4ª - Envio Dos Impostos"
    ]
   
   # cria identificador único para cliente
    if 'Cliente_Unico' not in df_outros.columns:
        df_outros['Cliente_Unico'] = df_outros['Cliente'].astype(str).str.strip() + '_' + df_outros['CNPJ/CPF'].astype(str).str.strip()
   
    df_etapa_maxima = (
        df_outros.groupby('Cliente_Unico')
        .agg({
            'Etapa DLF': lambda x: max(x, key=lambda y: etapas_principais.index(y) if y in etapas_principais else -1)
        })
        .reset_index()
    )
   
    # conta clientes por etapa
    etapas_contagem = df_etapa_maxima["Etapa DLF"].value_counts().reindex(etapas_principais, fill_value=0)
   
    df_etapas = pd.DataFrame({
        'Etapa': etapas_contagem.index,
        'Quantidade': etapas_contagem.values
    })
   
    grafico_etapas = alt.Chart(df_etapas).mark_bar(
        color='#1f77b4',
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X('Etapa:N', title='Etapa DLF', sort=etapas_principais),
        y=alt.Y('Quantidade:Q', title='Quantidade de Clientes'),
        tooltip=['Etapa', 'Quantidade']
    ).properties(
        title='Distribuição de Clientes por Etapa DLF'
    )
   
    st.altair_chart(grafico_etapas, use_container_width=True)
    
    st.write("### Quantidade de DLFs por Responsável e Etapa")
    
    df_dlf_responsavel = df_outros.groupby(["Responsável", "Etapa DLF"]).size().reset_index(name="Quantidade")
    
    df_dlf_responsavel = df_dlf_responsavel[df_dlf_responsavel["Etapa DLF"].isin(etapas_principais)]
    
    grafico_dlf_responsavel = alt.Chart(df_dlf_responsavel).mark_bar().encode(
        x=alt.X("Quantidade:Q", title="Quantidade de DLFs"),
        y=alt.Y("Responsável:N", title="Responsável"),
        color=alt.Color("Etapa DLF:N", 
                       title="Etapa",
                       scale=alt.Scale(scheme="blues"),
                       sort=etapas_principais),
        tooltip=["Responsável", "Etapa DLF", "Quantidade"]
    ).properties(
        title="Distribuição de DLFs por Responsável e Etapa",
        height=400
    )
    
    st.altair_chart(grafico_dlf_responsavel, use_container_width=True)
    

    st.write("#### Detalhamento por Responsável e Etapa")
    df_pivot = df_dlf_responsavel.pivot(index="Responsável", 
                                      columns="Etapa DLF", 
                                      values="Quantidade").fillna(0)
    df_pivot = df_pivot.reindex(columns=etapas_principais)
    df_pivot["Total"] = df_pivot.sum(axis=1)
    st.dataframe(df_pivot.sort_values(by="Total", ascending=False), use_container_width=True)


df_dlf = df[df["Nome"].str.contains("dlf", case=False, na=False)]


def contar_tarefas_dlf_unicas(df_original: pd.DataFrame):
    df = df_original.copy()
    df.columns = df.columns.str.strip()
    if "Nome" not in df.columns or "Cliente" not in df.columns:
        raise ValueError("O DataFrame precisa ter as colunas 'Nome' e 'Cliente'.")

    
    def normalizar_texto(texto):
        if pd.isna(texto):
            return ""
        texto = str(texto).strip().lower()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        return texto

    etapas_dlf = {
        "dlf 1": ("DLF 1ª - Recebimento de Informações Fiscais", 25.0),
        "dlf 2": ("DLF 2ª - Escrituração e apuração", 50.0),
        "dlf 3": ("DLF 3ª - Revisão E Conferência", 75.0),
        "dlf 4": ("DLF 4ª - Envio Dos Impostos", 100.0),
        "dlf 5": ("DLF 5ª - Dossiê", 100.0),
        "dlf - escrituracao concluida": ("DLF - Escrituração Concluída", 100.0)
    }
    ordem_etapas = [v[0] for v in etapas_dlf.values()]

    df["Nome_norm"] = df["Nome"].astype(str).apply(normalizar_texto)

    def identificar_etapa(nome_norm):
        for chave, (etapa_completa, pct) in etapas_dlf.items():
            if chave in nome_norm:
                return etapa_completa
        return None

    df["Etapa DLF"] = df["Nome_norm"].apply(identificar_etapa)

    df_outros = df[~df["Nome_norm"].str.contains("parcelamento", na=False)].copy()

    df_outros["Cliente"] = df_outros["Cliente"].astype(str).str.strip()

    contagem_por_etapa = df_outros["Etapa DLF"].value_counts().reindex(ordem_etapas, fill_value=0)
    
    total_clientes_dlf = contagem_por_etapa["DLF 1ª - Recebimento de Informações Fiscais"]

    clientes_etapa4 = df_outros.loc[
        df_outros["Etapa DLF"] == "DLF 4ª - Envio Dos Impostos", "Cliente"
    ].dropna().unique()
    total_clientes_etapa4 = len(clientes_etapa4)

    percentual_etapa4 = (total_clientes_etapa4 / total_clientes_dlf * 100) if total_clientes_dlf > 0 else 0.0

    return {
        "total_clientes_dlf": int(total_clientes_dlf),
        "contagem_por_etapa": contagem_por_etapa,
        "total_clientes_etapa4": int(total_clientes_etapa4),
        "percentual_etapa4": float(percentual_etapa4),
        "df_outros": df_outros  # opcional, útil para inspeção
    }

total_clientes_dlf = contar_tarefas_dlf_unicas(df_original)
resultado = contar_tarefas_dlf_unicas(df_original)

total_clientes_dlf = resultado["total_clientes_dlf"] 
total_clientes_geral = df_original["Cliente"].nunique()

percentual_dlf = (total_clientes_dlf / total_clientes_geral * 100) if total_clientes_geral > 0 else 0

contagem_por_etapa = (
        df_dlf.groupby("Nome")["Cliente"]
        .nunique()
        .reset_index()
        .rename(columns={"Nome": "Etapa DLF", "Cliente": "Quantidade de Clientes"})
        .sort_values(by="Etapa DLF")
    )

clientes_etapa4 = df_outros.loc[df_outros["Etapa DLF"] == "DLF 4ª - Envio Dos Impostos", "Cliente"].unique()
total_clientes_etapa4 = len(clientes_etapa4)

percentual_etapa4 = (total_clientes_etapa4 / total_clientes_dlf * 100) if total_clientes_dlf > 0 else 0

st.write("---")
st.write("## Análise de Conclusão por Cliente")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Clientes com DLF", total_clientes_dlf)
col2.metric("Clientes na Etapa de Envio dos Impostos", total_clientes_etapa4)
col3.metric("Percentual do Setor no Envio Dos Impostos", f"{percentual_etapa4:.2f}%")

# gráfico de progresso
df_progresso = pd.DataFrame([
    {"categoria": "Progresso", "percentual": percentual_etapa4, "tipo": "Atual"},
    {"categoria": "Progresso", "percentual": 100 - percentual_etapa4, "tipo": "Restante"}
])

grafico_progresso = alt.Chart(df_progresso).mark_bar().encode(
    y=alt.Y('categoria:N', title=None, axis=None),
    x=alt.X('percentual:Q', title='Percentual de Conclusão (%)'),
    color=alt.Color('tipo:N', 
                   scale=alt.Scale(domain=['Atual', 'Restante'],
                                 range=['#1f77b4', '#e1e1e1']),
                   legend=None)
).properties(
    title='Progresso do Setor na Etapa de Envio Dos Impostos',
    height=100
)


texto_percentual = alt.Chart(pd.DataFrame([{
    'categoria': 'Progresso',
    'percentual': percentual_etapa4/2,  # posição no meio da barra
    'text': f'{percentual_etapa4:.1f}%'
}])).mark_text(
    color='white',
    fontSize=14,
    fontWeight='bold'
).encode(
    y='categoria:N',
    x='percentual:Q',
    text='text:N'
)

st.altair_chart(grafico_progresso + texto_percentual, use_container_width=True)

df_etapa4_chart = pd.DataFrame({
    "Categoria": ["Clientes na Etapa de ", "Outros Clientes"],
    "Quantidade": [total_clientes_etapa4, total_clientes_dlf - total_clientes_etapa4]
})


df_outros["Data de Conclusão"] = pd.to_datetime(df_outros["Data de Conclusão"], errors="coerce")


data_atual = dt.datetime.now()
inicio_mes = dt.datetime(data_atual.year, data_atual.month, 1)

if data_atual.month == 12:
    fim_mes = dt.datetime(data_atual.year + 1, 1, 1) - dt.timedelta(days=1)
else:
    fim_mes = dt.datetime(data_atual.year, data_atual.month + 1, 1) - dt.timedelta(days=1)

df_outros_mes = df_outros[
    (df_outros["Data de Conclusão"] >= inicio_mes) & 
    (df_outros["Data de Conclusão"] <= fim_mes)
].copy()

if 'Cliente_Unico' not in df_outros_mes.columns:
    df_outros_mes['Cliente_Unico'] = df_outros_mes['Cliente'].astype(str).str.strip() + '_' + df_outros_mes['CNPJ/CPF'].astype(str).str.strip()

dias = pd.date_range(inicio_mes, fim_mes, freq="D")

dados_por_dia = []

unique_outros = df_outros['Cliente'].astype(str).str.strip() + '_' + df_outros['CNPJ/CPF'].astype(str).str.strip()
unique_parc = df_parcelamentos['Cliente'].astype(str).str.strip() + '_' + df_parcelamentos['CNPJ/CPF'].astype(str).str.strip()
total_setor = pd.Index(pd.concat([unique_outros, unique_parc], ignore_index=True)).nunique()

for dia in dias:
    df_ate_dia = df_outros_mes[
        (df_outros_mes['Data de Conclusão'].dt.date <= dia.date()) &
        (df_outros_mes['Etapa DLF'] == 'DLF 4ª - Envio Dos Impostos') &
        (df_outros_mes['Status'].astype(str).str.strip().str.upper() == 'CONCLUIDO')
    ]
    concluidos_unicos = df_ate_dia['Cliente_Unico'].dropna().unique()
    cumul_count = len(concluidos_unicos)

    percentual_acumulado = (cumul_count / total_setor * 100) if total_setor > 0 else 0

    dados_por_dia.append({
        'Data': dia.date(),
        'Percentual Dia (%)': None,
        'Percentual Acumulado (%)': percentual_acumulado
    })

df_evolucao = pd.DataFrame(dados_por_dia)

st.write(f"### Evolução Diária dos Clientes na Etapa 4 ({mes_nome})")

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    print("Local 'pt_BR.UTF-8' não encontrado. Usando o local padrão.")

df_evolucao["Data Formatada"] = pd.to_datetime(df_evolucao["Data"]).dt.strftime('%d de %b')
df_evolucao['Percentual Dia (%)'] = df_evolucao['Percentual Dia (%)'].astype(float)
df_evolucao['Percentual Acumulado (%)'] = df_evolucao['Percentual Acumulado (%)'].astype(float)
df_evolucao['Percentual_Acumulado'] = df_evolucao['Percentual Acumulado (%)']

grafico_evolucao = (
    alt.Chart(df_evolucao)
    .mark_line(point=True, strokeWidth=2, color="#1f77b4")
    .encode(
        x=alt.X("Data Formatada:O", title="Data", sort=df_evolucao["Data Formatada"].tolist()),
        y=alt.Y("Percentual_Acumulado:Q", title="Percentual Acumulado do Setor (%)", axis=alt.Axis(format=".2f")),
        tooltip=["Data Formatada", alt.Tooltip("Percentual_Acumulado:Q", format=".3f")]
    )
    .properties(title="Evolução Acumulada - Clientes na Etapa DLF 4 no mês")
)

st.altair_chart(grafico_evolucao, use_container_width=True)

df_dlf4 = df[
    (df["Nome"].str.strip().str.upper() == "DLF 4ª - ENVIO DOS IMPOSTOS") &
    (df["Status"].str.strip().str.upper() == "CONCLUIDO")
].copy()

df_dlf4 = df_dlf4.dropna(subset=["Data de Conclusão"])
df_dlf4["Data de Conclusão"] = pd.to_datetime(df_dlf4["Data de Conclusão"])

df_dlf4 = (
    df_dlf4
    .sort_values(by=["CNPJ/CPF", "Data de Conclusão"])
    .drop_duplicates(subset=["CNPJ/CPF"], keep="first")
)

dados_dlf4 = (
    df_dlf4
    .groupby(["Data de Conclusão", "Responsável"])
    .size()
    .reset_index(name="Tarefas Concluídas")
)


dados_dlf4["Data Formatada"] = dados_dlf4["Data de Conclusão"].dt.strftime("%d de %b")

st.write("### Tarefas de Envio de Impostos Concluídas por Dia e Responsável")


dados_ordenados = dados_dlf4.sort_values(by=["Data de Conclusão", "Responsável"])
tabela_exibicao = dados_ordenados[["Data Formatada", "Responsável", "Tarefas Concluídas"]]
tabela_exibicao = tabela_exibicao.rename(columns={
    "Data Formatada": "Data",
    "Responsável": "Responsável",
    "Tarefas Concluídas": "Qtd. de Tarefas"
})

st.dataframe(tabela_exibicao, use_container_width=True)

grafico_dlf4 = (
    alt.Chart(dados_dlf4)
    .mark_line(point=True, strokeWidth=2)
    .encode(
        x=alt.X("Data Formatada:O", title="Data", sort=dados_dlf4["Data Formatada"].tolist()),
        y=alt.Y("Tarefas Concluídas:Q", title="Quantidade de Tarefas Concluídas"),
        color=alt.Color("Responsável:N", title="Responsável"),
        tooltip=[
            alt.Tooltip("Data Formatada:N", title="Data"),
            alt.Tooltip("Responsável:N", title="Responsável"),
            alt.Tooltip("Tarefas Concluídas:Q", title="Tarefas Concluídas")
        ]
    )
    .properties(
        title="Evolução Diária - DLF 4ª (Envio dos Impostos) Concluídas por Responsável"
    )
)

st.altair_chart(grafico_dlf4, use_container_width=True)
