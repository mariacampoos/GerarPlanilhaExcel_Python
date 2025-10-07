from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import io
import os

# === CARREGA VARIÁVEIS DE AMBIENTE ===
load_dotenv()

app = Flask(__name__)
app.secret_key = "chave-secreta"  # Necessário para flash messages

# === CONEXÃO COM O BANCO ===
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)

# === ROTA SOBRE ===
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# === ROTA PRINCIPAL ===
@app.route('/')
def index():
    return render_template('index.html')

# === ROTA DE EXPORTAÇÃO ===
@app.route('/exportar', methods=['POST'])
def exportar():
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    status = request.form.get('status')

    # Validação dos campos
    if not data_inicio or not data_fim or not status:
        flash("Por favor, preencha todos os campos!")
        return redirect(url_for('index'))

    # Query SQL com parâmetros seguros
    query = text("""
        SELECT 
            p.id_pedido,
            c.nome AS cliente,
            p.data_pedido,
            p.valor,
            p.status
        FROM Pedidos p
        JOIN Clientes c ON p.id_cliente = c.id_cliente
        WHERE p.status = :status
          AND p.data_pedido BETWEEN :data_inicio AND :data_fim
    """)

    # Parâmetros a serem passados com segurança
    params = {
        "status": status,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }

    # Executa a query
    try:
        df = pd.read_sql_query(query, engine, params=params)
    except Exception as e:
        flash(f"Erro ao consultar o banco de dados: {e}")
        return redirect(url_for('index'))

    if df.empty:
        flash("Nenhum pedido encontrado com esses filtros.")
        return redirect(url_for('index'))

    # Geração do arquivo Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name="Pedidos")
    output.seek(0)

    nome_arquivo = f"pedidos_{status.lower()}_{data_inicio}_a_{data_fim}.xlsx"

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nome_arquivo
    )

if __name__ == '__main__':
    app.run(debug=True)
