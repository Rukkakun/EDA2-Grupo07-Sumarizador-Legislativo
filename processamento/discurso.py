from dataclasses import dataclass, field


@dataclass
class Discurso:
    orador: str
    frase: str


@dataclass
class DiscursoProcessado:
    orador: str
    frase: str
    tokens: list[int] = field(default_factory=list)
    bitset: int = 0
