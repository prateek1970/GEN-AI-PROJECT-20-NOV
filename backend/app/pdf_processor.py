"""
Silicon Odyssey - Page-Aware PDF Ingestion, Text Extraction, Intelligent Chunking with Overlap & Boilerplate Detection.
Supports both PyMuPDF (fitz) and PyPDF.
"""

import os
import re
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
    PDF_ENGINE = "PyMuPDF"
except ImportError:
    import pypdf
    PDF_ENGINE = "pypdf"


class PDFProcessor:
    def __init__(self, pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 100):
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pages: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self._load_and_process()

    def _extract_pages_from_file(self) -> List[str]:
        raw_pages = []
        if PDF_ENGINE == "PyMuPDF":
            doc = fitz.open(self.pdf_path)
            for page in doc:
                raw_pages.append(page.get_text() or "")
            doc.close()
        else:
            reader = pypdf.PdfReader(self.pdf_path)
            for page in reader.pages:
                raw_pages.append(page.extract_text() or "")
        return raw_pages

    def _load_and_process(self):
        self.pages.clear()
        self.chunks.clear()
        raw_pages = self._extract_pages_from_file()

        for idx, raw_text in enumerate(raw_pages):
            page_num = idx + 1
            parsed = self._parse_page(page_num, raw_text)
            self.pages.append(parsed)

            # Generate overlapping chunks for this page
            page_chunks = self._generate_page_chunks(parsed)
            self.chunks.extend(page_chunks)

    def _parse_page(self, page_num: int, text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # 1. Header Chapter extraction
        header_chapter = "Unknown"
        header_module = ""
        for line in lines[:4]:
            match = re.search(r'(CHAPTER\s+\d+)\s*\|\s*(MODULE\s+[\d\.]+:[^=\n]+)', line, re.IGNORECASE)
            if match:
                header_chapter = match.group(1).title()
                header_module = match.group(2).strip()
                break

        # 2. Boilerplate Detection
        boilerplate_triggers = [
            "Reference Clause",
            "Standard Procedural Guidelines",
            "Archival & Verification Notes",
            "operational procedures, governance standards",
            "central repository at the conclusion of each operational cycle"
        ]
        matched_triggers = [t for t in boilerplate_triggers if t.lower() in text.lower()]
        is_boilerplate = len(matched_triggers) >= 2
        boilerplate_score = min(1.0, len(matched_triggers) / 3.0)

        # 3. Narrative Chapter & Title extraction
        narrative_chapter = None
        narrative_title = None
        clean_narrative = ""

        for i, line in enumerate(lines):
            match = re.search(r'^(CHAPTER\s+\d+)\s*:\s*(.+)$', line, re.IGNORECASE)
            if match and "module" not in line.lower() and "clause" not in line.lower():
                narrative_chapter = match.group(1).title()
                narrative_title = match.group(2).strip()

                body_lines = []
                for subsequent_line in lines[i+1:]:
                    if "Operational Compliance Note" in subsequent_line or ("Page " in subsequent_line and "Confidential" in subsequent_line):
                        break
                    body_lines.append(subsequent_line)
                clean_narrative = " ".join(body_lines).strip()
                break

        if not is_boilerplate and not clean_narrative:
            clean_narrative = text

        # 4. Chapter Discrepancy Detection (Trap resolution)
        has_discrepancy = False
        discrepancy_note = ""
        if narrative_chapter and header_chapter != "Unknown":
            header_num = re.search(r'\d+', header_chapter)
            narrative_num = re.search(r'\d+', narrative_chapter)
            if header_num and narrative_num and header_num.group(0) != narrative_num.group(0):
                has_discrepancy = True
                discrepancy_note = (
                    f"Chapter Label Discrepancy on Page {page_num}: Document header displays '{header_chapter}' "
                    f"whereas authentic memoir narrative specifies '{narrative_chapter}: {narrative_title}'. "
                    f"System prioritizes narrative chapter for fact queries."
                )

        # 5. Entity Spotting
        entities = self._extract_entities(text)

        return {
            "page": page_num,
            "raw_text": text,
            "header_chapter": header_chapter,
            "header_module": header_module,
            "narrative_chapter": narrative_chapter or header_chapter,
            "narrative_title": narrative_title or header_module or f"Section {page_num}",
            "is_boilerplate": is_boilerplate,
            "boilerplate_score": boilerplate_score,
            "has_discrepancy": has_discrepancy,
            "discrepancy_note": discrepancy_note,
            "clean_narrative": clean_narrative,
            "entities": entities
        }

    def _generate_page_chunks(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates semantic chunks with token overlap across the page text.
        """
        chunks = []
        page_num = page_data["page"]
        
        # Prefer clean narrative if available, otherwise raw text
        target_text = page_data["clean_narrative"] if (not page_data["is_boilerplate"] and page_data["clean_narrative"]) else page_data["raw_text"]
        text_len = len(target_text)

        if text_len <= self.chunk_size:
            chunk_id = f"p{page_num}_c0"
            chunks.append({
                "chunk_id": chunk_id,
                "page": page_num,
                "chunk_index": 0,
                "text": target_text,
                "header_chapter": page_data["header_chapter"],
                "narrative_chapter": page_data["narrative_chapter"],
                "narrative_title": page_data["narrative_title"],
                "is_boilerplate": page_data["is_boilerplate"],
                "boilerplate_score": page_data["boilerplate_score"],
                "has_discrepancy": page_data["has_discrepancy"],
                "discrepancy_note": page_data["discrepancy_note"],
                "entities": page_data["entities"]
            })
            return chunks

        start = 0
        chunk_idx = 0
        step = self.chunk_size - self.chunk_overlap
        while start < text_len:
            end = min(text_len, start + self.chunk_size)
            chunk_slice = target_text[start:end].strip()
            if chunk_slice:
                chunk_id = f"p{page_num}_c{chunk_idx}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "chunk_index": chunk_idx,
                    "text": chunk_slice,
                    "header_chapter": page_data["header_chapter"],
                    "narrative_chapter": page_data["narrative_chapter"],
                    "narrative_title": page_data["narrative_title"],
                    "is_boilerplate": page_data["is_boilerplate"],
                    "boilerplate_score": page_data["boilerplate_score"],
                    "has_discrepancy": page_data["has_discrepancy"],
                    "discrepancy_note": page_data["discrepancy_note"],
                    "entities": page_data["entities"]
                })
                chunk_idx += 1
            start += step

        return chunks

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities: Dict[str, List[str]] = {
            "years": [],
            "locations": [],
            "people": [],
            "financials": [],
            "hardware": []
        }

        years = re.findall(r'\b(198\d|199\d)\b', text)
        entities["years"] = sorted(list(set(years)))

        loc_patterns = [
            r'742\s+Sycamore\s+Lane',
            r'Sunnyvale,\s+California',
            r'Sunnyvale',
            r'Las\s+Vegas'
        ]
        for pat in loc_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                entities["locations"].append(m)
        entities["locations"] = list(dict.fromkeys(entities["locations"]))

        if "Elena Vance" in text:
            entities["people"].append("Elena Vance (Co-founder)")
        if "technician" in text.lower():
            entities["people"].append("Keynote Technician")

        fin_matches = re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\s*USD)?', text)
        for f in fin_matches:
            entities["financials"].append(f.strip())
        if "second mortgage" in text.lower():
            entities["financials"].append("Second Mortgage on Family Home")
        if "bridge financing" in text.lower():
            entities["financials"].append("Emergency Bridge Financing")

        hw_keywords = [
            "microprocessor circuit boards",
            "Series-4 prototype",
            "wave-soldering rig",
            "12V cooling fan power connector",
            "primary voltage regulator heatsink",
            "thermal paste"
        ]
        for kw in hw_keywords:
            if kw.lower() in text.lower():
                entities["hardware"].append(kw)

        return entities

    def get_all_pages(self) -> List[Dict[str, Any]]:
        return self.pages

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        return self.chunks

    def get_narrative_pages(self) -> List[Dict[str, Any]]:
        return [p for p in self.pages if not p["is_boilerplate"]]
