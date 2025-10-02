# Geração de Relatórios

## 1. Introdução

<div style="text-align: justify; text-indent: 2cm;">
Esse código foi produzido em <b>Python</b>, utilizando o framework <a href="https://streamlit.io/"><b>Streamlit</b></a>. Tem como objetivo gerar relatórios de colaboradores com tabelas e gráficos. O dashboard gerado permite uma visualização mais clara das tarefas realizadas pelos colaboradores no mês de análise, como:
</div>
<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Competências em estado "ABERTO";
<li> Competências em estado "CONCLUÍDO";
<li> Porcentagem geral de competências concluídas;
<li> Porcentagem de competências abertas/concluídas por colaborador.
</ul>

## 2. Arquivos Necessários
<div style="text-align: justify; text-indent: 2cm;">
Os arquivos necessários para o código são:
</div>

<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Planilha Excel (.xlsx) gerada a partir do sistema <b>Gestta</b>. 
</ul>

## 3. Passos Necessários
<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Colocar o arquivo.xlsx no mesmo diretório da pasta do código Python
<li> Alterar o nome da planilha na importação, se necessário, no campo <b>"INPUT"</b>
<li> Rodar o Streamlit com o comando 
        <code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">
            python -m streamlit run relatorio.py
        </code>
</ul>

## 4. Histórico de Versão

| Versão |Descrição     |Autor                                       |Data |    
|:-:     | :-:          | :-:                                        | :-:        |
|1.0     |Criação do documento|[Mayara Marques](https://github.com/maymarquee)| 02/10/2025 | 