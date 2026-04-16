from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.database import get_db
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from app.core.personagens import Personagem, Raca, ClasseRPG
from app.core.simulador import SimuladorCombate
from app.core.equipamentos import Arma, Armadura, Escudo

class GameController:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # TRADUTOR (MAPPER): BANCO DE DADOS -> DOMÍNIO
    # ==========================================
    def converter_para_dominio(db_char: PersonagemDB) -> Personagem:
        """Converte um modelo do SQLAlchemy para a Entidade pura do RPG."""
        # 1. Recria a Raça do Domínio
        raca_domain = Raca(nome=db_char.raca.nome, bonus_atributos=db_char.raca.bonus_atributos)
        
        # 2. Recria a Classe do Domínio
        classe_domain = ClasseRPG(
            nome=db_char.classe.nome, 
            bonus_caminhos=db_char.classe.bonus_caminhos,
            habilidades=db_char.classe.habilidades,
            bonus_atributos=db_char.classe.bonus_atributos
        )
        
        # 3. Recria o Personagem
        personagem = Personagem(
            nome=db_char.nome,
            nivel=db_char.nivel,
            raca=raca_domain,
            classe_rpg=classe_domain,
            forca_base=db_char.forca_base,
            agilidade_base=db_char.agilidade_base,
            res_base=db_char.resistencia_base,
            perc_base=db_char.percepcao_base,
            exub_base=db_char.exuberancia_base
        )
        # Equipar itens se existirem no banco
        if db_char.mao_direita:
            personagem.mao_direita = Arma(db_char.mao_direita.nome, db_char.mao_direita.dano, db_char.mao_direita.tipo_ataque)
        if db_char.mao_esquerda:
            item = db_char.mao_esquerda
            if item.categoria == "escudo":
                personagem.mao_esquerda = Escudo(item.nome, item.defesa)
            else:
                personagem.mao_esquerda = Arma(item.nome, item.dano, item.tipo_ataque)
        if db_char.armadura_equipada:
            personagem.armadura = Armadura(db_char.armadura_equipada.nome, db_char.armadura_equipada.defesa)
        
        return personagem
    
    
    def equipar_item(self, personagem_id: int, item_id: int, slot: str):
        """
        Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'.
        """
        personagem = self.db.query(PersonagemDB).get(personagem_id)
        item = self.db.query(ItemDB).get(item_id)
        
        if not personagem or not item:
            raise ValueError("Personagem ou Item não encontrado.")

        if slot == 'direita': personagem.mao_direita_id = item.id
        elif slot == 'esquerda': personagem.mao_esquerda_id = item.id
        elif slot == 'armadura': personagem.armadura_id = item.id
        
        self.db.commit()
        return f"✅ {item.nome} equipado em {personagem.nome} ({slot})."

    # ==========================================
    # FUNÇÕES DE INTERAÇÃO DO CLI
    # ==========================================

    def criar_raca(db):
        print("\n--- 🧬 CRIAR NOVA RAÇA ---")
        nome = input("Nome da Raça: ")
        forca = int(input("Bônus de Força: "))
        agilidade = int(input("Bônus de Agilidade: "))
        resistencia = int(input("Bônus de Resistência: "))
        percepcao =  int(input("Bônus de Percepção: "))
        exuberancia =  int(input("Bônus de Exuberância: "))
        
        nova_raca = RacaDB(nome=nome, bonus_atributos={"forca": forca,
                                                    "agilidade": agilidade,
                                                    "resistencia": resistencia,
                                                    "percepcao" : percepcao,
                                                    "exuberancia": exuberancia})
        db.add(nova_raca)
        db.commit()
        print(f"✅ Raça '{nome}' salva com sucesso no Banco de Dados!")

    def criar_classe(db):
        print("\n--- 📜 CRIAR NOVA CLASSE ---")
        nome = input("Nome da Classe: ")
        caminho = input("Caminho de Magia Primário (ex: fogo, ar): ")
        pontos = int(input(f"Pontos no caminho {caminho}: "))
        
        forca = int(input("Bônus de Força: "))
        agilidade = int(input("Bônus de Agilidade: "))
        resistencia = int(input("Bônus de Resistência: "))
        percepcao =  int(input("Bônus de Percepção: "))
        exuberancia =  int(input("Bônus de Exuberância: "))
        
        nova_classe = ClasseRPGDB(nome=nome, bonus_caminhos={caminho: pontos}, bonus_atributos={"forca": forca,
                                                    "agilidade": agilidade,
                                                    "resistencia": resistencia,
                                                    "percepcao" : percepcao,
                                                    "exuberancia": exuberancia})
        
        db.add(nova_classe)
        db.commit()
        print(f"✅ Classe '{nome}' salva com sucesso!")

    def criar_personagem(db):
        print("\n--- 👤 CRIAR NOVO PERSONAGEM ---")
        
        # Lista Raças
        racas = db.query(RacaDB).all()
        print("\nRaças disponíveis:")
        for r in racas: print(f"[{r.id}] {r.nome}")
        raca_id = int(input("ID da Raça escolhida: "))
        
        # Lista Classes
        classes = db.query(ClasseRPGDB).all()
        print("\nClasses disponíveis:")
        for c in classes: print(f"[{c.id}] {c.nome}")
        classe_id = int(input("ID da Classe escolhida: "))
        
        nome = input("\nNome do Personagem: ")
        forca = int(input("Força Base (0 a 5): "))
        agilidade = int(input("Agilidade Base (0 a 5): "))
        resistencia = int(input("Resistência Base (0 a 5): "))
        percepcao = int(input("Percepção Base (0 a 5): "))
        exuberancia = int(input("Exuberância Base (0 a 5): "))
        
        novo_personagem = PersonagemDB(
            nome=nome, raca_id=raca_id, classe_id=classe_id,
            forca_base=forca, agilidade_base=agilidade, resistencia_base=resistencia,
            percepcao_base=percepcao, exuberancia_base=exuberancia
        )
        db.add(novo_personagem)
        db.commit()
        print(f"✅ Herói '{nome}' forjado e salvo no Banco de Dados!")

    def simular_arena(ids_aliados: List[int], ids_oponentes: List[int], num_batalhas: int = 1):
        
        
        # Busca no banco e converte para o Domínio
        equipa_aliada = [self.converter_para_dominio(self.db.query(PersonagemDB).get(i)) for i in ids_aliados]
        equipa_oponente = [self.converter_para_dominio(self.db.query(PersonagemDB).get(i)) for i in ids_oponentes]
        
        # Inicia o Simulador que construímos!
        simulador = SimuladorCombate(equipa_aliada, equipa_oponente)
        
        if num_batalhas == 1:
            return simulador.simular_batalha(silencioso=False)
        else:
            print("\n📊 ESTATÍSTICAS DA BATALHA:")
            for nome, stats in relatorio["estatisticas"].items():
                print(f" - {nome}: {stats['dano_causado']} Dano, {stats['abates']} Abates")
            return simulador.simular_multiplas_batalhas(num_batalhas, silencioso=True)
        
        
