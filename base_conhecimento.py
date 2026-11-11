import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
TAMANHO_MINIMO_PALAVRA = 4


def normalizar(texto):
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/'\"":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
        except FileNotFoundError:
            print(f"Erro: o arquivo {self.caminho} não foi encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"Erro: o arquivo {self.caminho} está corrompido (JSON inválido).")
            return False

        if not isinstance(registros, list):
            print("Erro: a base de conhecimento precisa ser uma lista de orientações.")
            return False

        self.orientacoes = []
        for registro in registros:
            if not isinstance(registro, dict) or not all(campo in registro for campo in CAMPOS_OBRIGATORIOS):
                print("Aviso: um registro da base está incompleto e foi ignorado.")
                continue
            orientacao = Orientacao(
                registro["id"], registro["categoria"], registro["titulo"],
                registro["palavras_chave"], registro["resposta"], registro["documentos"],
                registro["onde"], registro["fonte"], registro["verificado_em"],
            )
            self.orientacoes.append(orientacao)

        return len(self.orientacoes) > 0

    def categorias(self):
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        return [orientacao for orientacao in self.orientacoes if orientacao.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_normalizada = normalizar(pergunta)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        palavras_titulo = normalizar(orientacao.titulo).split()
        for palavra in set(pergunta_normalizada.split()):
            if len(palavra) >= TAMANHO_MINIMO_PALAVRA and palavra in palavras_titulo:
                pontos += PONTOS_TITULO

        return pontos

    def buscar(self, pergunta):
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda resultado: resultado[0], reverse=True)
        return resultados
