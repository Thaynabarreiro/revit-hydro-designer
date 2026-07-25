# Handoff — contexto para continuar em outro assistente

Cole o bloco abaixo como primeira mensagem em Antigravity, Cursor, Codex ou
qualquer cliente com MCP. Ele contém tudo que o assistente precisa saber para
retomar sem repetir descobertas.

---

## Prompt

> Estou construindo um plugin pyRevit que gera projetos hidrossanitários
> automaticamente a partir de um modelo arquitetônico BIM. O repositório está em
> `C:\Users\Shadow\Documents\00 - Claude - Revit`.
>
> **Leia primeiro, nesta ordem:**
> 1. `PLANO-HIDROSSANITARIO.md` — plano completo, decisões de engenharia,
>    achados e armadilhas de API já mapeadas. É a memória do projeto.
> 2. `README.md` — arquitetura e fluxo.
> 3. `tools/run_in_revit.sh` — como executar código dentro do Revit.
>
> **Como você executa código no Revit:**
> O Revit 2027 está aberto com o modelo `HID_Casa_AeR.rvt`. O pyRevit Routes
> está ativo em `http://localhost:48884`. Para rodar Python dentro do Revit:
> ```
> bash tools/run_in_revit.sh caminho/script.py "descricao"
> ```
> Isso faz POST em `/revit_mcp/execute_code/` e devolve o stdout. O objeto `doc`
> já vem injetado. Use este loop: escrever → rodar → ler o erro real → corrigir.
>
> **Regras que NÃO podem ser violadas** (cada uma custou uma sessão para
> descobrir — estão detalhadas no plano):
> - O motor do bridge é IronPython 2.7: sem f-strings, use `.format()`.
> - **Nunca** use literal acentuado num script que passa pelo bridge. O texto é
>   corrompido e `LookupParameter` nunca casa. Leia de JSON com `codecs`.
> - `elemento.Name` é ambíguo em `PipeType`, `PipingSystemType` e
>   `FamilySymbol`. Use `Element.Name.__get__(el)`.
> - Membros de `RoutingPreferenceRuleGroupType` são plurais: `Elbows`,
>   `Junctions`, `Crosses`, `Transitions`, `Unions`, `MechanicalJoints`, `Caps`.
> - `ElementId.Value` devolve `long`, que o `json` do IronPython não serializa.
>   Envolva em `int()`.
> - `doc.Delete` em lote falha inteiro se um id já saiu em cascata. Apague um a
>   um checando `doc.GetElement(id) is None`.
> - Peso é parâmetro de INSTÂNCIA nas famílias específicas e de TIPO nas
>   genéricas. Consulte os dois.
> - Requisições longas estouram o timeout do curl (300s) e **o servidor Routes é
>   single-thread**: se você redisparar, enfileira outra execução e trava o canal.
>   Sempre confirme com `curl http://localhost:48884/revit_mcp/status/` antes de
>   reenviar.
> - Se `status` responde mas `execute_code` não, há **diálogo modal aberto no
>   Revit**. Peça para o usuário fechá-lo — você não consegue.
>
> **Estado atual — água fria funciona ponta a ponta:**
> M0 auditoria, M1 leitura, M2–M4 dimensionamento, M5 colocação, M6e rede
> ortogonal (34 tubos, 78,58 m, 11/11 peças conectadas, 5 warnings), M8 memorial
> e M9 perda de carga, todos rodando. Os diâmetros saem 20/25/32 conforme
> perda de carga, não mais tudo DN 20.
>
> **Pendências conhecidas, em ordem de prioridade:**
>
> 1. **6 tês falham** com *"failed to insert tee"*: peças próximas em Y deixam o
>    trecho de espinha curto demais para o corpo do tê. Correção: agrupar peças
>    por faixa de Y (tolerância ~500 mm), um nó por faixa, com sub-ramal em X
>    servindo o grupo. Arquivo: `tools/m6e_ortogonal.py`.
> 2. **Reservatório modelado no dobro da altura** (12,40 m em vez de 6,20 m).
>    `NewFamilyInstance(ponto, simbolo, nivel, ...)` somou o Z do ponto à cota do
>    nível. Passar `Z = 0` ou o offset correto. Arquivos: `m5_colocar_pecas.py`,
>    `m6e_ortogonal.py`. O M9 já detecta e avisa.
> 3. **Escrever os resultados do M9 nos parâmetros UnMEP** das peças e tubos:
>    `Trecho`, `Pressão Calculada`, `Pressão Excedente`, `Comprimento
>    Equivalente`, `Diâmetro Nominal Água Fria`. Nomes em
>    `data/familias_unmep.json → parametros`. É o que faz as tags e tabelas
>    existentes da engenheira funcionarem sem alteração.
> 4. **Incluir o M9 no memorial** (`tools/m8_memorial.py`): ler
>    `data/verificacao_pressao.json` e acrescentar a tabela de trechos e a
>    verificação de pressão. Remover da seção de ressalvas o texto que diz que a
>    perda de carga não foi verificada — agora foi.
>
> **Fase B — transformar em produto (o grosso do trabalho restante):**
>
> Criar os botões que faltam na extensão pyRevit, seguindo o padrão de
> `revit-hydro-designer.extension/Hydro.tab/Projeto.panel/1 Configurar.pushbutton`
> (esses rodam em CPython 3.12, onde acento em literal é seguro):
>
> - `2 Levantar` — roda o M1 e mostra numa janela o que encontrou: ambientes,
>   dormitórios, pontos de consumo, o que foi agrupado e o que foi inferido.
>   **É o ponto de revisão humana e não pode ser pulado** — foi ele que teria
>   pego os dois bugs reais do projeto.
> - `3 Dimensionar` — roda M2–M4 e M9, exibe os resultados.
> - `4 Colocar peças` — roda o M5.
> - `5 Gerar rede` — roda o M6e.
> - `6 Memorial` — roda o M8 e abre o HTML.
>
> Mais duas tarefas de qualidade:
> - **Verificação de acervo**: antes de gerar, conferir se o template tem as
>   famílias de `data/familias_unmep.json` e listar as que faltam, em vez de
>   falhar no meio.
> - **Tirar os caminhos hardcoded** (`C:/Users/Shadow/...` aparece em todos os
>   scripts de `tools/`). Sem isso o projeto só roda nesta máquina.
>
> **Fases seguintes:** água quente (reaproveita ~80% da água fria), esgoto +
> ventilação (muda para UHC, exige declividade), pluvial (base de pluviometria
> por cidade), fossa/filtro/sumidouro, e o módulo de norma francesa DTU 60.11.
>
> Antes de escrever código, me diga o que entendeu do estado atual e qual sua
> abordagem.

---

## Por que este arquivo existe

Um assistente novo começa sem contexto e refaz as mesmas descobertas — e cada
uma delas custou tempo real de sessão. O plano é a memória do projeto; este
arquivo é o ponteiro para ela.

Vale para qualquer cliente MCP: Antigravity, Cursor, Codex, Windsurf, VS Code
com Copilot, Claude Desktop. O elo com o Revit é o pyRevit Routes (REST local),
não um produto específico — o mesmo `.mcp.json` serve para todos.
