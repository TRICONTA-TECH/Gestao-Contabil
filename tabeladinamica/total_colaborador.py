# Código que gera uma planilha que informa a quantidade de competências por colaborador

import pandas as pd

df = pd.read_excel("gestta.busca (1).xlsx")

# agrupa por responsável e conta as competências
relatorio = df.groupby("Responsável").size().reset_index(name="Competência")

relatorio.to_excel("relatorio_competencias.xlsx", index=False)
