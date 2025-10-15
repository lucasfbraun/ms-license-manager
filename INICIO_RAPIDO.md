# 🚀 INÍCIO RÁPIDO - Dashboard de Licenciamento

## ⚡ Método Mais Rápido (3 passos)

### Windows - Usando script automatizado

1. **Duplo-clique** no arquivo `iniciar_dashboard.bat`
2. **Escolha opção 1** (primeira vez) ou **opção 2** (já configurado)
3. **Aguarde** o navegador abrir automaticamente em http://localhost:5000

### OU use PowerShell:

```powershell
# Opção 1: Menu interativo
.\iniciar_dashboard.ps1

# Opção 2: Comandos diretos
.\iniciar_dashboard.ps1 rebuild  # Primeira vez
.\iniciar_dashboard.ps1 start    # Iniciar rápido
.\iniciar_dashboard.ps1 stop     # Parar
.\iniciar_dashboard.ps1 logs     # Ver logs
.\iniciar_dashboard.ps1 status   # Status
```

---

## 🐳 Método Manual (Docker)

```powershell
# Primeira vez ou após modificar código
docker-compose up -d --build

# Iniciar (já configurado)
docker-compose up -d

# Parar
docker-compose down

# Ver logs
docker-compose logs -f
```

**Acesse**: http://localhost:5000

---

## 📊 Usando o Dashboard

### 1️⃣ Filtros
- Use a barra lateral à esquerda
- Selecione **Empresa**, **Estado**, **Setor**, etc.
- Clique **"Aplicar Filtros"**

### 2️⃣ Ver Usuários de uma Licença
- Na seção **"Licenças Mais Usadas"**
- **Clique** em qualquer badge de licença
- Modal abre mostrando todos os usuários

### 3️⃣ Controle de Contratos
- Tabela no final da página
- **Vermelho**: Contrato vencido
- **Amarelo**: Vence em ≤7 dias
- **Azul**: Vence em ≤30 dias
- **Branco**: Mais de 30 dias

### 4️⃣ Atualizar Dados
- Modifique a planilha Excel
- Salve (Ctrl+S)
- Clique **"🔄 Atualizar"** no dashboard
- OU pressione **F5** no navegador

---

## 🔧 Comandos Úteis

```powershell
# Status dos containers
docker ps

# Ver logs em tempo real
docker-compose logs -f

# Reiniciar (após modificar Excel)
docker-compose restart

# Parar completamente
docker-compose down

# Remover tudo (containers + volumes)
docker-compose down -v
```

---

## ❓ Problemas Comuns

### Porta 5000 já em uso
```powershell
# Parar container
docker-compose down

# OU edite docker-compose.yml
# Mude "5000:5000" para "5001:5000"
# Acesse localhost:5001
```

### Dashboard não atualiza após modificar Excel
```powershell
# Certifique-se de salvar a planilha
# Depois reinicie
docker-compose restart
```

### Erro ao construir imagem
```powershell
# Limpe o cache do Docker
docker system prune -f
docker-compose up --build
```

---

## 📚 Documentação Completa

- **[GUIA_DOCKER.md](GUIA_DOCKER.md)** - Guia completo de Docker
- **[GUIA_FILTROS.md](GUIA_FILTROS.md)** - Como usar os filtros
- **[GUIA_CONTRATOS.md](GUIA_CONTRATOS.md)** - Controle de contratos
- **[README.md](README.md)** - Documentação geral

---

## ✅ Checklist de Primeira Execução

- [ ] Docker Desktop instalado
- [ ] Arquivo `LICENCIAMENTO MICROSOFT (1).xlsx` presente
- [ ] Executar `docker-compose up -d --build`
- [ ] Acessar http://localhost:5000
- [ ] Testar filtros
- [ ] Clicar em uma licença para ver usuários
- [ ] Verificar tabela de contratos (cores)

---

## 🎯 Próximos Passos

1. **Teste os filtros** - Selecione diferentes combinações
2. **Explore os gráficos** - Passe o mouse para ver detalhes
3. **Clique nas licenças** - Veja quem usa cada uma
4. **Monitore contratos** - Fique atento às cores (vermelho/amarelo)
5. **Atualize dados** - Modifique o Excel e veja as mudanças em tempo real

---

**🎉 Pronto! Dashboard rodando em Docker!**

Dúvidas? Consulte [GUIA_DOCKER.md](GUIA_DOCKER.md) ou verifique os logs com `docker-compose logs -f`.
