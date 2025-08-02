import os
import subprocess
import shutil
import time

# Identificação
misaka_id = "#18774"

# Caminhos
base_dir = r"C:\Programação\Projetos\A-certain-Digital-Database\src\img\LightNovel"
entrada_dir = os.path.join(base_dir, "Para automatizar")
saida_dir = base_dir  # PDF final vai para LightNovel diretamente

# Arquivos
arquivos_epub = {
    "pt": "NT_v11_pt.epub",
    "en": "NT_v11_en.epub"
}

nomes_pdf = {
    "pt": "Index_v11_pt.pdf",
    "en": "Index_v11_en.pdf"
}

nome_jpg_final = "Index_v11_cover.jpg"

def converter_epub_para_pdf(input_epub, output_pdf):
    print(f"Convertendo {input_epub} para {output_pdf} ...")
    comando = [
        "ebook-convert",
        input_epub,
        output_pdf
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode == 0:
        print(f"Conversão concluída: {output_pdf}")
    else:
        print(f"Erro na conversão de {input_epub}:\n{resultado.stderr}")

def mover_arquivo(origem, destino):
    if os.path.exists(origem):
        shutil.move(origem, destino)
        print(f"Movido: {origem} → {destino}")
    else:
        print(f"Arquivo não encontrado: {origem}")

def localizar_jpg():
    for nome in os.listdir(entrada_dir):
        if nome.lower().endswith(".jpg"):
            return os.path.join(entrada_dir, nome)
    return None

if __name__ == "__main__":
    print(f"Iniciando conversão, diz Misaka {misaka_id} com eficiência digital.")

    # 1. Converter cada .epub
    for lang, nome_arquivo in arquivos_epub.items():
        epub_path = os.path.join(entrada_dir, nome_arquivo)
        saida_temp_pdf = os.path.join(entrada_dir, f"temp_{lang}.pdf")
        converter_epub_para_pdf(epub_path, saida_temp_pdf)

    # 2. Mover e renomear PDFs convertidos
    for lang in ["pt", "en"]:
        temp_pdf = os.path.join(entrada_dir, f"temp_{lang}.pdf")
        nome_destino = os.path.join(saida_dir, nomes_pdf[lang])
        mover_arquivo(temp_pdf, nome_destino)

    # 3. Localizar e mover a imagem de capa
    capa = localizar_jpg()
    if capa:
        destino_capa = os.path.join(saida_dir, nome_jpg_final)
        mover_arquivo(capa, destino_capa)
    else:
        print("Imagem de capa JPG não encontrada em Para automatizar. Por favor, coloque-a manualmente.")

    print(f"Processo finalizado com sucesso, diz Misaka {misaka_id} com satisfação.")
