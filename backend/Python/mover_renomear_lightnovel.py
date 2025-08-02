import os
import shutil

# Caminhos
caminho_origem = r"C:\Users\goget\Biblioteca do calibre\Kazuma Kamachi"
caminho_destino = r"C:\Programação\Projetos\A-certain-Digital-Database\src\img\LightNovel\LightNovel"

# Verifica se o destino existe, senão cria
os.makedirs(caminho_destino, exist_ok=True)

# Listar volumes na origem
volumes = [v for v in os.listdir(caminho_origem) if os.path.isdir(os.path.join(caminho_origem, v))]

if not volumes:
    print("Nenhum volume encontrado na origem.")
else:
    for volume in volumes:
        volume_path = os.path.join(caminho_origem, volume)
        volume_num = ''.join(filter(str.isdigit, volume))  # extrai número do volume, ex: NT11 -> 11

        print(f"\n--- Processando volume: {volume} ---")

        arquivos = os.listdir(volume_path)

        jpg_encontrado = None
        pdf_pt_encontrado = None
        pdf_en_encontrado = None

        # Procurando arquivos
        for arquivo in arquivos:
            if arquivo.lower().endswith(".jpg") and not jpg_encontrado:
                jpg_encontrado = arquivo
            elif arquivo.lower().endswith("_pt.pdf") and not pdf_pt_encontrado:
                pdf_pt_encontrado = arquivo
            elif arquivo.lower().endswith("_en.pdf") and not pdf_en_encontrado:
                pdf_en_encontrado = arquivo

        # Logs do que foi encontrado
        print(f"Capa JPG encontrada: {jpg_encontrado}")
        print(f"PDF PT encontrado: {pdf_pt_encontrado}")
        print(f"PDF EN encontrado: {pdf_en_encontrado}")

        # Mover e renomear
        if jpg_encontrado:
            novo_nome = f"NT_v{volume_num}_cover.jpg"
            shutil.copy(os.path.join(volume_path, jpg_encontrado), os.path.join(caminho_destino, novo_nome))
            print(f"-> Capa copiada como {novo_nome}")

        if pdf_pt_encontrado:
            novo_nome = f"NT_v{volume_num}_pt.pdf"
            shutil.copy(os.path.join(volume_path, pdf_pt_encontrado), os.path.join(caminho_destino, novo_nome))
            print(f"-> PDF PT copiado como {novo_nome}")

        if pdf_en_encontrado:
            novo_nome = f"NT_v{volume_num}_en.pdf"
            shutil.copy(os.path.join(volume_path, pdf_en_encontrado), os.path.join(caminho_destino, novo_nome))
            print(f"-> PDF EN copiado como {novo_nome}")

        if not any([jpg_encontrado, pdf_pt_encontrado, pdf_en_encontrado]):
            print("Nenhum arquivo válido encontrado para este volume.")

print("\nProcesso concluído, diz Misaka enquanto fornece um relatório completo com uma pontada de eficiência orgulhosa.")
