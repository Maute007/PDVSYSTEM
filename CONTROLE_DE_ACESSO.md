# Sistema de Controle de Acesso por Perfil

## Perfis de Usuário

O sistema possui 4 tipos de perfis com diferentes níveis de acesso:

### 1. **CLIENTE (CUSTOMER)**
- ❌ **Sem acesso** a nenhuma página do sistema
- Ao fazer login, é imediatamente desconectado com mensagem de erro
- Perfil padrão para novos usuários
- Apenas o administrador pode alterar o perfil

### 2. **VENDEDOR (SELLER)**
- ✅ **Página Inicial** (Dashboard com dados do dia atual)
- ✅ **Produtos** (Listagem e pesquisa)
- ✅ **Nova Venda** (Sistema PDV para vendas diretas)
- ✅ **Pedidos** (Apenas pedidos do dia atual)
- ❌ **Relatórios** (Sem acesso)

**Restrições do Vendedor:**
- Vê apenas vendas e pedidos do **dia atual**
- Vê apenas **suas próprias vendas** no dashboard
- Não pode acessar relatórios históricos ou estatísticas gerais

### 3. **GERENTE (MANAGER)**
- ✅ **Página Inicial** (Dashboard completo com dados de hoje)
- ✅ **Produtos** (Listagem e pesquisa)
- ✅ **Nova Venda** (Sistema PDV)
- ✅ **Pedidos** (Todos os pedidos com filtros de data)
- ✅ **Relatórios** (Acesso completo a análises e estatísticas)

**Permissões do Gerente:**
- Vê todos os dados (não apenas do dia atual)
- Pode filtrar pedidos por data
- Acesso total a relatórios e análises
- Pode ver desempenho de todos os vendedores

### 4. **ADMINISTRADOR (ADMIN)**
- ✅ **Todas as páginas** do sistema (igual ao GERENTE)
- ✅ **Django Admin** (Painel administrativo completo)
- Controle total sobre usuários, produtos, vendas, etc.

---

## Decoradores de Permissão

O sistema usa decoradores customizados para controlar acesso:

```python
@seller_required      # Vendedor, Gerente ou Admin
@manager_required     # Apenas Gerente ou Admin
@admin_required       # Apenas Admin
@role_required('SELLER', 'MANAGER')  # Perfis específicos
```

### Exemplos de Uso:

```python
@login_required
@seller_required
def nova_venda(request):
    # Apenas vendedores, gerentes e admins podem acessar
    pass

@login_required
@manager_required
def relatorios(request):
    # Apenas gerentes e admins podem acessar
    pass
```

---

## Middleware de Controle de Acesso

O sistema possui um middleware customizado (`RoleBasedAccessMiddleware`) que:

1. **Cria automaticamente** um `UserProfile` se não existir
2. **Bloqueia clientes** de acessar qualquer página
3. **Redireciona clientes** para o login com mensagem de erro
4. **Permite logout** mesmo para clientes bloqueados

---

## Fluxo de Login e Verificação

```
1. Usuário faz login
   ↓
2. Sistema verifica se existe UserProfile
   ↓
3. Se não existe, cria com role='CUSTOMER'
   ↓
4. Middleware verifica o role
   ↓
5. Se CUSTOMER → Logout automático + mensagem de erro
   ↓
6. Se SELLER/MANAGER/ADMIN → Acesso permitido
   ↓
7. Views verificam permissões específicas
```

---

## Filtros de Dados por Perfil

### Dashboard (Página Inicial)

**VENDEDOR:**
```python
# Apenas vendas de hoje do próprio vendedor
sales_filter = Q(created_at__date=today) & Q(seller=request.user)
orders_filter = Q(created_at__date=today)
```

**GERENTE/ADMIN:**
```python
# Todos os dados de hoje
sales_filter = Q(created_at__date=today)
orders_filter = Q(created_at__date=today)
```

### Pedidos

**VENDEDOR:**
- Apenas pedidos criados **hoje**
- Sem filtro de data disponível

**GERENTE/ADMIN:**
- Todos os pedidos
- Filtro de data disponível
- Pode pesquisar por período

### Relatórios

**VENDEDOR:**
- ❌ Sem acesso

**GERENTE/ADMIN:**
- ✅ Acesso completo
- Período padrão: últimos 30 dias
- Filtros personalizados de data
- Estatísticas de vendas, lucro, vendedores
- Rankings de produtos e vendedores

---

## Configuração de Novos Usuários

### 1. Criar Usuário no Django Admin
```
1. Acesse: /admin/auth/user/add/
2. Defina username e password
3. Salve o usuário
```

### 2. Definir Perfil
```
1. Acesse: /admin/loja/userprofile/
2. Encontre o perfil do usuário (criado automaticamente)
3. Altere o campo "Função" (role):
   - CUSTOMER (padrão)
   - SELLER (vendedor)
   - MANAGER (gerente)
   - ADMIN (administrador)
4. Preencha outros dados (telefone, endereço, CPF, etc.)
5. Salve
```

### 3. Primeiro Login
- Usuário faz login com suas credenciais
- Sistema verifica o perfil e direciona para a página inicial
- Se for CUSTOMER, é imediatamente bloqueado

---

## URLs de Autenticação

O sistema usa as URLs padrão do Django:

```
/accounts/login/           → Página de login
/accounts/logout/          → Logout
/accounts/password_change/ → Alterar senha
/accounts/password_reset/  → Recuperar senha
```

Configurações em `settings.py`:
```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

---

## Signals Automáticos

O sistema cria automaticamente um `UserProfile` quando um novo usuário é criado:

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role='CUSTOMER'  # Perfil padrão
        )
```

---

## Mensagens de Erro

### Cliente tenta acessar o sistema:
> ❌ **"Clientes não têm acesso ao sistema. Contacte o administrador."**

### Usuário sem permissão tenta acessar página restrita:
> ❌ **"Você não tem permissão para acessar esta página."**

### Perfil não encontrado:
> ⚠️ **"Perfil criado. Contacte o administrador para definir suas permissões."**

---

## Segurança

✅ Todas as views requerem login (`@login_required`)  
✅ Verificação de perfil em cada view (`@seller_required`, etc.)  
✅ Middleware bloqueia clientes automaticamente  
✅ Filtros de dados garantem que usuários vejam apenas o permitido  
✅ Django Admin protegido (apenas staff e superusers)  

---

## Resumo da Hierarquia

```
┌─────────────────────────────────────────┐
│          ADMINISTRADOR                  │
│  ✅ Todas as páginas + Django Admin    │
└─────────────────────────────────────────┘
                 ▲
                 │
┌─────────────────────────────────────────┐
│            GERENTE                      │
│  ✅ Todas as páginas + Relatórios      │
└─────────────────────────────────────────┘
                 ▲
                 │
┌─────────────────────────────────────────┐
│           VENDEDOR                      │
│  ✅ Vendas, Produtos, Pedidos (hoje)   │
└─────────────────────────────────────────┘
                 ▲
                 │
┌─────────────────────────────────────────┐
│           CLIENTE                       │
│  ❌ Sem acesso a nenhuma página        │
└─────────────────────────────────────────┘
```

---

## Django Admin

O Django Admin oferece interface completa para:
- ✅ Gerenciar usuários e perfis
- ✅ CRUD de produtos, categorias, clientes
- ✅ Visualizar vendas e pedidos com filtros
- ✅ Confirmar pagamentos de pedidos
- ✅ Gerar relatórios semanais
- ✅ Consultar logs de auditoria
- ✅ Gerenciar estoque

**Não é necessário criar páginas customizadas para essas funções administrativas!**
