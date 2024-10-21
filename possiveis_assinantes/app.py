from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    idade = request.form['idade']
    renda = request.form['renda_per_capita']
    print(f"Formulário recebido! Nome: {idade}, Email: {renda}")
    return f"Formulário recebido! Nome: {idade}, Email: {renda}"

if __name__ == '__main__':
    app.run(debug=True)
