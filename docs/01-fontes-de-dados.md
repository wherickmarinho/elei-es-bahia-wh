# Etapa 1 — Fontes de dados

Pesquisa feita em 24/09/2026.

## Fonte principal: servidor de resultados do TSE

Os dados são buscados **direto de URLs públicas do TSE**, dentro do código.
Não é preciso baixar arquivos nem usar chave de acesso.

Endereço base: `https://resultados.tse.jus.br/oficial`

É o mesmo servidor usado pelo app oficial **Resultados** do TSE. Os arquivos
são JSON públicos. O TSE não publica um manual desta API; a estrutura dos
endereços foi identificada a partir do índice que o próprio servidor publica
(`/comum/config/ele-c.json`).

| O quê | URL (exemplo) |
|---|---|
| Lista de eleições | `/comum/config/ele-c.json` |
| Municípios (com código do IBGE) | `/ele2026/6259/config/mun-e006259-cm.json` |
| Resultado na Bahia inteira | `/ele2026/6259/dados/ba/ba-c0003-e006259-u.json` |
| Resultado em um município | `/ele2024/619/dados/ba/ba35335-c0011-e000619-u.json` |

A API também publica fotos dos candidatos, mas este site não as utiliza (usa um ícone genérico).

Como ler o nome do arquivo `ba35335-c0011-e000619-u.json`:

- `ba`: estado (Bahia)
- `35335`: código do município no TSE (35335 = Guanambi). Sem esse número, o arquivo é da Bahia inteira.
- `c0011`: cargo (0011 = Prefeito)
- `e000619`: código da eleição (619 = 2024, 1º turno)
- `u`: tipo do arquivo (resultado completo)

### Códigos usados

| Eleição | Código | Cargos disponíveis |
|---|---|---|
| 2026 — 1º turno (geral) | `ele2026/6259` | Governador (0003), Senador (0005), Dep. Federal (0006), Dep. Estadual (0007) |
| 2024 — 1º turno (municipal) | `ele2024/619` | Prefeito (0011), Vereador (0013) |
| 2024 — 2º turno (municipal) | `ele2024/620` | Prefeito (0011) |

> **Atualização de 30/09/2026:** o TSE retirou os arquivos de 2022 (`ele2022/546` e `547`)
> do servidor e publicou os de 2026. Antes da votação, os arquivos de 2026 trazem os
> candidatos registrados com 0 votos e situação vazia; os votos entram durante a apuração.
> O campo `tf` indica se a totalização terminou e `s.pst` o % de seções totalizadas.

### O que cada resultado traz

- Candidato: nome completo, nome de urna, número, partido, coligação/federação, vice.
- Situação: "Eleito", "Não eleito", "2º turno"...
- Votos e **percentual já calculado pelo TSE**.
- Totais: eleitorado, comparecimento, abstenção, brancos, nulos e votos válidos.

## Fonte complementar: IBGE

[API de Localidades e Malhas do IBGE](https://servicodados.ibge.gov.br/api/docs):
desenho do mapa da Bahia (417 municípios). O arquivo de municípios do TSE
já traz o código do IBGE de cada município (campo `cdi`), o que permite
ligar os dois.

## Limitações conhecidas

- A API do servidor de resultados não tem documentação oficial; o formato pode mudar.
- Não encontramos 2018 e 2020 nesse servidor. Para anos antigos, a fonte
  oficial é o [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/),
  que só permite download pelo navegador (downloads por programa recebem erro 403).
- Os resultados de 2026 só existirão a partir da eleição (4 de outubro de 2026).
