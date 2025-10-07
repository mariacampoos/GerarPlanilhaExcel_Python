from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from faker import Faker
import random
from sqlalchemy import create_engine

# Carrega variáveis de ambiente
load_dotenv()

database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
engine = create_engine(database_url)

# Cria tabelas
create_tables_sql = """
DROP TABLE IF EXISTS Pedidos;
DROP TABLE IF EXISTS Clientes;

CREATE TABLE Clientes (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefone VARCHAR(20)
);

CREATE TABLE Pedidos (
    id_pedido SERIAL PRIMARY KEY,
    id_cliente INTEGER REFERENCES Clientes(id_cliente),
    data_pedido DATE NOT NULL,
    valor NUMERIC(10,2),
    status VARCHAR(20),
    forma_pagamento VARCHAR(50),
    observacoes TEXT
);
"""

with engine.connect() as conn:
    conn.execute(text(create_tables_sql))
    conn.commit()

print("Tabelas criadas.")

# Usa Faker para gerar dados fake
fake = Faker('pt_BR')

# Insere clientes
num_clientes = 50
clientes = []
for _ in range(num_clientes):
    nome = fake.name()
    email = fake.email()
    telefone = fake.phone_number()
    clientes.append((nome, email, telefone))

with engine.connect() as conn:
    for nome, email, telefone in clientes:
        conn.execute(text(
            "INSERT INTO Clientes (nome, email, telefone) VALUES (:nome, :email, :telefone)"
        ), {"nome": nome, "email": email, "telefone": telefone})
    conn.commit()

print(f"{num_clientes} clientes inseridos.")

# Busca os ids dos clientes para usar nos pedidos
with engine.connect() as conn:
    result = conn.execute(text("SELECT id_cliente FROM Clientes"))
    clientes_ids = [row[0] for row in result]

# Dados possíveis para pedidos
status_list = ['Cancelado', 'Finalizado', 'Pendente', 'Em Processamento']
pagamentos = ['Cartão de Crédito', 'Boleto', 'Pix', 'Dinheiro', 'Cartão de Débito']
observacoes_possiveis = [
    None,
    'Cliente pediu urgência',
    'Pagamento recusado',
    'Pedido cancelado por falta de estoque',
    'Entrega atrasada',
    'Cliente desistiu',
    'Endereço incorreto',
]

from datetime import datetime, timedelta

# Gera pedidos aleatórios
num_pedidos = 200
pedidos = []
base_date = datetime(2025, 1, 1)

for _ in range(num_pedidos):
    id_cliente = random.choice(clientes_ids)
    data_pedido = base_date + timedelta(days=random.randint(0, 300))
    valor = round(random.uniform(50, 1000), 2)
    status = random.choice(status_list)
    forma_pagamento = random.choice(pagamentos)
    observacoes = random.choice(observacoes_possiveis)
    pedidos.append((id_cliente, data_pedido.date(), valor, status, forma_pagamento, observacoes))

with engine.connect() as conn:
    for pedido in pedidos:
        conn.execute(text("""
            INSERT INTO Pedidos (id_cliente, data_pedido, valor, status, forma_pagamento, observacoes)
            VALUES (:id_cliente, :data_pedido, :valor, :status, :forma_pagamento, :observacoes)
        """), {
            "id_cliente": pedido[0],
            "data_pedido": pedido[1],
            "valor": pedido[2],
            "status": pedido[3],
            "forma_pagamento": pedido[4],
            "observacoes": pedido[5]
        })
    conn.commit()

print(f"{num_pedidos} pedidos inseridos.")
