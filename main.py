import os

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento

OPCOES_MENU = (
    "Fazer uma pergunta",
    "Navegar por categorias",
    "Ver indicadores",
    "Exportar atendimentos (CSV)",
)


def mostrar_menu(nome):
    print()
    print("=" * 55)
    print(f"{nome.upper()} - Orientação ao cidadão")
    print("Público: famílias de baixa renda")
    print("Aviso: este assistente NÃO é um canal oficial.")
    print("=" * 55)
    for numero, texto in enumerate(OPCOES_MENU, start=1):
        print(f"  {numero} - {texto}")
    print("  0 - Sair")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    base = BaseConhecimento("data/base_conhecimento.json")
    if base.carregar():
        print(f"Base carregada: {len(base.orientacoes)} orientações em {len(base.categorias())} categorias.")
    else:
        print("Não foi possível carregar a base. O assistente vai funcionar sem orientações.")

    assistente = Assistente("Citizen Assist AI", base)

    while True:
        mostrar_menu(assistente.nome)
        opcao = ler_opcao("Escolha uma opção: ", 0, len(OPCOES_MENU))
        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        else:
            assistente.encerrar()
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAtendimento encerrado. Até logo!")
