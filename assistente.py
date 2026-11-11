import csv
import json
import os
import time
from datetime import datetime

PONTOS_CONFIANCA_ALTA = 6
PONTOS_CONFIANCA_MEDIA = 3
MAXIMO_ALTERNATIVAS = 2
MINIMO_DIGITOS_DADO_PESSOAL = 8

CAMPOS_CSV = ("data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "facilidade")

EXEMPLOS_DE_BUSCA = ("cadastro único", "tarifa social", "farmácia popular", "cartão do SUS")


def ler_opcao(mensagem, minimo, maximo):
    while True:
        resposta = input(mensagem).strip()
        if resposta == "":
            print("Você não digitou nada. Tente de novo.")
            continue
        if not resposta.isdigit():
            print(f"Digite apenas números, de {minimo} a {maximo}.")
            continue
        numero = int(resposta)
        if numero < minimo or numero > maximo:
            print(f"Opção inválida. Escolha um número de {minimo} a {maximo}.")
            continue
        return numero


def ler_sim_nao(mensagem):
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Responda apenas com s ou n.")


def tem_dado_pessoal(texto):
    quantidade_digitos = sum(1 for caractere in texto if caractere.isdigit())
    return quantidade_digitos >= MINIMO_DIGITOS_DADO_PESSOAL or "@" in texto


def nivel_confianca(pontos):
    if pontos >= PONTOS_CONFIANCA_ALTA:
        return "ALTA"
    if pontos >= PONTOS_CONFIANCA_MEDIA:
        return "MÉDIA"
    return "BAIXA"


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = self.carregar_historico()
        self.atendimentos_da_sessao = []

    def carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Aviso: o histórico estava corrompido. Um novo histórico será iniciado.")
            return []
        if not isinstance(dados, list):
            print("Aviso: o histórico estava em formato errado. Um novo histórico será iniciado.")
            return []
        return dados

    def salvar_historico(self):
        os.makedirs(os.path.dirname(self.caminho_historico), exist_ok=True)
        with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
            json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, inicio):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "facilidade": None,
        }
        self.historico.append(atendimento)
        self.atendimentos_da_sessao.append(atendimento)
        self.salvar_historico()

    def mostrar_nao_encontrado(self):
        print()
        print("Não encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras, por exemplo: " + ", ".join(EXEMPLOS_DE_BUSCA) + ".")
        print("Ou use a navegação por categorias: " + ", ".join(self.base.categorias()) + ".")

    def oferecer_alternativas(self, alternativas):
        print()
        print("Outras orientações que podem ajudar:")
        for numero, (pontos, orientacao) in enumerate(alternativas, start=1):
            print(f"  {numero} - {orientacao.titulo} ({pontos} pontos)")

    def perguntar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento está vazia. Verifique o arquivo de dados.")
            return

        print()
        print("Escreva sua dúvida com as suas palavras. Exemplo: como faço o cartão do SUS?")
        print("Não digite nome, CPF, telefone ou e-mail.")

        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        encontrou_algo = False
        id_encontrado = None

        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                if tentativas > 0:
                    self.registrar("pergunta", ultima_pergunta, id_encontrado,
                                   encontrou_algo, False, tentativas, inicio)
                return

            if pergunta == "":
                print("Você não digitou nada. Escreva sua dúvida ou 0 para voltar.")
                continue

            if tem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < PONTOS_CONFIANCA_MEDIA:
                self.mostrar_nao_encontrado()
                continue

            pontos, melhor = resultados[0]
            encontrou_algo = True
            id_encontrado = melhor.id

            print()
            print(f"Confiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [resultado for resultado in resultados[1:]
                            if resultado[0] >= PONTOS_CONFIANCA_MEDIA][:MAXIMO_ALTERNATIVAS]
            if alternativas:
                self.oferecer_alternativas(alternativas)

            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")

            if not ajudou and alternativas:
                escolha = ler_opcao("Digite o número de uma alternativa para ver (0 para reescrever): ",
                                    0, len(alternativas))
                if escolha != 0:
                    escolhida = alternativas[escolha - 1][1]
                    id_encontrado = escolhida.id
                    escolhida.exibir()
                    ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")

            if ajudou:
                self.registrar("pergunta", pergunta, id_encontrado, True, True, tentativas, inicio)
                print("Que bom! Se tiver outra dúvida, é só digitar.")
                inicio = time.time()
                tentativas = 0
                ultima_pergunta = ""
                encontrou_algo = False
                id_encontrado = None
            else:
                print("Tente escrever a dúvida de outro jeito ou digite 0 para voltar.")

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento está vazia. Verifique o arquivo de dados.")
            return

        inicio = time.time()
        while True:
            print()
            print("CATEGORIAS")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero} - {categoria}")
            print("  0 - Voltar")
            opcao = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return

            categoria = categorias[opcao - 1]
            while True:
                orientacoes = self.base.por_categoria(categoria)
                print()
                print(categoria.upper())
                for numero, orientacao in enumerate(orientacoes, start=1):
                    print(f"  {numero} - {orientacao.titulo}")
                print("  0 - Voltar")
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
                if escolha == 0:
                    break

                orientacao = orientacoes[escolha - 1]
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", f"[{categoria}] {orientacao.titulo}", orientacao.id,
                               True, ajudou, 1, inicio)
                inicio = time.time()

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return None

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo_segundos", 0) for a in ajudaram]
        tentativas = [a.get("tentativas", 0) for a in self.historico]
        notas = [a["facilidade"] for a in self.historico if a.get("facilidade")]

        sem_solucao = []
        for atendimento in self.historico:
            pergunta = atendimento.get("pergunta", "")
            if not atendimento.get("ajudou") and pergunta and pergunta not in sem_solucao:
                sem_solucao.append(pergunta)

        resultado = {
            "total": total,
            "encontrada": len(encontrados) / total * 100,
            "ajudou": len(ajudaram) / total * 100,
            "tempo_medio": sum(tempos) / len(tempos) if tempos else 0,
            "tentativas_media": sum(tentativas) / total,
            "facilidade": sum(notas) / len(notas) if notas else None,
            "sem_solucao": sem_solucao,
        }

        print()
        print("=" * 55)
        print("INDICADORES DE ATENDIMENTO")
        print("=" * 55)
        print(f"Total de atendimentos:          {resultado['total']}")
        print(f"Resposta encontrada:            {resultado['encontrada']:.1f}%")
        print(f"Taxa de acerto (ajudou):        {resultado['ajudou']:.1f}%")
        print(f"Tempo médio para encontrar:     {resultado['tempo_medio']:.1f} s")
        print(f"Tentativas por atendimento:     {resultado['tentativas_media']:.1f}")
        if resultado["facilidade"] is None:
            print("Facilidade de uso (1 a 5):      sem notas ainda")
        else:
            print(f"Facilidade de uso (1 a 5):      {resultado['facilidade']:.1f}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  nenhuma")
        print("=" * 55)
        return resultado

    def exportar_csv(self):
        if not self.historico:
            print("\nAinda não há atendimentos para exportar.")
            return False
        try:
            os.makedirs(os.path.dirname(self.caminho_csv), exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
        except OSError:
            print("\nNão foi possível salvar o CSV. Verifique se o arquivo está aberto em outro programa.")
            return False
        print(f"\n{len(self.historico)} atendimentos exportados para {self.caminho_csv}")
        return True

    def encerrar(self):
        if self.atendimentos_da_sessao:
            print()
            nota = ler_opcao("Antes de sair: de 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
            for atendimento in self.atendimentos_da_sessao:
                atendimento["facilidade"] = nota
            self.salvar_historico()
        print(f"\nObrigado por usar o {self.nome}. Até logo!")
