import streamlit as st
import pandas as pd
import altair as alt

# Configura página
st.set_page_config(page_title="Relatório de Competências", layout="wide")

st.write("# Relatório de Competências Gestão Contábil - mês de Setembro 2025")

# Carrega planilha
df = pd.read_excel("gestta.busca (1).xlsx")

st.write("## Relatório dos Responsáveis")

# Agrupa por Responsável e Status e conta competências
relatorio = (
    df.groupby(["Responsável", "Status"])
    .size()
    .unstack(fill_value=0)  # transforma Status em colunas
    .reset_index()
)

# Cria coluna Total Geral incluindo ABERTO, CONCLUIDO e IMPEDIMENTO
relatorio["Total Geral"] = relatorio.sum(axis=1, numeric_only=True)

# Calcula percentual concluído (CONCLUIDO / (ABERTO + CONCLUIDO + IMPEDIMENTO))
if "CONCLUIDO" in relatorio.columns:
    relatorio["% Concluído"] = (relatorio["CONCLUIDO"] / relatorio["Total Geral"]) * 100
else:
    relatorio["% Concluído"] = 0

# Exibe tabela
st.write("### Visão Geral por Responsável")
st.dataframe(relatorio)

# Gráfico de barras com Status ABERTO, CONCLUIDO e IMPEDIMENTO
st.write("### Gráfico da Análise Geral")
status_cols = [col for col in ["ABERTO", "CONCLUIDO", "IMPEDIMENTO"] if col in relatorio.columns]
st.bar_chart(relatorio.set_index("Responsável")[status_cols])

# Percentual concluído
st.write("### Percentual dos Responsáveis: Competências Concluídas")

st.dataframe(relatorio[["Responsável", "% Concluído"]])

# Criar gráfico de barras para % concluído
grafico_percentual = (
    alt.Chart(relatorio)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X("% Concluído", title="Percentual Concluído (%)"),
        y=alt.Y("Responsável", sort='-x', title="Responsável"),
        tooltip=["Responsável", "% Concluído"]
    )
    .properties(width=700, height=400, title="Percentual de Competências Concluídas por Responsável")
)

st.altair_chart(grafico_percentual, use_container_width=True)

# Resumo geral
st.metric("Total de Competências", relatorio["Total Geral"].sum())

# Agrupa por Status para obter totais gerais
totais_status = df.groupby("Status").size().to_dict()

status_aberto = totais_status.get("ABERTO", 0)
status_concluido = totais_status.get("CONCLUIDO", 0)
status_impedimento = totais_status.get("IMPEDIMENTO", 0)

total = status_aberto + status_concluido + status_impedimento
percentual_concluido = (status_concluido / total) * 100 if total != 0 else 0

st.write("## Relatório Geral")
st.write(f"### Percentual de competências concluídas: {percentual_concluido:.2f}%")

# Prepara dados para gráfico de barras
dados_grafico = pd.DataFrame({
    "Status": ["ABERTO", "CONCLUIDO", "IMPEDIMENTO"],
    "Quantidade": [status_aberto, status_concluido, status_impedimento]
})

# Cria gráfico
grafico = alt.Chart(dados_grafico).mark_bar().encode(
    x="Status:N",
    y="Quantidade:Q",
    color="Status:N",
    tooltip=["Status", "Quantidade"]
).properties(
    width=600,
    height=400
)

st.altair_chart(grafico, use_container_width=True)


# # SUGESTÕES
# # Sugerir criar relatórios desenvolvidos por IA de acordo com os gráficos -> teria que pagar a IA