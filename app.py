import json
import os
import shutil
from pathlib import Path

# Tenta importar o colorama para uma experiência visual melhor
try:
    import colorama
    colorama.init(autoreset=True)
    C_FOLDER = colorama.Fore.CYAN + colorama.Style.BRIGHT
    C_FILE = colorama.Fore.WHITE
    C_PROMPT = colorama.Fore.YELLOW + colorama.Style.BRIGHT
    C_SUCCESS = colorama.Fore.GREEN + colorama.Style.BRIGHT
    C_ERROR = colorama.Fore.RED + colorama.Style.BRIGHT
    C_RESET = colorama.Style.RESET_ALL
except ImportError:
    # Se o colorama não estiver instalado, define as cores como strings vazias
    C_FOLDER, C_FILE, C_PROMPT, C_SUCCESS, C_ERROR, C_RESET = "", "", "", "", "", ""

# --- Configurações ---
MANIFEST_FILE = "manifest.json"

# --- Funções Auxiliares ---

def clear_screen():
    """Limpa a tela do terminal para uma interface mais limpa."""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_backup():
    """Cria um backup do manifest.json. Essencial para segurança."""
    if not os.path.exists(MANIFEST_FILE):
        print(f"{C_ERROR}ERRO: {MANIFEST_FILE} não encontrado!")
        return False
    try:
        backup_path = f"{MANIFEST_FILE}.bak"
        shutil.copy2(MANIFEST_FILE, backup_path)
        print(f"{C_SUCCESS}✅ Backup de segurança criado: {backup_path}")
        return True
    except Exception as e:
        print(f"{C_ERROR}ERRO CRÍTICO ao criar backup: {e}")
        return False

def load_manifest():
    """Carrega os dados do manifest.json."""
    try:
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"{C_ERROR}ERRO ao carregar {MANIFEST_FILE}: {e}")
        return None

def save_manifest(data):
    """Salva os dados de volta no manifest.json."""
    try:
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{C_ERROR}ERRO CRÍTICO ao salvar {MANIFEST_FILE}: {e}")
        return False

def update_manifest(action, file_path_obj, old_path_obj=None):
    """Função central para adicionar, remover ou mover entradas no manifest."""
    manifest_data = load_manifest()
    if not manifest_data: return False

    # Converte os paths do Pathlib para strings com barras normais ('/')
    file_path_str = file_path_obj.as_posix()
    old_path_str = old_path_obj.as_posix() if old_path_obj else None

    # Função recursiva para encontrar e modificar a árvore
    def find_and_modify(nodes):
        # Para remover ou mover, primeiro encontramos e removemos a entrada antiga
        if action in ['remove', 'move']:
            nodes[:] = [node for node in nodes if node.get('path') != old_path_str]

        for node in nodes:
            if node.get("type") == "folder" and node.get("children"):
                # Para adicionar ou mover, encontramos a pasta pai e adicionamos a nova entrada
                if action in ['add', 'move']:
                    # O novo arquivo pertence a esta pasta?
                    if file_path_obj.parent.name == node.get("name"):
                        # Evita adicionar duplicatas
                        if not any(child.get('path') == file_path_str for child in node["children"]):
                            node["children"].append({"type": "file", "path": file_path_str})
                        return True # Indica que a operação foi concluída
                
                # Continua a busca recursivamente
                if find_and_modify(node["children"]):
                    return True
        return False

    if find_and_modify(manifest_data["tree"]):
        return save_manifest(manifest_data)
    else:
        # Caso especial: adicionar um arquivo em uma pasta que não está no manifest
        if action in ['add', 'move']:
             print(f"{C_PROMPT}AVISO: A pasta de destino não foi encontrada no manifest. Tente adicioná-lo manualmente.")
             # Mesmo com o aviso, a operação de arquivo já foi feita, então retornamos sucesso parcial.
             return True
    return False


def get_user_choice(prompt, max_value, allow_cancel=False):
    """Pede ao usuário para escolher um número de uma lista."""
    while True:
        extra_info = " ou 'c' para cancelar" if allow_cancel else ""
        try:
            choice = input(f"{C_PROMPT}{prompt}{extra_info}: {C_RESET}")
            if allow_cancel and choice.lower() == 'c':
                return None
            num_choice = int(choice)
            if 1 <= num_choice <= max_value:
                return num_choice
            else:
                print(f"{C_ERROR}Opção inválida. Tente novamente.")
        except ValueError:
            print(f"{C_ERROR}Por favor, digite um número válido.")

# --- Funções de Ação ---

def display_current_location(current_path):
    """Mostra a localização atual e lista os arquivos e pastas."""
    print("=" * 60)
    print(f"Você está em: {C_PROMPT}{current_path}")
    print("-" * 60)

    items = sorted(list(current_path.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
    
    if not items:
        print("Pasta vazia.")
        return []

    print("Conteúdo da pasta:")
    for i, item in enumerate(items):
        icon = "📁" if item.is_dir() else "📄"
        color = C_FOLDER if item.is_dir() else C_FILE
        print(f"  [{i+1}] {icon} {color}{item.name}{C_RESET}")
    
    return items

def handle_file_operation(op_type, items, current_path):
    """Lida com as operações de Mover, Copiar e Deletar."""
    print(f"\n--- Operação de {op_type.upper()} ---")
    files = [item for item in items if item.is_file()]
    if not files:
        print(f"{C_ERROR}Nenhum arquivo para {op_type} nesta pasta.")
        input("Pressione Enter para continuar...")
        return

    # 1. Escolher o arquivo de origem
    file_choice = get_user_choice("Escolha o número do arquivo para " + op_type, len(items), allow_cancel=True)
    if file_choice is None: return
    
    source_item = items[file_choice - 1]
    if not source_item.is_file():
        print(f"{C_ERROR}Ação inválida. Você só pode selecionar arquivos.")
        input("Pressione Enter para continuar...")
        return

    # 2. Lógica para Deletar
    if op_type == "deletar":
        print(f"{C_ERROR}\nATENÇÃO: Esta ação é permanente!")
        confirm = input(f"Tem certeza que deseja deletar '{source_item.name}'? (digite 'sim' para confirmar): ")
        if confirm.lower() == 'sim':
            if create_backup():
                try:
                    source_item.unlink() # Deleta o arquivo
                    update_manifest('remove', source_item, old_path_obj=source_item)
                    print(f"{C_SUCCESS}Arquivo '{source_item.name}' deletado com sucesso!")
                except Exception as e:
                    print(f"{C_ERROR}Erro ao deletar: {e}")
        else:
            print("Operação de exclusão cancelada.")
        input("Pressione Enter para continuar...")
        return
        
    # 3. Lógica para Mover ou Copiar: Escolher destino
    manifest_data = load_manifest()
    # Apenas pastas que começam com 'src/' são destinos válidos
    valid_dest_folders = sorted([p for p in Path('src').rglob('*') if p.is_dir()])

    print("\nEscolha a pasta de destino:")
    for i, folder in enumerate(valid_dest_folders):
        print(f"  [{i+1}] {C_FOLDER}{folder}{C_RESET}")

    dest_choice = get_user_choice("Escolha o número da pasta de destino", len(valid_dest_folders), allow_cancel=True)
    if dest_choice is None: return

    dest_folder = valid_dest_folders[dest_choice - 1]
    dest_path = dest_folder / source_item.name

    # 4. Executar a operação
    if create_backup():
        try:
            if op_type == "mover":
                shutil.move(source_item, dest_path)
                update_manifest('move', dest_path, old_path_obj=source_item)
                print(f"{C_SUCCESS}'{source_item.name}' movido para '{dest_folder}' com sucesso!")
            elif op_type == "copiar":
                shutil.copy2(source_item, dest_path)
                update_manifest('add', dest_path)
                print(f"{C_SUCCESS}'{source_item.name}' copiado para '{dest_folder}' com sucesso!")

        except Exception as e:
            print(f"{C_ERROR}Erro durante a operação: {e}")

    input("Pressione Enter para continuar...")


# --- Loop Principal ---

def main():
    """O loop principal do gerenciador de arquivos."""
    current_path = Path.cwd() # Começa na pasta atual
    
    print_header("Gerenciador de Arquivos do Projeto Toaru")
    print("Navegue pelas pastas e organize tudo com segurança, 17!")

    while True:
        clear_screen()
        items = display_current_location(current_path)

        print("\n--- AÇÕES DISPONÍVEIS ---")
        print(" [1] Navegar para uma pasta")
        print(" [2] Voltar para a pasta anterior (..)")
        print(" [3] Mover um arquivo")
        print(" [4] Copiar um arquivo")
        print(" [5] Deletar um arquivo")
        print(f"{C_PROMPT} [s] Sair do programa{C_RESET}")

        choice = input(f"\n{C_PROMPT}O que deseja fazer?{C_RESET} ").lower()

        if choice == '1':
            nav_choice = get_user_choice("Digite o número da pasta para entrar", len(items), allow_cancel=True)
            if nav_choice is not None:
                selected_item = items[nav_choice - 1]
                if selected_item.is_dir():
                    current_path = selected_item
                else:
                    input(f"{C_ERROR}Seleção inválida. Pressione Enter para continuar...")
        elif choice == '2':
            current_path = current_path.parent
        elif choice == '3':
            handle_file_operation("mover", items, current_path)
        elif choice == '4':
            handle_file_operation("copiar", items, current_path)
        elif choice == '5':
            handle_file_operation("deletar", items, current_path)
        elif choice == 's':
            print("\nMissão cumprida. Saindo...")
            break
        else:
            input(f"{C_ERROR}Comando desconhecido. Pressione Enter para tentar novamente...")

def print_header(message):
    """Imprime um cabeçalho estilizado."""
    clear_screen()
    print("=" * 60)
    print(f"🚀 {message} 🚀")
    print("=" * 60)
    input("Pressione Enter para iniciar...")

if __name__ == "__main__":
    main()