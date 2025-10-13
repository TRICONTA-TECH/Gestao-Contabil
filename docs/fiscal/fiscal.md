# Relatórios do Setor Fiscal

## 1. Introdução

<div style="text-align: justify; text-indent: 2cm;">
Esse código foi produzido em <b>Python</b>, utilizando o framework <a href="https://streamlit.io/"><b>Streamlit</b></a> e a biblioteca <a href="https://pandas.pydata.org/"><b>Pandas</b></a>. Ele tem como objetivo gerar relatórios de colaboradores do <b>setor fiscal</b> da empresa com tabelas e gráficos. O dashboard gerado permite uma visualização mais clara das tarefas realizadas pelos colaboradores no mês de análise, como:
</div>
<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Quantidade de tarefas concluídas por colaborador;
<li> Quantidade de tarefas abertas por colaborador;
<li> Análise da quantidade de parcelamentos abertos, concluídos e desconsiderados do setor;
<li> Listagem de parcelamentos abertos;
<li> Porcentagem de conclusão de DLFs de clientes; 
<li> Quantidades de DLFs por Responsável;
<li> Porcentagem de conclusão de tarefas do setor;
<li> Porcentagem de conclusão de tarefas por colaborador. 
</ul>

## 2. Arquivos Necessários
<div style="text-align: justify; text-indent: 2cm;">
Os arquivos necessários para o código são:
</div>

<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Planilha Excel (.xlsx) filtrada pelo setor fiscal gerada a partir do sistema <b>Gestta</b>. 
</ul>

## 3. Passos Necessários
<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Colocar o arquivo.xlsx no mesmo diretório da pasta do código Python (pasta fiscal)
<li> Alterar o nome da planilha na importação, se necessário, na <b> linha 30</b>
<li> Rodar o Streamlit com o comando 
        <code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">
            python -m streamlit run fiscal.py
        </code>
</ul>

## 4. Histórico de Versão

| Versão |Descrição     |Autor                                       |Data |    
|:-:     | :-:          | :-:                                        | :-:        |
|1.0     |Criação do documento|[Mayara Marques](https://github.com/maymarquee)| 13/10/2025 | 