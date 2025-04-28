class ValidationError(Exception):
    """
    Classe base para exceções relacionadas a validações.

    Atributos:
    - message (str): A mensagem de erro que será exibida.
    """

    def __init__(self, message):
        """
        Inicializa a exceção de validação.

        Parâmetros:
        - message (str): A mensagem de erro para a exceção.
        """
        self.message = message
        super().__init__(self.message)


class InvalidDateFormatError(ValidationError):
    """
    Exceção para erro de formato de data inválido.

    Esta classe herda de ValidationError e pode ser utilizada
    quando o formato de data fornecido for inválido.
    """
    pass


class MissingFieldError(ValidationError):
    """
    Exceção para erro de campo obrigatório ausente.

    Atributos:
    - field (str): Nome do campo que está ausente.
    """

    def __init__(self, field):
        """
        Inicializa a exceção com uma mensagem específica informando o campo ausente.

        Parâmetros:
        - field (str): O nome do campo obrigatório que está ausente.
        """
        self.message = f"O campo {field} é obrigatório."
        super().__init__(self.message)


class InvalidFieldError(ValidationError):
    """
    Exceção para erro de campo inválido.

    Essa exceção é usada quando um campo contém um valor inválido, herdando de ValidationError.
    """
    pass

class InvalidStakeholder(ValidationError):
    """
    Exceção para erro de Stakeholders.

    Essa exceção é usada quando um campo contém um valor inválido, herdando de ValidationError.
    """
    pass

class AuthorizationError(Exception):
    """
    Classe base para exceções relacionadas a autorização.

    Atributos:
    - message (str): Mensagem de erro relacionada à falha de autorização.
    """

    def __init__(self, message="Credenciais inválidas"):
        """
        Inicializa a exceção de autorização com uma mensagem opcional.

        Parâmetros:
        - message (str): Mensagem de erro a ser exibida. Valor padrão: "Credenciais inválidas".
        """
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(AuthorizationError):
    """
    Exceção para erro de token inválido ou expirado.

    Essa exceção é usada quando um token JWT é inválido ou expirou.
    """

    def __init__(self):
        """
        Inicializa a exceção com uma mensagem padrão informando que o token é inválido ou expirado.
        """
        super().__init__("Token inválido ou expirado")


class AuthHeaderError(AuthorizationError):
    """
    Exceção para erro de cabeçalho de autorização ausente.

    Essa exceção é usada quando o cabeçalho Authorization está ausente em uma requisição.
    """

    def __init__(self):
        """
        Inicializa a exceção com uma mensagem padrão informando a ausência do cabeçalho de autorização.
        """
        super().__init__("Cabeçalho de autorização ausente")


class HTTPError(Exception):
    """
    Exceção genérica para erros de requisições HTTP.

    Atributos:
    - message (str): Mensagem de erro relacionada à requisição HTTP.
    """

    def __init__(self, message="Erro ao fazer requisição HTTP"):
        """
        Inicializa a exceção com uma mensagem opcional.

        Parâmetros:
        - message (str): Mensagem de erro a ser exibida. Valor padrão: "Erro ao fazer requisição HTTP".
        """
        self.message = message
        super().__init__(self.message)