#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
	PYTHON=python3
elif command -v python >/dev/null 2>&1; then
	PYTHON=python
else
	printf '%s\n' "Erro: instale o Python 3 antes de iniciar o projeto."
	exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
	printf '%s\n' "Criando o ambiente virtual..."
	"$PYTHON" -m venv .venv
fi

printf '%s\n' "Instalando ou atualizando as dependencias..."
.venv/bin/python -m pip install -r requirements.txt

printf '%s\n' "Iniciando o site em http://localhost:5000"
exec .venv/bin/python app.py
