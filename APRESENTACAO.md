# Simulação de Apresentação — Sistema de Assistência à Saúde do Solo

> Roteiro completo para apresentação de ~15 minutos. Inclui falas sugeridas, demos ao vivo e argumentos técnicos para impressionar o professor.

---

## Abertura (1 min)

**Fala:**
> "Nosso projeto é um Sistema de Suporte à Decisão Agrônoma — não um CRUD com gráficos.
> A diferença está na arquitetura: toda a matemática agronômica é calculada deterministicamente
> no backend usando fórmulas da Embrapa Cerrado. A IA só recebe resultados verificados e
> gera linguagem natural. Isso é o que chamamos de arquitetura híbrida neuro-simbólica."

**Por que isso importa:** abre a apresentação posicionando o sistema acima de "API wrapper",
que é a crítica mais comum de professores a projetos com IA.

---

## 1. Visão Geral do Sistema (2 min)

**Mostre o Dashboard em `localhost:5173`**

Pontos a destacar:
- Score de saúde 0–100 calculado por desvio normalizado de 6 parâmetros (pH, MO, P, K, Ca, Mg)
- Ranking de propriedades por score
- Tendência de pH ao longo do tempo

**Fala:**
> "O score de saúde não é uma nota arbitrária da IA. É a média dos desvios normalizados
> de cada parâmetro em relação à faixa ideal do Cerrado definida pela Embrapa.
> O modelo numérico está todo em `recommendation_service.py` — posso mostrar o código."

---

## 2. Motor Agronômico — mostrar o código (3 min)

**Abra `backend/app/services/recommendation_service.py`**

Mostre e explique:

```python
# Faixas de referência Embrapa Cerrado
_P_THRESHOLDS = {
    "arenosa":  {"min": 10.0, "otimo": 20.0},   # < 150 g/kg argila
    "media":    {"min":  7.0, "otimo": 15.0},   # 150–350 g/kg
    "argilosa": {"min":  4.0, "otimo":  8.0},   # > 350 g/kg
}
```

**Fala:**
> "A interpretação do fósforo varia pela textura do solo. No extrator Mehlich-1 usado
> nos laboratórios brasileiros, o mesmo valor numérico é 'adequado' em solo argiloso
> mas 'baixo' em solo arenoso. Esse conhecimento está embutido no backend como regra
> determinística — não deixamos a IA adivinhar."

Mostre o cálculo de CTC e V%:
```python
fator_acidez = max(0.05, (7.0 - analise.ph) / (analise.ph - 3.5))
m.h_al_estimado = round(m.soma_bases * fator_acidez, 3)
m.ctc = round(m.soma_bases + m.h_al_estimado, 3)
m.saturacao_bases = round((m.soma_bases / m.ctc) * 100, 1)
```

**Fala:**
> "A estimativa de H+Al usa a correlação de Raij — quanto mais ácido o pH, maior a
> acidez potencial. A CTC e a saturação de bases são calculadas a partir disso.
> Esse é o mesmo método que agrônomos usam manualmente no campo."

---

## 3. Simulador de Calagem — demo ao vivo (3 min)

**Navegue para `/simulador`**

1. Selecione uma propriedade e análise com V% baixo (< 40%)
2. Selecione a cultura **Soja**
3. Mova o slider lentamente de 0 para 2.0 t/ha
4. Mostre o V% subindo e o pH mudando em tempo real
5. Espere a narrativa da IA aparecer

**Fala enquanto o slider se move:**
> "A fórmula que roda aqui é a inversa da saturação de bases da Embrapa:
> V2 = V1 + (dosagem × 10 × PRNT × 100) / CTC.
> O pH é estimado pela correlação empírica de Raij para Latossolos do Cerrado.
> O backend calcula tudo isso em microssegundos — a IA só entra depois, para
> explicar em linguagem natural o que aquelas mudanças químicas significam
> para o desenvolvimento radicular da soja."

**Mostre o código em `simulation_service.py`:**
```python
delta_v = (dosagem_calcario * 10 * prnt * 100) / m.ctc
v2 = min(round(m.saturacao_bases + delta_v, 1), 100.0)
ph2 = round(4.0 + 0.025 * v2, 1)
```

**Argumento chave:**
> "Outros sistemas passam o problema inteiro para a IA e pedem uma recomendação.
> Nós passamos a solução verificada e pedimos uma explicação. Isso elimina
> alucinação química — a IA não pode inventar doses porque não calcula doses."

---

## 4. Assistente Conversacional — demo ao vivo (2 min)

**Navegue para `/assistente`**

Faça estas perguntas em sequência:

1. *"Qual propriedade tem o pior score de saúde?"*
2. *"Qual a tendência do fósforo na Fazenda X nos últimos registros?"*
3. *"Com base nos dados, quando eu devo fazer a próxima calagem?"*

**Fala:**
> "O assistente não usa RAG — não há banco vetorial, não há embeddings.
> Avaliamos essa abordagem e descartamos porque embeddings destroem a integridade
> relacional de dados tabulares de série temporal. O que fazemos é serializar
> todo o histórico do usuário em JSON minificado e injetá-lo diretamente
> no contexto da IA com tags XML para isolamento."

**Mostre o código em `assistant_service.py`:**
```python
row = {
    "prop": a.propriedade.nome,
    "d": a.data_analise.isoformat(),
    "ph": a.ph, "p": a.fosforo, "v": m.saturacao_bases,
    "score": m.score_saude,
}
row = {k: v for k, v in row.items() if v is not None}
```

**Argumento chave:**
> "Com modelos de contexto de 128k tokens e dados agrícolas compactos, context stuffing
> garante 100% de recall — literalmente impossível o modelo confundir propriedades
> ou datas porque todos os dados estão presentes na íntegra."

---

## 5. Visualizador de Perfil de Solo Munsell (1 min)

**Navegue para `/report`, selecione uma propriedade com cor_munsell preenchida**

Mostre o perfil colorido vertical ao lado do radar chart.

**Fala:**
> "Cor de solo não é estético — é um proxy científico para carbono orgânico.
> O sistema de classificação Munsell é o padrão global. Nós convertemos a string
> armazenada no banco — por exemplo '10YR 3/2' — em RGB real usando adaptação
> cromática Bradford através do espaço LCHab. Isso é o que software geoespacial
> enterprise faz. O resultado é uma coluna de solo digital que correlaciona
> diretamente com o percentual de matéria orgânica visível no gráfico ao lado."

---

## 6. Testes — mostrar o terminal (2 min)

**Abra dois terminais lado a lado**

Terminal 1:
```bash
docker-compose exec backend pytest tests/ -v
```

Terminal 2:
```bash
docker-compose exec frontend npm run test
```

Mostre ambos rodando e chegando em:
```
23 passed in 0.84s
11 passed in 1.50s
```

**Fala:**
> "34 testes, nenhuma chamada real de API. O backend usa SQLite em memória
> com dependency injection — substituímos o banco e o usuário autenticado
> nos testes sem modificar uma linha do código de produção.
> O frontend mocka axios inteiro. Isso é engenharia de software, não só código que funciona."

**Mostre um teste representativo em `test_recommendation_service.py`:**
```python
def test_v2_calculation(self, mocker):
    mocker.patch("app.services.simulation_service.OpenAI", ...)
    metrics = SoilMetrics(saturacao_bases=40.0, ctc=20.0, ...)
    result = simular_calagem(metrics, dosagem_calcario=1.0, cultura="Soja", analise=None)
    assert result["depois"]["v_pct_simulado"] == 80.0  # 40 + (1*10*0.8*100)/20
```

**Fala:**
> "Esse teste verifica a fórmula Embrapa com valores conhecidos. V1=40%, CTC=20,
> 1 t/ha de calcário → delta_V = 40 pontos → V2 = 80%. Matemática verificável,
> resultado determinístico, cobertura garantida."

---

## Fechamento (1 min)

**Fala:**
> "O que diferencia esse sistema não é ter IA — qualquer projeto tem IA hoje.
> O que diferencia é saber onde a IA pode e onde não pode ser confiada.
>
> Para cálculos agronômicos: zero IA, 100% Embrapa.
> Para linguagem natural sobre resultados verificados: IA é ideal.
> Para consultas sobre dados estruturados: context stuffing, não RAG.
>
> Essa separação deliberada entre camada determinística e camada estocástica
> é o que torna o sistema academicamente defensável e agronomicamente seguro."

---

## Perguntas prováveis do professor — respostas prontas

**"Por que não usaram RAG?"**
> Dados tabulares relacionais com série temporal não embeddificam bem — a busca por
> similaridade semântica mistura propriedades e datas. Context stuffing com 128k tokens
> é mais preciso, mais simples e sem infraestrutura adicional para essa escala.

**"A IA pode errar as doses?"**
> Não. A IA nunca calcula doses. Recebe V% antes/depois já calculado pelo Python
> e gera uma explicação. O número que o agricultor vê vem da fórmula Embrapa, não da IA.

**"Como vocês garantem a qualidade do código?"**
> 34 testes automatizados: 23 backend (pytest), 11 frontend (vitest). Cobertura
> das fórmulas agronômicas com valores conhecidos, endpoints com mocks de LLM,
> componentes Vue com mocks de axios.

**"O sistema funciona sem internet?"**
> O motor agronômico funciona offline — cálculos, scores, recomendações baseadas em
> regras. Só as features que chamam a IA (simulador, assistente, recomendações LLM)
> precisam de conectividade.

**"Por que SQLite nos testes e não PostgreSQL?"**
> Isolamento e velocidade. SQLite em memória garante que cada teste começa limpo,
> roda em < 1s e não precisa de Docker rodando no CI. O SQLAlchemy abstrai
> as diferenças de dialeto para o que testamos (queries básicas + joins).

---

## Checklist pré-apresentação

- [ ] `docker-compose up` rodando — confirmar em `localhost:5173`
- [ ] Seed de dados: `docker-compose exec backend python seed_demo.py`
- [ ] Pelo menos uma análise com V% < 40% (para o simulador ser dramático)
- [ ] Pelo menos uma análise com `cor_munsell` preenchido (ex: `10YR 3/2`)
- [ ] Dois terminais abertos para rodar os testes ao vivo
- [ ] `recommendation_service.py`, `simulation_service.py`, `assistant_service.py` abertos no editor
- [ ] Browser em `localhost:5173/dashboard`
