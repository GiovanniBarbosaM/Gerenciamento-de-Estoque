# Importações principais
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import hashlib
from datetime import datetime

# Configuração da aplicação e do banco de dados
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
app.secret_key = 'sua_chave_secreta'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Modelos de dados
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    localizacao = db.Column(db.String(120), nullable=False)
    nivel_minimo = db.Column(db.Integer, nullable=False, default=5)

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer)
    data = db.Column(db.DateTime, default=datetime.utcnow)

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Carregar usuário para sessão de login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas de autenticação
@app.route('/usuario', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    novo_usuario = User(username=data['nome'], password=hash_senha(data['senha']))
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"mensagem": f"Usuário {data['nome']} cadastrado com sucesso!"})

@app.route('/usuario/login', methods=['POST'])
def autenticar_usuario():
    data = request.json
    user = User.query.filter_by(username=data['nome'], password=hash_senha(data['senha'])).first()
    if user:
        login_user(user)
        return jsonify({"mensagem": "Login bem-sucedido", "usuario": data['nome']})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rotas de gerenciamento de produtos
@app.route('/produto', methods=['POST'])
@login_required
def cadastrar_produto():
    data = request.json
    novo_produto = Produto(
        nome=data['nome'],
        categoria=data['categoria'],
        quantidade=data['quantidade'],
        preco=data['preco'],
        localizacao=data['localizacao']
    )
    db.session.add(novo_produto)
    db.session.commit()
    return jsonify({"mensagem": f"Produto {data['nome']} cadastrado com sucesso!"})

@app.route('/produto/<string:nome>', methods=['PUT'])
@login_required
def atualizar_estoque(nome):
    data = request.json
    produto = Produto.query.filter_by(nome=nome).first()
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    nova_quantidade = produto.quantidade + data['quantidade'] if data['operacao'] == 'entrada' else produto.quantidade - data['quantidade']
    if nova_quantidade < 0:
        return jsonify({"erro": "Quantidade insuficiente"}), 400

    produto.quantidade = nova_quantidade
    db.session.commit()
    return jsonify({"mensagem": f"Estoque de {nome} atualizado para {nova_quantidade}"})

@app.route('/produto/localizacao/<string:nome>', methods=['GET'])
@login_required
def rastrear_localizacao(nome):
    produto = Produto.query.filter_by(nome=nome).first()
    if produto:
        return jsonify({"localizacao": produto.localizacao})
    return jsonify({"erro": "Produto não encontrado"}), 404

@app.route('/produto/relatorio', methods=['GET'])
@login_required
def gerar_relatorio_estoque():
    produtos = Produto.query.all()
    relatorio = [{"nome": p.nome, "quantidade": p.quantidade} for p in produtos]
    return jsonify({"relatorio": relatorio})

# Rotas de movimentação no caixa
@app.route('/caixa/movimentacao', methods=['POST'])
@login_required
def registrar_movimentacao():
    data = request.json
    produto = Produto.query.filter_by(nome=data['produto_nome']).first()
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    valor = produto.preco * data['quantidade']
    return jsonify({"mensagem": f"Movimentação de {data['tipo']} registrada para {data['produto_nome']} no valor de R${valor:.2f}"})

@app.route('/caixa/relatorio', methods=['GET'])
@login_required
def gerar_relatorio_caixa():
    return jsonify({"mensagem": "Relatório de caixa gerado."})

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=5000)
