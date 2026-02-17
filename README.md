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
python manage.py makemigrations
python manage.py migrate
```

### 5. Execute o servidor
```bash
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`.

## 🔗 Endpoints Principais

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/accounts/` | Lista todas as contas ativas com saldo e rendimento total. |
| POST | `/api/accounts/` | Cria uma nova conta. |
| POST | `/api/accounts/{id}/close/` | Encerra uma conta (deve estar com saldo zero). |
| POST | `/api/accounts/{id}/reactivate/` | Reativa uma conta encerrada. |
| GET | `/api/accounts/total_wealth/` | Retorna o patrimônio total somado. |
| GET | `/api/transactions/dashboard/` | Resumo de receitas, despesas e saldo. |

## 📝 Estrutura de Histórico

O histórico das contas possui tipos específicos de movimentação:
- **I:** Início (Saldo inicial)
- **A:** Aporte
- **W:** Retirada (Withdraw)
- **R:** Rendimento
- **E:** Encerramento
- **V:** Reativação