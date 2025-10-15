# 🎯 GUIA VISUAL RÁPIDO - Docker Dashboard

## 🚀 Início em 3 Passos

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  PASSO 1: Duplo-clique em iniciar_dashboard.bat        │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  📁 iniciar_dashboard.bat                              │
│      └─ Verifica Docker ✓                              │
│      └─ Verifica arquivos ✓                            │
│      └─ Mostra menu interativo                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  PASSO 2: Escolha opção 1 (primeira vez)               │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  [1] Iniciar Dashboard (build + start)                 │
│      └─ Constrói imagem Docker 🐳                      │
│      └─ Inicia container                               │
│      └─ Abre navegador automaticamente                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  PASSO 3: Use o dashboard!                             │
│  ───────────────────────────────────────────────────    │
│                                                         │
│  🌐 http://localhost:5000                              │
│      └─ Aplique filtros 🔍                             │
│      └─ Clique nas licenças 👥                         │
│      └─ Monitore contratos 📅                          │
│      └─ Atualize dados 🔄                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                        SEU COMPUTADOR                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     DOCKER DESKTOP                         │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │           CONTAINER: dashboard                       │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌─────────────────────────────────────────────┐    │ │ │
│  │  │  │  Python 3.11                               │    │ │ │
│  │  │  │  ├── Flask 3.0.0                           │    │ │ │
│  │  │  │  ├── Pandas 2.1.3                          │    │ │ │
│  │  │  │  ├── Plotly 5.18.0                         │    │ │ │
│  │  │  │  └── openpyxl 3.1.2                        │    │ │ │
│  │  │  └─────────────────────────────────────────────┘    │ │ │
│  │  │                       ↓                              │ │ │
│  │  │  ┌─────────────────────────────────────────────┐    │ │ │
│  │  │  │  dashboard_flask.py                        │    │ │ │
│  │  │  │  ├── Carrega Excel                         │    │ │ │
│  │  │  │  ├── Processa dados                        │    │ │ │
│  │  │  │  ├── Gera gráficos                         │    │ │ │
│  │  │  │  └── Serve HTTP :5000                      │    │ │ │
│  │  │  └─────────────────────────────────────────────┘    │ │ │
│  │  │                                                      │ │ │
│  │  │  📁 VOLUME MONTADO:                                 │ │ │
│  │  │     LICENCIAMENTO MICROSOFT (1).xlsx ─────┐         │ │ │
│  │  │                                            │         │ │ │
│  │  └────────────────────────────────────────────┼─────────┘ │ │
│  │                                               │           │ │
│  └───────────────────────────────────────────────┼───────────┘ │
│                                                  │             │
│  ┌───────────────────────────────────────────────┼───────────┐ │
│  │  SEU SISTEMA DE ARQUIVOS                     │           │ │
│  │                                               ↓           │ │
│  │  📊 LICENCIAMENTO MICROSOFT (1).xlsx  ◄──── SYNC        │ │
│  │     (Você edita este arquivo)                           │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  NAVEGADOR WEB                                          │ │
│  │                                                          │ │
│  │  http://localhost:5000  ◄───── Porta mapeada 5000:5000 │ │
│  │                                                          │ │
│  │  Dashboard completo com:                                │ │
│  │  • 4 KPIs                                               │ │
│  │  • 7 Gráficos                                           │ │
│  │  • 6 Filtros                                            │ │
│  │  • Modal de usuários                                    │ │
│  │  • Controle de contratos                               │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Atualização de Dados

```
┌─────────────────┐
│  1. Você edita  │
│  Excel no PC    │
│  📝 Ctrl+S      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  2. Docker      │
│  detecta via    │
│  Volume Mount   │
│  🔗             │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  3. Você clica  │
│  🔄 Atualizar   │
│  no Dashboard   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  4. Flask       │
│  recarrega      │
│  dados do Excel │
│  ⚡             │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  5. Gráficos    │
│  atualizam      │
│  instantâneo    │
│  ✨             │
└─────────────────┘
```

**🎯 SEM NECESSIDADE DE REINICIAR O CONTAINER!**

---

## 🎨 Interface do Dashboard

```
┌────────────────────────────────────────────────────────────────┐
│  📊 Dashboard de Licenciamento Microsoft           [🔄 Atualizar]│
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │  💰      │ │  👥      │ │  🏢      │ │  📜      │         │
│  │  Gasto   │ │  Total   │ │  Número  │ │  Número  │         │
│  │  Total   │ │  Usuários│ │  Empresas│ │  Licenças│         │
│  │          │ │          │ │          │ │          │         │
│  │ R$ 150K  │ │   196    │ │    5     │ │    36    │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                 │
├─────────────┬───────────────────────────────────────────────────┤
│             │                                                   │
│  FILTROS 🔍 │  GRÁFICO 1: Gasto por Empresa (Pizza) 🥧         │
│             │  ┌─────────────────────────────────────────────┐ │
│  Empresa    │  │         [Gráfico Plotly Interativo]        │ │
│  [v]        │  └─────────────────────────────────────────────┘ │
│             │                                                   │
│  Estado     │  GRÁFICO 2: Gasto por Licença (Barras) 📊       │
│  [v]        │  ┌─────────────────────────────────────────────┐ │
│             │  │         [Gráfico Plotly Interativo]        │ │
│  Setor      │  └─────────────────────────────────────────────┘ │
│  [v]        │                                                   │
│             │  GRÁFICO 3: Timeline de Contratos 📅             │
│  C. Custo   │  ┌─────────────────────────────────────────────┐ │
│  [v]        │  │         [Gráfico Plotly Interativo]        │ │
│             │  └─────────────────────────────────────────────┘ │
│  Licença    │                                                   │
│  [v]        │  ... (mais 4 gráficos)                           │
│             │                                                   │
│  Modalidade │  LICENÇAS MAIS USADAS 👥                         │
│  [v]        │  ┌─────────────────────────────────────────────┐ │
│             │  │  Microsoft 365 E3 (50)  ◄── Clique aqui!   │ │
│  [Aplicar]  │  │  Microsoft 365 E5 (30)      para ver        │ │
│  [Limpar]   │  │  Office 365 E1 (25)         usuários        │ │
│             │  └─────────────────────────────────────────────┘ │
│             │                                                   │
│             │  CONTROLE DE CONTRATOS 📋                        │
│             │  ┌─────────────────────────────────────────────┐ │
│             │  │ Licença | Empresa | Fim | Dias | Status    │ │
│             │  │ E5      | ABC     | ... | -5   | 🔴 Vencido││
│             │  │ E3      | XYZ     | ... |  3   | 🟡 7 dias ││
│             │  │ E1      | QWE     | ... | 15   | 🔵 30 dias││
│             │  │ ...     | ...     | ... | ...  | ...       ││
│             │  └─────────────────────────────────────────────┘ │
│             │                                                   │
└─────────────┴───────────────────────────────────────────────────┘
```

---

## 🎮 Comandos Rápidos

### ⚡ Via Script (MAIS FÁCIL)
```batch
📁 iniciar_dashboard.bat
   └─ Menu com 7 opções
      [1] Build + Start (primeira vez)
      [2] Start rápido
      [3] Stop
      [4] Ver logs
      [5] Reiniciar
      [6] Status
      [7] Limpar tudo
```

### 🐳 Via Docker Compose
```powershell
docker-compose up -d --build    # 🚀 Build + Start
docker-compose up -d            # ▶️  Start rápido
docker-compose down             # ⏹️  Stop
docker-compose logs -f          # 📋 Ver logs
docker-compose restart          # 🔄 Reiniciar
docker-compose ps               # 📊 Status
docker-compose down -v          # 🗑️  Limpar tudo
```

---

## 🎯 Funcionalidades em Ação

### 1️⃣ FILTROS
```
Selecione → Aplique → Veja resultados
   ↓         ↓           ↓
[Empresa] → [Aplicar] → Todos os gráficos
[Estado]              → atualizam
[Setor]               → instantaneamente!
```

### 2️⃣ VER USUÁRIOS
```
Clique em licença → Modal abre → Lista completa
                                  ├─ Nome
                                  ├─ Email
                                  ├─ Empresa
                                  ├─ Setor
                                  ├─ Estado
                                  ├─ C. Custo
                                  └─ Valores
```

### 3️⃣ CONTROLE DE CONTRATOS
```
Cores indicam urgência:
🔴 Vermelho  → Vencido ou vence hoje
🟡 Amarelo   → Vence em ≤ 7 dias
🔵 Azul      → Vence em ≤ 30 dias
⚪ Branco    → Mais de 30 dias
```

---

## 📊 Gráficos Disponíveis

```
1. 🥧 Gasto por Empresa         (Pizza)
2. 📊 Gasto por Licença         (Barras H)
3. 📅 Timeline de Contratos     (Linha)
4. 🗺️  Gasto por Estado         (Barras)
5. 🥧 Modalidades de Licença    (Pizza)
6. 👥 Licenças Mais Usadas      (Barras)
7. 🏢 Gasto por Setor           (Barras)
```

---

## 🔧 Solução Rápida de Problemas

```
❌ Problema                      ✅ Solução
─────────────────────────────────────────────────────
Porta 5000 em uso              → docker-compose down
                                → Mudar porta em 
                                  docker-compose.yml

Dashboard não atualiza         → Salvar Excel (Ctrl+S)
                                → Clicar 🔄 Atualizar
                                → docker-compose restart

Erro ao construir imagem       → docker system prune -f
                                → docker-compose up --build

Container não inicia           → docker-compose logs
                                → Verificar erro específico

Excel não encontrado           → Verificar nome do arquivo
                                → Deve estar no mesmo dir
```

---

## 📱 Atalhos do Teclado

```
F5              → Atualizar página
Ctrl+Shift+R    → Atualizar forçado (limpa cache)
Ctrl+C          → Parar logs (se rodando em foreground)
Ctrl+S          → Salvar Excel
```

---

## 🎓 Recursos de Aprendizado

```
📖 Documentação
├── INICIO_RAPIDO.md      → ⚡ Comece aqui (3 passos)
├── GUIA_DOCKER.md        → 🐳 Tudo sobre Docker
├── GUIA_FILTROS.md       → 🔍 Como usar filtros
├── GUIA_CONTRATOS.md     → 📅 Sistema de alertas
├── CHECKLIST_DEPLOY.md   → ✅ Verificações antes deploy
├── CHANGELOG.md          → 📝 Histórico de versões
├── RESUMO_DOCKER.md      → 📦 Visão geral
└── README.md             → 📚 Documentação completa
```

---

## 🏆 Status do Projeto

```
✅ Análise de dados         → 100%
✅ Dashboard Flask          → 100%
✅ Sistema de filtros       → 100%
✅ Modal de usuários        → 100%
✅ Controle de contratos    → 100%
✅ Containerização Docker   → 100%
✅ Scripts de automação     → 100%
✅ Documentação completa    → 100%

────────────────────────────────────
🎉 PROJETO COMPLETO E PRONTO! 🎉
────────────────────────────────────
```

---

## 🚀 Próximos Passos Sugeridos

```
1. ✅ Teste local           → docker-compose up -d
2. ✅ Valide funcionalidades → CHECKLIST_DEPLOY.md
3. 🚀 Deploy em servidor    → GUIA_DOCKER.md
4. 🔐 Adicione autenticação → Futuro
5. 📧 Configure alertas     → Futuro
6. 📱 Crie versão mobile    → Futuro
```

---

**🎯 DASHBOARD 100% FUNCIONAL E DOCKERIZADO!**

**Acesse agora**: http://localhost:5000 (após iniciar com `docker-compose up -d`)
