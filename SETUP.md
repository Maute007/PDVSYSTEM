# 🚀 Setup Rápido - PDV System

## Passo a Passo para Iniciar o Sistema

### 1️⃣ Criar e Ativar Ambiente Virtual
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar (PowerShell)
.\venv\Scripts\Activate.ps1

# Ativar (CMD)
.\venv\Scripts\activate.bat
```

### 2️⃣ Instalar Dependências
```powershell
pip install django pillow
```

### 3️⃣ Criar Migrações e Banco de Dados
```powershell
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

### 4️⃣ Criar Superusuário (Admin)
```powershell
python manage.py createsuperuser
```
Siga as instruções e forneça:
- Username (ex: admin)
- Email (opcional)
- Password (escolha uma senha segura)

### 5️⃣ Iniciar Servidor
```powershell
python manage.py runserver
```

### 6️⃣ Acessar o Sistema
- **Frontend**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/

---

## 📦 Dados Iniciais (Opcional)

### Criar Categorias Básicas
No Admin Django (http://localhost:8000/admin/):

1. Acesse **Categorias**
2. Adicione as seguintes categorias:
   - Alimentos
   - Bebidas
   - Higiene
   - Limpeza
   - Diversos

### Criar Unidades de Medida
No Admin Django:

1. Acesse **Unidades de Medida**
2. Adicione:

**Peso:**
- Nome: Quilograma | Abreviação: kg | Tipo: WEIGHT | Conversão: 1000 | Permite Fração: ✓
- Nome: Grama | Abreviação: g | Tipo: WEIGHT | Conversão: 1 | Permite Fração: ✓

**Volume:**
- Nome: Litro | Abreviação: L | Tipo: VOLUME | Conversão: 1000 | Permite Fração: ✓
- Nome: Mililitro | Abreviação: ml | Tipo: VOLUME | Conversão: 1 | Permite Fração: ✓

**Outros:**
- Nome: Unidade | Abreviação: un | Tipo: UNIT | Conversão: 1 | Permite Fração: ✗
- Nome: Pacote | Abreviação: pct | Tipo: PACKAGE | Conversão: 1 | Permite Fração: ✗
- Nome: Caixa | Abreviação: cx | Tipo: PACKAGE | Conversão: 1 | Permite Fração: ✗

### Criar Produtos de Exemplo
1. Acesse **Produtos** > **Adicionar Produto**
2. Exemplos:

**Produto 1:**
- Código: PROD001
- Nome: Arroz Branco Tipo 1
- Categoria: Alimentos
- Unidade: Pacote
- Preço Custo: 20.00
- Preço Venda: 25.90
- Estoque: 100
- Estoque Mínimo: 20

**Produto 2:**
- Código: PROD002
- Nome: Feijão Preto
- Categoria: Alimentos
- Unidade: Quilograma
- Preço Custo: 6.00
- Preço Venda: 8.50
- Estoque: 50
- Estoque Mínimo: 10
- Permite Venda Avulsa: ✓

**Produto 3:**
- Código: PROD003
- Nome: Óleo de Soja
- Categoria: Alimentos
- Unidade: Litro
- Preço Custo: 5.50
- Preço Venda: 7.90
- Estoque: 80
- Estoque Mínimo: 15

### Criar Perfil de Usuário
1. No Admin, acesse **Perfis de Usuário**
2. Clique em **Adicionar Perfil**
3. Selecione seu usuário
4. Defina a função como **ADMIN** ou **SELLER**
5. Preencha telefone e outros dados
6. Salve

---

## ✅ Verificações

### Testar se está tudo funcionando:

1. ✅ Acesse http://localhost:8000/ - Deve mostrar a página inicial
2. ✅ Acesse http://localhost:8000/admin/ - Deve mostrar o admin
3. ✅ Acesse http://localhost:8000/produtos/ - Deve mostrar a lista de produtos
4. ✅ No admin, verifique se há:
   - Categorias
   - Unidades de Medida
   - Produtos
   - Perfis de Usuário

---

## 🔧 Comandos Úteis

### Criar novo superusuário
```powershell
python manage.py createsuperuser
```

### Resetar banco de dados (CUIDADO!)
```powershell
# Deletar banco
del db.sqlite3

# Deletar migrações antigas
del loja\migrations\0*.py

# Recriar tudo
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Coletar arquivos estáticos
```powershell
python manage.py collectstatic
```

### Ver rotas disponíveis
```powershell
python manage.py show_urls
# ou
python manage.py shell
>>> from django.urls import get_resolver
>>> print(get_resolver().url_patterns)
```

### Abrir shell do Django
```powershell
python manage.py shell
```

Exemplo de uso:
```python
from loja.models import Product, Category

# Listar todos os produtos
produtos = Product.objects.all()
for p in produtos:
    print(f"{p.code} - {p.name} - R$ {p.unit_price}")

# Criar categoria
categoria = Category.objects.create(
    name="Nova Categoria",
    description="Descrição da categoria"
)
```

---

## 🐛 Solução de Problemas

### Erro: "No module named 'loja'"
**Solução:** Certifique-se de que 'loja' está em INSTALLED_APPS no settings.py

### Erro: "Table doesn't exist"
**Solução:** Execute as migrações
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Erro: "CSRF verification failed"
**Solução:** Certifique-se de incluir {% csrf_token %} em todos os formulários POST

### Erro: "Static files not found"
**Solução:** Execute collectstatic
```powershell
python manage.py collectstatic
```

### Erro: "Permission denied" ao ativar venv
**Solução (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📱 Próximos Passos

1. ✅ Configurar o sistema básico
2. ✅ Criar categorias e unidades
3. ✅ Adicionar produtos
4. ✅ Criar perfis de usuário
5. 📊 Testar vendas e pedidos
6. 📈 Gerar relatórios
7. 🎨 Personalizar o tema (opcional)
8. 🚀 Deploy em produção (opcional)

---

## 🎯 Atalhos Rápidos

| Ação | URL |
|------|-----|
| Dashboard | http://localhost:8000/ |
| Admin | http://localhost:8000/admin/ |
| Produtos | http://localhost:8000/produtos/ |
| Nova Venda | http://localhost:8000/nova-venda/ |
| Pedidos | http://localhost:8000/pedidos/ |
| Relatórios | http://localhost:8000/relatorios/ |

---

**Pronto! Seu sistema está configurado e funcionando! 🎉**
