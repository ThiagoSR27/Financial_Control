# Financial Control API

API Backend para controle financeiro pessoal, desenvolvida com **Django** e **Django Rest Framework (DRF)**. O sistema permite o gerenciamento de contas (caixinhas), transações (receitas e despesas) e histórico de rendimentos.

## 🚀 Tecnologias

- **Python 3.9+**
- **Django 4.2**
- **Django Rest Framework**
- **MySQL** (Banco de dados)

## ⚙️ Funcionalidades Principais

- **Gerenciamento de Contas:**
  - Criação de contas com saldo inicial.
  - Cálculo automático de rendimentos (`total_yield`).
  - Encerramento e Reativação de contas com validação de saldo.
  - Histórico detalhado de movimentações (Aportes, Retiradas, Rendimentos).

- **Transações:**
  - Registro de Receitas e Despesas categorizadas.
  - Dashboard com totais de entradas, saídas e saldo.

- **Performance:**
  - Consultas otimizadas utilizando `prefetch_related` para evitar problemas de N+1 queries.

## 📦 Como Rodar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/financial-control.git
cd financial-control
```

### 2. Crie e ative o ambiente virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados
Certifique-se de ter o MySQL rodando e configure as credenciais no arquivo `settings.py` (ou variáveis de ambiente). Em seguida, execute as migrações:

```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

### 5. Execute o servidor
```bash
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`.

## 📄 Paginação

As respostas de listagem (GET para endpoints como `/api/accounts/`, `/api/transactions/`, etc.) são paginadas para melhorar a performance e a usabilidade. Por padrão, são retornados **10 itens por página**.

Você pode controlar a paginação usando os seguintes *query parameters*:

- `?page=<número>`: Para navegar até uma página específica.
- `?page_size=<número>`: Para alterar a quantidade de itens por página (o máximo é 100).

**Exemplo de requisição para a segunda página com 20 itens:**
```
/api/transactions/?page=2&page_size=20
```

## 🔗 Endpoints Principais

### Accounts

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/accounts/` | Lista todas as contas ativas com saldo e rendimento total. |
| POST | `/api/accounts/` | Cria uma nova conta. |
| GET | `/api/accounts/total_wealth/` | Retorna o patrimônio total somado. |
| POST | `/api/accounts/{id}/close/` | Encerra uma conta (deve estar com saldo zero). |
| POST | `/api/accounts/{id}/reactivate/` | Reativa uma conta encerrada. |

**Exemplo de Payload (Criar Conta):**
```json
{
  "name": "Nubank",
  "initial_value": 1000.00
}
```

### Categories

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/categories/` | Lista as categorias disponíveis. |
| POST | `/api/categories/` | Cria uma nova categoria. |

**Exemplo de Payload (Criar Categoria):**
```json
{
  "name": "Alimentação",
  "type": "D"
}
```

### Transactions

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/transactions/` | Lista as transações registradas. |
| POST | `/api/transactions/` | Cria uma nova transação. |
| GET | `/api/transactions/dashboard/` | Resumo de receitas, despesas e saldo. |

**Filtros Disponíveis:**
Os endpoints de listagem e dashboard suportam filtragem via *query parameters*:
- `date`: Filtra pela data exata da transação (formato: `AAAA-MM-DD`).
- `category`: ID da categoria.
- `category_type`: Tipo da categoria (`R` para Receita, `D` para Despesa).

**Exemplo de Payload (Criar Transação):**
```json
{
  "description": "Compras do Mês",
  "value": 450.50,
  "date": "2023-10-01",
  "category": 1
}
```

### Account History

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/account-history/` | Lista o histórico de movimentações com variação calculada. |
| POST | `/api/account-history/` | Cria um novo registro no histórico. |

**Filtros Disponíveis:**
- `account`: ID da conta.
- `type`: Tipo de registro no histórico (ex: `A` para Aporte).
- `date`: Filtra pela data exata do registro (formato: `AAAA-MM-DD`).

**Ordenação Disponível:**
Você pode ordenar os resultados usando o parâmetro `ordering`.
- `date`: Ordena pela data da operação.
- `value`: Ordena pelo valor da operação.
- `end_value`: Ordena pelo saldo final.

Para ordenação decrescente, adicione um hífen (`-`) no início do nome do campo (ex: `?ordering=-date`). O padrão é `-date, -id`.

**Formato da Resposta (GET):**
A resposta para a listagem do histórico agora inclui dois campos de valor para maior clareza:
- `value`: O valor da operação (ex: o aporte de `200.00` ou a retirada de `-50.00`).
- `end_value`: O saldo final da conta *após* a operação ter sido aplicada.

**Exemplo de Resposta (GET):**
```json
{
    "id": 5,
    "account_name": "Nubank",
    "value": "200.00",
    "end_value": "1200.00",
    "type": "A",
    "date": "2023-10-05",
    "monthly_variation": "200.00",
    "description": "Aporte Mensal"
}
```

**Exemplo de Payload (Adicionar Histórico - Aporte):**
```json
{
  "account": 1,
  "value": 200.00,
  "type": "A",
  "date": "2023-10-05",
  "description": "Aporte Mensal"
}
```

## 📝 Estrutura de Histórico

O histórico das contas possui tipos específicos de movimentação:
- **I:** Início (Saldo inicial)
- **A:** Aporte
- **W:** Retirada (Withdraw)
- **R:** Rendimento
- **E:** Encerramento
- **V:** Reativação