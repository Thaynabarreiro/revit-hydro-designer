# Auditoria de modelo - M0

**Modelo:** `HID_CT_PROJETO TIOS_AP_00_RV00;`

**Revit:** 2027 build 27.2.0.39

## 1. Tipos de tubulacao e routing preferences

| Tipo | Segments | Elbows | Junctions | Crosses | Transitions | Unions | MechanicalJoints | Caps | Pronto? |
|---|---|---|---|---|---|---|---|---|---|
| Gás | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | OK |
| UnMEP - PVC Esgoto Série Normal | 4 | 7 | 6 | 1 | 2 | 2 | 1 | 4 | OK |
| UnMEP - PVC Esgoto Série Reforçada | 1 | 7 | 4 | 1 | 2 | 2 | 1 | 2 | OK |
| UnMEP - PPR - PN 12 | 1 | 4 | 8 | 1 | 4 | 9 | 1 | 1 | OK |
| UnMEP - PPR - PN 20 | 1 | 4 | 8 | 1 | 4 | 9 | 1 | 1 | OK |
| UnMEP - PPR - PN 25 | 1 | 4 | 8 | 1 | 4 | 9 | 1 | 1 | OK |
| UnMEP - PVC Marrom Soldável | 6 | 5 | 3 | 1 | 3 | 12 | 0 | 3 | OK |
| UnMEP - CPVC Branco | 2 | 4 | 4 | 1 | 5 | 8 | 0 | 1 | OK |
| Tubo - Esgoto - Série Normal | 4 | 3 | 1 | 0 | 2 | 1 | 0 | 1 | OK |
| Tubo Marrom - Água Fria - Soldável | 6 | 3 | 1 | 0 | 2 | 2 | 0 | 1 | OK |
| PVC Esgoto Série Reforçada | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | OK |
| Tubo - Esgoto - Série Reforçada | 2 | 3 | 1 | 0 | 2 | 1 | 0 | 1 | OK |

## 2. Diametros disponiveis (pipe segments)

- **PEX - Monocamada** (4 bitolas): 16, 20, 25, 32 mm
- **CPVC - Tigrefire - Material** (7 bitolas): 25, 32, 40, 50, 60, 75, 85 mm
- **PPR - PN12 - Material** (7 bitolas): 32, 40, 50, 63, 75, 90, 110 mm
- **PPR - PN20 - Material** (9 bitolas): 20, 25, 32, 40, 50, 63, 75, 90, 110 mm
- **PPR - PN25 - Material** (9 bitolas): 20, 25, 32, 40, 50, 63, 75, 90, 110 mm
- **CPVC - Aquatherm - Material** (11 bitolas): 15, 20, 22, 25, 28, 35, 42, 54, 73, 89, 114 mm
- **PVC Marrom - Material** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **PVC Branco - Material** (11 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110, 125, 150 mm
- **PVC Branco - Série Normal - Material** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **PVC Bege Pérola - Série Reforçada - Material** (5 bitolas): 40, 50, 75, 100, 150 mm
- **PBS - Classe 12 - Marrom - Material** (2 bitolas): 140, 180 mm
- **PBS - Classe 15 - Marrom - Material** (2 bitolas): 140, 180 mm
- **PBS - Classe 20 - Marrom - Material** (6 bitolas): 50, 60, 75, 100, 140, 180 mm
- **PEX - Monocamada - Material** (4 bitolas): 16, 20, 25, 32 mm
- **ALPEX - Tigregás - Material** (4 bitolas): 16, 25, 26, 32 mm
- **Cobre - CLASSE E** (9 bitolas): 15, 22, 28, 35, 42, 54, 66, 79, 104 mm
- **Cobre2 - CLASSE E** (9 bitolas): 15, 22, 28, 35, 42, 54, 66, 79, 104 mm
- **Cobre2 - 4** (9 bitolas): 15, 22, 28, 35, 42, 54, 66, 79, 104 mm
- **Cobre2 - 5** (9 bitolas): 15, 22, 28, 35, 42, 54, 66, 79, 104 mm
- **Pex - A** (5 bitolas): 16, 20, 25, 32, 40 mm
- **PVC Silentium Amanco - A** (5 bitolas): 40, 50, 75, 100, 150 mm
- **PEAD - DIN 8074** (20 bitolas): 20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 225, 250, 280, 315, 355, 400 mm
- **Ferro Fundido Predial Tradicional - A** (4 bitolas): 50, 75, 100, 150 mm
- **Polipropileno (PP) - 1** (20 bitolas): 20, 25, 32, 40, 50, 63, 75, 90, 110, 125, 140, 160, 180, 200, 225, 250, 280, 315, 355, 400 mm
- **CPVC - Aquatherm** (9 bitolas): 15, 22, 28, 35, 42, 54, 73, 89, 114 mm
- **PVC - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **PVC - Marrom** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **PVC Marrom - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **CPVC - Aquatherm - OQN** (11 bitolas): 15, 20, 22, 25, 28, 35, 42, 54, 73, 89, 114 mm
- **.Esgoto Sanitário Primário - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **Pluvial - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **.Ventilação - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **Esgoto Sanitário Secundário - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **Reuso - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **PVC Branco - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **Alimentação AF - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **Limpeza e extravasor - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **AR CONDICIONADO - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **.Ventilação - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **PVC Azul - Material OQN** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **PVC Bege Pérola - Série Reforçada** (5 bitolas): 40, 50, 75, 100, 150 mm
- **PVC Série R - Gordura - Série Reforçada - Material** (5 bitolas): 40, 50, 75, 100, 150 mm
- **CPVC - AF - Aquaterm - OQN** (11 bitolas): 15, 20, 22, 25, 28, 35, 42, 54, 73, 89, 114 mm
- **UnMEP_PVC Branco - Série Normal** (6 bitolas): 40, 50, 75, 100, 150, 200 mm
- **UnMEP_PVC Bege Pérola - Esgoto Série Reforçada** (5 bitolas): 40, 50, 75, 100, 150 mm
- **UnMEP_PPR - PN12** (7 bitolas): 32, 40, 50, 63, 75, 90, 110 mm
- **UnMEP_PPR - PN20** (9 bitolas): 20, 25, 32, 40, 50, 63, 75, 90, 110 mm
- **UnMEP_PPR - PN25** (8 bitolas): 20, 25, 32, 40, 50, 63, 75, 90 mm
- **PVC Marrom - AF Soldável** (9 bitolas): 20, 25, 32, 40, 50, 60, 75, 85, 110 mm
- **UnMEP_CPVC Branco - Base Tigre** (10 bitolas): 15, 20, 22, 28, 35, 42, 54, 73, 89, 114 mm
- **UnMEP_CPVC Branco - Base Tigre (1)** (10 bitolas): 15, 20, 22, 28, 35, 42, 54, 73, 89, 114 mm

## 3. Sistemas de tubulacao

| Sistema | Abreviacao | Tubos |
|---|---|---|
| Esgoto Primário | ESGPRI | 0 |
| Esgoto Ventilação | ESGVEN | 0 |
| Retorno hidrônico |  | 0 |
| Sanitário | SAN | 0 |
| UnMEP Aqua - Alimentador Predial | UnMEP Aqua - AAP | 15 |
| UnMEP Aqua - Aproveitamento Pluvial | UnMEP Aqua - AAPL | 0 |
| UnMEP Aqua - Bypass/Ventilação/Barrilete | UnMEP Aqua -ABYVEBARR | 2 |
| UnMEP Aqua - Recalque | UnMEP Aqua - AR | 21 |
| UnMEP Aqua - Sucção | UnMEP Aqua - ASUC | 2 |
| UnMEP Aqua - Água Fria | UnMEP Aqua - AAF | 56 |
| UnMEP Aqua - Água Quente | UnMEP Aqua - AAQ | 0 |
| UnMEP Pluv - Dreno de AC | UNMEP Pluv - DAC | 33 |
| UnMEP Pluv - Pluvial | UnMEP Pluv - Pluvial | 27 |
| UnMEP Pool - Aspiração | UnMEP Pool - Aspiração | 0 |
| UnMEP Pool - Cascata | UnMEP Pool - Cascata | 0 |
| UnMEP Pool - Dreno de Fundo | UnMEP Pool - Dreno de Fundo | 0 |
| UnMEP Pool - Esgoto | UnMEP Pool - Esgoto | 0 |
| UnMEP Pool - Hidromassagem | UnMEP Pool - Hidromassagem | 0 |
| UnMEP Pool - Retorno Filtrado | UnMEP Pool - Retorno Filtrado | 0 |
| UnMEP Pool - Retorno de Borda Infinita | UnMEP Pool - Retorno de Borda Infinita | 0 |
| UnMEP Pool - Água Quente | UnMEP Pool - Água Quente | 0 |
| UnMEP Slope - Esgoto | UnMEP Slope - Esgoto | 55 |
| UnMEP Slope - Ventilação | UnMEP Slope - Ventilação | 26 |
| Z - Bombeiros |  | 0 |
| Z - Gás |  | 0 |
| Z - Incêndio Molhada |  | 0 |
| Z - Incêndio Seca |  | 0 |
| Z - Outra proteção contra incêndio |  | 0 |
| ZZ - Hydronic Supply |  | 0 |
| Água fria doméstica | AF | 0 |
| Água quente doméstica | AQ | 0 |

## 4. Familias e tipos por categoria

### Pecas hidrossanitarias - 17 elementos

| Familia :: Tipo | Qtd |
|---|---|
| UnMEP_PH_AF_Chuveiro Elétrico :: UnMEP | 2 |
| UnMEP_PH_AF-ESG_Lavatório Quadrado em Bancada :: UnMEP | 2 |
| UnMEP_PH_AF-ESG_Bacia Sanitária com Caixa Acoplada :: UnMEP | 2 |
| UnMEP_PH_AF-ESG_Pia de Cozinha Com Torneira de Mesa - 01 Cuba1 :: UnMEP 2 | 2 |
| UnMEP_PH_AF-ESG_Máquina de Lavar Comum :: UnMEP | 1 |
| UnMEP_RES_AF_Cavalete de Hidrômetro1 :: UnMEP - 25 mm | 1 |
| UnMEP_PH_AF_Peça Genérica de Parede :: 0 - Peça Genérica | 1 |
| UnMEP_PH_ESG_Fossa Circular Com Anel de Concreto :: UnMEP - DN 1500 | 1 |
| UnMEP_PH_AF_Peça Genérica de Parede :: TQ - Tanquinho | 1 |
| UnMEP_PH_ESG_Sumidouro Circular com Anel de Concreto :: UnMEP - DN 1500 | 1 |
| UnMEP_PH_ESG_Filtro Anaeróbio :: UnMEP - DN 1500 | 1 |
| UnMEP_RES_Reservatorio de Fibra de Vidro :: UnMEP - 1.500 L | 1 |
| UnMEP_PH_PLUV_Poço de Infiltraçao Circular com Anel de Concreto :: UnMEP  - DN 600 | 1 |

### Equipamentos mecanicos - 5 elementos

| Familia :: Tipo | Qtd |
|---|---|
| UnMEP_HVAC_PLUV_Ar Condicionado Split com Caixa de Passagem :: UnMEP - Split 09/12 kBTU's | 4 |
| UnMEP_EQM_MCM_Schneider BC 91 :: UnMEP BC-91 S/T - 1/6 cv | 1 |

### Acessorios de tubulacao - 80 elementos

| Familia :: Tipo | Qtd |
|---|---|
| UnMEP_NAOUTILIZAR_CON_Anel de Concreto :: UnMEP | 9 |
| UnMEP_NAOUTILIZAR_ACE_Engate Flexível - Apenas Quantitativo :: UnMEP | 6 |
| UnMEP_NAOUTILIZAR_ACE_Grelha Hemisférica de Ferro :: UnMEP | 6 |
| UnMEP_NAOUTILIZAR_ACE_Caixa Polar Saídas Laterais :: UnMEP | 4 |
| UnMEP_NAOUTILIZAR_ACE_Sifão Copo :: UnMEP | 4 |
| UnMEP_NAOUTILIZAR_ACE_Prolongador para Caixas e Ralos :: 100 mm | 3 |
| UnMEP_ACE_AFAQ_Registro de Gaveta Metalico :: UnMEP - 25 / 22 mm - 3/4" | 3 |
| UnMEP_ACE_PLUV_Caixa de Areia Quadrada com Tampa de Concreto :: UnMEP - Quadrada 30 x 30 cm | 3 |
| UnMEP_ACE_ESG_Válvula Admissora de Ar com Caixa :: UnMEP_ACE_ESG_Válvula Admissora de Ar com Caixa | 3 |
| UnMEP_ACE_ESG_Caixa Sifonada 100 x 150 x 50 :: UnMEP - Grelha Quadrada | 3 |
| UnMEP_ACE_PLUV_Calha Retangular Metálica1 :: UnMEP - 150 mm | 3 |
| UnMEP_NAOUTILIZAR_ACE_Anel de Vedação para Bacia Sanitária :: UnMEP | 2 |
| UnMEP_ACE_ESG_Caixa de Inspeção Quadrada com Tampa Articulada :: UnMEP - 60 cm | 2 |
| UnMEP_ACE_AF_PVC_Registro Esfera Plastico VS1 :: UnMEP - 25 mm 2 | 2 |
| UnMEP_NAOUTILIZAR_ACE_Valvula de Saida de Agua :: UnMEP - Cozinha | 2 |
| UnMEP_NAOUTILIZAR_CON_Anel de Concreto Auxiliar :: UnMEP | 2 |
| UnMEP_ACE_AFAQ_Registro de Pressao Metalico1 :: UnMEP - 25 / 22 mm - 3/4" | 2 |
| UnMEP_NAOUTILIZAR_ACE_Valvula de Saida de Agua :: UnMEP - Lavatorio | 2 |
| UnMEP_ACE_AF_PVC_Registro de Pressao Plastico :: UnMEP - 25 mm | 2 |
| UnMEP_ACE_PLUV_Calha Retangular Metálica1 :: UnMEP - 150 mm 2 | 2 |
| UnMEP_ACE_AF_PVC_Registro Esfera Plastico VS Compacto :: UnMEP - 32 mm | 1 |
| UnMEP_NAOUTILIZAR_ACE_AF_Caixa Padrão Embasa1 :: UnMEP 2 | 1 |
| UnMEP_ACE_AF_PVC_Registro Esfera Plastico VS :: UnMEP - 40 mm | 1 |
| UnMEP_ACE_AF_PVC_Valvula de Retençao Plastica :: UnMEP - 32 mm | 1 |
| UnMEP_NAOUTILIZAR_ACE_ESG_Toco de Tubo de Esgoto do Hidrômetro1 :: UnMEP 2 | 1 |
| UnMEP_NAOUTILIZAR_ACE_PVC_Torneira Boia :: UnMEP | 1 |
| Registro de Gaveta Bruto :: UnMEP - 32 / 28 mm - 1" | 1 |
| UnMEP_ACE_ESG_Ralo Seco_100 x 40 mm :: UnMEP - Grelha Quadrada | 1 |
| UnMEP_NAOUTILIZAR_ACE_Prolongador para Caixas e Ralos :: 100 x 100 mm | 1 |
| Registro de Gaveta Bruto :: UnMEP - 25 / 20 mm - 3/4" | 1 |
| UnMEP_ACE_AF_PVC_Valvula de Pe com Crivo Plastica :: UnMEP - 40 mm | 1 |
| UnMEP_ACE_ESGPLUV_SN_Valvula de Retencao :: 100mm | 1 |
| UnMEP_NAOUTILIZAR_CON_Anel de Concreto Auxiliar1 :: UnMEP | 1 |
| UnMEP_ACE_ESG_Caixa de Gordura Cilindrica Simples in Loco :: UnMEP | 1 |
| UnMEP_NAOUTILIZAR_CON_Prolongamento para Valvula de Retençao :: UnMEP | 1 |

### Conexoes de tubulacao - 432 elementos

| Familia :: Tipo | Qtd |
|---|---|
| UnMEP_NAOUTILIZAR_CON_SN_Anel de Borracha :: UnMEP | 68 |
| PVC Marrom Soldável_Curva 45°_90° :: Curva | 46 |
| UnMEP_CON_ESGPLUV_SN_Joelho 45_90 :: UnMEP | 36 |
| PVC Esgoto_Anel de Vedação Borracha :: Anel de Vedação Borracha | 30 |
| UnMEP_NAOUTILIZAR_CON_SN_Luva Simples :: UnMEP | 25 |
| Joelho 45_90 - Agua Fria_Soldavel - MEP - Tigre :: Standard | 17 |
| UnMEP_NAOUTILIZAR_CON_PVC_I_Luva com Bucha de Latao :: UnMEP | 17 |
| PVC Esgoto_Joelho 45_90 :: SR_Série Reforçada | 15 |
| PVC Esgoto_Luva Simples para Conexão :: Standard | 15 |
| UnMEP_NAOUTILIZAR_CON_PVC_Plug :: UnMEP | 11 |
| PVC Marrom Soldável_Joelho 45°_90° :: Joelho | 11 |
| Te_Reducao - Agua Fria_Soldavel - MEP - Tigre1 :: Standard 2 | 10 |
| PVC Marrom Soldável_Joelho 90° Azul com Bucha de Latão :: Joelho_20x1/2''_ 25x1/2''_ 25x3/4'' _ 32x3/4'' | 10 |
| UnMEP_NAOUTILIZAR_CON_BSP_Nipple Duplo :: UnMEP | 10 |
| Joelho 45_90 - Serie Reforcada - Esgoto - MEP - Tigre :: Standard | 9 |
| UnMEP_NAOUTILIZAR_CON_PVC_Adaptador com Anel para Caixa de Agua :: UnMEP | 8 |
| Curva 45_90 - Agua Fria_PBS - MEP - Tigre :: Standard | 8 |
| Curva 87 - Serie Reforcada - Esgoto - MEP - Tigre :: Standard | 7 |
| Bucha de Reducao Curta - Agua Fria_Soldavel - MEP - Tigre1 :: Standard 2 | 6 |
| Joelho 45_90 - Serie Normal - Esgoto - MEP - Tigre2 :: Standard | 6 |
| UnMEP_NAOUTILIZAR_CON_SR_Anel de Borracha :: UnMEP | 6 |
| UnMEP_CON_ESGPLUV_SN_Te_Juncao :: UnMEP | 5 |
| UnMEP_NAOUTILIZAR_CON_SN_Te :: UnMEP | 4 |
| UnMEP_CON_ESGPLUV_SN_Bucha de Reducao Longa :: UnMEP | 4 |
| UnMEP_CON_ESGPLUV_SN_Terminal de Ventilacao :: UnMEP | 4 |
| Luva Simples para Conexão - Serie Normal - Esgoto - MEP - Tigre1 :: Standard 2 | 4 |
| Te_Juncao - Serie Normal - Esgoto - MEP - Tigre2 :: Standard | 4 |
| UnMEP_NAOUTILIZAR_CON_PVC_I_Adaptador Curto com Bolsa e Rosca :: UnMEP | 4 |
| Curva 90 Curta - Serie Normal - Esgoto - Tigre :: Standard | 3 |
| UnMEP_NAOUTILIZAR_CON_SN_Plug :: UnMEP | 3 |
| UnMEP_CON_ESGPLUV_SN_Curva 90 Curta :: UnMEP | 2 |
| Bucha de Reducao Longa - Agua Fria_Soldavel - MEP - Tigre1 :: Standard 2 | 2 |
| UnMEP_NAOUTILIZAR_CON_SR_Luva Simples :: UnMEP | 2 |
| Bucha de Reducao Longa - Serie Normal - Esgoto - MEP - Tigre2 :: Standard | 2 |
| Joelho 45_90 - Serie Normal - Esgoto - MEP - Tigre1 :: Standard 2 | 2 |
| UnMEP_CON_ESGPLUV_SR_Te_Juncao :: UnMEP | 2 |
| UnMEP_CON_AF_PVC_Uniao :: UnMEP | 2 |
| Luva Simples para Conexão - Serie Normal - Esgoto - MEP - Tigre :: Standard | 2 |
| UnMEP_CON_AF_PVC_Bucha de Reducao Longa :: UnMEP | 1 |
| Torneira de Jardim :: Torneira de Jardim, 25mm x Ø3/4'' | 1 |
| Luva Simples para Conexão - Serie Normal - Esgoto - MEP - Tigre1 :: Standard | 1 |
| UnMEP_CON_AF_PVC_Te :: UnMEP | 1 |
| UnMEP_CON_ESGPLUV_SN_Curva 45_90 Longa :: UnMEP | 1 |
| Te_Juncao - Serie Reforcada - Esgoto - MEP - Tigre :: Standard | 1 |
| Luva Simples para Conexão - Serie Reforcada - Esgoto - MEP - Tigre :: Standard | 1 |
| Reducao Excentrica - Serie Normal - Esgoto - MEP - Tigre1 :: Standard 2 | 1 |
| UnMEP_NAOUTILIZAR_CON_SN_Joelho 45_90 :: UnMEP | 1 |
| UnMEP_CON_ESGPLUV_SN_Luva de Correr :: UnMEP | 1 |

### Tubulacao - 237 elementos

| Familia :: Tipo | Qtd |
|---|---|
| Tubo Marrom - Água Fria - Soldável | 129 |
| UnMEP - PVC Esgoto Série Normal | 58 |
| Tubo - Esgoto - Série Normal | 16 |
| PVC Esgoto Série Reforçada | 14 |
| Tubo - Esgoto - Série Reforçada | 11 |
| UnMEP - PVC Esgoto Série Reforçada | 9 |

## 5. Parametros preenchidos nas pecas hidrossanitarias

Amostra de 17 peca(s) de 17.

| Parametro | Pecas com valor |
|---|---|
| Famille | 17 |
| Famille et type | 17 |
| Décalage par rapport à l'hôte | 17 |
| Niveau | 17 |
| IfcGUID | 17 |
| Phase de création | 17 |
| Type | 17 |
| Identifiant | 17 |
| Élévation par rapport au niveau | 17 |
| Exporter au format IFC | 17 |
| UnMEP: Calcular Peça | 12 |
| UnMEP: Plug Roscável | 11 |
| UnMEP: CMProvável | 11 |
| UnMEP: Considerar Vazão | 11 |
| UnMEP: CMPossível | 11 |
| UnMEP: Pressão Calculada | 11 |
| UnMEP: Pressão Mínima de Funcionamento da Peça Hidrossanitária | 10 |
| UnMEP: Geometria 3D | 10 |
| UnMEP: Acessórios de Água Fria e Quente | 9 |
| UnMEP: Sigla 3D Esgoto | 9 |
| UnMEP: Altura do Ponto de Água | 9 |
| UnMEP: Sigla 3D Água Fria e Quente | 9 |
| UnMEP: Acessórios de Esgoto | 9 |
| UnMEP: Desconector | 7 |
| UnMEP: Pressão Excedente | 7 |
| UnMEP: Altura do Ponto de Esgoto | 7 |
| UnMEP: Trecho | 6 |
| UnMEP: Raio Nominal Esgoto | 4 |
| UnMEP - Profundidade | 4 |
| UnMEP - Largura | 4 |
| Altura do Pescoço | 4 |
| UnMEP - Distância do Eixo da Cuba | 4 |
| UnMEP - Altura da Bancada | 4 |
| Acabamento | 3 |
| M.T.X | 3 |
| R TAMP. | 3 |
| UnMEP: Profundidade Útil | 3 |
| M.T.Y | 3 |
| Profundidade Não Utilizável | 3 |
| Texto Auxiliar de Posicionamento | 2 |

## 6. Nomenclatura

### Niveis

- `térreo` - 500 mm
- `Cobertura` - 3600 mm
- `Reserv. Superior` - 6200 mm

### Folhas (16)

- `00` - capa
- `01` - Planta Baixa - Água Fria -Térreo
- `02` - Planta Baixa - Esgoto e Pluvial - Térreo
- `03` - Planta Baixa - Pluvial - Cobertura
- `04` - Detalhes - Cozinha
- `05` - Detalhes - Lavanderia
- `06` - Detalhes - Banheiro Suíte
- `07` - Detalhes - Banheiro Principal
- `09` - Detalhes - HID - Cozinha Gourmet
- `10` - Detalhes - ESG - Cozinha Gourmet
- `11` - Detalhes - HID - Banheiro - 2 Pav.
- `12` - Detalhes - ESG - Banheiro - 2 Pav.
- `13` - Detalhes - Coord - Cobertura
- `14` - Lista de Materiais - Hidráulica
- `15` - Lista de Materiais - Pluvial
- `16` - Lista de Materiais - Sanitário

### Vistas (135) - prefixos

| Prefixo | Vistas |
|---|---|
| (sem prefixo) | 45 |
| 3D | 17 |
| Detalhes | 9 |
| UnMEP | 8 |
| PB | 7 |
| Detalhe | 7 |
| Section | 5 |
| Pluvial | 4 |
| Tabela | 4 |
| Lista | 3 |
| Planta | 3 |
| Caixa | 3 |
| TABELA | 2 |
| Catalogos | 2 |
| ALTURA | 2 |
| HIDRO | 1 |
| Banheiro | 1 |
| Perda | 1 |
| Vue | 1 |
| Coeficiente | 1 |

## 7. Health check

- **Warnings:** 24

| Warning | Ocorrencias |
|---|---|
| Aucune déperdition définie | 11 |
| UnMEP Slope - Esgoto 10: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifi | 1 |
| Dans UnMEP Slope - Esgoto 1, les éléments ne sont pas raccordés en un seul réseau physique à cause de l'une ou | 1 |
| Dans UnMEP Slope - Esgoto 5, les éléments ne sont pas raccordés en un seul réseau physique à cause de l'une ou | 1 |
| ESGPRI 1: le flux ne peut pas être calculé parce que la configuration du flux est définie sur Prédéfinie ou Sy | 1 |
| UnMEP Slope - Esgoto 2: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifie | 1 |
| UnMEP Aqua - ASUC 1: le flux ne peut pas être calculé parce que la configuration du flux est définie sur Prédé | 1 |
| ESGPRI 6: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifier la direction | 1 |
| UnMEP Aqua - AR 2: le flux ne peut pas être calculé parce que la configuration du flux est définie sur Prédéfi | 1 |
| UnMEP Aqua - AAF 3: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifier la | 1 |
| UnMEP Slope - Esgoto 9: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifie | 1 |
| Dans UnMEP Aqua - AAF 1, les éléments ne sont pas raccordés en un seul réseau physique à cause de l'une ou des | 1 |
| UnMEP Aqua - AR 1: le flux ne peut pas être calculé, car la direction ne correspond pas. Veuillez vérifier la  | 1 |
| UnMEP Aqua - AAP 1: le flux ne peut pas être calculé parce que la configuration du flux est définie sur Prédéf | 1 |

- **Familias in-place:** 0
- **CAD importado (nao vinculado):** 0
- **Vistas fora de folha:** 112 de 135
- **Grupos de modelo:** 0

---

_Gerado por revit-hydro-designer (M0)._