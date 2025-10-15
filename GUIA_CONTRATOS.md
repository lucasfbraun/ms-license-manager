# 📋 Controle de Contratos - Guia Completo

## 🎯 Nova Funcionalidade: Gestão de Contratos

Foi adicionado um **card de controle de contratos** que permite monitorar vencimentos e renovações de forma visual e automatizada!

---

## 📊 Localização

O card "📋 Controle de Contratos por Empresa" está localizado:
- **No final do dashboard**
- Logo após os gráficos de Setor e Fornecedor
- Exibe uma tabela completa de todos os contratos

---

## 🎨 Sistema de Alertas Visuais

### **Código de Cores:**

| Status | Cor | Condição | Ação Necessária |
|--------|-----|----------|-----------------|
| 🔴 **Vencido** | Vermelho | Já passou da data | URGENTE: Renovar imediatamente |
| ⚠️ **Vence em breve** | Amarelo | 7 dias ou menos | ATENÇÃO: Preparar renovação |
| 🔵 **Atenção** | Azul claro | 8 a 30 dias | PLANEJAMENTO: Iniciar processo |
| ✅ **OK** | Branco | Mais de 30 dias | NORMAL: Monitorar |

---

## 📋 Informações Exibidas

### Para cada Empresa:

1. **Status** - Indicador visual do estado do contrato
2. **Empresa** - Nome da empresa
3. **Início do Contrato** - Data de início
4. **Vencimento** - Data de término do contrato
5. **Dias Restantes** - Quantos dias faltam (ou já passaram)
6. **Licenças** - Quantidade total de licenças
7. **Valor Total** - Gasto total com aquela empresa

---

## 🚨 Alertas Críticos

### 🔴 **Contratos Vencidos**
- **Linha em vermelho**
- Mostra "X dias atrás"
- **Ação imediata necessária!**

**Exemplo:**
```
Status: 🔴 Vencido
Empresa: EMPRESA X
Vencimento: 01/10/2025
Dias Restantes: 13 dias atrás
```

### ⚠️ **Vence em 7 Dias ou Menos**
- **Linha em amarelo**
- Mostra "X dias"
- **Preparar renovação urgente**

**Exemplo:**
```
Status: ⚠️ Vence em breve
Empresa: EMPRESA Y
Vencimento: 20/10/2025
Dias Restantes: 6 dias
```

### 🔵 **Vence em até 30 Dias**
- **Linha em azul claro**
- Período de planejamento
- **Iniciar processo de renovação**

**Exemplo:**
```
Status: 🔵 Atenção
Empresa: EMPRESA Z
Vencimento: 10/11/2025
Dias Restantes: 27 dias
```

---

## 📊 Como os Dados São Agrupados

### Agrupamento por Empresa:
- Se uma empresa tem **múltiplos contratos**, o sistema pega:
  - **Data de início**: A mais antiga
  - **Data de vencimento**: A mais recente
  - **Valor total**: Soma de todos os contratos
  - **Licenças**: Soma de todas as licenças

### Ordenação:
- Contratos são ordenados por **data de vencimento**
- **Mais urgentes aparecem primeiro** (no topo)

---

## 💡 Exemplos de Uso

### **Cenário 1: Auditoria Semanal**
```
1. Acesse o dashboard semanalmente
2. Role até "Controle de Contratos"
3. Verifique linhas vermelhas e amarelas
4. Tome ações imediatas nos contratos críticos
```

### **Cenário 2: Planejamento Mensal**
```
1. No início do mês
2. Identifique contratos azuis (30 dias)
3. Inicie processo de cotação/renovação
4. Planeje orçamento necessário
```

### **Cenário 3: Relatório para Gestão**
```
1. Filtre por empresa específica (filtros no topo)
2. Veja status do contrato
3. Exporte dados para relatório
4. Apresente para diretoria
```

### **Cenário 4: Controle Financeiro**
```
1. Veja coluna "Valor Total"
2. Some contratos que vencem no mês
3. Provisione budget para renovações
4. Planeje negociações com fornecedores
```

---

## 🔍 Detalhes Técnicos

### Cálculo de Dias Restantes:
```
Dias Restantes = Data de Vencimento - Data Atual

Se resultado < 0: Contrato vencido
Se resultado ≤ 7: Vence em breve
Se resultado ≤ 30: Atenção
Se resultado > 30: OK
```

### Fonte de Dados:
- **Coluna**: `inicio contrato`
- **Coluna**: `final contrato`
- **Agrupamento**: Por `Empresa`

---

## ⚙️ Funcionalidades Automáticas

### ✅ **Atualização Automática**
- Quando você atualiza a planilha Excel
- Pressiona F5 no navegador
- Os status são recalculados automaticamente

### ✅ **Ordenação Inteligente**
- Contratos mais urgentes no topo
- Facilita identificação rápida

### ✅ **Formatação Brasileira**
- Datas em DD/MM/YYYY
- Valores em R$ X.XXX,XX

### ✅ **Legenda Integrada**
- Explicação dos badges no rodapé da tabela
- Facilita entendimento para todos os usuários

---

## 📈 Workflow Recomendado

### **Processo Semanal:**
1. Segunda-feira: Acessar dashboard
2. Verificar contratos vermelhos (vencidos)
3. Verificar contratos amarelos (< 7 dias)
4. Tomar ações corretivas

### **Processo Mensal:**
1. Início do mês: Revisar todos os contratos
2. Identificar os que vencem em 30 dias
3. Iniciar processo de cotação
4. Preparar documentação de renovação

### **Processo Trimestral:**
1. Análise geral de todos os contratos
2. Verificar histórico de renovações
3. Negociar condições melhores
4. Planejar consolidações/otimizações

---

## 🎯 Benefícios

### ✅ **Nunca Mais Esqueça Renovações**
- Alertas visuais claros
- Sistema de cores intuitivo

### ✅ **Evite Multas por Atraso**
- Identificação proativa de vencimentos
- Tempo hábil para renovação

### ✅ **Otimize Negociações**
- Planejamento antecipado
- Tempo para buscar melhores condições

### ✅ **Controle Financeiro**
- Provisione budget com antecedência
- Evite surpresas no fluxo de caixa

### ✅ **Compliance**
- Mantenha contratos regularizados
- Evite problemas legais

---

## 🚀 Dicas Profissionais

### **Dica 1: Crie Alertas de E-mail**
- Configure lembretes no seu calendário
- Baseado nos contratos amarelos

### **Dica 2: Documente Renovações**
- Anote condições anteriores
- Compare com novas propostas

### **Dica 3: Negocie com Antecedência**
- Use contratos azuis (30 dias) como gatilho
- Peça cotações de múltiplos fornecedores

### **Dica 4: Consolide Contratos**
- Empresas com múltiplos contratos
- Negocie pacotes consolidados

### **Dica 5: Use com Filtros**
- Combine com filtros de empresa/estado
- Análise específica por região

---

## ❓ FAQs

### **P: E se não houver data de contrato?**
**R:** O sistema ignora registros sem data. Apenas contratos com `final contrato` aparecem.

### **P: Como saber qual licença específica está vencendo?**
**R:** A tabela agrupa por empresa. Use os filtros para ver licenças específicas.

### **P: Posso exportar essa lista?**
**R:** Atualmente não, mas você pode copiar/colar da tabela ou fazer print screen.

### **P: O cálculo considera feriados?**
**R:** Não, conta dias corridos. Planeje com margem de segurança.

### **P: Como adicionar novos contratos?**
**R:** Adicione na planilha Excel as colunas `inicio contrato` e `final contrato`.

---

## 📞 Casos de Uso Reais

### **Caso 1: Departamento Financeiro**
"Agora vejo todo mês quais contratos precisam de renovação. Consigo provisionar budget com antecedência e negociar melhores condições!"

### **Caso 2: Gerente de TI**
"As linhas vermelhas me alertam imediatamente sobre contratos vencidos. Nunca mais tive problema de licenças expiradas!"

### **Caso 3: Diretor**
"Uso os contratos azuis (30 dias) para iniciar negociações. Tenho tempo para buscar 3 cotações e escolher a melhor!"

---

## 🎊 Próximas Melhorias Sugeridas

- [ ] Exportar tabela para Excel
- [ ] Enviar alertas automáticos por e-mail
- [ ] Gráfico de vencimentos por mês
- [ ] Histórico de renovações
- [ ] Comparação de preços entre renovações

---

**Mantenha seus contratos sob controle! 💪**

**Acesse agora:** http://localhost:5000
