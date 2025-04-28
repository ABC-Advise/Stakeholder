class Link:
    def __init__(self, source=None, target=None, label=None):
        self.source = source
        self.target = target
        self.label = label

    def __repr__(self):
        return (
            f"Link(source={self.source}, target={self.target}, label={self.label})"
        )

    def to_dict(self):
        """
        Retorna um dicionário representando o objeto Link.
        """
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
        }

    def __eq__(self, other):
        """
        Verifica se dois objetos Link são iguais.
        A comparação é feita com base nos campos source e target
        """
        if isinstance(other, Link):
            return (self.source == other.source and self.target == other.target)
        return False

    def __hash__(self):
        """
        Retorna um valor hash para o objeto Link. O hash é gerado com base nos
        campos source e target.
        """
        return hash((self.source, self.target))
