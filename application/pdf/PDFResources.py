"""
pdf_resource.py
Classe PDFResource modernizada com pypdf + reportlab.
Remove dependências de PyPDF2 (deprecated), fpdf e Django.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PDFReadResult:
    source: Path
    destination: Path
    pages_extracted: int
    success: bool
    error: str | None = None


@dataclass(frozen=True)
class PDFBuildResult:
    destination: Path
    success: bool
    error: str | None = None


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class PDFBuildConfig:
    """Parâmetros de construção do PDF — tudo com defaults sensatos."""
    pagesize: tuple[float, float] = field(default_factory=lambda: letter)
    top_margin: float = 20 * mm
    bottom_margin: float = 20 * mm
    left_margin: float = 20 * mm
    right_margin: float = 20 * mm
    title_font_size: int = 16
    body_font_size: int = 12
    include_divider: bool = True


# ---------------------------------------------------------------------------
# Core class
# ---------------------------------------------------------------------------

class PDFResource:
    """
    Utilitário de leitura e criação de PDFs.

    Modernizações:
    - PyPDF2 (deprecated)  →  pypdf
    - fpdf                 →  reportlab (suporte a Unicode, layouts ricos)
    - Sem dependência de Django
    - Retorna value objects em vez de códigos de status inteiros
    - Suporte a múltiplos blocos de conteúdo no build
    - Context-manager para operações em lote
    """

    def __init__(self, config: PDFBuildConfig | None = None) -> None:
        self.config = config or PDFBuildConfig()
        self._styles = getSampleStyleSheet()

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def read(self, source: str | Path, destination: str | Path) -> PDFReadResult:
        """
        Extrai o texto de *source* (PDF) e grava em *destination* (txt/md).

        Returns:
            PDFReadResult com metadados da operação.
        """
        source = Path(source)
        destination = Path(destination)

        try:
            pages_written = 0
            destination.parent.mkdir(parents=True, exist_ok=True)

            with destination.open("w", encoding="utf-8") as out:
                for i, text in enumerate(self._iter_pages(source), start=1):
                    out.write(f"--- Página {i} ---\n{text}\n\n")
                    pages_written += 1

            logger.info("Extraídas %d páginas de '%s'", pages_written, source)
            return PDFReadResult(source, destination, pages_written, success=True)

        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha ao ler '%s'", source)
            return PDFReadResult(source, destination, 0, success=False, error=str(exc))

    def read_text(self, source: str | Path) -> str:
        """Atalho: retorna o texto completo do PDF como string."""
        return "\n".join(self._iter_pages(Path(source)))

    # ------------------------------------------------------------------
    # Construção
    # ------------------------------------------------------------------

    def build(
        self,
        content: str | list[str],
        destination: str | Path,
        title: str = "",
    ) -> PDFBuildResult:
        """
        Cria um PDF a partir de *content* (string ou lista de parágrafos).

        Args:
            content:     Texto simples ou lista de blocos de texto.
            destination: Caminho do arquivo PDF de saída.
            title:       Título opcional exibido no topo do documento.

        Returns:
            PDFBuildResult com status da operação.
        """
        destination = Path(destination)

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            blocks = [content] if isinstance(content, str) else content
            self._render_pdf(blocks, destination, title)

            logger.info("PDF gerado em '%s'", destination)
            return PDFBuildResult(destination, success=True)

        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha ao gerar '%s'", destination)
            return PDFBuildResult(destination, success=False, error=str(exc))

    # ------------------------------------------------------------------
    # Operações utilitárias
    # ------------------------------------------------------------------

    def merge(self, sources: list[str | Path], destination: str | Path) -> PDFBuildResult:
        """Combina múltiplos PDFs em um único arquivo."""
        destination = Path(destination)
        try:
            writer = PdfWriter()
            for src in sources:
                reader = PdfReader(str(src))
                for page in reader.pages:
                    writer.add_page(page)

            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("wb") as out:
                writer.write(out)

            logger.info("Merged %d PDFs → '%s'", len(sources), destination)
            return PDFBuildResult(destination, success=True)

        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha ao mesclar PDFs")
            return PDFBuildResult(destination, success=False, error=str(exc))

    def split(self, source: str | Path, output_dir: str | Path) -> list[PDFBuildResult]:
        """Divide cada página do PDF de *source* em arquivos separados."""
        source = Path(source)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[PDFBuildResult] = []

        reader = PdfReader(str(source))
        for i, page in enumerate(reader.pages, start=1):
            dest = output_dir / f"{source.stem}_page_{i:03d}.pdf"
            try:
                writer = PdfWriter()
                writer.add_page(page)
                with dest.open("wb") as out:
                    writer.write(out)
                results.append(PDFBuildResult(dest, success=True))
            except Exception as exc:  # noqa: BLE001
                results.append(PDFBuildResult(dest, success=False, error=str(exc)))

        return results

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _iter_pages(self, source: Path) -> Iterator[str]:
        reader = PdfReader(str(source))
        for page in reader.pages:
            text = page.extract_text() or ""
            yield text.strip()

    def _render_pdf(
        self,
        blocks: list[str],
        destination: Path,
        title: str,
    ) -> None:
        cfg = self.config

        doc = SimpleDocTemplate(
            str(destination),
            pagesize=cfg.pagesize,
            topMargin=cfg.top_margin,
            bottomMargin=cfg.bottom_margin,
            leftMargin=cfg.left_margin,
            rightMargin=cfg.right_margin,
        )

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=self._styles["Title"],
            fontSize=cfg.title_font_size,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "CustomBody",
            parent=self._styles["Normal"],
            fontSize=cfg.body_font_size,
            leading=cfg.body_font_size * 1.4,
        )

        story = []

        if title:
            story.append(Paragraph(title, title_style))
            if cfg.include_divider:
                story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8))
            story.append(Spacer(1, 4 * mm))

        for block in blocks:
            # Separa parágrafos por linha em branco dentro do bloco
            for para in block.split("\n\n"):
                text = para.strip()
                if text:
                    story.append(Paragraph(text.replace("\n", "<br/>"), body_style))
                    story.append(Spacer(1, 3 * mm))

        doc.build(story)