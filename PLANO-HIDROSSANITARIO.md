# Plano — Sistema de Projeto Hidrossanitário Automatizado (pyRevit)

**Autora:** Thayna Barreiro
**Ambiente:** Revit 2027 + pyRevit
**Objetivo:** plugin que lê um projeto arquitetônico e entrega projeto hidrossanitário
completo (traçado + dimensionamento + memorial), configurável para normas BR e FR.

---

## 1. Arquivos de referência

| Papel | Arquivo |
|---|---|
| Input / modelo de teste | `Casa A&R final 2.rvt` |
| Gabarito de validação (projeto real aprovado) | `HID_CT_PROJETO TIOS_AP_00_RV00.rvt` |
| Reserva — fase elétrica futura | `ELE_CT_PROJETO TIOS_EXE_00_RV00.rvt` |

O gabarito serve para extrair convenções reais (nomes de tipos de tubo, parâmetros,
famílias usadas, padrão de traçado) e para benchmark: comparar saída do script × projeto humano.

---

## 2. Arquitetura do sistema

Princípio central: **separar motor de cálculo (varia por país) de motor de modelagem (único)**.

```
revit-hidro/
├── core/
│   ├── reader.py          # lê o modelo: ambientes, paredes, louças, níveis, telhado
│   ├── router.py          # traçado da rede (regras de engenharia) — comum BR/FR
│   ├── modeler.py         # cria tubos/conexões no Revit — comum BR/FR
│   └── writer.py          # escreve parâmetros de volta no modelo
├── norms/
│   ├── base.py            # interface comum (contrato que toda norma implementa)
│   ├── br.py              # NBR 5626 / 7198 / 8160 / 10844 / 7229 / 13969
│   └── fr.py              # DTU 60.11 / DTU 64.1 (ANC) / NF EN 12056
├── data/
│   ├── pluviometria_br.json   # intensidade de chuva por cidade (BR)
│   ├── pluviometria_fr.json   # idem (FR)
│   └── pecas.json             # peças de utilização: vazão/peso/UHC por tipo
├── report/
│   └── memorial.py        # gera memorial de cálculo (DOCX/PDF)
└── ui/                    # botões pyRevit
```

**Por que assim:** trocar BR↔FR vira trocar um módulo em `norms/`. Adicionar uma
terceira norma (Portugal, Espanha) no futuro = adicionar um arquivo. É argumento
de portfólio: arquitetura extensível, não script monolítico.

---

## 3. Subsistemas — escopo e normas

| # | Subsistema | Norma BR | Norma FR | Fase |
|---|---|---|---|---|
| 1 | Água fria (AF) | NBR 5626 | DTU 60.11 | MVP |
| 2 | Hidrômetro / ramal de entrada | NBR 5626 + concessionária | DTU 60.11 | MVP |
| 3 | Reservatório (caixa d'água) | NBR 5626 | DTU 60.11 | MVP |
| 4 | Memorial de cálculo | — | — | MVP |
| 5 | Água quente (AQ) | NBR 7198 | DTU 60.11 + RE2020 | Fase 2 |
| 6 | Esgoto sanitário + ventilação | NBR 8160 | NF EN 12056 | Fase 3 |
| 7 | Pluvial (calhas/condutores) | NBR 10844 | NF EN 12056-3 | Fase 4 |
| 8 | Fossa + filtro + sumidouro | NBR 7229 / 13969 | DTU 64.1 (ANC) | Fase 5 |

### Diferenças BR × FR que afetam a arquitetura (não só fórmulas)

- **Esgoto:** no BR, fossa+filtro+sumidouro é comum em residência sem rede.
  Na FR, o padrão é `tout-à-l'égout`; ANC é caso rural e exige `étude de sol` legal.
  → o plugin precisa perguntar "há rede coletora?" antes de decidir o subsistema 8.
- **Água quente:** FR tem peso regulatório de eficiência (RE2020) — bomba de calor/solar
  mais comum que aquecedor a gás.
- **Pluvial:** muitas comunas FR exigem cisterna de reúso e limitam vazão de despejo
  na rede pública — regra sem equivalente no residencial BR comum.
- **Método de dimensionamento AF:** BR usa método dos pesos (NBR 5626);
  FR usa coeficiente de simultaneidade sobre débito bruto (DTU 60.11). São
  matematicamente diferentes → justifica a separação em `norms/`.

---

## 4. Pluviometria por cidade

Requisito: usuário digita a cidade → sistema retorna intensidade pluviométrica (mm/h).
Fallback: se cidade não estiver na base, mostrar link + campo para inserir manual.

**Fontes:**
- **BR:** Pluvio 2.1 (UFV) e tabelas de IDF da NBR 10844 (anexo com ~200 cidades).
  Também: ANA / INMET para séries históricas.
  Link de fallback a exibir no plugin: http://www.gprh.ufv.br/?area=softwares
- **FR:** Météo-France (données publiques) e as zonas de pluviométrie da NF EN 12056-3.
  Link de fallback: https://meteofrance.com / https://donneespubliques.meteofrance.fr

**Implementação:** `data/pluviometria_*.json` com as cidades mais comuns pré-carregadas
(capitais BR + principais cidades FR, incluindo Nice/PACA). Estrutura:
```json
{ "Nice": { "i_mm_h": 90, "periodo_retorno_anos": 10, "fonte": "NF EN 12056-3 / Météo-France" } }
```

---

## 5. Fossa / filtro / sumidouro — dois modos

Conforme decidido: implementar **ambos**.

- **Modo A — padrão:** assume taxa de percolação típica por tipo de solo
  (usuário escolhe: arenoso / areno-argiloso / argiloso). Rápido, para anteprojeto.
- **Modo B — com ensaio:** usuário insere a taxa de percolação real medida em campo
  (min/cm ou L/m²/dia). Obrigatório para projeto executivo e para ANC na França.

O memorial deve declarar explicitamente qual modo foi usado — é questão de
responsabilidade técnica, não só de cálculo.

---

## 6. Roadmap de execução

### MVP (entregável 1) — AF + hidrômetro + caixa d'água + memorial

| Etapa | Descrição |
|---|---|
| ✅ M0 | Auditoria do gabarito `HID_CT_PROJETO TIOS` — extrair convenções reais |
| ✅ M1 | `reader.py` — ler ambientes, louças e níveis de `Casa A&R final 2.rvt` |
| ✅ M2 | `norms/br.py` — método dos pesos NBR 5626 (vazões, diâmetros, pressão) |
| ✅ M3 | Cálculo de reservatório + posição/altura mínima para pressão |
| ✅ M4 | Dimensionamento do ramal de entrada + hidrômetro |
| 🟡 M5 | `router.py` — traçado por regras (prumadas, paredes hidráulicas, menor caminho) |
| 🟡 M6 | `modeler.py` — criar tubulação real no Revit com diâmetros calculados |
| M7 | `norms/fr.py` — DTU 60.11 (coeficiente de simultaneidade) |
| ✅ M8 | `memorial.py` — gerar HTML/PDF com fórmulas, tabelas e resultados |
| M9 | Validação: rodar no projeto real e comparar com o gabarito humano |

### Fases seguintes
- **Fase 2:** AQ (água quente) — reaproveita ~80% do MVP
- **Fase 3:** Esgoto + ventilação (UHC, declividade, tubo de queda)
- **Fase 4:** Pluvial (área de contribuição do telhado, calhas, condutores)
- **Fase 5:** Fossa + filtro + sumidouro (modos A e B)
- **Fase 6:** Elétrico (usa `ELE_CT_PROJETO TIOS` como gabarito)

---

## 7. Riscos e limites declarados

1. **"Traçado ótimo de menor custo"** — o sistema faz traçado *bom por regras de
   engenharia* com estimativa de custo comparativa, não otimização combinatória
   global (problema tipo árvore de Steiner). Alegação honesta e defensável.
2. **Responsabilidade técnica** — o plugin calcula; a validação e a assinatura são
   da engenheira. O memorial deve trazer aviso explícito.
3. **Validação de norma** — as fórmulas codificadas precisam ser conferidas por
   Thayna contra o texto normativo antes de qualquer uso em projeto real.
4. **Famílias/templates** — o traçado depende de existirem famílias de tubulação e
   conexões carregadas com routing preferences configuradas. Se o template não
   tiver, o `modeler.py` falha. → verificar em M0.

---

## 7b. Progresso e achados

### Infraestrutura
Bridge de execução direta funcionando: `tools/run_in_revit.sh <script.py>` executa
Python dentro do Revit via pyRevit Routes (porta 48884). Permite iterar
(escrever → rodar → ler erro → corrigir) sem intervenção manual.
Motor do Routes é **IronPython 2.7** (sem f-strings); o dos botões pyRevit é CPython 3.12.

### Armadilhas de API já mapeadas (Revit 2027)
1. `elemento.Name` falha por ambiguidade em `PipeType`, `PipingSystemType` e
   `FamilySymbol`. Usar `Element.Name.__get__(el)`.
2. Membros de `RoutingPreferenceRuleGroupType` são **plurais**:
   `Elbows`, `Junctions`, `Crosses`, `Transitions`, `Unions`, `MechanicalJoints`, `Caps`.
3. `ElementId.Value` retorna `long`, que o `json` do IronPython não serializa.
   Envolver em `int()`.

### M0 — auditoria do gabarito (concluído)
- **12 tipos de tubulação, todos com routing preferences completas** → risco 4 eliminado.
- Template é **UnMEP**. A licença do plugin não está mais ativa, mas famílias e
  parâmetros permanecem — inclusive `UnMEP: Pressão Calculada`, `UnMEP: Considerar
  Vazão`, `UnMEP: Trecho`, `UnMEP: Altura do Ponto de Água`. O gerador escreve neles.
  **Decisão:** cálculos próprios usam prefixo próprio, para não depender da UnMEP.
- Convenção de sistemas a reproduzir: `AAF`, `AAQ`, `AAP`, `AR`, `ASUC`,
  `ABYVEBARR`, `AAPL`, `Slope - Esgoto`, `Slope - Ventilação`, `Pluv - Pluvial`.
- Famílias dos 8 subsistemas já existem (fossa, filtro anaeróbio, sumidouro,
  poço de infiltração, reservatório, cavalete de hidrômetro, caixa de gordura).
- Achados de QA: 24 warnings (redes com fluxo não calculável), 112/135 vistas fora
  de folha, nomenclatura de vistas inconsistente, folha 08 ausente, 51 pipe
  segments com duplicatas.

### M1 — reader (concluído)
Casa A&R final 2: 14 ambientes colocados, 22 peças hidráulicas.

**Contagem dupla detectada e corrigida.** Famílias distintas modelando a mesma
louça (cuba + torneira + cuba shared a 0–205 mm; lavatório Manzanita em duas
famílias a 200 mm) inflavam o peso total. Solução: clusterização por proximidade
(`raio_cluster_mm: 700`) — famílias próximas no mesmo ambiente viram um único
ponto de consumo, classificado pela regra mais específica do cluster.

| | peso total | vazão de projeto |
|---|---|---|
| Sem clusterização (errado) | 5,4 | 0,697 L/s |
| Com clusterização | **4,1** | **0,607 L/s** |

Resultado: **9 pontos de consumo**, 0 pendências.
Saída em `data/pontos_consumo.json`; base normativa em `data/pecas_br.json`.

### M2/M3/M4 — dimensionamento AF, reservatório e hidrômetro (concluído)

**Princípio novo, vindo da prática:** o modelo arquitetônico *sempre* vem sem
algumas peças. Em vez de exigir que a arquitetura seja corrigida, o sistema aceita
`pecas_complementares` na configuração do projeto — elas entram no cálculo como se
estivessem modeladas, com a origem registrada (`modelo` × `complementar`).
Neste projeto: máquina de lavar e torneira de jardim.

**Nada de números fixos no código.** Ocupação, consumo per capita, dias de reserva,
coeficiente C, velocidade máxima, diâmetros e modelos de hidrômetro vivem em
`data/config_projeto.json`, um por obra.

Resultados para a Casa A&R:

| Item | Valor |
|---|---|
| Dormitórios detectados | 3 (dormitório 01, dormitório 02, suíte) |
| Moradores | 6 (3 × 2) |
| Consumo diário | 900 L/dia |
| Reservação (2 dias) | 1800 L necessários → **2000 L** adotado |
| Pontos de consumo | 11 (9 do modelo + 2 complementares) |
| Peso total | 5,5 |
| Vazão de projeto | 0,704 L/s (2,53 m³/h) |
| Hidrômetro | 3,0 m³/h DN 20 (folga de 18%) |
| Ramal de entrada | DN 20 mm (v = 2,24 m/s) |

Bug corrigido no caminho: o regex de dormitório capturava `banho suíte 108` pela
palavra "suíte", inflando a ocupação para 8 moradores. Resolvido com
`regex_excluir_dormitorio`.

### Base do template — decisão tomada

Comparação entre as duas opções:

| | Template ERIK `.rte` | Projeto dos Tios |
|---|---|---|
| Tipos de tubulação | 5 | **12** |
| Sistemas | 19 | **31** |
| Pipe segments | 40 | **51** |
| Tipos de louça | 28 | **496** |
| fossa / sumidouro / hidrômetro / calha / poço de infiltração | **ausentes** | presentes |

**Escolhido: o projeto dos Tios.** As famílias de infraestrutura vieram da
biblioteca UnMEP e não podem mais ser baixadas (licença encerrada) — são
insubstituíveis. As instâncias, ao contrário, são triviais de refazer.

Executado em `HID_Casa_AeR.rvt` (cópia): 771 instâncias MEP removidas, acervo
integralmente preservado (12 tipos de tubulação, 31 sistemas, 51 segments,
496 tipos de louça, 320 tipos de conexão). `HID_CT_PROJETO TIOS.rvt` permanece
intocado como benchmark de comparação.

Vínculos apontavam para `Y:\01 - BIMHAUS\...` (drive de rede extinto).
Arquitetura repontada para a cópia local e recarregada.

### Validação da tabela normativa — resolvida

Os tipos da família `UnMEP_PH_AF_Peça Genérica` carregam vazão e peso relativo.
Conferência de `data/pecas_br.json` contra eles:

| Tipo UnMEP | Vazão | Peso | Nossa tabela |
|---|---|---|---|
| LAV - Lavatório | 0,150 L/s | 0,3 | ✅ |
| DUC - Ducha | 0,201 L/s | 0,4 | ✅ |
| CHE - Chuveiro Elétrico | 0,099 L/s | 0,1 | ✅ |
| BSCA - Bacia c/ caixa | 0,150 L/s | 0,3 | ✅ |
| BSVD - Bacia c/ válvula | 1,699 L/s | 32,0 | ✅ |
| PC - Pia de Cozinha | 0,249 L/s | 0,7 | ✅ |
| MLR - Máq. Lavar Roupas | 0,300 L/s | 1,0 | ✅ |
| TQ - Tanquinho | 0,249 L/s | 0,7 | ✅ |
| TJ - Torneira de Jardim | 0,201 L/s | 0,4 | ✅ |

Todos batem. **Divergência única:** o UnMEP adota pressão mínima de 2 mca
(19,6 kPa) para praticamente todas as peças, contra os 5–10 kPa mínimos da norma.
Configurável em `criterio_pressao` (`"norma"` ou `"unmep"`); adotado `"unmep"`
por ser mais conservador. Impacto: altura mínima do reservatório passa de
1,02 m para 2,0 m acima do ponto mais desfavorável.

### Estrutura de famílias UnMEP (essencial para o M5)

O UnMEP não usa uma família por louça: usa **famílias genéricas com um tipo por
peça** — `UnMEP_PH_AF_Peça Genérica de Parede` / `de Piso` (água fria) e
`UnMEP_PH_ESG_Peça Genérica de Parede` / `de Piso` (esgoto). O tipo (`LAV`,
`DUC`, `BSCA`, `PC`, `MLR`, `TQ`, `TJ`…) define vazão, peso e pressão.
O código do tipo está mapeado em `pecas_br.json` no campo `unmep_tipo`.

Armadilha de nomenclatura registrada: buscar "tanque" retorna
`Tanque fortplus - Fortlev`, que é **reservatório de água**, não tanque de lavar
roupa. Usar sempre o código `TQ - Tanquinho` da família genérica.

### M5/M6 — colocação e rede (primeira versão funcionando)

`tools/m5_colocar_pecas.py` lê a arquitetura **através do vínculo** (com
`GetTotalTransform`), clusteriza, e coloca 11 peças no modelo hidro — 9 do modelo
mais 2 complementares. Zero falhas. Mapeamento em `data/familias_unmep.json`.

`tools/m6_rede_agua_fria.py` coloca reservatório (2.000 L) e cavalete de
hidrômetro (DN 20) conforme o M2, e gera a rede de água fria:
**25 tubos, 24 conexões automáticas, 89,84 m**, sistema `UnMEP Aqua - Água Fria`,
tipo `Tubo Marrom - Água Fria - Soldável`. Idempotente: apaga a rede anterior
antes de recriar.

Topologia: cavalete → alimentador predial → reservatório → coluna de descida →
barrilete (dimensionado por peso acumulado) → sub-ramais até a altura do ponto
de água (700 mm).

Peso total lido das famílias: **5,50** — idêntico ao calculado no M2. ✅

#### Limitações desta versão (declaradas, não escondidas)

1. **Todos os trechos saíram DN 20.** O critério de velocidade não é restritivo
   na escala residencial nem no tronco (peso 5,5 → D teórico 17,3 mm). Um
   projetista poria DN 25 no barrilete. **Só o critério de perda de carga (M9)
   corrige isso** — é hoje a lacuna mais relevante do sistema.
2. **Traçado é uma cadeia, não uma árvore.** Os pontos são encadeados por
   distância ao reservatório; não há agrupamento por prumada nem roteamento
   por paredes hidráulicas. Os 89,84 m são bem mais que um projeto real.
3. **Os tubos não estão fisicamente conectados aos conectores das peças.**
   Terminam na coordenada do ponto de água. Enquanto isso não for feito, o Revit
   não calcula vazão na rede (é a origem dos warnings de fluxo).
4. Tubos atravessam paredes em linha reta — sem detecção de obstáculo.

#### M6c/M6d — conexão física (abordagem B)

`Pipe.Create` **a partir de um conector** faz o Revit resolver a conexão na hora;
quando não consegue, abre diálogo modal e trava o script — foi o que derrubou a
sessão anterior. A abordagem que funciona:

1. Criar os tubos **por coordenada** (rápido), ancorando o sub-ramal exatamente
   na origem do conector da peça.
2. Ligar depois com `ConnectTo`, um par por vez, com `try/except` individual.

Resultado: **11 de 11 peças conectadas**, warnings de 25 → 12.

Os tês entre barrilete e sub-ramal (`m6d_tes.py`) saíram **6 de 12**. As seis
falhas trazem todas a mesma mensagem: *"Fitting cannot be created between the
input connectors because the angle..."*.

**Causa raiz identificada:** o traçado é uma cadeia por proximidade, então
trechos consecutivos se encontram em ângulos arbitrários, e o Revit só cria tê
em ângulo válido. Um barrilete real corre **ortogonalmente**, junto às paredes —
e aí todo tê é de 90°.

Ou seja: roteamento ortogonal (Manhattan) resolve três problemas de uma vez —
os tês passam a ser válidos, a rede fica com aparência de projeto real, e o
comprimento total cai. É a próxima tarefa do M5.

### M6e — roteamento ortogonal (concluído)

Traçado em cadeia produzia ângulos arbitrários e o Revit recusava criar tê.
Topologia nova, de barrilete real:

```
reservatorio -> coluna (Z) -> no0
no0 -> espinha (corre em Y, no X do reservatorio)
         |-- ramal (corre em X) -- descida (Z) -- peca
```

Espinha, ramal e descida são mutuamente perpendiculares, então todo encontro
é de 90° e o Revit consegue inserir tê e joelho.

| | cadeia | ortogonal |
|---|---|---|
| Conexões criadas | 6 | **17** |
| Comprimento | 89,84 m | **78,58 m** |
| Warnings | 25 | **5** |
| Peças ligadas | 11/11 | 11/11 |

Restam **6 tês** que falham com *"failed to insert tee"* — peças muito próximas
em Y deixam o trecho de espinha curto demais para o corpo do tê caber.
**Correção especificada:** agrupar peças por faixa de Y (tolerância ~500 mm) e
servir cada faixa por um único nó, com um sub-ramal em X atendendo o grupo.

### M9 — perda de carga (concluído)

`tools/m9_perda_carga.py` + `data/perda_carga_br.json`.
Fair-Whipple-Hsiao para tubo liso (`J = K·Q^1,75·D^-4,75`) mais perdas
localizadas por comprimentos equivalentes. Iteração: a cada passo sobe **um**
diâmetro — o do trecho de maior perda no caminho da peça mais deficitária.
Subir o caminho inteiro de uma vez superdimensionava grosseiramente (a coluna
chegava a DN 110 numa unifamiliar).

**Resultado — acabou o "tudo DN 20":**

| Trecho | DN | v (m/s) |
|---|---|---|
| Coluna | 32 | 0,87 |
| Espinha (tronco) | 32 | 0,54–0,85 |
| Espinha (pontas) | 20–25 | 0,60–1,43 |
| Ramais e descidas | 20 | 0,52–0,95 |

11 de 11 peças atendidas, em 13 iterações.

**Dois achados de engenharia:**
1. A peça crítica é a ducha, com folga de **0,02 mca**. Altura mínima do
   reservatório: **6,18 m**; o nível "Reserv. Superior" está a **6,20 m**.
   O projeto passa raspando — decisão consciente a tomar em revisão.
2. **Bug de colocação:** o reservatório foi modelado a **12,40 m**, o dobro da
   cota do nível. `NewFamilyInstance` interpretou o Z do ponto como
   deslocamento somado à cota do nível. O M9 detecta e usa a cota do nível
   (conservador), mas o M5 precisa passar `Z = 0` ou o offset correto.

#### Armadilhas de API acrescentadas

4. **Nome de parâmetro com acento não pode ser literal no script.** O bridge
   corrompe o texto e `LookupParameter` nunca casa. Todos os nomes vivem em
   `familias_unmep.json → parametros`.
5. **Peso é parâmetro de INSTÂNCIA nas famílias específicas e de TIPO nas
   genéricas.** Consultar os dois antes de assumir um padrão — foi o que causou
   peso total 5,30 em vez de 5,50 na primeira rodada.
6. **`doc.Delete` em lote falha inteiro** se um id já saiu em cascata (apagar um
   tubo remove suas conexões). Apagar um a um, checando `GetElement(id) is None`.
7. **`ElementId(int)` é ambíguo no Revit 2027** — colide com as sobrecargas
   `BuiltInParameter` e `BuiltInCategory`. Usar `ElementId(System.Int64(i))`.
8. **`Pipe.Create` a partir de `Connector` pode abrir diálogo modal** e travar o
   script indefinidamente. Criar por coordenada e ligar depois com `ConnectTo`.

### Decisões de arquitetura do produto

**Modelo hidro é o dono das peças, não a arquitetura.**
O arquitetônico entra apenas como **vínculo** (prática da Thayna e da ISO 19650).
A arquitetura modela mal hidro/elétrica, então o que ela coloca nunca fecha 100%.
Fluxo adotado:

1. O sistema **propõe** as peças a partir dos ambientes do vínculo (banheiro →
   bacia + chuveiro + lavatório; cozinha → pia; lavanderia → tanque + máquina),
   posicionadas no nível correto, com as famílias UnMEP do template hidro.
2. A engenheira **ajusta** — adiciona, remove, move.
3. O cálculo lê **o modelo hidro**, não o vínculo.

Isso substitui com vantagem o fluxo manual antigo: mesmo controle, sem começar do zero.
O vínculo continua servindo para contexto (paredes, níveis, ambientes) e para o
traçado (M5) saber por onde os tubos podem passar.

**Texto fora do código.** Todo texto visível vive em `data/textos_memorial_*.json`.
Motivo técnico: o bridge entrega o script ao `exec()` como unicode e literais
acentuados sofrem dupla codificação (`Cálculo` → `CÃ¡lculo`). Texto lido de JSON
via `codecs` não sofre. Efeito colateral: a versão FR é traduzir um arquivo.

### Pendências de validação de engenharia
- [ ] Tabela de pesos/vazões da NBR 5626 (`data/pecas_br.json`) — conferir contra
      o texto normativo, atentando para a revisão de 2020.
- [ ] Coeficiente C = 0,30 da fórmula Q = C·√(Σpesos).
- [ ] `varanda 119` classificada como `pia` (área gourmet) — confirmar.
- [ ] Lavanderia tem tanque mas nenhuma máquina de lavar modelada — incluir?
- [ ] Nenhuma torneira de jardim modelada — incluir?
- [ ] 68 de 82 elementos de ambiente não estão colocados (achado de QA no arquitetônico).
- [ ] Todos os sub-ramais saíram DN 20. O critério aplicado é só velocidade
      (v ≤ 3 m/s), que não é restritivo na escala residencial. Falta o critério de
      **perda de carga** (M9) — a lavanderia (peso 1,7: tanque + máquina) é a
      candidata mais provável a subir para DN 25.
- [ ] O cálculo de pressão ainda não inclui perda de carga distribuída nem
      localizada; hoje só compara a exigência da peça mais crítica (10 kPa).

## 8. Valor para portfólio (3 frentes)

- **Loom / entrevista:** demonstra engenharia MEP real + automação — combinação rara.
- **Instagram/LinkedIn:** casa vazia → rede completa aparecendo é visualmente forte.
- **GitHub:** projeto complexo, arquitetura extensível, multi-norma. Nome sugerido:
  `revit-hydro-designer`.
