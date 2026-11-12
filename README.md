# Citizen Assist AI — Orientação para famílias de baixa renda

**Global Solution 2026.2 · Pensamento Computacional e Automação com Python · FIAP · Turma 1CCPY**

## Integrantes

| Nome | RM |
|---|---|
| Yan Luiz Neves Lemos | 571717 |
| Matheus da Costa Gonçalves | 570756 |
| Guilherme Wadt de Oliveira | 569375 |

## Vídeo técnico

(https://youtu.be/n9KQTnFjSm8)

## Público e problema

**Público:** famílias de baixa renda.

**Problema:** essas famílias têm direito a vários serviços e benefícios — Cadastro Único, Tarifa Social de energia, Farmácia Popular, BPC — mas a informação está espalhada em vários sites, usa linguagem técnica e convive com páginas falsas que imitam as oficiais. Muita gente deixa de pedir um direito simplesmente porque não sabe por onde começar.

**Solução:** o Citizen Assist AI é um assistente de terminal que responde dúvidas em texto livre ou por categorias, sempre com base em informações conferidas em fontes oficiais. Cada resposta mostra os documentos necessários, onde ir, a fonte, a data em que a equipe conferiu a informação e o aviso de que o assistente não é um canal oficial. O programa não pede nem guarda dados pessoais.

## ODS relacionados

- **ODS 1 – Erradicação da pobreza:** facilita o acesso a benefícios sociais como Cadastro Único, BPC e Bolsa Família.
- **ODS 3 – Saúde e bem-estar:** orienta sobre Cartão SUS, Farmácia Popular e vacinação.
- **ODS 7 – Energia limpa e acessível:** explica a Tarifa Social de energia elétrica.
- **ODS 10 – Redução das desigualdades:** leva informação em linguagem simples a quem tem mais dificuldade de acesso.
- **ODS 16 – Instituições eficazes:** direciona o cidadão aos canais oficiais e alerta que o assistente não substitui esses canais.

## Como executar

Requisito: **Python 3** (não usa bibliotecas externas).

```
python main.py
```

Menu principal:

```
1 - Fazer uma pergunta
2 - Navegar por categorias
3 - Ver indicadores
4 - Exportar atendimentos (CSV)
0 - Sair
```

## Estrutura do projeto

```
citizen-assist-ai/
├── README.md
├── main.py                 → ponto de entrada e menu principal
├── orientacao.py           → classe Orientacao
├── base_conhecimento.py    → classe BaseConhecimento e função normalizar()
├── assistente.py           → classe Assistente (atendimento, histórico, indicadores e CSV)
└── data/
    ├── base_conhecimento.json   → 14 orientações em 4 categorias
    ├── historico.json           → atendimentos registrados
    └── atendimentos.csv         → exportação dos atendimentos
```

## Classes e composição

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico, caminho_historico, caminho_csv, atendimentos_da_sessao | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `encerrar()` |

As classes se encaixam por **composição**:

```
Assistente
 └── base: BaseConhecimento
      └── orientacoes: [Orientacao, Orientacao, ...]
```

## Base de conhecimento

O arquivo `data/base_conhecimento.json` é uma **lista de dicionários**, um por orientação. São **14 orientações** em **4 categorias**:

| Categoria | Orientações |
|---|---|
| Documentos | CPF, Carteira de Trabalho Digital |
| Assistência Social | Inscrição no CadÚnico, atualização do CadÚnico, BPC para pessoa com deficiência, Bolsa Família |
| Saúde | Cartão SUS, Farmácia Popular, fraldas geriátricas, absorventes (Dignidade Menstrual), vacinação |
| Energia e Consumo | Tarifa Social, reclamação contra a distribuidora, reclamação de compra no consumidor.gov.br |

Cada orientação tem pelo menos 3 palavras-chave, uma fonte oficial e a data em que a equipe conferiu a informação.

## Regra de pontuação (busca inteligente por regras)

1. **Normalização:** pergunta, palavras-chave e título são comparados em minúsculas, sem acentos e sem pontuação. Além dos sinais sugeridos no enunciado, também removemos `-`, `/`, aspas simples e aspas duplas.
2. **Pontuação:**

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada palavra conta uma vez) |

3. **Confiança:**

| Pontuação da melhor orientação | Resultado |
|---|---|
| 6 pontos ou mais | Confiança ALTA |
| 3 a 5 pontos | Confiança MÉDIA |
| Menos de 3 pontos | "Não encontrei": o assistente sugere outras palavras e as categorias |

`buscar()` devolve uma **lista de tuplas** `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até **duas alternativas** com pelo menos 3 pontos. Se a primeira não resolver, o cidadão pode abrir uma alternativa.

**Exemplo:** em "Como faço o cartão do SUS?", a orientação 7 recebe +3 por `cartao do sus`, +3 por `sus` e +1 porque `cartao` está no título. Total: **7 pontos, confiança ALTA**.

**Ajustes feitos nos testes internos:** em "preciso atualizar o cadunico", as orientações de inscrição e de atualização empatavam com 4 pontos. Incluímos "(CadÚnico)" no título da orientação de atualização, que passou a vencer com 5. Em "minha conta de luz veio errada", a Tarifa Social vencia a orientação de reclamação. Incluímos as palavras-chave `veio errada`, `conta de luz errada` e `cobranca errada`.

## Regras de atendimento

- **Navegação:** categorias e orientações numeradas, com "0 para voltar" em todas as telas.
- **Entradas inválidas:** letras, números fora da faixa, resposta vazia e s/n inválido nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Perguntas com 8 ou mais dígitos ou com `@` são recusadas e **não são registradas**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** se o JSON da base estiver ausente, corrompido ou com registros incompletos, o programa avisa e continua funcionando sem travar. O mesmo vale para o histórico.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos (`time.time()`) e nota de facilidade. Ao sair, o assistente pede uma nota de 1 a 5, que é gravada nos atendimentos da sessão.

Indicadores calculados (opção 3 do menu):

- Resposta encontrada (%)
- Taxa de acerto: ajudou (%)
- Tempo médio para encontrar (s)
- Tentativas por atendimento
- Facilidade de uso (1 a 5)
- Lista de dúvidas sem solução

A opção 4 exporta tudo para `data/atendimentos.csv` com `csv.DictWriter`.

## Integração com outras disciplinas

Não há integração de código. O tema conversa com a contribuição da equipe para **Soluções em Energias Renováveis e Sustentáveis**, que trata do consumo de energia de famílias de baixa renda (repositório: https://github.com/yanluiz2007/gs-citizen-assist-energia). As informações sobre Tarifa Social são as mesmas nos dois projetos.

## Fontes consultadas

| Orientação | Fonte oficial |
|---|---|
| CPF | https://www.gov.br/pt-br/servicos/inscrever-no-cpf |
| Carteira de Trabalho Digital | https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho |
| Cadastro Único (inscrição e atualização) | https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal |
| BPC para pessoa com deficiência | https://www.gov.br/pt-br/servicos/solicitar-beneficio-assistencial-a-pessoa-com-deficiencia |
| Bolsa Família | https://www.gov.br/mds/pt-br/acoes-e-programas/bolsa-familia |
| Cartão SUS / Meu SUS Digital | https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital |
| Farmácia Popular, fraldas e absorventes | https://www.gov.br/saude/pt-br/composicao/sectics/farmacia-popular |
| Vacinação | https://www.gov.br/saude/pt-br/vacinacao |
| Tarifa Social de energia | https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social |
| Reclamação contra a distribuidora | https://www.gov.br/aneel/pt-br/canais_atendimento |
| Reclamação de compra | https://www.consumidor.gov.br/pages/conteudo/publico/1 |

Todas as fontes foram conferidas pela equipe em 09/11/2026.

## Teste com usuários

**Como foi feito:** o assistente foi testado com **3 pessoas de fora da equipe**, em sessões separadas. As pessoas enviaram as próprias dúvidas, que foram digitadas no assistente. Elas avaliaram se a resposta ajudou (s/n) e, ao final de cada sessão, deram uma nota de facilidade de 1 a 5. Não registramos nomes nem dados dos participantes, e o histórico guarda apenas as perguntas, sem informação pessoal.

**Indicadores obtidos (opção 3 do menu):**

| Indicador | Resultado |
|---|---|
| Total de atendimentos | 10 |
| Resposta encontrada (%) | 80,0% |
| Taxa de acerto: ajudou (%) | 80,0% |
| Tempo médio para encontrar (s) | 28,6 s |
| Tentativas por atendimento | 2,0 |
| Facilidade de uso (1 a 5) | 3,0 |

**Dúvidas sem solução:**

- "onde faco reclamacoes sobre energia" (última de 4 tentativas para reclamar da queda de energia; antes, a pessoa tinha escrito "Minha luz caiu e a Enel não resolve, onde reclamo?" e "Minha energia acabou onde reclamo")
- "Comprei um celular que veio com defeito, onde reclamo?"

Também observamos que "Como pego remédio de pressão de graça?" não foi encontrada. Ela não aparece na lista porque, no mesmo atendimento, a pessoa fez outra pergunta que foi respondida, e o atendimento é registrado com a última pergunta.

**Análise:** as perguntas encontradas tiveram confiança média ou alta e foram consideradas úteis. As falhas aconteceram quando as pessoas usaram palavras do dia a dia que não estavam nas palavras-chave: "luz caiu", "energia acabou", "comprei" (em vez de "compra"), "defeito" e "remédio de pressão". A pessoa que mais teve perguntas sem resposta deu a menor nota de facilidade, o que puxou a média para 3,0.

**Melhoria feita a partir do teste:** incluímos novas palavras-chave no JSON, sem alterar o código:

| Orientação | Palavras-chave incluídas |
|---|---|
| 13 – Reclamar da distribuidora de energia | `luz caiu`, `energia caiu`, `energia acabou`, `enel nao resolve`, `reclamacoes sobre energia` |
| 8 – Remédio de graça na Farmácia Popular | `remedio`, `remedio de pressao`, `pressao alta`, `diabetes` |
| 14 – Reclamar de uma compra | `comprei`, `defeito`, `veio com defeito` |
| 4 – Atualizar o Cadastro Único | `vencido`, `esta vencido`, `venceu` |

A última melhoria corrige um erro de escolha: "Meu cadastro do CadÚnico está vencido, o que faço?" mostrava a orientação de **inscrição**, e o correto era a de **atualização**.

Depois da melhoria, refizemos as mesmas perguntas do teste. Todas passaram a ser encontradas na orientação correta, com confiança média ou alta: por exemplo, "Minha luz caiu e a Enel não resolve, onde reclamo?" passou de "não encontrei" para 6 pontos, e "Comprei um celular que veio com defeito, onde reclamo?" para 9 pontos.

## Decisão técnica

Mantivemos a busca por regras (palavras-chave e título), em vez de um modelo de IA, porque ela é **explicável e previsível**: dá para mostrar exatamente por que cada resposta apareceu e com quantos pontos. Num assistente sobre direitos do cidadão, isso evita respostas inventadas e deixa claro quando o assistente não sabe.

## Limitações

- O assistente só responde o que está na base. Dúvidas fora das 14 orientações não são atendidas.
- A busca depende das palavras usadas. Sinônimos não cadastrados e erros de digitação (ex.: "cadúnico" escrito "cad unicoo") podem não ser encontrados.
- As regras de benefícios mudam com o tempo. As informações valem para a data de verificação e precisam ser revisadas periodicamente.
- As orientações são gerais. Endereços de CRAS e UBS variam de cidade para cidade.
- O assistente funciona apenas no terminal, o que exige um computador e alguma familiaridade com digitação.
