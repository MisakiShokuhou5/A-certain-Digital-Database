import os
import shutil

def limpar_pasta(pasta):
    if os.path.exists(pasta):
        for item in os.listdir(pasta):
            caminho = os.path.join(pasta, item)
            if os.path.isfile(caminho):
                os.remove(caminho)
            elif os.path.isdir(caminho):
                shutil.rmtree(caminho)
    else:
        os.makedirs(pasta)

def mover_e_renomear_arquivos(origem, destino):
    # Vamos procurar as pastas dentro da origem (Kazuma Kamachi)
    for pasta in os.listdir(origem):
        caminho_pasta = os.path.join(origem, pasta)
        if os.path.isdir(caminho_pasta):
            arquivos = os.listdir(caminho_pasta)
            # Filtra arquivos que queremos manter
            jpg_arquivo = None
            pdf_arquivo_pt = None
            pdf_arquivo_en = None
            
            for arq in arquivos:
                arq_lower = arq.lower()
                if arq_lower.endswith(".jpg") and "cover" not in arq_lower:
                    jpg_arquivo = arq
                elif arq_lower.endswith(".pdf") and "_pt" in arq_lower:
                    pdf_arquivo_pt = arq
                elif arq_lower.endswith(".pdf") and "_en" in arq_lower:
                    pdf_arquivo_en = arq

            # Copiar e renomear para pasta destino
            if jpg_arquivo:
                shutil.copy2(os.path.join(caminho_pasta, jpg_arquivo), os.path.join(destino, "NT_v11_cover.jpg"))
            if pdf_arquivo_pt:
                shutil.copy2(os.path.join(caminho_pasta, pdf_arquivo_pt), os.path.join(destino, "NT_v11_pt.pdf"))
            if pdf_arquivo_en:
                shutil.copy2(os.path.join(caminho_pasta, pdf_arquivo_en), os.path.join(destino, "NT_v11_en.pdf"))
            
            # Apagar a pasta depois de copiar os arquivos
            shutil.rmtree(caminho_pasta)

if __name__ == "__main__":
    base_dir = os.getcwd()
    entrada_dir = os.path.join(base_dir, "Kazuma Kamachi")  # Ajuste se a pasta estiver em outro local
    destino_dir = os.path.join(base_dir, "LightNovel")

    print(f"Limpeza da pasta destino: {destino_dir}")
    limpar_pasta(destino_dir)

    print(f"Movendo arquivos da pasta {entrada_dir} para {destino_dir} ...")
    mover_e_renomear_arquivos(entrada_dir, destino_dir)

    print("Arquivos movidos e renomeados com sucesso!")
