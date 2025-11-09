"""
Módulo para geração de PDFs profissionais a partir de conteúdo Markdown.
Utiliza WeasyPrint para conversão HTML->PDF com formatação profissional.
"""

import markdown
import weasyprint
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_pdf_from_markdown(markdown_content: str, filename: str) -> str:
    """
    Converte conteúdo Markdown para PDF usando WeasyPrint com formatação profissional.

    Args:
        markdown_content (str): Conteúdo em formato Markdown
        filename (str): Nome do arquivo PDF a ser criado

    Returns:
        str: Caminho completo do arquivo PDF gerado

    Raises:
        Exception: Se houver erro na geração do PDF
    """
    logger.info(f"🔧 Iniciando geração de PDF: {filename}")

    # Criar diretório se não existir
    os.makedirs('reports', exist_ok=True)
    logger.info("📁 Diretório reports verificado/criado")

    # Converter Markdown para HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    logger.info("🔄 Markdown processor inicializado")

    # CSS para formatação profissional
    css = _get_professional_css()
    logger.info("🎨 CSS profissional carregado")

    # Separar conteúdo principal das referências
    content_parts = markdown_content.split(' References:')
    main_content = content_parts[0].strip()
    references = content_parts[1].strip() if len(content_parts) > 1 else ""
    logger.info(
        f"📝 Conteúdo processado: {len(main_content)} chars principais, {len(references)} chars referências")

    # Converter conteúdo principal
    main_html = md.convert(main_content)

    # Processar referências se existirem
    references_html = ""
    if references:
        references_html = f"""
        <h2>Referências</h2>
        {md.convert(references)}
        """
        logger.info("🔗 Referências processadas e convertidas")

    # HTML completo
    html_content = _build_complete_html(css, main_html, references_html)
    logger.info("📄 HTML completo montado")

    # Gerar PDF
    pdf_path = f"reports/{filename}"
    try:
        weasyprint.HTML(string=html_content).write_pdf(pdf_path)
        logger.info(f"✅ PDF gerado com sucesso: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF com WeasyPrint: {str(e)}")
        raise


def save_markdown_file(markdown_content: str, filename: str) -> str:
    """
    Salva conteúdo Markdown em arquivo.

    Args:
        markdown_content (str): Conteúdo em formato Markdown
        filename (str): Nome do arquivo Markdown a ser criado

    Returns:
        str: Caminho completo do arquivo Markdown salvo
    """
    logger.info(f"💾 Salvando arquivo Markdown: {filename}")

    # Criar diretório se não existir
    os.makedirs('reports', exist_ok=True)

    markdown_path = f"reports/{filename}"
    try:
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"✅ Markdown salvo: {markdown_path}")
        return markdown_path
    except Exception as e:
        logger.error(f"❌ Erro ao salvar Markdown: {str(e)}")
        raise


def generate_report_files(content: str, base_timestamp: str = None, user_input: str = None) -> dict:
    """
    Gera ambos os arquivos PDF e Markdown com timestamp único e nome baseado no assunto.

    Args:
        content (str): Conteúdo do relatório em Markdown
        base_timestamp (str): Timestamp personalizado (opcional)
        user_input (str): Entrada do usuário para extrair o assunto (opcional)

    Returns:
        dict: Dicionário com paths dos arquivos gerados
        {
            'pdf_path': str,
            'markdown_path': str,
            'timestamp': str,
            'subject': str
        }
    """
    # Gerar timestamp se não fornecido
    if base_timestamp is None:
        base_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Extrair assunto do conteúdo ou user_input
    subject = _extract_subject_from_content(content, user_input)

    logger.info(f"📊 Gerando relatório completo - timestamp: {base_timestamp}")
    logger.info(f"📋 Assunto identificado: {subject}")

    # Nomes dos arquivos com assunto
    pdf_filename = f"{subject}_{base_timestamp}.pdf"
    markdown_filename = f"{subject}_{base_timestamp}.md"

    try:
        # Gerar PDF
        pdf_path = create_pdf_from_markdown(content, pdf_filename)

        # Salvar Markdown
        markdown_path = save_markdown_file(content, markdown_filename)

        result = {
            'pdf_path': pdf_path,
            'markdown_path': markdown_path,
            'timestamp': base_timestamp,
            'subject': subject
        }

        logger.info("🎯 Relatório completo gerado com sucesso!")
        logger.info(f"📄 PDF: {pdf_path}")
        logger.info(f"📝 Markdown: {markdown_path}")

        return result

    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório completo: {str(e)}")
        raise


def _extract_subject_from_content(content: str, user_input: str = None) -> str:
    """
    Extrai o assunto do relatório a partir do conteúdo ou user_input.

    Args:
        content (str): Conteúdo do relatório em Markdown
        user_input (str): Entrada original do usuário (opcional)

    Returns:
        str: Assunto formatado para uso em nome de arquivo
    """
    import re

    subject = "relatorio"  # Fallback padrão

    try:
        # Prioridade 1: Usar user_input se disponível
        if user_input and user_input.strip():
            subject = _sanitize_filename(user_input.strip())
            logger.info(f"📝 Assunto extraído do user_input: {subject}")
        else:
            # Prioridade 2: Extrair do título H1 do Markdown
            h1_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
            if h1_match:
                subject = _sanitize_filename(h1_match.group(1).strip())
                logger.info(f"📝 Assunto extraído do título H1: {subject}")
            else:
                # Prioridade 3: Usar as primeiras palavras significativas
                lines = content.split('\n')
                for line in lines[:10]:  # Verificar primeiras 10 linhas
                    line = line.strip()
                    if len(line) > 10 and not line.startswith('#'):
                        # Pegar primeiras palavras significativas
                        words = line.split()[:5]
                        if words:
                            subject = _sanitize_filename(' '.join(words))
                            logger.info(
                                f"📝 Assunto extraído do conteúdo: {subject}")
                            break

        # Limitar tamanho do assunto
        if len(subject) > 50:
            subject = subject[:50]
            logger.info(f"📝 Assunto truncado para: {subject}")

    except Exception as e:
        logger.warning(f"⚠️ Erro ao extrair assunto, usando padrão: {str(e)}")
        subject = "relatorio"

    return subject


def _sanitize_filename(text: str) -> str:
    """
    Sanitiza texto para uso seguro em nomes de arquivos.

    Args:
        text (str): Texto a ser sanitizado

    Returns:
        str: Texto seguro para nomes de arquivos
    """
    import re

    # Converter para minúsculas
    text = text.lower()

    # Remover acentos e caracteres especiais
    replacements = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
        'ß': 'ss'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Substituir espaços e caracteres especiais por underscore
    text = re.sub(r'[^a-z0-9]+', '_', text)

    # Remover underscores no início e fim
    text = text.strip('_')

    # Substituir múltiplos underscores por um só
    text = re.sub(r'_+', '_', text)

    return text if text else "relatorio"


def _get_professional_css() -> str:
    """
    Retorna o CSS para formatação profissional do PDF.

    Returns:
        str: CSS completo para formatação
    """
    return """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "Página " counter(page);
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-size: 24px;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 18px;
        }
        
        h3 {
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 16px;
        }
        
        p {
            text-align: justify;
            margin-bottom: 15px;
            font-size: 12px;
        }
        
        ul, ol {
            margin: 15px 0;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
            font-size: 12px;
        }
        
        strong {
            color: #2c3e50;
            font-weight: bold;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 20px;
        }
        
        .date {
            color: #7f8c8d;
            font-size: 10px;
            text-align: right;
            margin-bottom: 30px;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        /* Estilização adicional para citações */
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        /* Código inline */
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10px;
        }
        
        /* Tabelas */
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            font-size: 11px;
        }
        
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
    </style>
    """


def _build_complete_html(css: str, main_html: str, references_html: str) -> str:
    """
    Constrói o HTML completo do documento.

    Args:
        css (str): CSS para formatação
        main_html (str): HTML do conteúdo principal
        references_html (str): HTML das referências

    Returns:
        str: HTML completo do documento
    """
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório AI Agent</title>
        {css}
    </head>
    <body>
        <div class="header">
            <h1>🤖 Relatório AI Agent</h1>
            <div class="date">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</div>
        </div>
        
        {main_html}
        {references_html}
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1; text-align: center; color: #7f8c8d; font-size: 10px;">
            <p>Relatório gerado automaticamente pelo Agente de Pesquisa e Geração de Relatórios com IA</p>
        </div>
    </body>
    </html>
    """


def create_pdf_from_existing_markdown(markdown_file_path: str, output_pdf_name: str = None) -> str:
    """
    Gera PDF a partir de um arquivo Markdown existente.

    Útil para regenerar PDFs após edições manuais no arquivo Markdown.

    Args:
        markdown_file_path (str): Caminho para o arquivo Markdown existente
        output_pdf_name (str): Nome do PDF de saída (opcional). Se não fornecido, 
                              usa o mesmo nome do MD mas com extensão .pdf

    Returns:
        str: Caminho completo do arquivo PDF gerado

    Raises:
        FileNotFoundError: Se o arquivo Markdown não for encontrado
        Exception: Se houver erro na geração do PDF

    Exemplo:
        >>> create_pdf_from_existing_markdown("reports/meu_relatorio.md")
        'reports/meu_relatorio.pdf'

        >>> create_pdf_from_existing_markdown("reports/original.md", "relatorio_editado.pdf")
        'reports/relatorio_editado.pdf'
    """
    logger.info(
        f"📄 Gerando PDF a partir do arquivo Markdown: {markdown_file_path}")

    # Verificar se o arquivo existe
    if not os.path.exists(markdown_file_path):
        error_msg = f"Arquivo Markdown não encontrado: {markdown_file_path}"
        logger.error(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)

    try:
        # Ler o conteúdo do arquivo Markdown
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        logger.info(
            f"✅ Conteúdo Markdown carregado: {len(markdown_content)} caracteres")

        # Determinar nome do PDF de saída
        if output_pdf_name is None:
            # Usar mesmo nome do arquivo MD, mas com extensão .pdf
            base_name = os.path.splitext(
                os.path.basename(markdown_file_path))[0]
            output_pdf_name = f"{base_name}.pdf"

        # Garantir que o nome termine com .pdf
        if not output_pdf_name.endswith('.pdf'):
            output_pdf_name += '.pdf'

        logger.info(f"🎯 Nome do PDF de saída: {output_pdf_name}")

        # Gerar o PDF usando a função existente
        pdf_path = create_pdf_from_markdown(markdown_content, output_pdf_name)

        logger.info(f"🎉 PDF gerado com sucesso a partir do Markdown existente!")
        logger.info(f"📄 Arquivo original: {markdown_file_path}")
        logger.info(f"📄 PDF gerado: {pdf_path}")

        return pdf_path

    except FileNotFoundError:
        raise  # Re-raise FileNotFoundError
    except Exception as e:
        error_msg = f"Erro ao gerar PDF a partir do Markdown: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)
