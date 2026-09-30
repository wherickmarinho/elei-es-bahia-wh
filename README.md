# Eleições Bahia

Site com resultados eleitorais da Bahia, feito em **Python** com **Flask**.
Os dados são buscados na hora na **API pública de resultados do TSE**.

Projeto acadêmico e **apartidário**: apenas apresenta dados oficiais, sem
recomendar, classificar ou avaliar candidatos.

**Site no ar:** https://elei-es-bahia.vercel.app

## O que o site faz

- **2026** (governador, senador, deputados): candidatos registrados agora e votos
  automaticamente durante a apuração (4 de outubro de 2026).
- **2024** (prefeito e vereador, 1º e 2º turnos): resultados completos.
- Bahia inteira ou qualquer um dos 417 municípios.
- Nome, número, partido, coligação, vice/suplentes, votos, % e situação de cada candidato.
- Busca de município e de candidato (nome, número ou partido).
- Municípios agrupados pelas regiões do IBGE.
- Interface baseada nas [10 heurísticas de Nielsen](docs/02-heuristicas-nielsen.md).

## Como funciona

```
API do TSE (resultados.tse.jus.br)  +  API do IBGE (regiões)
        ↓  dados/tse.py e dados/municipios.py buscam as URLs (biblioteca requests)
        ↓  e transformam o JSON em dicionários Python simples
app.py  (Flask)  escolhe o que mostrar em cada página
        ↓
templates/*.html  montam a página que aparece no navegador
```

## Estrutura de pastas

| Arquivo / pasta | O que tem |
|---|---|
| `app.py` | As páginas do site. Cada função com `@app.route` é uma página |
| `dados/tse.py` | Busca os resultados na API do TSE e organiza os dados |
| `dados/municipios.py` | Lista os municípios da Bahia (TSE + regiões do IBGE) e faz a busca por nome |
| `templates/` | O HTML de cada página (`base.html` é o molde comum) |
| `public/` | CSS (`estilo.css`) e o ícone de rosto (`avatar.svg`) |
| `requirements.txt` | Bibliotecas usadas: `flask` e `requests` |
| `vercel.json` | Configuração da publicação na Vercel |
| `docs/` | Explicações: fontes de dados e heurísticas de Nielsen |

## Como rodar no seu computador

Pré-requisito: [Python 3.10 ou mais novo](https://www.python.org/downloads/).
Na instalação no Windows, marque a opção **"Add python.exe to PATH"**.

```bash
git clone https://github.com/W2701/elei-es-bahia.git   # baixa o projeto
cd elei-es-bahia                                        # entra na pasta
pip install -r requirements.txt                         # instala flask e requests (só na 1ª vez)
python app.py                                           # liga o site
```

Depois abra **http://localhost:5000** no navegador. Para desligar: `Ctrl + C` no terminal.

Sem Git: no GitHub, clique em **Code → Download ZIP**, extraia e rode só os
dois últimos comandos dentro da pasta.

## Para incluir no site base da turma

Não é preciso copiar o código. Basta apontar a aba "Eleições" para o site publicado,
com um link:

```html
<a href="https://elei-es-bahia.vercel.app">Eleições</a>
```

ou exibindo o site dentro da página (iframe):

```html
<iframe src="https://elei-es-bahia.vercel.app"
        style="width:100%; height:100vh; border:0"
        title="Eleições Bahia"></iframe>
```

## Documentação

1. [Fontes de dados e endereços da API](docs/01-fontes-de-dados.md)
2. [Heurísticas de Nielsen aplicadas](docs/02-heuristicas-nielsen.md)

## Limitações

- A API de resultados do TSE é pública, mas não tem manual oficial; o formato pode mudar.
- O servidor do TSE guarda só eleições recentes (hoje: 2026 e 2024). Os dados de 2022
  foram retirados em 30/09/2026.
- O site não mostra fotos dos candidatos; usa um ícone genérico.
