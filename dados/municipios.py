"""
Lista dos municípios da Bahia.

Junta duas fontes oficiais:
- TSE: código eleitoral do município (usado nos endereços de resultado)
- IBGE: nome com acentuação correta e região geográfica
As duas se ligam pelo código do IBGE, que o próprio TSE informa (campo "cdi").
"""

import unicodedata
from functools import lru_cache

from dados.tse import URL_BASE, ErroNaApi, buscar_json

# Lista de municípios publicada pelo TSE para a eleição de 2026 (todos os estados)
URL_MUNICIPIOS_TSE = f"{URL_BASE}/ele2026/6259/config/mun-e006259-cm.json"
URL_MUNICIPIOS_IBGE = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/estados/29/municipios"
)


def normalizar(texto):
    """Remove acentos e deixa minúsculo: "Camaçari" -> "camacari".

    Assim a busca funciona mesmo se a pessoa digitar sem acento.
    """
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(letra for letra in sem_acento if unicodedata.category(letra) != "Mn")
    return sem_acento.lower().strip()


def corrigir_texto_ibge(texto):
    """A API do IBGE envia "Ilhéus ¿ Itabuna" (o travessão chega como "¿")."""
    return texto.replace(" ¿ ", " – ")


@lru_cache(maxsize=1)
def listar_municipios():
    """Devolve os 417 municípios da Bahia em ordem alfabética."""
    dados_tse = buscar_json(URL_MUNICIPIOS_TSE)
    if not dados_tse:
        raise ErroNaApi("Lista de municípios do TSE indisponível.")
    bahia = next(uf for uf in dados_tse["abr"] if uf["cd"].lower() == "ba")

    # O IBGE é complementar: se falhar, o site continua funcionando sem as regiões.
    try:
        dados_ibge = buscar_json(URL_MUNICIPIOS_IBGE) or []
    except ErroNaApi:
        dados_ibge = []
    ibge_por_codigo = {str(m["id"]): m for m in dados_ibge}

    municipios = []
    for m in bahia["mu"]:
        ibge = ibge_por_codigo.get(m["cdi"])
        if ibge:
            nome = ibge["nome"]
            regiao = corrigir_texto_ibge(ibge["regiao-imediata"]["regiao-intermediaria"]["nome"])
            regiao_imediata = corrigir_texto_ibge(ibge["regiao-imediata"]["nome"])
        else:
            nome = m["nm"].title()
            regiao = regiao_imediata = "Não informada"

        municipios.append({
            "codigo_tse": m["cd"],
            "codigo_ibge": m["cdi"],
            "nome": nome,
            "capital": m["c"] == "s",
            "regiao": regiao,
            "regiao_imediata": regiao_imediata,
        })

    municipios.sort(key=lambda municipio: normalizar(municipio["nome"]))
    return municipios


def encontrar_municipio(termo):
    """Aceita o código do TSE ("35335") ou o nome ("guanambi"). Devolve None se não achar."""
    busca = normalizar(termo)
    for municipio in listar_municipios():
        if municipio["codigo_tse"] == termo or normalizar(municipio["nome"]) == busca:
            return municipio
    return None


def sugerir_municipios(termo, limite=8):
    """Municípios cujo nome contém o termo digitado (para "Você quis dizer...")."""
    busca = normalizar(termo)
    parecidos = [m for m in listar_municipios() if busca in normalizar(m["nome"])]
    return parecidos[:limite]


def agrupar_por_regiao(municipios):
    """Transforma a lista em {"Guanambi": [...], "Salvador": [...]} em ordem alfabética."""
    grupos = {}
    for municipio in municipios:
        grupos.setdefault(municipio["regiao"], []).append(municipio)
    return dict(sorted(grupos.items(), key=lambda item: normalizar(item[0])))
