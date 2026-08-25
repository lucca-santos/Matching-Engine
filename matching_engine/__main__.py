# Serve como a “porta de entrada” para iniciar o programa. Permite iniciar a aplicação com: python -m matching_engine. Ele chama a função main() da CLI para iniciar o programa.


from .cli import main


if __name__ == "__main__":
    main()