from flask import Flask, render_template, request, session
import pandas as pd
import pickle
from sklearn.metrics import *

with open(r'./possiveis_assinantes/possiveis_assinantes.pkl', 'rb') as arquivo:  
    modelo = pickle.load(arquivo)

app = Flask(__name__)
app.secret_key = '123leontis#'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interesse_em_arte', methods = ['POST'])
def interesse_em_arte():
    
    session['Em qual faixa etária você se encaixa?'] = request.form.get('idade')
    session['Qual a renda per capita da sua casa?'] = request.form.get('renda_per_capita')
    session['Há quanto tempo você se interessa por arte?'] = request.form.get('tempo_interesse')

    return render_template('interesse_em_arte.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        session['Qual das opções de arte abaixo você mais gosta?'] = request.form.get('arte_interesse')
        if session.get('Qual das opções de arte abaixo você mais gosta?') == None:
            return render_template('formulario_enviado.html', predicao=False)
        session['Com que frequência você vai aos museus?'] = request.form.get('frequencia_museus')
        session['Você já participou de algum curso ou atividade relacionada à arte?'] = request.form.get('curso_arte')
        session['Você segue artístas ou páginas relacionadas à arte nas rede sociais?'] = request.form.get('segue_artistas')
        session['Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.'] = request.form.get('experiencia_museu')
        session['O que mais te atrai em visitar museus ou exposições de arte?'] = request.form.get('atracao_museu')
        session['Você sente falta de mais informações sobre as obras nos museus?'] = request.form.get('info_obras')
        session['Você procura saber sobre essas informações faltantes?'] = request.form.get('info_busca')
        session['Você encontra o que precisa/esperava ao pesquisar?'] = request.form.get('acha_informacao')
        print(f"{session.get('arte_interesse')}")

        dados = pd.DataFrame(session, index=[0])

        dados.fillna({'Qual das opções de arte abaixo você mais gosta?': 'Não se interessa por arte', 'Com que frequência você vai aos museus?': 'Não se interessa por arte', 'Você já participou de algum curso ou atividade relacionada à arte?': 'Não se interessa por arte', 'Você segue artístas ou páginas relacionadas à arte nas rede sociais?': 'Não se interessa por arte', 'Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.': 'Não se interessa por arte', 'Você já usou um aplicativo de um museu ou relacionado à arte?': 'Não se interessa por arte', 'O que mais te atrai em visitar museus ou exposições de arte?': 'Não se interessa por arte'}, inplace=True)
        dados.fillna({'Você sente falta de mais informações sobre as obras nos museus?': 'Não vai a museus'}, inplace=True)
        dados.fillna({'Você procura saber sobre essas informações faltantes?': 'Não sente falta de informações'}, inplace=True)
        dados.fillna({'De que forma você costuma buscar essas informações?': 'Não procura essas informações', 'Você encontra o que precisa/esperava ao pesquisar?': 'Não procura essas informações'}, inplace=True)

        dados = dados[modelo['colunas']]

        for i in dados:
            if dados[i].dtype == object:
                if i in modelo['aplicacao_de_pesos'].keys():
                    dados[i] = dados[i].map(modelo['aplicacao_de_pesos'][i])
                else:
                    dados[i] = dados[i].map(modelo['numerico'][i])

        dados = modelo['StandardScaler'].transform(dados)
        dados = modelo['PCA'].transform(dados)

        predict = modelo['modelo'].predict(dados)
        predict = bool((predict == True)[0])
        
    return render_template('formulario_enviado.html',predicao=predict)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
