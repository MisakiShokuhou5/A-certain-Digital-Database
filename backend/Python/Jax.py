import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator

def traduzir_texto(texto):
    try:
        traduzido = GoogleTranslator(source='auto', target='pt').translate(texto)
        # Se a API retornar None ou string vazia, mantém o original
        if not traduzido:
            raise ValueError("Tradução falhou ou retornou vazia.")
        return traduzido
    except Exception as e:
        print(f"Erro na tradução de: {texto}\n→ Mantido original. ({e})")
        return texto

def traduzir_epub(arquivo_epub):
    print(f"\nTraduzindo: {arquivo_epub}")
    
    try:
        book = epub.read_epub(arquivo_epub)
    except Exception as e:
        print(f"Erro ao abrir o arquivo {arquivo_epub}: {e}")
        return

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            for tag in soup.find_all(['p', 'span', 'div']):
                for content in tag.contents:
                    if isinstance(content, NavigableString):
                        texto_original = str(content).strip()
                        if texto_original:
                            texto_traduzido = traduzir_texto(texto_original)
                            print(f'Traduzindo: {texto_original}\n→ {texto_traduzido}\n')
                            content.replace_with(texto_traduzido)
            item.set_content(str(soup).encode('utf-8'))

    nome_arquivo = os.path.splitext(arquivo_epub)[0]
    novo_arquivo = f"{nome_arquivo}_pt.epub"
    epub.write_epub(novo_arquivo, book)
    print(f"Arquivo traduzido salvo como: {novo_arquivo}\n")

def traduzir_todos_na_pasta():
    pasta_atual = os.getcwd()
    for nome_arquivo in os.listdir(pasta_atual):
        if nome_arquivo.lower().endswith('.epub'):
            traduzir_epub(nome_arquivo)

if __name__ == "__main__":
    traduzir_todos_na_pasta()
