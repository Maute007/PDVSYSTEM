# Guia de Primeiros Passos - PDV System

## 1. Criar Banco de Dados

```powershell
python manage.py makemigrations
python manage.py migrate
```

## 2. Criar Superusuário (Admin)

```powershell
python manage.py createsuperuser
```

Informe:
- Username: `admin`
- Email: `admin@pdvsystem.com` (opcional)
- Password: (escolha uma senha forte)

## 3. Iniciar o Servidor

```powershell
python manage.py runserver
```

Acesse: **http://localhost:8000**

---

## 4. Configurar Perfil do Admin

1. Acesse o Django Admin: **http://localhost:8000/admin**
2. Faça login com o superusuário criado
3. Vá em **Sistema de Vendas → Perfis de Usuário**
4. Clique no perfil do seu usuário (criado automaticamente)
5. Altere o campo **Função** para `ADMIN`
6. Preencha os dados opcionais (telefone, endereço, CPF)
7. Clique em **Salvar**

---

## 5. Criar Dados Iniciais

### 5.1 Unidades de Medida

Acesse: **Admin → Unidades de Medida → Adicionar**

Exemplos:

| Nome | Abreviação | Tipo | Conversão | Permite Fração |
|------|------------|------|-----------|----------------|
| Quilograma | kg | Peso | 1000 | ✅ Sim |
| Grama | g | Peso | 1 | ✅ Sim |
| Litro | L | Volume | 1000 | ✅ Sim |
| Mililitro | ml | Volume | 1 | ✅ Sim |
| Unidade | un | Unidade | 1 | ❌ Não |
| Pacote | pct | Embalagem | 1 | ❌ Não |
| Caixa | cx | Embalagem | 1 | ❌ Não |

### 5.2 Categorias

Acesse: **Admin → Categorias → Adicionar**

Exemplos:
- Bebidas
- Cereais e Grãos
- Carnes e Frios
- Laticínios
- Frutas e Verduras
- Higiene e Limpeza
- Padaria

### 5.3 Produtos

Acesse: **Admin → Produtos → Adicionar**

Exemplos:

**Arroz Branco 5kg**
- Código: `ARR001`
- Nome: `Arroz Branco Tipo 1`
- Categoria: `Cereais e Grãos`
- Unidade: `kg`
- Preço Unitário: `6.50` (por kg)
- Preço de Custo: `5.00`
- Quantidade em Estoque: `100.000`
- Estoque Mínimo: `20.000`
- Permite Venda Avulsa: ✅ Sim

**Refrigerante 2L**
- Código: `REF001`
- Nome: `Refrigerante Cola 2L`
- Categoria: `Bebidas`
- Unidade: `un`
- Preço Unitário: `8.50`
- Preço de Custo: `6.00`
- Quantidade em Estoque: `50.000`
- Estoque Mínimo: `10.000`
- Permite Venda Avulsa: ❌ Não

---

## 6. Criar Usuários de Teste

### 6.1 Vendedor

1. **Admin → Usuários → Adicionar usuário**
2. Username: `vendedor1`
3. Password: (defina uma senha)
4. **Salvar e continuar editando**
5. Preencha: Nome, Sobrenome, Email (opcional)
6. **NÃO marque** "Acesso ao site de administração"
7. **Salvar**

8. **Admin → Perfis de Usuário**
9. Encontre o perfil `vendedor1`
10. Altere **Função** para `SELLER`
11. Preencha Telefone, Endereço (opcional)
12. **Salvar**

### 6.2 Gerente

Repita o processo acima, mas:
- Username: `gerente1`
- Função: `MANAGER`

### 6.3 Cliente (para testar bloqueio)

Repita o processo:
- Username: `cliente1`
- Função: `CUSTOMER` (padrão)

---

## 7. Testar Acessos

### 7.1 Como Admin
1. Faça logout: **http://localhost:8000/accounts/logout/**
2. Login com: `admin`
3. Você deve ver:
   - ✅ Dashboard completo
   - ✅ Menu: Vendas, Produtos, Pedidos, Relatórios
   - ✅ Todas as funcionalidades

### 7.2 Como Vendedor
1. Logout e login com: `vendedor1`
2. Você deve ver:
   - ✅ Dashboard com dados de hoje
   - ✅ Menu: Vendas, Produtos, Pedidos (sem Relatórios)
   - ✅ Apenas vendas e pedidos de hoje

### 7.3 Como Gerente
1. Logout e login com: `gerente1`
2. Você deve ver:
   - ✅ Dashboard completo
   - ✅ Menu: Vendas, Produtos, Pedidos, Relatórios
   - ✅ Filtros de data em Pedidos
   - ✅ Acesso a Relatórios

### 7.4 Como Cliente (Bloqueado)
1. Logout e login com: `cliente1`
2. Você deve:
   - ❌ Ser imediatamente desconectado
   - ❌ Ver mensagem: "Clientes não têm acesso ao sistema"
   - ❌ Ser redirecionado para o login

---

## 8. Fazer uma Venda de Teste

1. Login como vendedor ou gerente
2. Menu: **Vendas → Nova Venda**
3. Selecione ou crie um cliente
4. Adicione produtos:
   - Pesquise pelo nome
   - Digite a quantidade
   - Clique em **Adicionar**
5. Revise os itens no carrinho
6. Confira o total
7. Selecione método de pagamento
8. Digite valor pago (se dinheiro)
9. Sistema calcula o troco
10. Clique em **Finalizar Venda**

---

## 9. Criar um Pedido de Teste

1. **Admin → Clientes → Adicionar cliente**
2. Preencha: Nome, Telefone, Endereço
3. **Admin → Pedidos → Adicionar pedido**
4. Selecione o cliente
5. Método de pagamento: `DEBIT` (Mpesa)
6. Adicione itens na seção **Itens do Pedido**
7. **Salvar**
8. Sistema gera código automático (ex: `ORD20241113001`)
9. Cliente recebe o código e pode fazer upload do comprovante

---

## 10. Confirmar Pagamento de Pedido

1. **Admin → Pedidos**
2. Clique no pedido
3. No campo **Comprovante de Pagamento**, faça upload da imagem/PDF
4. Status muda para: `PAYMENT_UPLOADED`
5. Na lista de pedidos, selecione o pedido
6. Ação: **Confirmar pagamento dos pedidos selecionados**
7. Status muda para: `CONFIRMED`

---

## 11. Gerar Relatório Semanal

1. Login como gerente ou admin
2. Menu: **Relatórios**
3. Selecione período:
   - Data Início: `2024-11-01`
   - Data Fim: `2024-11-13`
4. Clique em **Filtrar**
5. Veja:
   - Total de Vendas
   - Receita Total
   - Lucro Total
   - Ticket Médio
   - Top 5 Vendedores
   - Top 10 Produtos

Ou via Django Admin:
1. **Admin → Relatórios Semanais de Vendas → Adicionar**
2. Sistema calcula automaticamente ao salvar

---

## 12. Consultar Logs de Auditoria

1. **Admin → Logs de Auditoria**
2. Filtros disponíveis:
   - Tipo de ação (Criação, Atualização, Exclusão, etc.)
   - Usuário
   - Data
3. Cada log mostra:
   - Usuário que executou
   - Ação realizada
   - Endereço IP
   - Data/Hora
   - Mudanças (em JSON)

---

## 13. Verificar Estoque Baixo

### No Dashboard:
- Card "Produtos em Falta" mostra quantidade

### No Admin:
1. **Admin → Produtos**
2. Filtro lateral: **Status do Estoque → Estoque Baixo**
3. Lista mostra produtos abaixo do estoque mínimo

### Atualização Automática:
- Ao fazer venda, estoque é descontado automaticamente
- Status muda para:
  - `IN_STOCK`: Estoque normal
  - `LOW_STOCK`: Abaixo do mínimo
  - `OUT_OF_STOCK`: Sem estoque (0)

---

## 14. Principais URLs do Sistema

| URL | Descrição | Acesso |
|-----|-----------|--------|
| `/` | Dashboard | SELLER+ |
| `/produtos/` | Listagem de produtos | SELLER+ |
| `/vendas/nova/` | Nova venda (PDV) | SELLER+ |
| `/pedidos/` | Gestão de pedidos | SELLER+ |
| `/relatorios/` | Relatórios e análises | MANAGER+ |
| `/admin/` | Django Admin | ADMIN |
| `/accounts/login/` | Login | Todos |
| `/accounts/logout/` | Logout | Todos |

**SELLER+** = Vendedor, Gerente ou Admin  
**MANAGER+** = Gerente ou Admin  
**ADMIN** = Apenas Administrador

---

## 15. Dicas Importantes

### ✅ Boas Práticas
- Sempre defina o estoque mínimo dos produtos
- Configure preço de custo para cálculo de lucro correto
- Use códigos únicos para produtos (SKU)
- Mantenha categorias organizadas
- Faça backup regular do banco de dados

### ⚠️ Atenção
- Vendedores veem apenas dados do dia atual
- Clientes não têm acesso ao sistema
- Altere perfis apenas pelo Django Admin
- Comprovantes de pagamento são obrigatórios para pedidos

### 🔒 Segurança
- Use senhas fortes
- Não compartilhe credenciais de admin
- Revise logs de auditoria regularmente
- Em produção, configure HTTPS

---

## 16. Próximos Passos

1. ✅ Criar produtos reais do seu negócio
2. ✅ Cadastrar seus vendedores
3. ✅ Configurar categorias específicas
4. ✅ Importar clientes existentes (se houver)
5. ✅ Treinar equipe no uso do sistema
6. ✅ Fazer vendas de teste
7. ✅ Configurar backup automático
8. ✅ Preparar para produção

---

## Suporte

Para dúvidas, consulte:
- `CONTROLE_DE_ACESSO.md` - Detalhes sobre perfis e permissões
- `CAMPOS_FORMULARIOS.md` - Referência de campos dos modelos
- `RESUMO_PROJETO.md` - Visão geral do projeto
- Django Admin - Interface completa de gestão

**Boas vendas! 🚀**
