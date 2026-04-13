from dataclasses import dataclass
from typing import Optional

# ==========================================
# DOMÍNIO: SISTEMA DE EQUIPAMENTOS
# ==========================================

@dataclass
class Item:
    """Classe base para todos os itens do jogo."""
    nome: str
    peso: float = 0.0
    emoji: str = "📦"

@dataclass
class Arma(Item):
    """Herda de Item. Adiciona propriedades de ataque."""
    dano: int = 0
    tipo: str = "corpo" # "corpo" ou "distancia"
    emoji: str = "🗡️"

@dataclass
class Armadura(Item):
    """Herda de Item. Adiciona propriedades de defesa base."""
    defesa: int = 0
    emoji: str = "🦺"

@dataclass
class Escudo(Item):
    """Herda de Item. Adiciona propriedades de defesa extra."""
    defesa_extra: int = 0
    emoji: str = "🛡️"

# Dicionário visual de emojis para mapeamento rápido (Conforme SPEC.md)
DICIONARIO_EMOJIS = {
    "espada": "🗡️",
    "armadura": "🦺",
    "escudo": "🛡️",
    "machado": "🪓",
    "arco": "🏹",
    "poção": "🧪",
    "chave": "🗝️",
    "livro": "📖"
}