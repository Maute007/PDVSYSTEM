# 🛒 PDV System - Sistema de Vendas

Sistema completo de gerenciamento de vendas para mercearias, desenvolvido com Django e Bootstrap 5.

**Desenvolvido por:** Carlos Maute  
**Localização:** Moçambique, Maputo  
**Contato:** +258 865105545 | carlxyzsmaute@gmail.com  
**WhatsApp:** [+258 865105545](https://wa.me/258865105545)

## 🚀 Deploy no Render

### Pré-requisitos
- Conta no [Render.com](https://render.com)
- Repositório Git (GitHub, GitLab, etc.)

### Passos para Deploy

1. **Push do código para o repositório Git:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Maute007/PDVSYSTEM.git
git push -u origin main
```

2. **Criar PostgreSQL Database no Render:**
   - Acesse [Render Dashboard](https://dashboard.render.com)
   - Clique em "New +" e selecione "PostgreSQL"
   - Preencha:
     - **Name:** pdvsystem-db
     - **Database:** pdvsystem
     - **User:** pdvsystem
     - **Region:** Frankfurt (ou mais próximo)
   - Clique em "Create Database"
   - **Copie a URL interna** (Internal Database URL)

3. **Criar Web Service no Render:**
   - No Dashboard, clique em "New +" e selecione "Web Service"
   - Conecte seu repositório Git
   - Preencha:
     - **Name:** pdvsystem
     - **Region:** Frankfurt (mesma do banco)
     - **Branch:** main
     - **Root Directory:** (deixe vazio)
     - **Runtime:** Python 3
     - **Build Command:** `./build.sh`
     - **Start Command:** `gunicorn PDVSYSTEM.wsgi:application`

4. **Configurar Variáveis de Ambiente:**
   Na seção "Environment Variables", adicione:
   ```
   SECRET_KEY=your-secret-key-here-generate-a-random-one
   DEBUG=False
   ALLOWED_HOSTS=pdvsystem.onrender.com
   DATABASE_URL=postgresql://user:password@host/database
   ```

5. **Deploy:**
   - Clique em "Create Web Service"
   - Aguarde 5-10 minutos para build e deploy
   - Acesse: `https://pdvsystem.onrender.com/admin/`
   - Login: `admin` / `admin123` (ALTERE IMEDIATAMENTE!)

### 📦 Arquivos de Configuração Criados

- ✅ `requirements.txt` - Dependências Python
- ✅ `build.sh` - Script de build automático
- ✅ `Procfile` - Comando de inicialização
- ✅ `runtime.txt` - Python 3.13.0
- ✅ `.gitignore` - Arquivos ignorados

---

## ✨ Funcionalidades

### 📦 Gestão de Produtos
- Cadastro completo de produtos
- Controle de estoque com alertas
- Suporte para múltiplas unidades de medida (kg, g, L, unidade, pacote, caixa)
- Vendas fracionadas (ex: 0.5kg)
- Categorização de produtos
- Código de barras

### 💰 Vendas
- Registro de vendas presenciais
- Sistema de PDV intuitivo
- Múltiplos métodos de pagamento (Dinheiro, Débito, Crédito, PIX, Transferência)
- Cálculo automático de troco
- Impressão de recibos

### 📋 Pedidos Remotos
- Clientes podem fazer pedidos à distância
- Código único por pedido
- Upload de comprovante de pagamento
- Confirmação manual pelo vendedor
- Status: Pendente, Comprovante Enviado, Confirmado, Processando, Pronto, Concluído

### 👥 Gestão de Clientes
- Cadastro completo de clientes
- Histórico de compras
- Perfis de usuário com diferentes roles (Admin, Gerente, Vendedor, Cliente)

### 📊 Relatórios
- Relatórios semanais automáticos
- Desempenho por vendedor
- Produtos mais vendidos
- Análise de receitas e lucros
- Exportação de dados

### 🔍 Auditoria
- Log completo de todas as ações
- Rastreamento de usuário, IP, data/hora
- Histórico de alterações

## 🚀 Instalação

### Requisitos
- Python 3.8+
- Django 4.2+
- pip

### Passos

1. **Clone o repositório** (ou navegue até a pasta do projeto)
```bash
cd "D:\MEUS SOFTWARES\PDVSYSTEM"
```

2. **Crie um ambiente virtual**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Instale as dependências**
```powershell
pip install django pillow
```

4. **Configure o banco de dados**
```powershell
python manage.py makemigrations
python manage.py migrate
```

5. **Crie um superusuário**
```powershell
python manage.py createsuperuser
```

6. **Colete arquivos estáticos** (se necessário)
```powershell
python manage.py collectstatic
```

7. **Inicie o servidor**
```powershell
python manage.py runserver
```

8. **Acesse o sistema**
- Frontend: http://localhost:8000/
- Admin: http://localhost:8000/admin/

## 📁 Estrutura do Projeto

```
PDVSYSTEM/
├── loja/                       # App principal
│   ├── models.py              # Modelos de dados
│   ├── views.py               # Views
│   ├── urls.py                # URLs
│   ├── admin.py               # Admin customizado
│   ├── templates/             # Templates HTML
│   │   ├── base.html         # Template base
│   │   ├── home.html         # Dashboard
│   │   ├── produtos.html     # Gestão de produtos
│   │   ├── nova_venda.html   # Nova venda
│   │   ├── pedidos.html      # Gestão de pedidos
│   │   └── relatorios.html   # Relatórios
│   └── static/               # Arquivos estáticos
│       ├── css/
│       │   └── custom.css    # CSS customizado
│       └── js/
│           └── main.js       # JavaScript customizado
├── PDVSYSTEM/                # Configurações do projeto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

## 🎨 Frontend

### Tecnologias
- **Bootstrap 5.3** - Framework CSS
- **Bootstrap Icons** - Ícones
- **Typed.js** - Efeito de digitação
- **Animate.css** - Animações
- **Google Fonts (Inter)** - Tipografia

### Cores do Sistema
- Primary: `#4f46e5` (Índigo)
- Success: `#22c55e` (Verde)
- Warning: `#f59e0b` (Âmbar)
- Danger: `#ef4444` (Vermelho)
- Info: `#06b6d4` (Ciano)

### Recursos
- **Responsivo** - Funciona em todos os dispositivos
- **Toasts** - Notificações elegantes
- **Modals** - Janelas modais para ações
- **Badges** - Indicadores visuais de status
- **Animações** - Transições suaves
- **Ícones** - Bootstrap Icons integrado

## 📊 Modelos de Dados

### Category
Categorias de produtos

### UnitOfMeasure
Unidades de medida (kg, g, L, unidade, etc.)

### Product
Produtos com controle de estoque

### UserProfile
Perfis de usuário estendidos

### Customer
Clientes do sistema

### Order
Pedidos remotos de clientes

### OrderItem
Itens dos pedidos

### Sale
Vendas diretas (presenciais)

### SaleItem
Itens das vendas

### WeeklySalesReport
Relatórios semanais automáticos

### SellerPerformance
Desempenho dos vendedores

### AuditLog
Log de auditoria do sistema

## 🔧 Configurações

### Settings.py
Adicione ao seu `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'loja',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'loja' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### URLs principais
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('loja.urls')),
]
```

## 📝 Como Usar

### Adicionar Produtos
1. Acesse o Admin Django
2. Vá em "Produtos" > "Adicionar produto"
3. Preencha os dados (código, nome, preço, estoque, etc.)
4. Salve

### Realizar Venda
1. Na página inicial, clique em "Nova Venda"
2. Adicione produtos ao carrinho
3. Selecione cliente (opcional)
4. Escolha o método de pagamento
5. Informe o valor pago
6. Finalize a venda

### Gerenciar Pedidos
1. Acesse "Pedidos" no menu
2. Visualize pedidos pendentes
3. Confirme pagamentos após verificar comprovante
4. Mude status conforme processamento

### Visualizar Relatórios
1. Acesse "Relatórios" no menu
2. Selecione o período desejado
3. Visualize estatísticas e gráficos
4. Exporte dados se necessário

## 🎯 Próximos Passos

- [ ] Integração com APIs de pagamento
- [ ] Impressão de cupons fiscais
- [ ] App mobile
- [ ] Sincronização em nuvem
- [ ] Leitor de código de barras
- [ ] Dashboard com gráficos Chart.js
- [ ] Sistema de comissões
- [ ] Gestão de fornecedores
- [ ] Controle de validade de produtos

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto está sob a licença MIT.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato através do e-mail: contato@pdvsystem.com

---

**Desenvolvido com ❤️ usando Django e Bootstrap**
