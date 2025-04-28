import os
from app import app


def main():
    """
    Ponto de entrada para iniciar a aplicação Flask.

    A função configura e inicia a aplicação Flask utilizando os seguintes parâmetros:

    - **Host**: Define o endereço IP no qual a API escutará. O valor padrão é '0.0.0.0', que permite
      conexões de todas as interfaces de rede. Pode ser configurado através da variável de ambiente
      'STAKEHOLDERS_API_IP'.
    - **Porta**: Define a porta em que a API será executada. O valor padrão é '5000'. Pode ser configurada
      através da variável de ambiente 'STAKEHOLDERS_API_PORT'.
    - **Debug**: Define se o modo de depuração está ativado. O modo de depuração, útil para desenvolvimento,
      exibe erros detalhados diretamente no navegador e no terminal. É definido com base na configuração
      `app.config['DEBUG']`.

    Variáveis de ambiente:
    - `STAKEHOLDERS_API_IP`: Endereço IP no qual a API será executada. Padrão: '0.0.0.0'.
    - `STAKEHOLDERS_API_PORT`: Porta em que a API escutará. Padrão: '5000'.
    - `DEBUG`: Define se o modo de depuração está ativado. Padrão: configurado em `app.config['DEBUG']`.

    Executa a aplicação Flask com as configurações fornecidas.
    """
    # DESCOMENTAR SE FOR TESTAR A API LOCALMENTE.
    app.run(host=os.getenv("STAKEHOLDERS_API_IP", '0.0.0.0'),
            port=int(os.getenv("STAKEHOLDERS_API_PORT", '5000')),
            debug=app.config['DEBUG'])


if __name__ == '__main__':
    main()
