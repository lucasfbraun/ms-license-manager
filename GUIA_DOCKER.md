# 🐳 Guia de Docker - Dashboard de Licenciamento

## 📋 Pré-requisitos

Certifique-se de ter o Docker instalado:
- **Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Verifique a instalação: `docker --version` e `docker-compose --version`

---

## 🚀 Iniciando o Dashboard no Docker

### Opção 1: Usando Docker Compose (RECOMENDADO)

```powershell
# 1. Construir e iniciar em um único comando
docker-compose up --build

# 2. Ou, para rodar em background (modo daemon)
docker-compose up -d --build
```

**Acesse o dashboard**: http://localhost:5000

### Opção 2: Usando comandos Docker manuais

```powershell
# 1. Construir a imagem
docker build -t licenciamento-dashboard .

# 2. Executar o container
docker run -d `
  --name dashboard `
  -p 5000:5000 `
  -v "${PWD}/LICENCIAMENTO MICROSOFT (1).xlsx:/app/LICENCIAMENTO MICROSOFT (1).xlsx" `
  licenciamento-dashboard
```

---

## 📊 Usando o Dashboard

1. **Abra seu navegador** e acesse: http://localhost:5000
2. **Interaja com os filtros** na barra lateral
3. **Clique nas licenças** para ver usuários
4. **Atualize a planilha** e clique no botão "🔄 Atualizar" no dashboard

---

## 🔄 Atualizando Dados da Planilha

### Método 1: Atualização Automática (Volume Montado)

Com Docker Compose, a planilha está montada como volume. Basta:

1. Abra `LICENCIAMENTO MICROSOFT (1).xlsx` no Excel
2. Faça as modificações necessárias
3. **Salve o arquivo** (Ctrl+S)
4. No dashboard, clique em **"🔄 Atualizar"** ou pressione **F5**

✅ **Não é necessário reiniciar o container!**

### Método 2: Forçar Recarga do Container

Se preferir reiniciar o container:

```powershell
docker-compose restart
```

---

## 🛠️ Comandos Úteis

### Verificar Status dos Containers

```powershell
# Listar containers em execução
docker ps

# Ver logs do dashboard
docker-compose logs

# Ver logs em tempo real (Ctrl+C para sair)
docker-compose logs -f
```

### Parar e Iniciar o Dashboard

```powershell
# Parar o dashboard
docker-compose stop

# Iniciar novamente
docker-compose start

# Parar e remover containers
docker-compose down
```

### Reconstruir a Imagem

Se você modificou arquivos Python (dashboard_flask.py):

```powershell
# Parar, reconstruir e iniciar
docker-compose down
docker-compose up --build -d
```

### Acessar o Terminal do Container

```powershell
# Entrar no container em execução
docker exec -it licenciamento-dashboard-dashboard-1 /bin/bash

# Ou se o nome for diferente
docker exec -it dashboard /bin/bash

# Dentro do container você pode:
# - Ver arquivos: ls -la
# - Verificar processos: ps aux
# - Testar Python: python3 -c "import pandas; print(pandas.__version__)"
```

---

## 🐛 Resolução de Problemas

### Problema: "Port 5000 is already allocated"

**Solução 1**: Parar o container que está usando a porta
```powershell
docker-compose down
```

**Solução 2**: Mudar a porta no docker-compose.yml
```yaml
ports:
  - "5001:5000"  # Acesse localhost:5001
```

### Problema: Dashboard não atualiza após modificar Excel

**Verificações**:
1. Certifique-se de **salvar** a planilha no Excel
2. Clique em **"🔄 Atualizar"** no dashboard
3. Verifique se o volume está montado corretamente:

```powershell
docker inspect licenciamento-dashboard-dashboard-1 | Select-String -Pattern "Mounts" -Context 0,10
```

**Solução**: Reinicie o container
```powershell
docker-compose restart
```

### Problema: "No such file or directory: 'LICENCIAMENTO MICROSOFT (1).xlsx'"

**Causa**: O arquivo Excel não está no diretório esperado

**Solução**:
```powershell
# Verifique se o arquivo está no diretório correto
ls "LICENCIAMENTO MICROSOFT (1).xlsx"

# Reconstrua a imagem
docker-compose down
docker-compose up --build
```

### Problema: Erros ao instalar dependências (pandas, openpyxl)

**Causa**: Falta de compiladores no container

**Solução**: O Dockerfile já inclui gcc/g++. Se ainda assim falhar:
```powershell
# Limpe o cache do Docker e reconstrua
docker-compose down
docker system prune -f
docker-compose up --build
```

### Problema: Container inicia mas não responde

**Verificações**:
```powershell
# Ver logs completos
docker-compose logs

# Verificar se o processo Flask está rodando
docker exec -it licenciamento-dashboard-dashboard-1 ps aux | Select-String -Pattern "python"

# Testar conectividade
curl http://localhost:5000
```

---

## 📦 Estrutura de Arquivos Docker

```
c:\Users\Lucas Braun\Documents\Licenciamento Microsoft\
│
├── Dockerfile              # Definição da imagem Docker
├── docker-compose.yml      # Orquestração do container
├── requirements.txt        # Dependências Python
├── .dockerignore          # Arquivos excluídos do build
│
├── dashboard_flask.py     # Aplicação Flask
├── LICENCIAMENTO MICROSOFT (1).xlsx  # Base de dados
│
└── GUIA_DOCKER.md         # Este guia
```

---

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Edite o `docker-compose.yml` para adicionar variáveis:

```yaml
environment:
  - FLASK_ENV=production
  - EXCEL_FILE=LICENCIAMENTO MICROSOFT (1).xlsx
  - PORT=5000
```

### Alterar Memória e CPU

```yaml
services:
  dashboard:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### Persistência de Logs

```yaml
volumes:
  - ./LICENCIAMENTO MICROSOFT (1).xlsx:/app/LICENCIAMENTO MICROSOFT (1).xlsx
  - ./logs:/app/logs  # Adicione esta linha
```

---

## 🚢 Deploy em Produção

### Opção 1: Servidor Linux

1. **Transfira os arquivos** para o servidor:
```bash
scp -r "Licenciamento Microsoft" usuario@servidor:/opt/
```

2. **No servidor**:
```bash
cd /opt/Licenciamento\ Microsoft
docker-compose up -d --build
```

3. **Configure Nginx como proxy reverso** (opcional):
```nginx
server {
    listen 80;
    server_name licenciamento.suaempresa.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Opção 2: Docker Swarm ou Kubernetes

Para ambientes mais complexos, considere:
- Docker Swarm para clusters simples
- Kubernetes para orquestração avançada

---

## 📚 Recursos Adicionais

- [Documentação Oficial Docker](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Hub - Python Images](https://hub.docker.com/_/python)

---

## ✅ Checklist de Inicialização

- [ ] Docker Desktop instalado e rodando
- [ ] Arquivo `LICENCIAMENTO MICROSOFT (1).xlsx` no diretório
- [ ] Executar `docker-compose up -d --build`
- [ ] Acessar http://localhost:5000
- [ ] Testar filtros e interações
- [ ] Modificar planilha e clicar em "Atualizar"
- [ ] Verificar controle de contratos (cores das linhas)

---

**🎉 Pronto! Seu dashboard está rodando em Docker!**

**Dúvidas?** Consulte a seção de resolução de problemas acima ou verifique os logs com `docker-compose logs -f`.
