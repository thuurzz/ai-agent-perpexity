#!/usr/bin/env python3
"""
Utilitário para regenerar PDFs a partir de arquivos Markdown editados.

Uso:
    python regenerate_pdf.py <caminho_do_markdown> [nome_do_pdf_saida]
    
Exemplos:
    python regenerate_pdf.py reports/meu_relatorio.md
    python regenerate_pdf.py reports/original.md relatorio_editado.pdf
"""

import sys
import os
import logging
from pdf_generator import create_pdf_from_existing_markdown

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Função principal do utilitário."""

    if len(sys.argv) < 2:
        print("❌ Erro: Caminho do arquivo Markdown é obrigatório")
        print("\n📖 Uso:")
        print(
            "    python regenerate_pdf.py <caminho_do_markdown> [nome_do_pdf_saida]")
        print("\n💡 Exemplos:")
        print("    python regenerate_pdf.py reports/meu_relatorio.md")
        print("    python regenerate_pdf.py reports/original.md relatorio_editado.pdf")
        sys.exit(1)

    markdown_path = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        logger.info(
            "🚀 Iniciando geração de PDF a partir de Markdown existente...")
        logger.info(f"📄 Arquivo Markdown: {markdown_path}")

        if output_name:
            logger.info(f"🎯 Nome do PDF de saída: {output_name}")
        else:
            logger.info("🎯 Usando nome automático para o PDF")

        # Gerar PDF
        pdf_path = create_pdf_from_existing_markdown(
            markdown_path, output_name)

        print("\n" + "="*50)
        print("🎉 PDF GERADO COM SUCESSO!")
        print("="*50)
        print(f"📄 Arquivo original: {markdown_path}")
        print(f"📄 PDF gerado: {pdf_path}")

        # Verificar se o arquivo foi realmente criado
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 Tamanho do arquivo: {file_size:,} bytes")

        print("\n✅ Processo concluído!")

    except FileNotFoundError as e:
        print(f"\n❌ Erro: Arquivo não encontrado")
        print(f"   {str(e)}")
        print(f"\n💡 Verifique se o caminho está correto: {markdown_path}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erro ao gerar PDF:")
        print(f"   {str(e)}")
        print(f"\n🔍 Verifique os logs acima para mais detalhes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
