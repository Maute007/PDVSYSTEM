# 🚀 Guia Rápido de Deploy no Render

## 📋 Checklist de Arquivos Criados

✅ `requirements.txt` - Todas as dependências Python
✅ `build.sh` - Script de build automático  
✅ `Procfile` - Comando para iniciar o Gunicorn
✅ `runtime.txt` - Python 3.13.0
✅ `.gitignore` - Arquivos a ignorar no Git
✅ `.env.example` - Exemplo de variáveis de ambiente

## 🎯 Passos Resumidos

### 1. Subir código para GitHub
```bash
git init
git add .
git commit -m "Preparado para deploy no Render"
git remote add origin https://github.com/Maute007/PDVSYSTEM.git
git push -u origin main
```

### 2. Criar PostgreSQL no Render
- Dashboard → New + → PostgreSQL
- Name: `pdvsystem-db`
- Copiar: **Internal Database URL**

### 3. Criar Web Service no Render
- Dashboard → New + → Web Service
- Conectar repositório GitHub
- Build Command: `./build.sh`
- Start Command: `gunicorn PDVSYSTEM.wsgi:application`

### 4. Variáveis de Ambiente
Adicionar no Render:
```
SECRET_KEY=gerar-chave-aleatoria-segura
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
DATABASE_URL=colar-url-do-postgresql
```

### 5. Deploy e Acessar
- Aguardar build (5-10 min)
- Acessar: `https://seu-app.onrender.com/admin/`
- Login inicial: `admin` / `admin123`
- **⚠️ TROCAR SENHA IMEDIATAMENTE!**

## 🔑 Gerar SECRET_KEY Segura

Execute no terminal Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 📱 URLs do Sistema

Após deploy, seu sistema estará em:
- **Admin:** `/admin/`
- **Dashboard:** `/admin/dashboard/`
- **Relatórios:** `/admin/sales-reports/`
- **Nova Venda:** `/nova-venda/`
- **Produtos:** `/produtos/`

## ⚙️ Configurações Importantes no settings.py

Já configurado automaticamente:
- ✅ WhiteNoise para arquivos estáticos
- ✅ PostgreSQL em produção
- ✅ SQLite em desenvolvimento local
- ✅ Segurança SSL em produção
- ✅ Compressão de arquivos estáticos

## 🔄 Atualizações Futuras

Para atualizar o sistema:
```bash
git add .
git commit -m "Descrição da mudança"
git push
```

O Render detecta mudanças e faz redeploy automático!

## 🆘 Problemas Comuns

**Build falhou?**
- Verifique se `build.sh` tem permissão de execução
- Confirme que todas as dependências estão em `requirements.txt`

**Erro 502?**
- Verifique logs no Render Dashboard
- Confirme DATABASE_URL está correta

**Static files não carregam?**
- Execute: `python manage.py collectstatic --noinput`
- Verifique WhiteNoise está instalado

## 📞 Suporte

**Desenvolvedor:** Carlos Maute  
**WhatsApp:** +258 865105545  
**Email:** carlxyzsmaute@gmail.com  
**Localização:** Moçambique, Maputo

---

© 2025 PDV System - Sistema desenvolvido com ❤️ em Moçambique
