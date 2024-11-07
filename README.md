# Análise de Dados - Leontis 

[![NPM](https://img.shields.io/npm/l/react)](https://github.com/leontis2024/analise_de_dados/blob/main/LICENSE)

## Descrição do Projeto

Este repositório contém a análise de dados para o desenvolvimento do Leontis, aplicativo de cultura e arte voltado a museus e a experiência do usuário ao visitá-los. O objetivo principal é explorar informações públicas sobre museus e entender melhor este universo, além de criar modelos inteligentes para a predição de informações relevantes ao desenvolvimento do mesmo. Como dizer se uma pessoa é um usuário em potencial ou se um usuário é um possível assinante, isto de acordo com características como idade, renda per capita da residência, tempo de interesse em arte em anos, tipo de arte favorita, se utiliza de guias, frequência de ida a museus, entre outras features. Neste repositório também contém RPAs que servem para a sincronização de dois bancos de dados e suas validações necessárias de acordo com as regras de normalização. E a criação de um modelo de deep learning para o escaneamento de obras que retorna o índice de identificação da mesma, na qual será passada por uma api, em flask, para implementação no mobile.

## Estrutura do Repositório

O repositório está organizado nas seguintes pastas e arquivos principais:

- **RPA Git/**: Códigos de RPA e conexão aos bancos.
- **possiveis_assinantes/**: Site com formulário e implementação de modelo preditivo.
- **notebooks/**: Notebooks Jupyter com as análises exploratórias e criação dos modelos preditivos.
- **bases/**: Bases de dados utilizadas para as análises e treinamento dos modelos.
- **README.md**: Documentação do projeto, objetivos e instruções de uso.

## Tecnologias Utilizadas

- **Python**: Linguagem principal para manipulação e análise de dados.
- **Pandas e NumPy**: Para manipulação e análise de dados.
- **Matplotlib e Seaborn**: Para criação de gráficos e visualizações de dados.
- **Jupyter Notebook**: Para organização das análises e visualizações.
- **Scikit-Learn**: Para criação de modelos inteligentes de predição.
- **Flask**: Para pegar os dados enviados pelo forms, tratar e realizar a predição

## Objetivos

1. **Predição de usuários**: Dizer se uma pessoa é ou não um possível usuário.
2. **Predição de assinantes**: Dizer se um usuário é ou não um assinante em potencial.
3. **Análise exploratória sobre museus**: Identificar insights e informações sobre museus nacionais, afim de fazer possíveis atualizações e mudanças no app.
4. **RPA**: Transportar as informações entre os bancos do Primeiro Ano e do Segundo Ano.

## Como Executar as Análises

1. Clone este repositório:

   git clone https://github.com/leontis2024/analise_de_dados.git

2. Instale as dependências:

   pip install -r Requirements.txt

3. Acesse os notebooks em **notebooks/** para acompanhar as análises e execute o **possiveis_assinantes/app.py** para instanciar a página web com flask.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](https://github.com/leontis2024/analise_de_dados/blob/main/LICENSE) para mais detalhes.
