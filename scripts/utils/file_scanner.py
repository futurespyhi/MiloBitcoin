#!/usr/bin/env python3
"""
Document Scanner - 文档发现和分类工具
支持递归扫描rag_data目录，发现并分类各种格式的文档
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DocumentInfo:
    """文档信息数据类"""
    path: str
    filename: str
    format: str
    category: str  # authoritative/supplementary
    subcategory: str  # whitepaper/bitcoin_org/academic_papers等
    size: int
    modified_time: float


class DocumentScanner:
    """文档扫描器"""

    SUPPORTED_FORMATS = {
        '.pdf': 'PDF',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.docx': 'Word',
        '.doc': 'Word'
    }

    def __init__(self, rag_data_path: str):
        """
        初始化文档扫描器

        Args:
            rag_data_path: rag_data目录路径
        """
        self.rag_data_path = Path(rag_data_path)
        self.sources_path = self.rag_data_path / "rag_sources"

        if not self.sources_path.exists():
            raise FileNotFoundError(f"RAG sources path not found: {self.sources_path}")

    def scan_all_documents(self) -> List[DocumentInfo]:
        """
        扫描所有支持的文档

        Returns:
            文档信息列表
        """
        documents = []

        for root, dirs, files in os.walk(self.sources_path):
            for file in files:
                file_path = Path(root) / file
                doc_info = self._analyze_document(file_path)

                if doc_info:
                    documents.append(doc_info)

        return sorted(documents, key=lambda x: (x.category, x.subcategory, x.filename))

    def scan_by_category(self, category: str) -> List[DocumentInfo]:
        """
        按类别扫描文档

        Args:
            category: 'authoritative' 或 'supplementary'

        Returns:
            指定类别的文档列表
        """
        category_path = self.sources_path / category

        if not category_path.exists():
            return []

        documents = []
        for root, dirs, files in os.walk(category_path):
            for file in files:
                file_path = Path(root) / file
                doc_info = self._analyze_document(file_path)

                if doc_info and doc_info.category == category:
                    documents.append(doc_info)

        return sorted(documents, key=lambda x: (x.subcategory, x.filename))

    def find_new_documents(self, processed_files: List[str]) -> List[DocumentInfo]:
        """
        查找未处理的新文档

        Args:
            processed_files: 已处理文件列表

        Returns:
            新文档列表
        """
        all_docs = self.scan_all_documents()
        processed_set = set(processed_files)

        return [doc for doc in all_docs if doc.path not in processed_set]

    def _analyze_document(self, file_path: Path) -> DocumentInfo:
        """
        分析单个文档信息

        Args:
            file_path: 文件路径

        Returns:
            文档信息对象，如果不支持则返回None
        """
        try:
            # 检查文件格式
            suffix = file_path.suffix.lower()
            if suffix not in self.SUPPORTED_FORMATS:
                return None

            # 分析文件路径结构
            relative_path = file_path.relative_to(self.sources_path)
            path_parts = relative_path.parts

            if len(path_parts) < 2:
                return None

            category = path_parts[0]  # authoritative/supplementary
            subcategory = path_parts[1] if len(path_parts) > 1 else "unknown"

            # 获取文件信息
            stat = file_path.stat()

            return DocumentInfo(
                path=str(file_path),
                filename=file_path.name,
                format=self.SUPPORTED_FORMATS[suffix],
                category=category,
                subcategory=subcategory,
                size=stat.st_size,
                modified_time=stat.st_mtime
            )

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")
            return None

    def get_statistics(self) -> Dict:
        """
        获取文档统计信息

        Returns:
            统计信息字典
        """
        documents = self.scan_all_documents()

        stats = {
            "total_documents": len(documents),
            "by_format": {},
            "by_category": {},
            "by_subcategory": {},
            "total_size": 0
        }

        for doc in documents:
            # 按格式统计
            stats["by_format"][doc.format] = stats["by_format"].get(doc.format, 0) + 1

            # 按类别统计
            stats["by_category"][doc.category] = stats["by_category"].get(doc.category, 0) + 1

            # 按子类别统计
            key = f"{doc.category}/{doc.subcategory}"
            stats["by_subcategory"][key] = stats["by_subcategory"].get(key, 0) + 1

            # 总大小
            stats["total_size"] += doc.size

        return stats


if __name__ == "__main__":
    # 测试代码
    try:
        scanner = DocumentScanner("../rag_data")
        docs = scanner.scan_all_documents()

        print(f"Found {len(docs)} documents:")
        for doc in docs:
            print(f"  {doc.filename} ({doc.format}) - {doc.category}/{doc.subcategory}")

        stats = scanner.get_statistics()
        print(f"\nStatistics: {stats}")

    except Exception as e:
        print(f"Error: {e}")