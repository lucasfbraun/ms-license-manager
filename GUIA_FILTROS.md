# 🔍 Guia Rápido de Filtros

## 📊 Dashboard de Licenciamento Microsoft

---

## 🎯 Como Usar os Filtros

### **Opção 1: Dashboard Flask (Python)**

1. ✅ **Inicie o servidor:**
   ```
   python dashboard_flask.py
   ```

2. ✅ **Abra no navegador:**
   ```
   http://localhost:5000
   ```

3. ✅ **Use os filtros:**
   - No topo da página, você verá 6 dropdowns de filtros
   - Selecione os valores desejados
   - Clique em "🔍 Aplicar Filtros"
   - Os gráficos são atualizados instantaneamente!

---

### **Opção 2: Dashboard HTML com Filtros**

1. ✅ **Abra o arquivo:**
   - Localize: `dashboard_filtros.html`
   - Clique duas vezes

2. ✅ **Carregue a planilha:**
   - Arraste `LICENCIAMENTO MICROSOFT (1).xlsx` para a área indicada

3. ✅ **Use os filtros:**
   - Selecione os valores nos dropdowns
   - Clique em "🔍 Aplicar Filtros"
   - Pronto!

---

## 🔍 Tipos de Filtros Disponíveis

### 1️⃣ **Filtro por Empresa**
- **Para que serve:** Analisar gastos de uma empresa específica
- **Exemplo de uso:** Ver quanto a "EVO SOLUCOES TERMOACUSTICAS" está gastando
- **Resultado:** Todos os gráficos mostram apenas dados dessa empresa

### 2️⃣ **Filtro por Estado**
- **Para que serve:** Análise regional de gastos
- **Exemplo de uso:** Comparar gastos entre SP, RJ, MG
- **Resultado:** Visualize distribuição por estado selecionado

### 3️⃣ **Filtro por Setor**
- **Para que serve:** Análise departamental
- **Exemplo de uso:** Ver gastos do setor "TI" ou "Financeiro"
- **Resultado:** Foco nos gastos de um setor específico

### 4️⃣ **Filtro por Centro de Custo**
- **Para que serve:** Controle financeiro detalhado
- **Exemplo de uso:** Monitorar gastos do centro de custo "CC-001"
- **Resultado:** Visão precisa de um centro de custo

### 5️⃣ **Filtro por Licença**
- **Para que serve:** Análise por tipo de licença
- **Exemplo de uso:** Ver quantas licenças "Microsoft 365 E3" você tem
- **Resultado:** Foco em um tipo específico de licença

### 6️⃣ **Filtro por Modalidade**
- **Para que serve:** Comparar Cloud vs On-Premise
- **Exemplo de uso:** Ver gastos apenas com licenças "Cloud"
- **Resultado:** Análise por modelo de licenciamento

---

## 💡 Exemplos Práticos de Uso

### **Cenário 1: Analisar Gastos de Uma Empresa**
```
1. Filtro Empresa: Selecione "FLEXIVEL-JGS"
2. Clique em "Aplicar Filtros"
3. Veja: Gasto total, quantas licenças, distribuição por setor
```

### **Cenário 2: Comparar Estados**
```
1. Filtro Estado: Selecione "SP"
2. Clique em "Aplicar Filtros"
3. Anote os valores
4. Clique em "Limpar Filtros"
5. Filtro Estado: Selecione "RJ"
6. Compare os resultados!
```

### **Cenário 3: Análise de Centro de Custo**
```
1. Filtro Centro de Custo: Selecione o centro desejado
2. Clique em "Aplicar Filtros"
3. Veja: Quanto está gastando, quais licenças, quais setores
```

### **Cenário 4: Múltiplos Filtros Combinados**
```
1. Filtro Empresa: "EVO SOLUCOES"
2. Filtro Estado: "SP"
3. Filtro Setor: "TI"
4. Clique em "Aplicar Filtros"
5. Resultado: Gastos da empresa EVO, em SP, no setor TI
```

---

## 🎯 Dicas de Uso

### ✅ **Dica 1: Comece com Filtros Amplos**
- Primeiro filtre por Empresa
- Depois refine por Estado ou Setor
- Isso ajuda a entender a hierarquia dos dados

### ✅ **Dica 2: Use "Limpar Filtros"**
- Sempre que quiser voltar à visão completa
- Clique em "🔄 Limpar Filtros"
- Todos os dados voltam a aparecer

### ✅ **Dica 3: Combine Filtros**
- Você pode usar múltiplos filtros ao mesmo tempo
- Exemplo: Empresa + Estado + Setor
- Isso permite análises muito específicas

### ✅ **Dica 4: Monitore os KPIs**
- Ao aplicar filtros, observe os cards no topo
- Eles mostram totais filtrados
- Compare valores antes e depois dos filtros

---

## 📊 Como os Filtros Afetam os Gráficos

Quando você aplica filtros, **TODOS os elementos são atualizados**:

✅ **KPIs (Cards no topo)**
- Gasto Total → Recalculado com dados filtrados
- Total de Usuários → Apenas usuários que atendem aos filtros
- Empresas → Quantidade de empresas nos dados filtrados
- Licenças → Total de licenças filtradas

✅ **Todos os Gráficos**
- Gastos por Empresa → Top empresas filtradas
- Distribuição por Estado → Estados nos dados filtrados
- Centros de Custo → Centros dentro do filtro
- Licenças Mais Usadas → Licenças filtradas
- Modalidades → Distribuição filtrada
- Setores → Setores filtrados
- Fornecedores → Fornecedores filtrados

✅ **Tabela Detalhada**
- Mostra apenas os 50 primeiros registros filtrados

---

## 🔄 Workflow Recomendado

### Para Análise Mensal:

```
1. Abra o dashboard
2. Limpe todos os filtros (visão geral)
3. Anote os totais gerais
4. Filtre por cada empresa individualmente
5. Compare os gastos
6. Identifique empresas com gastos elevados
7. Filtre empresa + centro de custo
8. Encontre onde estão os maiores gastos
9. Tome decisões baseadas nos dados!
```

### Para Análise de Otimização:

```
1. Filtro Modalidade: "Cloud"
2. Veja total de gastos Cloud
3. Limpe filtros
4. Filtro Modalidade: "On-Premise"
5. Compare custos
6. Decida estratégia de migração
```

---

## ❓ Perguntas que os Filtros Respondem

### 💰 **Financeiras:**
- Quanto cada empresa está gastando?
- Qual centro de custo tem maior gasto?
- Qual estado gera mais custos?

### 📊 **Operacionais:**
- Quantas licenças temos por tipo?
- Qual setor usa mais licenças?
- Quais empresas têm mais usuários?

### 🎯 **Estratégicas:**
- Vale a pena migrar para Cloud?
- Quais setores podem otimizar licenças?
- Onde focar esforços de redução de custos?

---

## 🚀 Próximos Passos

1. ✅ Experimente cada filtro individualmente
2. ✅ Combine filtros para análises específicas
3. ✅ Compare períodos (antes/depois de mudanças)
4. ✅ Use os insights para tomar decisões
5. ✅ Atualize a planilha regularmente
6. ✅ Monitore tendências ao longo do tempo

---

**Pronto para otimizar seus gastos com licenças! 💪**
