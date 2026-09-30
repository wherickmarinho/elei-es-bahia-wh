# Heurísticas de usabilidade de Nielsen no site

As 10 heurísticas de Jakob Nielsen são princípios para avaliar se uma interface é
fácil de usar. Abaixo, como cada uma foi aplicada e onde encontrar no código.
No HTML, os trechos estão marcados com comentários `{# Heurística N ... #}`.

| # | Heurística | Como foi aplicada | Onde |
|---|---|---|---|
| 1 | **Visibilidade do status do sistema** | Menu destaca a página atual; título diz exatamente o que está na tela ("Prefeito · Guanambi"); selo "Apuração ainda não iniciada / em andamento / concluída"; botão muda para "Buscando…" ao enviar | `templates/base.html`, `templates/resultados.html` |
| 2 | **Correspondência com o mundo real** | Linguagem do eleitor (não técnica); números no padrão brasileiro (4.019.830 e 49,45%); termos oficiais do TSE ("Eleito por QP") explicados no glossário | `app.py` (filtros `numero` e `percentual`), `templates/ajuda.html` |
| 3 | **Controle e liberdade do usuário** | Trilha "Início › Resultados › Guanambi"; botão "Limpar filtros"; o endereço da página guarda as escolhas, e o botão Voltar do navegador funciona | `templates/resultados.html` |
| 4 | **Consistência e padrões** | Todas as páginas usam o mesmo molde (cabeçalho, menu, rodapé), as mesmas cores e os mesmos componentes | `templates/base.html`, `public/estilo.css` |
| 5 | **Prevenção de erros** | Só aparecem os cargos que existem na eleição escolhida; a lista de municípios sugere nomes válidos; campo obrigatório na busca da página inicial | `templates/resultados.html`, `templates/inicio.html` |
| 6 | **Reconhecer em vez de lembrar** | Opções de eleição e cargo sempre visíveis, com a escolhida destacada; o município escolhido continua no campo; sugestões enquanto se digita | `templates/resultados.html` |
| 7 | **Flexibilidade e eficiência de uso** | "Consultas rápidas" na página inicial; busca de candidato por nome, número ou partido; links compartilháveis | `templates/inicio.html`, `app.py` |
| 8 | **Estética e design minimalista** | Só o essencial à vista; detalhes do candidato ficam em "Mais informações"; listas grandes mostram os 50 primeiros; sem fotos, com um ícone neutro | `templates/_candidato.html`, `app.py` |
| 9 | **Ajudar a reconhecer, diagnosticar e recuperar erros** | Município digitado errado → "Você quis dizer: Guanambi"; API fora do ar → mensagem clara com "Tentar novamente"; página inexistente → página de erro com "Voltar ao início" | `templates/resultados.html`, `templates/erro.html` |
| 10 | **Ajuda e documentação** | Página "Ajuda" com passo a passo e glossário; dicas abaixo dos campos; link para o glossário ao lado dos resultados | `templates/ajuda.html` |
