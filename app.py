from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
db = SQLAlchemy(app)

# Estruturas de Dados
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, default=0)
    preco = db.Column(db.Float, nullable=False)
    localizacao = db.Column(db.String(100))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))

class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    operacao = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    data = db.Column(db.DateTime, default=datetime.utcnow)

# Funções de Cadastro de Produtos
@app.route('/cadastrar_produto', methods=['POST'])
def cadastrar_produto():
    data = request.get_json()
    novo_produto = Produto(
        nome=data['nome'],
        quantidade=data['quantidade'],
        preco=data['preco'],
        localizacao=data['localizacao'],
        categoria_id=data['categoria_id']
    )
    db.session.add(novo_produto)
    db.session.commit()
    return jsonify({'message': 'Produto cadastrado com sucesso!'})

# Funções de Consulta de Produtos
@app.route('/consultar_produto', methods=['GET'])
def consultar_produto():
    produtos = Produto.query.all()
    resultado = [{
        'id': p.id,
        'nome': p.nome,
        'quantidade': p.quantidade,
        'preco': p.preco,
        'localizacao': p.localizacao
    } for p in produtos]
    return jsonify(resultado)

# Funções de Movimentação de Estoque
@app.route('/registrar_movimentacao', methods=['POST'])
def registrar_movimentacao():
    data = request.get_json()
    movimentacao = Movimentacao(
        produto_id=data['produto_id'],
        quantidade=data['quantidade'],
        operacao=data['operacao']
    )
    # Atualiza o estoque
    produto = Produto.query.get(data['produto_id'])
    if data['operacao'] == 'entrada':
        produto.quantidade += data['quantidade']
    elif data['operacao'] == 'saida':
        produto.quantidade -= data['quantidade']
    db.session.add(movimentacao)
    db.session.commit()
    return jsonify({'message': 'Movimentação registrada com sucesso!'})

# Funções de Relatório de Movimentação
@app.route('/historico_movimentacao', methods=['GET'])
def historico_movimentacao():
    movimentacoes = Movimentacao.query.all()
    resultado = [{
        'produto_id': m.produto_id,
        'quantidade': m.quantidade,
        'operacao': m.operacao,
        'data': m.data.strftime('%Y-%m-%d %H:%M:%S')
    } for m in movimentacoes]
    return jsonify(resultado)

if __name__ == '__main__':
    db.create_all()  # Cria as tabelas
    app.run(debug=True)
