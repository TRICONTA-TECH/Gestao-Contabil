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
Os arquivos necessários para a geração do relatório são:
</div>

<ul style="text-align: justify; padding-left: 4em; margin-top: 0.5em;">
<li> Planilha Excel (.xlsx) filtrada pelo setor fiscal gerada a partir do sistema <b>Gestta</b>. 
</ul>

## 3. Deploy
<div style="text-align: justify; text-indent: 2cm;">
O deploy do relatório foi realizado pelo Streamlit e pode ser acessado pelo link: <a href="https://gestao-contabil-fiscal.streamlit.app/">https://gestao-contabil-fiscal.streamlit.app/</a>.
</div>

## 4. Histórico de Versão

| Versão |Descrição     |Autor                                       |Data |    
|:-:     | :-:          | :-:                                        | :-:        |
|1.0     |Criação do documento|[Mayara Marques](https://github.com/maymarquee)| 13/10/2025 | 
|1.1     |Adiciona documentação do deploy|[Mayara Marques](https://github.com/maymarquee)| 18/11/2025 | 