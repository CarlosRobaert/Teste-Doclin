
import os
import tempfile

from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.pdf_reader import extract_pdf_text


app = FastAPI(
    title="Revisão On-line - Leitor de PDF",
    description="API para extração de texto de arquivos PDF",
    version="1.0.0"
)


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/health")
def health_check():
    return {"status": "API funcionando"}


@app.post("/pdf/extract")
def extract_pdf(
    file: Annotated[UploadFile, File()]
):

    caminho_temporario = None

    try:

        # Verifica se o arquivo possui assinatura PDF
        assinatura = file.file.read(5)
        file.file.seek(0)

        if assinatura != b"%PDF-":
            raise HTTPException(
                status_code=400,
                detail="O arquivo enviado não é um PDF válido."
            )

        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as arquivo_temp:

            caminho_temporario = arquivo_temp.name

            tamanho = 0

            # Copia o conteúdo para o arquivo temporário
            while True:

                bloco = file.file.read(1024 * 1024)

                if not bloco:
                    break

                tamanho += len(bloco)

                if tamanho > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="O arquivo ultrapassa o limite de 10 MB."
                    )

                arquivo_temp.write(bloco)

        # Chama o módulo responsável pela extração
        resultado = extract_pdf_text(caminho_temporario)

        if not resultado["texto"].strip():
            raise HTTPException(
                status_code=422,
                detail="Não foi encontrado texto extraível no PDF."
            )

        # Retorna os dados em JSON
        return {
            "arquivo": file.filename,
            "status": "processado",
            "total_paginas": resultado["total_paginas"],
            "texto": resultado["texto"]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível processar o PDF."
        )

    finally:

        # Remove o arquivo temporário
        if caminho_temporario and os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)
