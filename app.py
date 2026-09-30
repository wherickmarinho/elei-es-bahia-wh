"""
Eleições Bahia: site de resultados eleitorais feito com Flask.

Cada função com @app.route é uma página do site.
Os dados vêm das APIs do TSE e do IBGE (pasta "dados").
O HTML de cada página fica na pasta "templates".

Para rodar:  python app.py   e abrir http://localhost:5000
"""

from flask import Flask, render_template, request

from dados.municipios import (
    agrupar_por_regiao,
    encontrar_municipio,
    listar_municipios,
    normalizar,
    sugerir_municipios,
)
from dados.tse import ELEICAO_PADRAO, ELEICOES, ErroNaApi, buscar_resultado

# static_folder="public": o CSS e o ícone ficam na pasta "public"
# (é a pasta que a Vercel usa para arquivos estáticos).
app = Flask(__name__, static_folder="public", static_url_path="")

# Listas muito grandes (deputados têm centenas de candidatos)
# mostram só os primeiros, para a página não ficar pesada.
LIMITE_DE_CANDIDATOS = 50


# ---------------------------------------------------------------------------
# Filtros para exibir números no padrão brasileiro dentro do HTML
# Uso no template:  {{ 4019830 | numero }}  ->  4.019.830
# ---------------------------------------------------------------------------

@app.template_filter("numero")
def formatar_numero(valor):
    return f"{valor:,}".replace(",", ".")


@app.template_filter("percentual")
def formatar_percentual(valor):
    return f"{valor:.2f}".replace(".", ",") + "%"


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

@app.route("/")
def inicio():
    municipios = []
    destaque = None
    try:
        municipios = listar_municipios()
        # Números de destaque: governador de 2026, Bahia inteira
        destaque = buscar_resultado("2026-1", "0003")
    except ErroNaApi:
        pass  # sem destaques, mas a página continua funcionando

    regioes = {m["regiao"] for m in municipios}
    return render_template(
        "inicio.html",
        municipios=municipios,
        destaque=destaque,
        total_regioes=len(regioes),
        eleicoes=ELEICOES,
    )


@app.route("/resultados")
def resultados():
    # 1. Ler as escolhas do usuário (elas ficam na URL)
    #    Ex.: /resultados?eleicao=2024-1&cargo=0011&municipio=35335
    eleicao_id = request.args.get("eleicao", ELEICAO_PADRAO)
    if eleicao_id not in ELEICOES:
        eleicao_id = ELEICAO_PADRAO
    eleicao = ELEICOES[eleicao_id]

    cargo = request.args.get("cargo", "")
    if cargo not in eleicao["cargos"]:
        cargo = next(iter(eleicao["cargos"]))  # primeiro cargo da eleição

    termo_municipio = request.args.get("municipio", "").strip()
    busca = request.args.get("busca", "").strip()
    mostrar_todos = request.args.get("todos") == "1" or busca != ""

    # 2. Buscar os dados
    erro = None
    municipios = []
    municipio = None
    sugestoes = []
    resultado = None
    try:
        municipios = listar_municipios()
        if termo_municipio:
            municipio = encontrar_municipio(termo_municipio)
            if municipio is None:
                sugestoes = sugerir_municipios(termo_municipio)

        municipio_invalido = termo_municipio and municipio is None
        falta_municipio = eleicao["municipal"] and municipio is None
        if not municipio_invalido and not falta_municipio:
            codigo = municipio["codigo_tse"] if municipio else None
            resultado = buscar_resultado(eleicao_id, cargo, codigo)
    except ErroNaApi as problema:
        erro = str(problema)

    # 3. Filtrar candidatos pela busca e limitar listas grandes
    candidatos = resultado["candidatos"] if resultado else []
    if busca:
        termo = normalizar(busca)
        candidatos = [
            c for c in candidatos
            if termo in normalizar(f"{c['nome_urna']} {c['nome_completo']} {c['numero']} {c['partido']}")
        ]
    total_encontrado = len(candidatos)
    if not mostrar_todos:
        candidatos = candidatos[:LIMITE_DE_CANDIDATOS]

    return render_template(
        "resultados.html",
        eleicoes=ELEICOES,
        eleicao_id=eleicao_id,
        eleicao=eleicao,
        cargo=cargo,
        nome_cargo=eleicao["cargos"][cargo],
        municipios=municipios,
        municipio=municipio,
        termo_municipio=termo_municipio,
        sugestoes=sugestoes,
        busca=busca,
        resultado=resultado,
        candidatos=candidatos,
        total_encontrado=total_encontrado,
        erro=erro,
    )


@app.route("/municipios")
def municipios():
    filtro = request.args.get("q", "").strip()
    erro = None
    lista = []
    try:
        lista = listar_municipios()
    except ErroNaApi as problema:
        erro = str(problema)

    if filtro:
        lista = [m for m in lista if normalizar(filtro) in normalizar(m["nome"])]

    return render_template(
        "municipios.html",
        filtro=filtro,
        regioes=agrupar_por_regiao(lista),
        total=len(lista),
        erro=erro,
    )


@app.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.errorhandler(404)
def pagina_nao_encontrada(_erro):
    return render_template("erro.html", titulo="Página não encontrada",
                           mensagem="O endereço digitado não existe neste site."), 404


@app.errorhandler(500)
def erro_interno(_erro):
    return render_template("erro.html", titulo="Algo deu errado",
                           mensagem="Não foi possível exibir esta página agora. "
                                    "Tente novamente em alguns minutos."), 500


# Só roda quando executamos "python app.py" no computador.
# Na Vercel, ela mesma inicia o "app".
if __name__ == "__main__":
    app.run(debug=True)
