# app.py (Versão Final com Sincronização Inteligente)
import json
import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'sincronizacao-inteligente-final' 

MANIFEST_FILE = "manifest.json"

#region Funções Auxiliares e de Lógica (sem grandes alterações)
def create_backup():
    if not os.path.exists(MANIFEST_FILE):
        flash(f"ERRO: {MANIFEST_FILE} não encontrado!", "danger"); return False
    try:
        backup_path = f"{MANIFEST_FILE}.bak"
        shutil.copy2(MANIFEST_FILE, backup_path)
        print(f"✅ Backup criado: {backup_path}"); return True
    except Exception as e:
        flash(f"ERRO CRÍTICO ao criar backup: {e}", "danger"); return False

def load_manifest():
    try:
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception as e:
        flash(f"ERRO ao carregar {MANIFEST_FILE}: {e}", "danger"); return None

def save_manifest(data):
    try:
        def sort_children(node):
            if node.get("type") == "folder" and "children" in node:
                node["children"].sort(key=lambda x: (x.get("type", "file") == "file", x.get("name") or x.get("path")))
                for child in node["children"]: sort_children(child)
        for top_node in data.get("tree", []): sort_children(top_node)
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        flash(f"ERRO CRÍTICO ao salvar {MANIFEST_FILE}: {e}", "danger"); return False

def get_all_paths_in_manifest(nodes):
    paths = set()
    for node in nodes:
        if node.get("type") == "file": paths.add(Path(node.get("path")).as_posix())
        elif node.get("type") == "folder" and "children" in node:
            paths.update(get_all_paths_in_manifest(node["children"]))
    return paths

def get_untracked_files(manifest_paths):
    untracked = []
    excluded_dirs = {'.git', 'templates', '__pycache__'}
    excluded_files = {'app.py', 'manifest.json', 'manifest.json.bak', 'seu_script_original.py'}
    for path_obj in Path('.').rglob('*'):
        if path_obj.is_file():
            path_str = path_obj.as_posix()
            is_in_excluded_dir = any(part in excluded_dirs for part in path_obj.parts)
            if path_str not in manifest_paths and path_obj.name not in excluded_files and not is_in_excluded_dir:
                untracked.append(path_str)
    return sorted(untracked)

def update_manifest(action, file_path_str, old_path_str=None, target_folder_path=None):
    manifest_data = load_manifest()
    if not manifest_data: return False
    def find_and_modify(nodes, current_path=''):
        if action in ['remove', 'move'] and old_path_str:
            nodes[:] = [node for node in nodes if node.get('path') != old_path_str]
        for node in nodes:
            if node.get("type") == "folder":
                node_path = f"{current_path}/{node['name']}" if current_path else node['name']
                if action == 'add' and node_path == target_folder_path:
                    if not any(child.get('path') == file_path_str for child in node.get("children", [])):
                        node.setdefault("children", []).append({"type": "file", "path": file_path_str})
                    return True
                if "children" in node and find_and_modify(node["children"], node_path): return True
        return False
    if find_and_modify(manifest_data["tree"]):
        return save_manifest(manifest_data)
    else:
        flash(f"AVISO: A pasta de destino '{target_folder_path}' não pôde ser encontrada.", "warning")
        return False
#endregion

@app.route('/')
def index():
    manifest_data = load_manifest()
    if not manifest_data: return "<h1>Erro fatal: Não foi possível carregar o manifest.json</h1>"
    return render_template('index.html', project_name=manifest_data.get('project_name', 'Gerenciador'), tree=manifest_data.get('tree', []))

# --- NOVAS ROTAS DE SINCRONIZAÇÃO INTELIGENTE ---
@app.route('/analyze_sync')
def analyze_sync():
    """Analisa o manifesto e o sistema de arquivos e retorna as diferenças."""
    manifest_data = load_manifest()
    if not manifest_data:
        return jsonify({"error": "Não foi possível carregar o manifest.json"}), 500
    
    paths_in_manifest = get_all_paths_in_manifest(manifest_data.get('tree', []))
    
    # Encontra links quebrados (arquivos no manifesto que não existem no disco)
    broken_links = [p for p in paths_in_manifest if not Path(p).exists()]
    
    # Encontra arquivos não rastreados (arquivos no disco que não estão no manifesto)
    untracked_files = get_untracked_files(paths_in_manifest)
    
    return jsonify({
        "broken_links": sorted(broken_links),
        "untracked_files": untracked_files
    })

@app.route('/execute_sync', methods=['POST'])
def execute_sync():
    """Executa a limpeza do manifesto, removendo os links quebrados."""
    if not create_backup():
        return redirect(url_for('index'))
        
    manifest_data = load_manifest()
    paths_in_manifest = get_all_paths_in_manifest(manifest_data.get('tree', []))
    broken_paths_set = {p for p in paths_in_manifest if not Path(p).exists()}

    if not broken_paths_set:
        flash("Nenhum link quebrado encontrado. O manifesto já está limpo!", "info")
        return redirect(url_for('index'))

    def _clean_tree_recursive(nodes):
        """Função auxiliar para remover recursivamente nós com caminhos quebrados."""
        initial_count = len(nodes)
        nodes[:] = [node for node in nodes if node.get('path', '') not in broken_paths_set]
        
        for node in nodes:
            if node.get("type") == "folder" and "children" in node:
                _clean_tree_recursive(node["children"])
    
    _clean_tree_recursive(manifest_data['tree'])
    
    if save_manifest(manifest_data):
        flash(f"Sincronização completa! {len(broken_paths_set)} link(s) quebrado(s) foram removidos do manifesto.", "success")
    
    return redirect(url_for('index'))

#region Outras Rotas de Ação (A-Z)
@app.route('/add', methods=['POST'])
def add_file():
    files_to_add = request.form.getlist('files_to_add')
    target_folder = request.form.get('target_manifest_folder')
    if not files_to_add or not target_folder:
        flash("Nenhum arquivo ou pasta de destino selecionada.", "warning"); return redirect(url_for('index'))
    if create_backup():
        added_count = 0
        for file_path in files_to_add:
            if update_manifest('add', file_path, target_folder_path=target_folder):
                added_count += 1
        if added_count > 0:
            flash(f"{added_count} arquivo(s) adicionado(s) à seção '{target_folder}'!", "success")
    return redirect(url_for('index'))

@app.route('/add_folder', methods=['POST'])
def add_folder():
    folder_name = request.form.get('folder_name'); folder_icon = request.form.get('folder_icon', 'fas fa-folder'); create_physical = request.form.get('create_physical_folder')
    if not folder_name:
        flash('O nome da seção não pode ser vazio!', 'danger'); return redirect(url_for('index'))
    manifest_data = load_manifest()
    if any(folder.get('name') == folder_name for folder in manifest_data.get('tree', [])):
        flash(f"A seção '{folder_name}' já existe!", 'warning'); return redirect(url_for('index'))
    if create_backup():
        if create_physical:
            try:
                new_dir = Path(folder_name)
                if not new_dir.exists(): new_dir.mkdir(); flash(f"Pasta física '{folder_name}' criada.", "info")
                else: flash(f"A pasta física '{folder_name}' já existe.", "info")
            except Exception as e:
                flash(f"Erro ao criar pasta física: {e}", "danger"); return redirect(url_for('index'))
        new_folder_obj = {"type": "folder", "name": folder_name, "icon": folder_icon, "children": []}
        manifest_data['tree'].append(new_folder_obj)
        if save_manifest(manifest_data): flash(f"Nova seção '{folder_name}' adicionada!", 'success')
    return redirect(url_for('index'))

@app.route('/copy', methods=['POST'])
def copy_file():
    paths_str = request.form.get('source_paths'); dest_folder = request.form.get('dest_folder')
    if not paths_str: flash("Nenhum arquivo selecionado.", "warning"); return redirect(url_for('index'))
    paths = paths_str.split(',')
    if create_backup():
        count = 0
        for path in paths:
            source_obj = Path(path); dest_obj = Path(dest_folder) / source_obj.name
            if dest_obj.exists(): flash(f"Erro: '{dest_obj.name}' já existe. Pulando.", "danger"); continue
            try: shutil.copy2(source_obj, dest_obj); update_manifest('add', dest_obj.as_posix(), target_folder_path=dest_folder); count += 1
            except Exception as e: flash(f"Erro ao copiar '{source_obj.name}': {e}", "danger")
        if count > 0: flash(f"{count} arquivo(s) copiado(s) para '{dest_folder}'!", "success")
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_file():
    paths_str = request.form.get('source_paths')
    if not paths_str: flash("Nenhum arquivo selecionado.", "warning"); return redirect(url_for('index'))
    paths = paths_str.split(',')
    if create_backup():
        count = 0
        for path_str in paths:
            try:
                # Tenta deletar o arquivo físico, mas não para se ele não existir
                if Path(path_str).exists(): Path(path_str).unlink()
                # Sempre remove do manifesto
                update_manifest('remove', path_str, old_path_str=path_str)
                count += 1
            except Exception as e: flash(f"Erro ao processar '{path_str}': {e}", "danger")
        if count > 0: flash(f"{count} referência(s) processada(s) para exclusão!", "success")
    return redirect(url_for('index'))

@app.route('/edit_folder', methods=['POST'])
def edit_folder():
    original_name = request.form.get('original_name'); new_name = request.form.get('new_name'); new_icon = request.form.get('new_icon', 'fas fa-folder'); rename_physical = request.form.get('rename_physical_folder')
    if not new_name:
        flash('O nome da seção não pode ser vazio!', 'danger'); return redirect(url_for('index'))
    manifest = load_manifest()
    if any(f.get('name') == new_name for f in manifest['tree'] if f.get('name') != original_name):
        flash(f"Uma seção com o nome '{new_name}' já existe!", 'danger'); return redirect(url_for('index'))
    if create_backup():
        folder_to_edit = next((f for f in manifest['tree'] if f.get('name') == original_name), None)
        if folder_to_edit:
            if rename_physical and original_name != new_name:
                try:
                    os.rename(original_name, new_name)
                    if 'children' in folder_to_edit:
                        for child in folder_to_edit['children']:
                            if child.get('type') == 'file' and child.get('path'):
                                child['path'] = child['path'].replace(f"{original_name}/", f"{new_name}/", 1)
                    flash(f"Pasta física renomeada.", 'info')
                except Exception as e:
                    flash(f"Erro ao renomear pasta física: {e}", "danger"); return redirect(url_for('index'))
            folder_to_edit['name'] = new_name; folder_to_edit['icon'] = new_icon
            if save_manifest(manifest): flash(f"Seção '{original_name}' atualizada para '{new_name}'!", 'success')
        else: flash(f"Erro: Seção '{original_name}' não encontrada.", 'danger')
    return redirect(url_for('index'))

@app.route('/move', methods=['POST'])
def move_file():
    paths_str = request.form.get('source_paths'); dest_folder = request.form.get('dest_folder')
    if not paths_str: flash("Nenhum arquivo selecionado.", "warning"); return redirect(url_for('index'))
    paths = paths_str.split(',')
    if create_backup():
        count = 0
        for path in paths:
            source_obj = Path(path); dest_obj = Path(dest_folder) / source_obj.name
            if dest_obj.exists(): flash(f"Erro: '{dest_obj.name}' já existe. Pulando.", "danger"); continue
            try: shutil.move(source_obj, dest_obj); update_manifest('move', dest_obj.as_posix(), old_path_str=path); count += 1
            except Exception as e: flash(f"Erro ao mover '{source_obj.name}': {e}", "danger")
        if count > 0: flash(f"{count} arquivo(s) movido(s) para '{dest_folder}'!", "success")
    return redirect(url_for('index'))

@app.route('/rename', methods=['POST'])
def rename_file():
    original_path = request.form['original_path']; new_name = request.form['new_name']
    original_obj = Path(original_path)
    if Path(new_name).suffix == '' and original_obj.suffix != '': new_name += original_obj.suffix
    new_obj = original_obj.with_name(new_name)
    if new_obj.exists(): flash(f"Erro: '{new_name}' já existe!", "danger")
    elif create_backup():
        try: os.rename(original_obj, new_obj); update_manifest('move', new_obj.as_posix(), old_path_str=original_path); flash(f"Arquivo renomeado para '{new_name}'!", "success")
        except Exception as e: flash(f"Erro ao renomear: {e}", "danger")
    return redirect(url_for('index'))
#endregion

if __name__ == '__main__':
    app.run(debug=True, port=5000)