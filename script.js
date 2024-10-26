// URL do servidor Flask
const baseUrl = 'http://localhost:5000';

// Função para fazer uma requisição e tratar a resposta
async function fazerRequisicao(url, method, body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : null,
    };

    const response = await fetch(url, options);
    return response.json();
}

// Função para cadastrar produtos
async function cadastrarProduto() {
    const produto = {
        nome: document.getElementById("nome").value,
        categoria: document.getElementById("categoria").value,
        quantidade: parseInt(document.getElementById("quantidade").value),
        preco: parseFloat(document.getElementById("preco").value),
        localizacao: document.getElementById("localizacao").value,
    };

    try {
        const result = await fazerRequisicao(`${baseUrl}/produto`, 'POST', produto);
        document.getElementById("cadastro-mensagem").innerText = result.mensagem;
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Função para atualizar o estoque
async function atualizarEstoque() {
    const nome = document.getElementById("nome-atualizar").value;
    const quantidade = parseInt(document.getElementById("quantidade-atualizar").value);
    const operacao = document.getElementById("operacao").value;

    try {
        const result = await fazerRequisicao(`${baseUrl}/produto/${nome}`, 'PUT', { quantidade, operacao });
        document.getElementById("atualizar-mensagem").innerText = result.mensagem;
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Função para consultar a localização do produto
async function consultarLocalizacao() {
    const nome = document.getElementById("nome-consulta").value;

    try {
        const result = await fazerRequisicao(`${baseUrl}/produto/localizacao/${nome}`, 'GET');
        document.getElementById("consulta-mensagem").innerText = result.localizacao ? `Localização: ${result.localizacao}` : result.erro;
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Função para gerar o relatório de estoque
async function gerarRelatorio() {
    try {
        const result = await fazerRequisicao(`${baseUrl}/produto/relatorio`, 'GET');
        const listaRelatorio = document.getElementById("relatorio-estoque");
        listaRelatorio.innerHTML = ''; // Limpa a lista

        result.relatorio.forEach(produto => {
            const item = document.createElement("li");
            item.innerText = `Produto: ${produto.nome} - Quantidade: ${produto.quantidade}`;
            listaRelatorio.appendChild(item);
        });
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Função para consultar produtos
function consultarProduto() {
    const categoria_id = document.getElementById('categoria_id').value;
    const fornecedor_id = document.getElementById('fornecedor_id').value;

    fazerRequisicao(`/consultar_produto?categoria_id=${categoria_id}&fornecedor_id=${fornecedor_id}`, 'GET')
        .then(data => {
            const resultadoConsulta = document.getElementById('resultado-consulta');
            resultadoConsulta.innerHTML = data.map(produto =>
                `<li>${produto.nome} - Preço: R$${produto.preco} - Quantidade: ${produto.quantidade}</li>`
            ).join('');
        });
}

// Função para gerar alertas de estoque
function gerarAlerta() {
    fazerRequisicao('/gerar_alerta', 'GET')
        .then(data => {
            const alertasEstoque = document.getElementById('alertas-estoque');
            alertasEstoque.innerHTML = data.map(produto =>
                `<li>${produto.nome} - Estoque Baixo: ${produto.quantidade} unidades - Preço: R$${produto.preco}</li>`
            ).join('');
        });
}

// Função para saída de produtos
function saidaProduto() {
    const nome = document.getElementById("nome-saida").value;
    const quantidade = parseInt(document.getElementById("quantidade-saida").value);
    
    if (quantidade > 0) {
        alert(`Saída de ${quantidade} unidades do produto ${nome} registrada com sucesso.`);
        document.getElementById("saida-mensagem").textContent = "Saída registrada!";
    } else {
        document.getElementById("saida-mensagem").textContent = "Quantidade inválida.";
    }
}
