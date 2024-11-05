from flask import Flask, render_template, request, session
import pandas as pd
import pickle
from sklearn.metrics import *

with open(r'possiveis_assinantes/possiveis_assinantes.pkl', 'rb') as arquivo:  
    modelo = pickle.load(arquivo)

app = Flask(__name__)
app.secret_key = '123leontis#'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interesse_em_arte', methods = ['POST'])
def interesse_em_arte():
    
    # Armazenando respostas utilizando 'session'
    session['Em qual faixa etária você se encaixa?'] = request.form.get('idade')
    session['Qual a renda per capita da sua casa?'] = request.form.get('renda_per_capita')
    session['Há quanto tempo você se interessa por arte?'] = request.form.get('tempo_interesse')

    return render_template('interesse_em_arte.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':

        # Armazenando respostas utilizando 'session'
        session['Qual das opções de arte abaixo você mais gosta?'] = request.form.get('arte_interesse')

        # Verificando se passou pela página de 'interesse_em_arte'
        if session.get('Qual das opções de arte abaixo você mais gosta?') == None:
            return render_template('formulario_enviado.html', predicao=False) # Retornando página de 'formulario_enviado' finalizando a pesquisa
        
        # Armazenando respostas utilizando 'session'
        session['Com que frequência você vai aos museus?'] = request.form.get('frequencia_museus')
        session['Você já participou de algum curso ou atividade relacionada à arte?'] = request.form.get('curso_arte')
        session['Você segue artístas ou páginas relacionadas à arte nas rede sociais?'] = request.form.get('segue_artistas')
        session['Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.'] = request.form.get('experiencia_museu')
        session['O que mais te atrai em visitar museus ou exposições de arte?'] = request.form.get('atracao_museu')
        session['Você sente falta de mais informações sobre as obras nos museus?'] = request.form.get('info_obras')
        session['Você procura saber sobre essas informações faltantes?'] = request.form.get('info_busca')
        session['Você encontra o que precisa/esperava ao pesquisar?'] = request.form.get('acha_informacao')

        # Passando dados coletados da pesquisa para um DataFrame
        dados = pd.DataFrame(session, index=[0])

        # Tratando dados nulos
        dados.fillna({'Qual das opções de arte abaixo você mais gosta?': 'Não se interessa por arte', 'Com que frequência você vai aos museus?': 'Não se interessa por arte', 'Você já participou de algum curso ou atividade relacionada à arte?': 'Não se interessa por arte', 'Você segue artístas ou páginas relacionadas à arte nas rede sociais?': 'Não se interessa por arte', 'Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.': 'Não se interessa por arte', 'O que mais te atrai em visitar museus ou exposições de arte?': 'Não se interessa por arte'}, inplace=True)
        dados.fillna({'Você sente falta de mais informações sobre as obras nos museus?': 'Não vai a museus'}, inplace=True)
        dados.fillna({'Você procura saber sobre essas informações faltantes?': 'Não sente falta de informações'}, inplace=True)
        dados.fillna({'Você encontra o que precisa/esperava ao pesquisar?': 'Não procura essas informações'}, inplace=True)


        # Reordenando DataFrame na ordem na qual o StandardScaler foi ajustado
        dados = dados[modelo['colunas']]

        # Transformando dados em numérico
        for i in dados:
            if dados[i].dtype == object:
                if i in modelo['aplicacao_de_pesos'].keys():
                    print("Com peso:", i)
                    dados[i] = dados[i].map(modelo['aplicacao_de_pesos'][i]) # Aplicando pesos nas colunas mais relevantes
                else:
                    print("Sem peso:", i)
                    dados[i] = dados[i].map(modelo['numerico'][i]) # Apenas transformando em númerico as outras colunas no mesmo padrão que foram transformadas no treino do modelo

        dados = modelo['StandardScaler'].transform(dados) # Aplicando StandardScaler
        dados = modelo['PCA'].transform(dados) # Aplicando o PCA

        predict = modelo['modelo'].predict(dados) # Predizendo os dados
        predict = bool((predict == True)[0]) # Transformando o resultado em booleano
        
    return render_template('formulario_enviado.html',predicao=predict) # Página de finalização da pesquisa


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
