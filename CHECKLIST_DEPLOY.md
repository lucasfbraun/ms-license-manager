# ✅ CHECKLIST PRÉ-DEPLOY - Dashboard de Licenciamento

Use este checklist para garantir que tudo está funcionando antes de fazer deploy.

---

## 📋 Verificações Antes de Iniciar

### 1. Arquivos Necessários
```powershell
# Verificar se todos os arquivos existem
ls Dockerfile
ls docker-compose.yml
ls requirements.txt
ls dashboard_flask.py
ls "LICENCIAMENTO MICROSOFT (1).xlsx"
```

**Esperado**: Todos os arquivos devem ser encontrados

### 2. Docker Instalado e Rodando
```powershell
# Verificar versão do Docker
docker --version

# Verificar versão do Docker Compose
docker-compose --version

# Verificar se Docker está rodando
docker ps
```

**Esperado**: 
- Docker version 20.x ou superior
- docker-compose version 1.29.x ou superior
- Lista de containers (pode estar vazia)

### 3. Porta 5000 Disponível
```powershell
# Windows - Verificar se porta 5000 está em uso
netstat -ano | findstr :5000
```

**Esperado**: Nenhum resultado (porta livre)

**Se porta estiver em uso**:
```powershell
# Opção 1: Descobrir processo usando a porta
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess

# Opção 2: Mudar porta no docker-compose.yml
# Edite: ports: "5001:5000"
```

### 4. Espaço em Disco
```powershell
# Verificar espaço disponível
Get-PSDrive C | Select-Object Used,Free
```

**Esperado**: Pelo menos 1GB livre

---

## 🔍 Testes Locais Antes do Deploy

### Teste 1: Build da Imagem
```powershell
# Construir imagem (não iniciar ainda)
docker-compose build
```

**Esperado**: 
```
Successfully built [ID]
Successfully tagged licenciamento-dashboard-dashboard:latest
```

**Se falhar**:
- Verifique se Dockerfile está correto
- Verifique internet (precisa baixar Python 3.11)
- Execute `docker system prune -f` e tente novamente

### Teste 2: Iniciar Container
```powershell
# Iniciar em foreground para ver logs
docker-compose up
```

**Esperado**:
```
dashboard_1 | ================================================================================
dashboard_1 | 🚀 Dashboard de Licenciamento Microsoft
dashboard_1 | ================================================================================
dashboard_1 | 
dashboard_1 | 📊 Dashboard iniciando...
dashboard_1 | 🐳 Rodando em Docker
dashboard_1 | 🌐 Acesse: http://localhost:5000 (do seu navegador)
dashboard_1 | 
dashboard_1 |  * Running on all addresses (0.0.0.0)
dashboard_1 |  * Running on http://127.0.0.1:5000
dashboard_1 |  * Running on http://172.x.x.x:5000
```

**Se falhar**:
- Verifique logs para erros específicos
- Certifique-se de que Excel existe
- Verifique se todas as dependências foram instaladas

**Parar**: Pressione `Ctrl+C`

### Teste 3: Acessar Dashboard
```powershell
# Iniciar em background
docker-compose up -d

# Aguardar 5 segundos
Start-Sleep -Seconds 5

# Testar acesso
curl http://localhost:5000
```

**Esperado**: HTML do dashboard retornado

**Ou abra no navegador**: http://localhost:5000

**Verificar**:
- [ ] Página carrega completamente
- [ ] 4 KPIs aparecem com valores corretos
- [ ] 7 gráficos são exibidos
- [ ] Filtros aparecem na barra lateral
- [ ] Tabela de contratos no final da página

### Teste 4: Testar Filtros
**No navegador**:
1. Selecione uma empresa no filtro
2. Clique "Aplicar Filtros"
3. Verifique se gráficos atualizaram
4. Clique "Limpar Filtros"
5. Verifique se voltou ao normal

**Esperado**: Filtros funcionam sem erros

### Teste 5: Testar Modal de Usuários
**No navegador**:
1. Role até "Licenças Mais Usadas"
2. Clique em qualquer badge de licença
3. Modal deve abrir com lista de usuários
4. Verifique se dados estão corretos
5. Feche o modal

**Esperado**: Modal abre e mostra usuários corretamente

### Teste 6: Testar Controle de Contratos
**No navegador**:
1. Role até a tabela de contratos
2. Verifique se há linhas coloridas:
   - Vermelho: Vencidos
   - Amarelo: ≤7 dias
   - Azul: ≤30 dias
3. Confira se as datas estão corretas

**Esperado**: Cores correspondem aos prazos

### Teste 7: Testar Atualização de Dados
```powershell
# 1. Abrir Excel
& "LICENCIAMENTO MICROSOFT (1).xlsx"

# 2. Fazer uma modificação (ex: mudar valor)
# 3. Salvar (Ctrl+S)
# 4. No navegador, clicar "🔄 Atualizar"
```

**Esperado**: Dashboard atualiza com novos valores

### Teste 8: Volume Mount Funcionando
```powershell
# Verificar se volume está montado
docker inspect licenciamento-dashboard-dashboard-1 | Select-String -Pattern "Source"
```

**Esperado**: Deve mostrar caminho do Excel

### Teste 9: Logs do Container
```powershell
# Ver logs
docker-compose logs

# Ver logs em tempo real
docker-compose logs -f
```

**Esperado**: Sem erros, apenas logs normais do Flask

### Teste 10: Restart Automático
```powershell
# Forçar stop do container
docker stop licenciamento-dashboard-dashboard-1

# Aguardar 10 segundos
Start-Sleep -Seconds 10

# Verificar se reiniciou
docker ps
```

**Esperado**: Container deve reiniciar automaticamente

---

## 🔒 Verificações de Segurança

### 1. Arquivos Sensíveis
```powershell
# Verificar se .env não tem senhas hardcoded
cat .env.example
```

**Esperado**: Apenas valores de exemplo, sem dados reais

### 2. Dockerfile Seguro
```powershell
# Verificar Dockerfile
cat Dockerfile
```

**Verificar**:
- [ ] Não usa imagem `latest` (usa versão específica)
- [ ] Não roda como root (boa prática - futuro)
- [ ] Não expõe informações sensíveis

### 3. Porta Não Exposta Publicamente
```powershell
# Verificar se porta está exposta apenas localmente
docker port licenciamento-dashboard-dashboard-1
```

**Esperado**: `5000/tcp -> 0.0.0.0:5000` (ou 127.0.0.1:5000)

---

## 📊 Verificações de Performance

### 1. Uso de Recursos
```powershell
# Ver uso de CPU e memória
docker stats licenciamento-dashboard-dashboard-1 --no-stream
```

**Esperado**:
- CPU: <10% em idle
- Memória: <300MB em idle

### 2. Tempo de Inicialização
```powershell
# Medir tempo de inicialização
Measure-Command { docker-compose up -d }
```

**Esperado**: 
- Primeira vez: 2-5 minutos (build)
- Subsequentes: 5-15 segundos

### 3. Tempo de Resposta
```powershell
# Testar tempo de resposta
Measure-Command { Invoke-WebRequest http://localhost:5000 }
```

**Esperado**: <2 segundos

---

## 🧹 Limpeza Após Testes

### Se tudo funcionou:
```powershell
# Manter rodando
docker-compose up -d
```

### Se precisa limpar e recomeçar:
```powershell
# Parar e remover tudo
docker-compose down -v

# Limpar cache do Docker
docker system prune -f

# Reconstruir do zero
docker-compose up -d --build
```

---

## 📝 Checklist Final

Antes de considerar pronto para produção:

### Funcionalidades
- [ ] Dashboard carrega sem erros
- [ ] Todos os 7 gráficos aparecem
- [ ] 4 KPIs mostram valores corretos
- [ ] 6 filtros funcionam corretamente
- [ ] Modal de usuários abre e mostra dados
- [ ] Controle de contratos com cores corretas
- [ ] Botão "Atualizar" recarrega dados
- [ ] Volume mount permite editar Excel sem rebuild

### Docker
- [ ] Build da imagem sem erros
- [ ] Container inicia corretamente
- [ ] Logs não mostram erros
- [ ] Porta 5000 acessível
- [ ] Volume montado corretamente
- [ ] Auto-restart funcionando

### Performance
- [ ] Página carrega em <3 segundos
- [ ] Filtros respondem instantaneamente
- [ ] Uso de memória <500MB
- [ ] Uso de CPU <20% em uso normal

### Documentação
- [ ] README.md atualizado
- [ ] GUIA_DOCKER.md completo
- [ ] INICIO_RAPIDO.md testado
- [ ] Scripts .bat e .ps1 funcionando
- [ ] Todos os guias revisados

### Segurança
- [ ] Sem senhas no código
- [ ] .env.example sem dados reais
- [ ] Dockerfile seguro
- [ ] Porta não exposta publicamente (localhost apenas)

---

## 🚀 Pronto para Deploy!

Se todos os checkboxes acima estão marcados, você está pronto para:

### Deploy Local
```powershell
docker-compose up -d
```

### Deploy em Servidor
```bash
# 1. Transferir arquivos
scp -r . usuario@servidor:/opt/dashboard/

# 2. No servidor
cd /opt/dashboard
docker-compose up -d --build

# 3. (Opcional) Configurar Nginx
# Ver GUIA_DOCKER.md seção "Deploy em Produção"
```

---

## 📞 Suporte

**Se algum teste falhar**:
1. Consulte [GUIA_DOCKER.md](GUIA_DOCKER.md) seção "Resolução de Problemas"
2. Execute `docker-compose logs -f` para ver erros detalhados
3. Verifique cada teste individualmente
4. Reconstrua do zero se necessário: `docker-compose down -v && docker-compose up -d --build`

---

**✅ Checklist criado para garantir qualidade e funcionalidade completa!**

**Última atualização**: Data atual  
**Versão**: 1.0.0
