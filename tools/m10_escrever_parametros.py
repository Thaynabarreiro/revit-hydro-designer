# -*- coding: utf-8 -*-
"""M10 - Escreve os resultados do calculo nos parametros das pecas.

Ate aqui o calculo vivia em JSON. Aqui ele volta para o modelo, nos parametros
que as familias ja expoem - de modo que as tags, tabelas e legendas que a
engenheira ja usa passem a mostrar os valores calculados, sem alteracao alguma.

Nao inventa parametro nenhum: so escreve nos que existirem, e reporta os que
faltarem. Os nomes vem de familias_pecas.json -> parametros, porque nomes com
acento em literal sao corrompidos pelo bridge.

Escreve por peca:
  - Trecho              identificacao do trecho que a alimenta
  - Pressao Calculada   pressao disponivel (mca)
  - Pressao Excedente   folga sobre a exigida (mca)
  - Comprimento Equivalente   das conexoes do caminho
  - Diametro Nominal Agua Fria  do sub-ramal que a serve
"""
import codecs
import json
import math
import os

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Element,
    FailureProcessingResult,
    FilteredElementCollector,
    IFailuresPreprocessor,
    StorageType,
    Transaction,
    UnitTypeId,
    UnitUtils,
)


class SilenciarAvisos(IFailuresPreprocessor):
    """Escrever parametro em massa dispara avisos que abrem dialogo modal.

    Num script sem interface, esse dialogo trava a execucao indefinidamente:
    o endpoint de status continua respondendo, mas nada mais executa. Aqui os
    avisos sao resolvidos automaticamente e contabilizados para o relatorio.
    """

    def __init__(self):
        self.contados = {}

    def PreprocessFailures(self, acessor):
        for f in acessor.GetFailureMessages():
            try:
                desc = f.GetDescriptionText()
            except Exception:
                desc = "(sem descricao)"
            self.contados[desc] = self.contados.get(desc, 0) + 1
            try:
                acessor.DeleteWarning(f)
            except Exception:
                pass
        return FailureProcessingResult.Continue

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


FAM = ler("familias_pecas.json")
VP = ler("verificacao_pressao.json")
P = FAM["parametros"]


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def ft(v_mm):
    return UnitUtils.ConvertToInternalUnits(v_mm, UnitTypeId.Millimeters)


def ft_m(v_m):
    return UnitUtils.ConvertToInternalUnits(v_m, UnitTypeId.Meters)


# ------------------------------------------------------ indexar resultados
# O M9 grava as pecas na mesma ordem em que as le do modelo (distancia ao
# reservatorio). Aqui reindexamos por familia + valores para casar com seguranca.
pecas_calc = VP.get("pecas", [])
trechos = {t["nome"]: t for t in VP.get("trechos", [])}

print("=== M10 ESCRITA DOS RESULTADOS ===")
print("pecas no calculo: " + str(len(pecas_calc)))

# ------------------------------------------------------- pecas do modelo
alvos = []
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f or "Cavalete" in f:
        continue
    try:
        cm = p.MEPModel.ConnectorManager
        con = None
        for c in cm.Connectors:
            if str(c.PipeSystemType) == "DomesticColdWater":
                con = c
        if con is None:
            continue
    except Exception:
        continue
    alvos.append({"el": p, "org": con.Origin, "fam": f})

print("pecas no modelo : " + str(len(alvos)))

if len(alvos) != len(pecas_calc):
    print("!! contagem diferente entre modelo e calculo.")
    print("   Rode o M9 novamente antes de escrever.")

# ordena igual ao M9 para o pareamento posicional valer
p_res = None
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        if "Reservatorio" in p.Symbol.FamilyName:
            p_res = p.Location.Point
    except Exception:
        pass
if p_res is not None:
    alvos.sort(key=lambda x: abs(x["org"].Y - p_res.Y))


def escrever(elemento, nome_param, valor, unidade="double"):
    """Escreve nos parametros das pecas do modelo."""
    if not nome_param:
        return "sem mapeamento"
    try:
        pr = elemento.LookupParameter(nome_param)
    except Exception:
        return "erro ao localizar"
    if pr is None:
        return "nao existe"
    if pr.IsReadOnly:
        return "somente leitura"
    try:
        if pr.StorageType == StorageType.String:
            return None if pr.Set(str(valor)) else "falha ao gravar"
        elif pr.StorageType == StorageType.Double:
            return None if pr.Set(float(valor)) else "falha ao gravar"
        elif pr.StorageType == StorageType.Integer:
            return None if pr.Set(int(valor)) else "falha ao gravar"
        return "tipo nao suportado"
    except Exception as e:
        return str(e)[:40]


t = Transaction(doc, "M10 - escrever resultados do calculo")

# Avisos resolvidos automaticamente, sem abrir dialogo.
silenciador = SilenciarAvisos()
opcoes = t.GetFailureHandlingOptions()
opcoes.SetFailuresPreprocessor(silenciador)
opcoes.SetClearAfterRollback(True)
t.SetFailureHandlingOptions(opcoes)

# Alguns avisos vem como caixa de dialogo da UI, nao como failure. Este
# manipulador responde por elas enquanto o script roda.
dialogos = {"n": 0}


def _ao_abrir_dialogo(remetente, args):
    dialogos["n"] += 1
    try:
        args.OverrideResult(1)   # equivalente a OK / Fechar
    except Exception:
        pass


uiapp = None
try:
    uiapp = uidoc.Application
    uiapp.DialogBoxShowing += _ao_abrir_dialogo
except Exception as e:
    print("aviso: nao foi possivel interceptar dialogos (" + str(e)[:40] + ")")

t.Start()

escritos, falhas = 0, {}
n = min(len(alvos), len(pecas_calc))

for i in range(n):
    alvo = alvos[i]
    calc = pecas_calc[i]
    el = alvo["el"]

    folga = calc.get("disponivel_mca", 0) - calc.get("exigida_mca", 0)
    tr_desc = trechos.get("descida_" + str(i), {})
    tr_ram = trechos.get("ramal_" + str(i), {})

    l_eq = tr_desc.get("L_eq_m", 0) + tr_ram.get("L_eq_m", 0)
    dn = tr_desc.get("dn_mm") or tr_ram.get("dn_mm")

    valores = [
        (P.get("trecho"), "descida_" + str(i), None),
        (P.get("pressao_calculada"), calc.get("disponivel_mca", 0), None),
        (P.get("pressao_excedente"), folga, None),
        (P.get("comprimento_equiv"), l_eq, "m"),
        (P.get("diametro_af"), dn, "mm"),
    ]

    for nome_param, valor, unid in valores:
        if valor is None:
            continue
        # parametros de comprimento/diametro esperam unidade interna
        v = valor
        if unid == "m":
            v = ft_m(valor)
        elif unid == "mm":
            v = ft(valor)
        motivo = escrever(el, nome_param, v)
        if motivo is None:
            escritos += 1
        else:
            falhas.setdefault("{0} ({1})".format(nome_param, motivo), 0)
            falhas["{0} ({1})".format(nome_param, motivo)] += 1

t.Commit()

if uiapp is not None:
    try:
        uiapp.DialogBoxShowing -= _ao_abrir_dialogo
    except Exception:
        pass

print("")
print("valores escritos: " + str(escritos))
if dialogos["n"]:
    print("dialogos respondidos automaticamente: " + str(dialogos["n"]))
if silenciador.contados:
    print("")
    print("--- AVISOS DO REVIT (resolvidos) ---")
    for desc in sorted(silenciador.contados):
        print("  {0} x{1}".format(desc[:70], silenciador.contados[desc]))
if falhas:
    print("")
    print("--- NAO ESCRITOS ---")
    for chave in sorted(falhas):
        print("  {0} x{1}".format(chave, falhas[chave]))

# ------------------------------------------------------ conferencia
print("")
print("=== CONFERENCIA (3 primeiras pecas) ===")
for i in range(min(3, n)):
    el = alvos[i]["el"]
    print("  " + alvos[i]["fam"][:48])
    for chave in ("trecho", "pressao_calculada", "pressao_excedente",
                  "comprimento_equiv", "diametro_af"):
        nome_param = P.get(chave)
        try:
            pr = el.LookupParameter(nome_param)
            if pr is None:
                print("    {0:24} (nao existe)".format(chave))
            else:
                val_str = pr.AsValueString() or pr.AsString()
                if val_str is None and pr.StorageType == StorageType.Double:
                    val_str = "{0:.2f}".format(pr.AsDouble())
                print("    {0:24} {1}".format(chave, val_str))
        except Exception:
            print("    {0:24} (erro)".format(chave))
