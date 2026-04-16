import os
from app.db.database import SessionLocal, engine, Base
from app.controllers.game_controller import GameController as GC
from app.models.personagens_db import PersonagemDB
from app.models.equipamentos_db import ItemDB

# Garante que as tabelas existem (útil para rodar o CLI a primeira vez)
Base.metadata.create_all(bind=engine)

def menu_equipar(ctrl: GC):
    print("\n--- 🗡️ EQUIPAR PERSONAGEM ---")
    chars = ctrl.db.query(PersonagemDB).all()
    for p in chars: print(f"[{p.id}] {p.nome}")
    char_id = int(input("ID do Personagem: "))
    
    itens = ctrl.db.query(ItemDB).all()
    for i in itens: print(f"[{i.id}] {i.nome} ({i.categoria})")
    item_id = int(input("ID do Item: "))
    
    slot = input("Slot (direita/esquerda/armadura): ").lower()
    print(ctrl.equipar_item(char_id, item_id, slot))

def menu_arena(ctrl: GC):
    print("\n--- ⚔️ ARENA DE SIMULAÇÃO ---")
    aliados = [int(i.strip()) for i in input("IDs Aliados (ex: 1,2): ").split(",")]
    oponentes = [int(i.strip()) for i in input("IDs Oponentes (ex: 3,4): ").split(",")]
    qtd = int(input("Quantidade de batalhas (1 para detalhado): "))
    
    resultado = ctrl.simular_arena(aliados, oponentes, qtd)
    
    if qtd == 1:
        print(f"\n🏆 Vencedor: {resultado['vencedor']}")
    else:
        print(f"\n📊 Resultados de {qtd} batalhas:")
        print(f"Aliados: {resultado['vitorias_aliados']} vitórias")
        print(f"Oponentes: {resultado['vitorias_oponentes']} vitórias")

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
        print("4. Equipar Item")
        print("5. Simular Batalha na Arena")
        print("6. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        try:
            if escolha == '1': GC.criar_raca(db)
            elif escolha == '2': GC.criar_classe(db)
            elif escolha == '3': GC.criar_personagem(db)
            elif escolha == '4': menu_equipar(GC(db))
            elif escolha == '5': menu_arena(GC(db))
            elif escolha == '6': 
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