class Node:
    def __init__(self, node_id=None, label=None, tipo=None, documento=None,
                 stakeholder=None, em_prospeccao=None, matched=None, root=None, subgroup=None):
        self.id = node_id
        self.label = label
        self.type = bool(tipo)
        self.title = label
        self.documento = documento
        self.stakeholder = bool(stakeholder)
        self.em_prospeccao = bool(em_prospeccao)
        self.matched = matched
        self.root = root
        self.subgroup = subgroup

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return (
            f"Node(id={self.id}, label={self.label}, type={self.type}, "
            f"title={self.title}, documento={self.documento}, "
            f"stakeholder={self.stakeholder}, em_prospeccao={self.em_prospeccao}, "
            f"matched={self.matched}, root={self.root}, subgroup={self.subgroup})"
        )

    def to_dict(self):
        """
        Retorna um dicionário representando o objeto Node.
        """
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "title": self.title,
            "documento": self.documento,
            "stakeholder": self.stakeholder,
            "em_prospeccao": self.em_prospeccao,
            "matched": self.matched,
            "root": self.root,
            "subgroup": self.subgroup
        }
