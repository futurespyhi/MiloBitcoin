#!/usr/bin/env python3
"""
Format Detector - 文档格式检测和处理策略选择
根据文件格式选择最佳的处理策略
"""

import mimetypes
from pathlib import Path
from typing import Dict, Optional, Tuple
from enum import Enum


class ProcessingStrategy(Enum):
    """处理策略枚举"""
    GRANITE_DOCLING = "granite_docling"  # 使用Granite Docling处理
    STANDARD_DOCLING = "standard_docling"  # 使用标准Docling处理
    DIRECT_COPY = "direct_copy"  # 直接复制(已是Markdown)
    SIMPLE_PARSE = "simple_parse"  # 简单解析(纯文本)
    UNSUPPORTED = "unsupported"  # 不支持的格式


class FormatDetector:
    """文档格式检测器"""

    # 格式处理策略映射
    FORMAT_STRATEGIES = {
        'PDF': ProcessingStrategy.GRANITE_DOCLING,
        'HTML': ProcessingStrategy.STANDARD_DOCLING,
        'Markdown': ProcessingStrategy.DIRECT_COPY,
        'Text': ProcessingStrategy.SIMPLE_PARSE,
        'Word': ProcessingStrategy.STANDARD_DOCLING,
    }

    # 文件扩展名到格式的映射
    EXTENSION_FORMATS = {
        '.pdf': 'PDF',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.md': 'Markdown',
        '.markdown': 'Markdown',
        '.txt': 'Text',
        '.docx': 'Word',
        '.doc': 'Word',
        '.odt': 'Word',
        '.rtf': 'Text',
    }

    # MIME类型到格式的映射
    MIME_FORMATS = {
        'application/pdf': 'PDF',
        'text/html': 'HTML',
        'text/markdown': 'Markdown',
        'text/plain': 'Text',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
        'application/msword': 'Word',
    }

    @classmethod
    def detect_format(cls, file_path: str) -> Tuple[str, ProcessingStrategy]:
        """
        检测文件格式并返回处理策略

        Args:
            file_path: 文件路径

        Returns:
            (格式名称, 处理策略)
        """
        path = Path(file_path)

        # 首先通过扩展名检测
        extension = path.suffix.lower()
        if extension in cls.EXTENSION_FORMATS:
            format_name = cls.EXTENSION_FORMATS[extension]
            strategy = cls.FORMAT_STRATEGIES.get(format_name, ProcessingStrategy.UNSUPPORTED)
            return format_name, strategy

        # 通过MIME类型检测
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type in cls.MIME_FORMATS:
            format_name = cls.MIME_FORMATS[mime_type]
            strategy = cls.FORMAT_STRATEGIES.get(format_name, ProcessingStrategy.UNSUPPORTED)
            return format_name, strategy

        # 通过文件内容检测（简单启发式）
        format_name = cls._detect_by_content(file_path)
        if format_name:
            strategy = cls.FORMAT_STRATEGIES.get(format_name, ProcessingStrategy.UNSUPPORTED)
            return format_name, strategy

        return "Unknown", ProcessingStrategy.UNSUPPORTED

    @classmethod
    def _detect_by_content(cls, file_path: str) -> Optional[str]:
        """
        通过文件内容检测格式

        Args:
            file_path: 文件路径

        Returns:
            格式名称或None
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)

            # PDF文件检测
            if header.startswith(b'%PDF-'):
                return 'PDF'

            # HTML文件检测
            if b'<html' in header.lower() or b'<!doctype html' in header.lower():
                return 'HTML'

            # 尝试作为文本文件读取
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)

                # Markdown文件检测
                if any(marker in content for marker in ['# ', '## ', '### ', '```', '**', '__']):
                    return 'Markdown'

                # HTML文件检测（文本模式）
                if any(tag in content.lower() for tag in ['<html', '<head', '<body', '<div']):
                    return 'HTML'

                return 'Text'

            except UnicodeDecodeError:
                # 非文本文件
                pass

        except Exception:
            pass

        return None

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        检查文件是否支持处理

        Args:
            file_path: 文件路径

        Returns:
            是否支持
        """
        _, strategy = cls.detect_format(file_path)
        return strategy != ProcessingStrategy.UNSUPPORTED

    @classmethod
    def get_processing_command(cls, file_path: str, output_dir: str) -> Optional[str]:
        """
        根据文件格式生成处理命令

        Args:
            file_path: 输入文件路径
            output_dir: 输出目录

        Returns:
            处理命令字符串，如果不支持则返回None
        """
        format_name, strategy = cls.detect_format(file_path)

        if strategy == ProcessingStrategy.GRANITE_DOCLING:
            return f"uv run rag_test/test_scripts/granite_docling.py {file_path}"

        elif strategy == ProcessingStrategy.STANDARD_DOCLING:
            # 未来实现标准Docling处理
            return f"docling --to md {file_path} --output {output_dir}"

        elif strategy == ProcessingStrategy.DIRECT_COPY:
            # Markdown文件直接复制
            return f"cp {file_path} {output_dir}"

        elif strategy == ProcessingStrategy.SIMPLE_PARSE:
            # 简单文本处理
            return f"python scripts/utils/text_processor.py {file_path} {output_dir}"

        else:
            return None

    @classmethod
    def get_format_info(cls) -> Dict:
        """
        获取支持的格式信息

        Returns:
            格式信息字典
        """
        return {
            "supported_formats": list(cls.FORMAT_STRATEGIES.keys()),
            "file_extensions": list(cls.EXTENSION_FORMATS.keys()),
            "processing_strategies": [strategy.value for strategy in ProcessingStrategy],
            "format_strategy_mapping": {
                fmt: strategy.value for fmt, strategy in cls.FORMAT_STRATEGIES.items()
            }
        }


if __name__ == "__main__":
    # 测试代码
    test_files = [
        "../rag_data/rag_sources/authoritative/whitepaper/bitcoin.pdf",
        "../rag_data/rag_sources/supplementary/academic_papers/lightning_network.pdf"
    ]

    detector = FormatDetector()

    print("Format Detection Test:")
    print("=" * 50)

    for file_path in test_files:
        if Path(file_path).exists():
            format_name, strategy = detector.detect_format(file_path)
            command = detector.get_processing_command(file_path, "output/")

            print(f"File: {Path(file_path).name}")
            print(f"  Format: {format_name}")
            print(f"  Strategy: {strategy.value}")
            print(f"  Command: {command}")
            print()

    print("Supported Formats:", detector.get_format_info())