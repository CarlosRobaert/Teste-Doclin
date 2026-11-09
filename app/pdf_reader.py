
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption
)

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


# Configurações do processamento de PDF
pipeline_options = PdfPipelineOptions()

# Desabilita OCR nesta primeira versão
pipeline_options.do_ocr = False


# Inicializa o conversor aceitando somente PDF
converter = DocumentConverter(
    allowed_formats=[InputFormat.PDF],
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)


def extract_pdf_text(caminho_pdf):
    """
    Recebe o caminho de um PDF e retorna
    seu conteúdo textual e a quantidade de páginas.
    """

    resultado = converter.convert(caminho_pdf)

    documento = resultado.document

    texto = documento.export_to_text()

    total_paginas = len(documento.pages)

    return {
        "total_paginas": total_paginas,
        "texto": texto
    }
