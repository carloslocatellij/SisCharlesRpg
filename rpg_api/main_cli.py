import os
from app.db.database import SessionLocal, engine, Base
from app.models.personagens_db import RacaDB, ClasseRPGDB, PersonagemDB
from app.models.equipamentos_db import ItemDB
from app.core.personagens import Personagem, Raca, ClasseRPG
from app.core.simulador import SimuladorCombate

# Garante que as tabelas existem (útil para rodar o CLI a primeira vez)
Base.metadata.create_all(bind=engine)

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
    return personagem

# ==========================================
# FUNÇÕES DE INTERAÇÃO DO CLI
# ==========================================

def criar_raca(db):
    print("\n--- 🧬 CRIAR NOVA RAÇA ---")
    nome = input("Nome da Raça: ")
    forca = int(input("Bônus de Força: "))
    agilidade = int(input("Bônus de Agilidade: "))
    
    nova_raca = RacaDB(nome=nome, bonus_atributos={"forca": forca, "agilidade": agilidade})
    db.add(nova_raca)
    db.commit()
    print(f"✅ Raça '{nome}' salva com sucesso no Banco de Dados!")

def criar_classe(db):
    print("\n--- 📜 CRIAR NOVA CLASSE ---")
    nome = input("Nome da Classe: ")
    caminho = input("Caminho de Magia Primário (ex: fogo, ar): ")
    pontos = int(input(f"Pontos no caminho {caminho}: "))
    
    nova_classe = ClasseRPGDB(nome=nome, bonus_caminhos={caminho: pontos})
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

def simular_arena(db):
    print("\n--- ⚔️ ARENA DE SIMULAÇÃO ⚔️ ---")
    personagens = db.query(PersonagemDB).all()
    
    if len(personagens) < 2:
        print("⚠️ Crie pelo menos 2 personagens primeiro!")
        return

    print("\nLutadores disponíveis:")
    for p in personagens:
        print(f"[{p.id}] {p.nome} (Nível {p.nivel} {p.raca.nome} {p.classe.nome})")
        
    ids_aliados = input("\nDigite os IDs da Equipa Aliada (separados por vírgula): ")
    ids_oponentes = input("Digite os IDs da Equipa Oponente (separados por vírgula): ")
    
    # Converte a string "1,2" numa lista de inteiros [1, 2]
    lista_aliados_id = [int(i.strip()) for i in ids_aliados.split(",")]
    lista_oponentes_id = [int(i.strip()) for i in ids_oponentes.split(",")]
    
    # Busca no banco e converte para o Domínio
    equipa_aliada = [converter_para_dominio(db.query(PersonagemDB).get(i)) for i in lista_aliados_id]
    equipa_oponente = [converter_para_dominio(db.query(PersonagemDB).get(i)) for i in lista_oponentes_id]
    
    # Inicia o Simulador que construímos!
    simulador = SimuladorCombate(equipa_aliada, equipa_oponente)
    relatorio = simulador.simular_batalha(silencioso=False)
    
    print("\n📊 ESTATÍSTICAS DA BATALHA:")
    for nome, stats in relatorio["estatisticas"].items():
        print(f" - {nome}: {stats['dano_causado']} Dano, {stats['abates']} Abates")

# ==========================================
# LOOP PRINCIPAL DO PROGRAMA
# ==========================================
def main():
    db = SessionLocal()
    
    while True:
        print("\n" + "="*40)
        print("🛡️ GERENCIADOR DE RPG DE MESA 🛡️")
        print("="*40)
        print("1. Criar Raça")
        print("2. Criar Classe")
        print("3. Criar Personagem")
        print("4. Simular Batalha na Arena")
        print("5. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        try:
            if escolha == '1': criar_raca(db)
            elif escolha == '2': criar_classe(db)
            elif escolha == '3': criar_personagem(db)
            elif escolha == '4': simular_arena(db)
            elif escolha == '5': 
                print("Encerrando o sistema...")
                break
            else:
                print("⚠️ Opção inválida!")
        except Exception as e:
            print(f"❌ Ocorreu um erro: {e}")
            db.rollback() # Previne que o banco trave em caso de erro de input

    db.close()

if __name__ == "__main__":
    main()