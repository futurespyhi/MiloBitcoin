#!/usr/bin/env python3
"""
Quality Checker - 文档处理质量检查工具
评估处理后文档的质量，检测潜在问题
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QualityReport:
    """质量检查报告"""
    file_path: str
    total_score: float  # 0-100
    content_length: int
    line_count: int
    issues: List[str]
    strengths: List[str]
    metadata: Dict


class QualityChecker:
    """文档质量检查器"""

    # Bitcoin相关关键词（用于相关性检查）
    BITCOIN_KEYWORDS = [
        'bitcoin', 'blockchain', 'cryptocurrency', 'satoshi', 'nakamoto',
        'peer-to-peer', 'p2p', 'cryptographic', 'hash', 'mining',
        'transaction', 'block', 'network', 'protocol', 'consensus',
        'proof-of-work', 'pow', 'digital', 'signature', 'wallet',
        'lightning', 'layer-2', 'payment', 'channel', 'node'
    ]

    # 技术术语（用于技术深度检查）
    TECHNICAL_TERMS = [
        'algorithm', 'cryptography', 'merkle', 'tree', 'utxo',
        'segwit', 'taproot', 'schnorr', 'ecdsa', 'sha256',
        'ripemd160', 'base58', 'bech32', 'multisig', 'timelock',
        'htlc', 'commitment', 'revocation', 'onion', 'routing'
    ]

    def __init__(self):
        """初始化质量检查器"""
        pass

    def check_document_quality(self, file_path: str) -> QualityReport:
        """
        检查文档质量

        Args:
            file_path: 文档文件路径

        Returns:
            质量报告
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 基础统计
            lines = content.split('\n')
            line_count = len(lines)
            content_length = len(content)

            # 质量检查
            issues = []
            strengths = []
            scores = {}

            # 1. 内容长度检查
            length_score = self._check_content_length(content_length, issues, strengths)
            scores['length'] = length_score

            # 2. 结构检查
            structure_score = self._check_structure(content, issues, strengths)
            scores['structure'] = structure_score

            # 3. Bitcoin相关性检查
            relevance_score = self._check_bitcoin_relevance(content, issues, strengths)
            scores['relevance'] = relevance_score

            # 4. 技术深度检查
            technical_score = self._check_technical_depth(content, issues, strengths)
            scores['technical'] = technical_score

            # 5. 格式质量检查
            format_score = self._check_format_quality(content, issues, strengths)
            scores['format'] = format_score

            # 6. 重复内容检查
            duplication_score = self._check_duplication(content, issues, strengths)
            scores['duplication'] = duplication_score

            # 计算总分（加权平均）
            weights = {
                'length': 0.15,
                'structure': 0.25,
                'relevance': 0.20,
                'technical': 0.15,
                'format': 0.15,
                'duplication': 0.10
            }

            total_score = sum(scores[key] * weights[key] for key in scores)

            # 生成元数据
            metadata = {
                'scores': scores,
                'weights': weights,
                'bitcoin_keyword_count': self._count_keywords(content, self.BITCOIN_KEYWORDS),
                'technical_term_count': self._count_keywords(content, self.TECHNICAL_TERMS),
                'header_count': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
                'code_block_count': len(re.findall(r'```', content)),
                'table_count': len(re.findall(r'^\|', content, re.MULTILINE)),
                'word_count': len(content.split())
            }

            return QualityReport(
                file_path=file_path,
                total_score=round(total_score, 2),
                content_length=content_length,
                line_count=line_count,
                issues=issues,
                strengths=strengths,
                metadata=metadata
            )

        except Exception as e:
            return QualityReport(
                file_path=file_path,
                total_score=0.0,
                content_length=0,
                line_count=0,
                issues=[f"Failed to process file: {str(e)}"],
                strengths=[],
                metadata={}
            )

    def _check_content_length(self, length: int, issues: List[str], strengths: List[str]) -> float:
        """检查内容长度"""
        if length < 1000:
            issues.append("Content too short (< 1000 characters)")
            return 30.0
        elif length < 5000:
            issues.append("Content relatively short (< 5000 characters)")
            return 60.0
        elif length > 100000:
            strengths.append("Rich content with substantial length")
            return 95.0
        else:
            strengths.append("Good content length")
            return 85.0

    def _check_structure(self, content: str, issues: List[str], strengths: List[str]) -> float:
        """检查文档结构"""
        score = 100.0

        # 检查标题结构
        headers = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        if not headers:
            issues.append("No headers found - poor structure")
            score -= 40
        elif len(headers) < 3:
            issues.append("Few headers - limited structure")
            score -= 20
        else:
            strengths.append(f"Good structure with {len(headers)} headers")

        # 检查段落分布
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 5:
            issues.append("Few paragraphs - content may be poorly organized")
            score -= 15

        # 检查列表和表格
        lists = re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)
        tables = re.findall(r'^\|', content, re.MULTILINE)

        if lists:
            strengths.append(f"Contains {len(lists)} list items")
        if tables:
            strengths.append(f"Contains {len(tables)} table rows")

        return max(score, 0.0)

    def _check_bitcoin_relevance(self, content: str, issues: List[str], strengths: List[str]) -> float:
        """检查Bitcoin相关性"""
        content_lower = content.lower()
        found_keywords = [kw for kw in self.BITCOIN_KEYWORDS if kw in content_lower]

        relevance_ratio = len(found_keywords) / len(self.BITCOIN_KEYWORDS)

        if relevance_ratio < 0.1:
            issues.append("Low Bitcoin relevance - few related keywords found")
            return 20.0
        elif relevance_ratio < 0.3:
            issues.append("Moderate Bitcoin relevance")
            return 60.0
        else:
            strengths.append(f"High Bitcoin relevance ({len(found_keywords)} keywords)")
            return 90.0

    def _check_technical_depth(self, content: str, issues: List[str], strengths: List[str]) -> float:
        """检查技术深度"""
        content_lower = content.lower()
        found_terms = [term for term in self.TECHNICAL_TERMS if term in content_lower]

        if not found_terms:
            issues.append("No technical terms found - may lack technical depth")
            return 30.0
        elif len(found_terms) < 5:
            issues.append("Limited technical depth")
            return 60.0
        else:
            strengths.append(f"Good technical depth ({len(found_terms)} technical terms)")
            return 85.0

    def _check_format_quality(self, content: str, issues: List[str], strengths: List[str]) -> float:
        """检查格式质量"""
        score = 100.0

        # 检查异常重复字符
        excessive_repeats = re.findall(r'(.)\1{10,}', content)
        if excessive_repeats:
            issues.append("Excessive character repetition detected")
            score -= 30

        # 检查异常的章节编号
        weird_numbering = re.findall(r'#+\s*\d+(\.\d+){5,}', content)
        if weird_numbering:
            issues.append("Abnormal section numbering detected")
            score -= 25

        # 检查格式标记
        if '```' in content:
            strengths.append("Contains code blocks")
        if re.search(r'\*\*[^*]+\*\*', content):
            strengths.append("Contains bold formatting")
        if re.search(r'^\|', content, re.MULTILINE):
            strengths.append("Contains tables")

        return max(score, 0.0)

    def _check_duplication(self, content: str, issues: List[str], strengths: List[str]) -> float:
        """检查重复内容"""
        lines = content.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())

        if len(lines) == 0:
            return 0.0

        uniqueness_ratio = len(unique_lines) / len([line for line in lines if line.strip()])

        if uniqueness_ratio < 0.7:
            issues.append("High content duplication detected")
            return 30.0
        elif uniqueness_ratio < 0.9:
            issues.append("Some content duplication detected")
            return 70.0
        else:
            strengths.append("Good content uniqueness")
            return 95.0

    def _count_keywords(self, content: str, keywords: List[str]) -> int:
        """统计关键词出现次数"""
        content_lower = content.lower()
        return sum(content_lower.count(keyword) for keyword in keywords)

    def generate_report_summary(self, report: QualityReport) -> str:
        """生成报告摘要"""
        summary = f"""
📊 Document Quality Report
{'=' * 50}
File: {Path(report.file_path).name}
Overall Score: {report.total_score:.1f}/100

📈 Statistics:
  - Content Length: {report.content_length:,} characters
  - Line Count: {report.line_count:,}
  - Word Count: {report.metadata.get('word_count', 'N/A'):,}
  - Headers: {report.metadata.get('header_count', 0)}

✅ Strengths:
{chr(10).join(f'  • {strength}' for strength in report.strengths)}

⚠️  Issues:
{chr(10).join(f'  • {issue}' for issue in report.issues)}

🔍 Detailed Scores:
{chr(10).join(f'  • {key.title()}: {score:.1f}/100' for key, score in report.metadata.get('scores', {}).items())}
"""
        return summary


if __name__ == "__main__":
    # 测试代码
    checker = QualityChecker()

    test_files = [
        "../rag_test/test_outputs/markdown_results/bitcoin_api_standard_20250925_230354.md",
        "../rag_test/test_outputs/markdown_results/lightning_network_standard_20250927_113431.md"
    ]

    for file_path in test_files:
        if Path(file_path).exists():
            report = checker.check_document_quality(file_path)
            print(checker.generate_report_summary(report))
            print("\n" + "=" * 70 + "\n")
        else:
            print(f"File not found: {file_path}")