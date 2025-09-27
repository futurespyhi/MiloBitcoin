#!/usr/bin/env python3
"""
Milo Bitcoin RAG - 单GPU顺序批量文档处理器
专为单GPU环境设计，顺序处理PDF文档，自动GPU内存管理

功能特性:
- 单GPU顺序处理，避免CUDA内存冲突
- 自动发现rag_data目录下的PDF文档
- 使用生产环境granite_docling.py处理管道
- 智能输出管理和质量检查
- 处理进度跟踪和错误处理

使用方法:
    python scripts/batch_process_docs.py [选项]

示例:
    python scripts/batch_process_docs.py                           # 处理所有PDF
    python scripts/batch_process_docs.py --scan-only               # 仅扫描文档
    python scripts/batch_process_docs.py --category authoritative  # 仅处理权威文档
    python scripts/batch_process_docs.py --force                   # 强制重新处理
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from scripts.utils import DocumentScanner, QualityChecker
    from scripts.utils.file_scanner import DocumentInfo
    from scripts.utils.quality_checker import QualityReport
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run from project root directory")
    sys.exit(1)


class SingleGPUBatchProcessor:
    """单GPU顺序批量处理器"""

    def __init__(self, rag_data_path: str = "rag_data"):
        """
        初始化处理器

        Args:
            rag_data_path: RAG数据目录路径
        """
        self.rag_data_path = Path(rag_data_path)
        self.sources_path = self.rag_data_path / "rag_sources"
        self.processed_path = self.rag_data_path / "rag_sources" / "processed"

        # 创建输出目录
        self.chunks_dir = self.processed_path / "chunks"
        self.metadata_dir = self.processed_path / "metadata"
        self.logs_dir = Path("logs") / "processing"

        for dir_path in [self.chunks_dir, self.metadata_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 初始化工具
        self.scanner = DocumentScanner(str(self.rag_data_path))
        self.quality_checker = QualityChecker()

        # granite_docling脚本路径（生产环境版本）
        self.granite_script = Path("scripts/granite_docling.py")
        if not self.granite_script.exists():
            raise FileNotFoundError(f"Granite script not found: {self.granite_script}")

        # 处理统计
        self.stats = {
            'total_found': 0,
            'processed': 0,
            'skipped': 0,
            'failed': 0,
            'quality_passed': 0,
            'quality_failed': 0
        }

        # 初始化日志
        self._setup_logging()

    def _setup_logging(self):
        """设置日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"batch_processing_{timestamp}.log"
        print(f"📋 Log file: {self.log_file}")

    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        print(log_entry)

        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def scan_documents(self, category: Optional[str] = None) -> List[DocumentInfo]:
        """
        扫描PDF文档

        Args:
            category: 可选的文档类别过滤 ('authoritative' 或 'supplementary')

        Returns:
            PDF文档信息列表
        """
        self._log("Starting document scan...")

        if category:
            all_docs = self.scanner.scan_by_category(category)
        else:
            all_docs = self.scanner.scan_all_documents()

        # 仅保留PDF文档
        pdf_docs = [doc for doc in all_docs if doc.format == 'PDF']

        self._log(f"Found {len(pdf_docs)} PDF documents")
        if category:
            self._log(f"Filtered by category: {category}")

        # 显示文档列表
        for i, doc in enumerate(pdf_docs, 1):
            self._log(f"  {i}. {doc.filename} ({doc.category}/{doc.subcategory})")

        self.stats['total_found'] = len(pdf_docs)
        return pdf_docs

    def process_documents(self, documents: List[DocumentInfo], force: bool = False) -> List[Tuple[DocumentInfo, bool, Optional[QualityReport]]]:
        """
        顺序处理PDF文档

        Args:
            documents: 要处理的文档列表
            force: 是否强制重新处理已存在的文件

        Returns:
            处理结果列表 (文档信息, 是否成功, 质量报告)
        """
        if not documents:
            self._log("No documents to process", "WARNING")
            return []

        self._log(f"Starting single-GPU sequential processing of {len(documents)} documents")
        results = []

        for i, doc in enumerate(documents, 1):
            self._log(f"\n{'='*60}")
            self._log(f"Processing document {i}/{len(documents)}: {doc.filename}")
            self._log(f"{'='*60}")

            try:
                success, quality_report, output_file = self._process_single_document(doc, force)
                results.append((doc, success, quality_report))

                if success:
                    self.stats['processed'] += 1
                    if quality_report and quality_report.total_score >= 60.0:
                        self.stats['quality_passed'] += 1
                    else:
                        self.stats['quality_failed'] += 1

                    self._log(f"✅ Successfully processed: {doc.filename}")
                    self._log(f"   Output: {output_file}")
                else:
                    self.stats['failed'] += 1
                    self._log(f"❌ Failed to process: {doc.filename}", "ERROR")

                # GPU降温间隔（可选）
                if i < len(documents):  # 不是最后一个文档
                    self._log("⏸️  GPU cooling interval (2 seconds)...")
                    time.sleep(2)

            except Exception as e:
                self._log(f"Unexpected error processing {doc.filename}: {e}", "ERROR")
                results.append((doc, False, None))
                self.stats['failed'] += 1

        self._log(f"\n🎉 Batch processing completed!")
        self._log(f"Processed: {self.stats['processed']}, Failed: {self.stats['failed']}")

        return results

    def _process_single_document(self, doc: DocumentInfo, force: bool = False) -> Tuple[bool, Optional[QualityReport], Optional[str]]:
        """
        处理单个PDF文档

        Args:
            doc: 文档信息
            force: 是否强制重新处理

        Returns:
            (是否成功, 质量报告, 输出文件路径)
        """
        # 构建预期的输出文件路径
        expected_output = self._get_expected_output_path(doc)

        # 检查是否已处理
        if not force and expected_output.exists():
            self._log(f"⏭️  Skipping {doc.filename} - already processed")
            self.stats['skipped'] += 1
            return True, None, str(expected_output)

        # 使用生产环境 granite_docling.py 处理文档
        self._log(f"🔄 Calling production granite_docling.py for {doc.filename}")

        try:
            # 构建处理命令
            cmd = [
                "python",
                str(self.granite_script),
                doc.path,
                "--output-dir", str(self.chunks_dir)
            ]

            self._log(f"Command: {' '.join(cmd)}")

            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                cwd=str(Path.cwd())  # 确保在项目根目录运行
            )

            elapsed = time.time() - start_time

            if result.returncode != 0:
                self._log(f"❌ Granite processing failed: {result.stderr}", "ERROR")
                return False, None, None

            self._log(f"✅ Granite processing completed in {elapsed:.1f}s")

            # 从输出中提取生成的文件路径
            output_file = self._extract_output_file_from_result(result.stdout, doc)
            if not output_file:
                self._log(f"❌ Could not determine output file for {doc.filename}", "ERROR")
                return False, None, None

            # 质量检查
            quality_report = self.quality_checker.check_document_quality(output_file)
            self._save_quality_report(quality_report, doc)

            self._log(f"📊 Quality score: {quality_report.total_score:.1f}/100")

            return True, quality_report, output_file

        except subprocess.TimeoutExpired:
            self._log(f"⏰ Processing timeout for {doc.filename}", "ERROR")
            return False, None, None
        except Exception as e:
            self._log(f"💥 Processing error for {doc.filename}: {e}", "ERROR")
            return False, None, None

    def _get_expected_output_path(self, doc: DocumentInfo) -> Path:
        """获取预期的输出文件路径"""
        input_filename = Path(doc.path).stem
        return self.chunks_dir / f"{input_filename}_processed.md"

    def _extract_output_file_from_result(self, stdout: str, doc: DocumentInfo) -> Optional[str]:
        """从granite_docling的输出中提取生成的文件路径"""
        # 查找 "RESULT_FILE:" 行
        for line in stdout.split('\n'):
            if 'RESULT_FILE:' in line:
                return line.split('RESULT_FILE:')[1].strip()

        # 回退方案：检查预期位置
        expected = self._get_expected_output_path(doc)
        if expected.exists():
            return str(expected)

        return None

    def _save_quality_report(self, report: QualityReport, doc: DocumentInfo):
        """保存质量报告到metadata目录"""
        try:
            # 构建元数据文件路径
            relative_path = Path(doc.path).relative_to(self.sources_path)
            metadata_file = self.metadata_dir / relative_path.with_suffix('.json')

            # 确保目录存在
            metadata_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存报告
            import json
            report_data = {
                'file_path': report.file_path,
                'total_score': report.total_score,
                'content_length': report.content_length,
                'line_count': report.line_count,
                'issues': report.issues,
                'strengths': report.strengths,
                'metadata': report.metadata,
                'processed_at': datetime.now().isoformat()
            }

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            self._log(f"💾 Saved quality report: {metadata_file.name}")

        except Exception as e:
            self._log(f"⚠️  Failed to save quality report for {doc.filename}: {e}", "WARNING")

    def generate_summary_report(self) -> str:
        """生成处理摘要报告"""
        return f"""
📊 Single-GPU Batch Processing Summary
{'='*60}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Processing Statistics:
  • Total PDF Documents Found: {self.stats['total_found']}
  • Successfully Processed: {self.stats['processed']}
  • Skipped (Already Processed): {self.stats['skipped']}
  • Failed: {self.stats['failed']}

📋 Quality Control:
  • Quality Checks Passed: {self.stats['quality_passed']}
  • Quality Checks Failed: {self.stats['quality_failed']}

📁 Output Locations:
  • Processed Documents: {self.chunks_dir}
  • Quality Reports: {self.metadata_dir}
  • Processing Logs: {self.log_file}

🎯 GPU Processing:
  • Sequential processing (no CUDA conflicts)
  • Automatic GPU memory cleanup per document
  • 2-second cooling intervals between documents

✅ Processing Complete!
"""


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Milo Bitcoin RAG - Single GPU Batch Document Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--scan-only',
        action='store_true',
        help='仅扫描文档，不进行处理'
    )

    parser.add_argument(
        '--category',
        choices=['authoritative', 'supplementary'],
        help='仅处理指定类别的文档'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新处理所有文档（忽略已存在的文件）'
    )

    parser.add_argument(
        '--rag-data',
        default='rag_data',
        help='RAG数据目录路径（默认: rag_data）'
    )

    args = parser.parse_args()

    try:
        print("🚀 Milo Bitcoin RAG - Single GPU Batch Processor")
        print("="*60)

        # 初始化处理器
        processor = SingleGPUBatchProcessor(args.rag_data)

        # 扫描文档
        documents = processor.scan_documents(args.category)

        if args.scan_only:
            print(f"\n📊 Scan Results: Found {len(documents)} PDF documents")
            return

        if not documents:
            print("⚠️  No PDF documents found to process.")
            return

        # 确认处理
        print(f"\n🎯 Ready to process {len(documents)} PDF documents")
        if not args.force:
            response = input("Continue? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Processing cancelled by user")
                return

        # 处理文档
        results = processor.process_documents(documents, force=args.force)

        # 生成并显示摘要报告
        summary = processor.generate_summary_report()
        print(summary)

        # 显示失败的文档
        failed_docs = [doc for doc, success, _ in results if not success]
        if failed_docs:
            print("❌ Failed Documents:")
            for doc in failed_docs:
                print(f"  • {doc.filename}")

        # 显示低质量文档
        low_quality_docs = [
            (doc, report) for doc, success, report in results
            if success and report and report.total_score < 60.0
        ]
        if low_quality_docs:
            print("⚠️  Low Quality Documents (< 60.0):")
            for doc, report in low_quality_docs:
                print(f"  • {doc.filename}: {report.total_score:.1f}/100")

    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()