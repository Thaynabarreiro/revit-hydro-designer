# revit-hydro-designer

Extensão pyRevit para automação de projeto hidrossanitário no Revit.
Ver planejamento completo em [`../PLANO-HIDROSSANITARIO.md`](../PLANO-HIDROSSANITARIO.md).

## Instalação

1. Abra o Revit 2027.
2. Aba **pyRevit** → **Settings**.
3. Em *Custom Extension Directories*, clique em **+** e adicione:
   ```
   C:\Users\Shadow\Documents\00 - Claude - Revit
   ```
   (a pasta **pai** da `.extension`, não a `.extension` em si)
4. **Save Settings and Reload**.
5. Uma aba **Hydro** aparece na faixa de opções.

## Ferramentas

### Auditoria M0

Painel *Auditoria* → botão **Auditoria M0**.

Roda no modelo aberto e extrai:

| Seção | O que responde |
|---|---|
| Tipos de tubulação + routing preferences | O template consegue gerar rede automaticamente? |
| Diâmetros disponíveis | Quais bitolas o dimensionamento pode escolher |
| Sistemas de tubulação | AF / AQ / esgoto / pluvial já definidos? |
| Famílias por categoria | Quais louças e conexões você usa de verdade |
| Parâmetros preenchidos | Quais parâmetros o gerador deve preencher |
| Nomenclatura | Padrão de níveis, folhas e vistas |
| Health check | Warnings, in-place, CAD importado, vistas órfãs |

Saída: relatório `.md` em `..\auditoria\auditoria_<modelo>.md` + resumo na tela.

## Ordem de uso

1. Rode no **`HID_CT_PROJETO TIOS`** (projeto hidrossanitário real) — extrai as
   convenções que o gerador deve seguir.
2. Rode no **`Casa A&R final 2`** (arquitetônico) — verifica o que existe no
   modelo de entrada antes de gerar a rede.
