from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import pickle
from sklearn.metrics import *

with open(r'C:\Users\leticiapitta-ieg\OneDrive - Instituto Germinare\2 ano\Interdiscipinar\analises e predicoes\analise_de_dados_antigo\possiveis_assinantes\possiveis_usuarios.pkl', 'rb') as arquivo:  
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
    print(f"Idade: {session.get('Em qual faixa etária você se encaixa?')}, Renda: {session.get('Qual a renda per capita da sua casa?')}, Tempo de interesse: {session.get('Há quanto tempo você se interessa por arte?')}")

    return render_template('interesse_em_arte.html')

@app.route('/não_interesse', methods=['POST'])
def não_interesse():
    return render_template('não_interesse.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        session['Qual das opções de arte abaixo você mais gosta?'] = request.form.get('arte_interesse')
        session['Com que frequência você vai aos museus?'] = request.form.get('frequencia_museus')
        session['Você já participou de algum curso ou atividade relacionada à arte?'] = request.form.get('curso_arte')
        session['Você segue artístas ou páginas relacionadas à arte nas rede sociais?'] = request.form.get('segue_artistas')
        session['Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.'] = request.form.get('experiencia_museu')
        session['Você já usou um aplicativo de um museu ou relacionado à arte?'] = request.form.get('usou_app')
        session['O que mais te atrai em visitar museus ou exposições de arte?'] = request.form.get('atracao_museu')
        session['Você sente falta de mais informações sobre as obras nos museus?'] = request.form.get('info_obras')
        session['Você procura saber sobre essas informações faltantes?'] = request.form.get('info_busca')
        session['De que forma você costuma buscar essas informações?'] = request.form.get('onde_busca')
        session['Você encontra o que precisa/esperava ao pesquisar?'] = request.form.get('acha_informacao')
        print(f"{session.get('arte_interesse')}")

        session['Usaria o aplicativo?'] = 'Sim'

        dados = pd.DataFrame(session, index=[0])

        dados.fillna({'Qual das opções de arte abaixo você mais gosta?': 'Não se interessa por arte', 'Com que frequência você vai aos museus?': 'Não se interessa por arte', 'Você já participou de algum curso ou atividade relacionada à arte?': 'Não se interessa por arte', 'Você segue artístas ou páginas relacionadas à arte nas rede sociais?': 'Não se interessa por arte', 'Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.': 'Não se interessa por arte', 'Você já usou um aplicativo de um museu ou relacionado à arte?': 'Não se interessa por arte', 'O que mais te atrai em visitar museus ou exposições de arte?': 'Não se interessa por arte'}, inplace=True)
        dados.fillna({'Você sente falta de mais informações sobre as obras nos museus?': 'Não vai a museus'}, inplace=True)
        dados.fillna({'Você procura saber sobre essas informações faltantes?': 'Não sente falta de informações'}, inplace=True)
        dados.fillna({'De que forma você costuma buscar essas informações?': 'Não procura essas informações', 'Você encontra o que precisa/esperava ao pesquisar?': 'Não procura essas informações'}, inplace=True)

        mapeamento_tipo_arte = {'Não se interessa por arte': 0, 'Pintura': 8, 'Fotografia': 8, 'Escultura': 6, 'Arquitetura e Urbanismo': 5, 'Arte digital': 4,'Arte de rua/grafite': 3}
        mapeamento_frequencia = {'Não se interessa por arte': 0, 'Frequentemente (máximo cinco vezes ao ano)': 10,'Muito frequentemente (mais de cinco vezes ao ano)': 9,'Ocasionalmente (máximo três vezes ao ano)': 8,'Raramente (uma vez ao ano)': 5,'Nunca': 1}
        mapeamento_guia = {'Não se interessa por arte': 0, 'Planejo minha rota antes.': 10, 'Utilizo o planejamento de terceiros (sites, blogs, páginas em redes sociais que disponibilizam).': 9, 'Com um guia do próprio museu.': 8, 'Sem um guia/planejamento para ver as obras.': 2}
        mapeamento_motivo = {'Não se interessa por arte': 0, 'Aprendizado': 10, 'Inspiração': 9, 'Lazer': 6, 'Apenas acompanho alguém': 3, 'Não visito': 1}
        mapeamento_falta_info = {'Não vai a museus': 1, 'Sim, sinto falta de mais informações': 10, 'Não, acredito que o que tem no museu é o suficiente': 4}
        mapeamento_procurar_info = {'Não sente falta de informações': 3, 'Sim, procuro': 10, 'Não, apenas me conformo': 5}
        mapeamento_achar_info = {'Não procura essas informações': 3, 'Sim': 4, 'Não': 10}
        mapeamento = {'Qual das opções de arte abaixo você mais gosta?': mapeamento_tipo_arte, 'Com que frequência você vai aos museus?': mapeamento_frequencia, 'Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.': mapeamento_guia, 'O que mais te atrai em visitar museus ou exposições de arte?': mapeamento_motivo, 'Você sente falta de mais informações sobre as obras nos museus?': mapeamento_falta_info, 'Você procura saber sobre essas informações faltantes?': mapeamento_procurar_info, 'Você encontra o que precisa/esperava ao pesquisar?': mapeamento_achar_info}

        mapeamento_geral = {'Em qual faixa etária você se encaixa?': {'Menos de 18 anos': 0,
        'Entre 25 e 35 anos': 1,
        'Entre 46 e 59 anos': 2,
        'Entre 36 e 45 anos': 3,
        'Entre 18 e 24 anos': 4,
        '60+ anos': 5},
        'Qual a renda per capita da sua casa?': {'Classes D/E: até R$ 2,9 mil': 0,
        'Classe C: entre R$ 2,9 mil e R$ 7,1 mil': 1,
        'Classe B: entre R$ 7,1 mil e R$ 22 mil': 2,
        'Classe A: superior a R$ 22 mil': 3},
        'Há quanto tempo você se interessa por arte?': {'Menos de 2 anos': 0,
        'Não me interesso': 1,
        'De 2 a 4 anos': 2,
        'Estou iniciando agora': 3,
        'Há mais de 10 anos': 4,
        'De 5 a 9 anos': 5},
        'Você já participou de algum curso ou atividade relacionada à arte?': {'Não': 0,
        'Não se interessa por arte': 1,
        'Sim': 2},
        'Você segue artístas ou páginas relacionadas à arte nas rede sociais?': {'Sim': 0,
        'Não se interessa por arte': 1,
        'Não': 2},
        'Você já usou um aplicativo de um museu ou relacionado à arte?': {'Não': 0,
        'Não se interessa por arte': 1,
        'Sim': 2},
        'De que forma você costuma buscar essas informações?': {'Busca em navegadores (Google, Yahoo, Edge, Opera, Fox, entre outros)': 0,
        'Não procura essas informações': 1,
        'Aplicativos': 2,
        'Busca em inteligências artificiais (ChatGPT, Gemini, entre outros)': 3,
        'Redes sociais': 4,
        'Blogs favoritos': 5,
        'Livros': 6}}

        print(dados.columns)

        df_x = dados.drop(columns=['Usaria o aplicativo?'])

        for i in df_x:
            if df_x[i].dtype == object:
                if i in mapeamento.keys():
                    df_x[i] = df_x[i].map(mapeamento[i])
                else:
                    df_x[i] = df_x[i].map(mapeamento_geral[i])

        df_x = df_x[['Em qual faixa etária você se encaixa?',
       'Qual a renda per capita da sua casa?',
       'Há quanto tempo você se interessa por arte?',
       'Qual das opções de arte abaixo você mais gosta?',
       'Com que frequência você vai aos museus?',
       'Você já participou de algum curso ou atividade relacionada à arte?',
       'Você segue artístas ou páginas relacionadas à arte nas rede sociais?',
       'Como é sua experiência ao visitar um museu normalmente? Caso nunca tenha visitado, selecione a que você acredita que seguiria.',
       'Você já usou um aplicativo de um museu ou relacionado à arte?',
       'O que mais te atrai em visitar museus ou exposições de arte?',
       'Você sente falta de mais informações sobre as obras nos museus?',
       'Você procura saber sobre essas informações faltantes?',
       'De que forma você costuma buscar essas informações?',
       'Você encontra o que precisa/esperava ao pesquisar?']]

        predict = modelo.predict(df_x)
        mapeamento_usaria_app = {'Sim': 1, 'Não': 0}
        predict = predict.map(mapeamento_usaria_app)
        print("Predict: ", predict)
        
    return render_template('formulario_enviado.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
