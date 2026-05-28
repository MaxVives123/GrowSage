"""
Indexa documentos en el vector store.

Uso:
  python ingest.py                     # indexa todo lo que haya en data/
  python ingest.py --url <URL>         # indexa una página web
  python ingest.py --file <ruta>       # indexa un fichero concreto (PDF o TXT)
"""
import argparse
from dotenv import load_dotenv
from src.loader import load_data_folder, load_url, load_pdf, load_txt, split_documents
from src.vectorstore import add_documents

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Ingestión de documentos botánicos")
    parser.add_argument("--url", help="URL a indexar")
    parser.add_argument("--file", help="Fichero a indexar (PDF o TXT)")
    args = parser.parse_args()

    if args.url:
        print(f"Cargando URL: {args.url}")
        docs = load_url(args.url)
    elif args.file:
        print(f"Cargando fichero: {args.file}")
        if args.file.endswith(".pdf"):
            docs = load_pdf(args.file)
        else:
            docs = load_txt(args.file)
    else:
        print("Cargando carpeta data/...")
        docs = load_data_folder("data")

    if not docs:
        print("No se encontraron documentos.")
        return

    print(f"Dividiendo {len(docs)} documentos en fragmentos...")
    chunks = split_documents(docs)
    print(f"Indexando {len(chunks)} fragmentos...")
    add_documents(chunks)
    print("Listo.")


if __name__ == "__main__":
    main()
