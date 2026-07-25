#!/usr/bin/env bash
# Executa um arquivo .py dentro do Revit via pyRevit Routes.
#
# Uso:  ./run_in_revit.sh caminho/script.py ["descricao"] [--tx]
#
# --tx  envolve a execucao numa Transaction (necessario para MODIFICAR o modelo).
#       Sem a flag, roda em modo leitura (mais seguro para auditoria).
#
# Nota: o motor do Routes e IronPython 2.7 - sem f-strings, use .format().

set -euo pipefail

ARQUIVO="${1:?informe o arquivo .py}"
DESCRICAO="${2:-execucao via bridge}"
USA_TX="false"
[[ "${3:-}" == "--tx" ]] && USA_TX="true"

PAYLOAD="$(mktemp)"
trap 'rm -f "$PAYLOAD"' EXIT

python_json_escape() {
  # Escapa o conteudo do arquivo como string JSON usando jq se houver,
  # senao faz na mao com sed.
  if command -v jq >/dev/null 2>&1; then
    jq -Rs . < "$1"
  else
    sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\r//g' "$1" \
      | awk 'BEGIN{printf "\""} {printf "%s\\n", $0} END{printf "\""}'
  fi
}

{
  printf '{"code": '
  python_json_escape "$ARQUIVO"
  printf ', "description": "%s", "use_transaction": %s}' "$DESCRICAO" "$USA_TX"
} > "$PAYLOAD"

curl -s -m 300 -X POST http://localhost:48884/revit_mcp/execute_code/ \
  -H "Content-Type: application/json" \
  --data-binary @"$PAYLOAD"
