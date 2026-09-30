"""
Acesso à API pública de resultados do TSE.

Endereço base: https://resultados.tse.jus.br/oficial
É o mesmo servidor usado pelo aplicativo oficial "Resultados" do TSE.
Os endereços usados aqui estão explicados em docs/01-fontes-de-dados.md
"""

import time

import requests

URL_BASE = "https://resultados.tse.jus.br/oficial"

# Eleições disponíveis na API para a Bahia (verificadas em 30/09/2026).
# "ciclo" e "codigo" são as pastas usadas pelo TSE nos endereços.
# "cargos" liga o código do cargo no TSE ao nome que aparece na tela.
ELEICOES = {
    "2026-1": {
        "titulo": "2026 · 1º turno",
        "ciclo": "ele2026",
        "codigo": "6259",
        "municipal": False,
        "cargos": {
            "0003": "Governador",
            "0005": "Senador",
            "0006": "Deputado Federal",
            "0007": "Deputado Estadual",
        },
    },
    "2024-1": {
        "titulo": "2024 · 1º turno",
        "ciclo": "ele2024",
        "codigo": "619",
        "municipal": True,  # prefeito/vereador: é preciso escolher um município
        "cargos": {"0011": "Prefeito", "0013": "Vereador"},
    },
    "2024-2": {
        "titulo": "2024 · 2º turno",
        "ciclo": "ele2024",
        "codigo": "620",
        "municipal": True,
        "cargos": {"0011": "Prefeito"},
    },
}

# Eleição mostrada quando o usuário ainda não escolheu nenhuma
ELEICAO_PADRAO = "2026-1"


class ErroNaApi(Exception):
    """Erro usado quando a API está fora do ar ou responde com problema."""


# ---------------------------------------------------------------------------
# Busca genérica
# ---------------------------------------------------------------------------

# Cache: guarda cada resposta por alguns minutos para não pedir a mesma
# URL ao TSE a cada visita. O tempo é curto para que, durante a apuração,
# os números novos apareçam logo.
SEGUNDOS_NO_CACHE = 300  # 5 minutos
_cache = {}  # { url: (momento_da_busca, resposta) }


def buscar_json(url):
    """Busca uma URL e devolve o JSON já convertido para dicionário/lista.

    - Devolve None se o arquivo não existir (erro 404).
    - Lança ErroNaApi se a API estiver fora do ar.
    """
    agora = time.time()
    if url in _cache and agora - _cache[url][0] < SEGUNDOS_NO_CACHE:
        return _cache[url][1]

    try:
        resposta = requests.get(url, timeout=15)
    except requests.RequestException:
        raise ErroNaApi("Não foi possível conectar ao servidor de dados.")

    if resposta.status_code == 404:
        dados = None
    elif resposta.ok:
        dados = resposta.json()
    else:
        raise ErroNaApi(f"O servidor de dados respondeu com erro {resposta.status_code}.")

    _cache[url] = (agora, dados)
    return dados


# ---------------------------------------------------------------------------
# Resultado de uma eleição
# ---------------------------------------------------------------------------

def montar_url_resultado(eleicao_id, cargo, codigo_municipio=None):
    """Monta o endereço do resultado no TSE.

    Exemplo (prefeito de Guanambi em 2024):
    .../ele2024/619/dados/ba/ba35335-c0011-e000619-u.json
    Sem município, o arquivo é da Bahia inteira: ba-c0003-e006259-u.json
    """
    eleicao = ELEICOES[eleicao_id]
    codigo = eleicao["codigo"]
    local = f"ba{codigo_municipio}" if codigo_municipio else "ba"
    arquivo = f"{local}-c{cargo}-e{codigo.zfill(6)}-u.json"
    return f"{URL_BASE}/{eleicao['ciclo']}/{codigo}/dados/ba/{arquivo}"


def texto_para_numero(texto):
    """O TSE escreve decimais com vírgula ("80,46"); o Python usa ponto (80.46)."""
    return float(texto.replace(",", "."))


# Na API, vice e suplentes vêm com códigos curtos
TIPOS_DE_COMPANHEIRO = {"v": "Vice", "s1": "1º suplente", "s2": "2º suplente"}


def situacao_da_apuracao(dados):
    """Diz em que ponto está a contagem de votos.

    Campos do TSE usados:
    - "tf": totalização finalizada ("s" = sim)
    - "s" -> "pst": percentual de seções eleitorais já totalizadas
    """
    secoes = dados.get("s", {}).get("pst", "0")
    if dados.get("tf") == "s":
        return {"iniciada": True, "texto": "Totalização concluída"}
    if texto_para_numero(secoes) > 0:
        return {"iniciada": True, "texto": f"Apuração em andamento: {secoes}% das seções totalizadas"}
    return {"iniciada": False, "texto": "Apuração ainda não iniciada"}


def buscar_resultado(eleicao_id, cargo, codigo_municipio=None):
    """Busca o resultado de um cargo e devolve um dicionário organizado.

    Devolve None quando o TSE não tem esse resultado
    (ex.: 2º turno num município que não teve 2º turno).
    """
    dados = buscar_json(montar_url_resultado(eleicao_id, cargo, codigo_municipio))
    if not dados or "carg" not in dados:
        return None

    # A resposta do TSE vem "em camadas":
    # cargo -> agrupamentos (coligações) -> partidos -> candidatos
    candidatos = []
    for agrupamento in dados["carg"][0]["agr"]:
        # tp: "i" = partido isolado, "c" = coligação, "f" = federação
        tem_coligacao = agrupamento["tp"] in ("c", "f")

        for partido in agrupamento["par"]:
            for c in partido["cand"]:
                companheiros = [
                    {
                        "tipo": TIPOS_DE_COMPANHEIRO.get(v["tp"], v["tp"]),
                        "nome_urna": v["nmu"],
                        "nome": v["nm"],
                        "partido": v["sgp"],
                    }
                    for v in c.get("vs", [])
                ]

                # Aqui trocamos os nomes curtos do TSE por nomes claros
                candidatos.append({
                    "numero": c["n"],
                    "nome_urna": c["nmu"],
                    "nome_completo": c["nm"],
                    "partido": partido["sg"],
                    "partido_nome": partido["nm"],
                    "coligacao": agrupamento["nm"] if tem_coligacao else None,
                    "composicao": agrupamento["com"] if tem_coligacao else None,
                    "votos": int(c["vap"]),
                    "percentual": texto_para_numero(c["pvapn"]),
                    # Antes da apuração o TSE manda a situação vazia e não manda "dvt"
                    "situacao": c.get("st", ""),
                    "destino_votos": c.get("dvt", ""),
                    "companheiros": companheiros,
                    "codigo_tse": c["sqcand"],
                })

    # Ordena pela quantidade de votos (maior primeiro).
    # Antes da apuração todos têm 0 votos; aí a ordem fica alfabética.
    candidatos.sort(key=lambda candidato: (-candidato["votos"], candidato["nome_urna"]))

    return {
        "atualizado_em": f"{dados['dg']} às {dados['hg']}",
        "apuracao": situacao_da_apuracao(dados),
        "totais": {
            "eleitorado": int(dados["e"]["te"]),
            "comparecimento": int(dados["e"]["c"]),
            "percentual_comparecimento": dados["e"]["pc"],
            "abstencao": int(dados["e"]["a"]),
            "percentual_abstencao": dados["e"]["pa"],
            "validos": int(dados["v"]["vv"]),
            "brancos": int(dados["v"]["vb"]),
            "nulos": int(dados["v"]["tvn"]),
        },
        "candidatos": candidatos,
    }
