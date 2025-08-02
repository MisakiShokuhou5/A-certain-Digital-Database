import os

# Caminho da pasta onde estão as imagens
pasta = r'C:\Users\goget\OneDrive\Desktop\Programação\Projetos\ToaruCrunchyrol-main\src\img\Manga'  # Ajuste conforme necessário

# Extensões a serem convertidas
extensoes_para_converter = ['.jpeg', '.png', '.webp']

# Percorre todos os arquivos na pasta
for nome_arquivo in os.listdir(pasta):
    nome_arquivo_lower = nome_arquivo.lower()
    for ext in extensoes_para_converter:
        if nome_arquivo_lower.endswith(ext):
            nome_antigo = os.path.join(pasta, nome_arquivo)
            nome_novo = os.path.join(pasta, nome_arquivo[:-len(ext)] + '.jpg')
            os.rename(nome_antigo, nome_novo)
            print(f'Renomeado: {nome_arquivo} -> {os.path.basename(nome_novo)}')
            break  # Evita tentar trocar a extensão várias vezes

print('Renomeação concluída.')
