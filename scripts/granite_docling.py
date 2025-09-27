#!/usr/bin/env python3
"""
Granite Docling Production: 生产环境标准文档处理工具
使用Docling标准处理管道，输出到RAG生产目录
适用于批量处理和RAG系统构建

使用方法:
    python scripts/granite_docling.py <pdf_file_path> [--output-dir <output_directory>]

示例:
    python scripts/granite_docling.py rag_data/rag_sources/authoritative/whitepaper/bitcoin.pdf
    python scripts/granite_docling.py file.pdf --output-dir rag_data/rag_sources/processed/chunks
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path


def process_pdf_standard(pdf_path, output_dir=None):
    """
    使用标准处理管道处理PDF文件

    Args:
        pdf_path: PDF文件路径
        output_dir: 可选的输出目录，默认为 rag_data/rag_sources/processed/chunks

    Returns:
        (成功标志, 结果字典)
    """
    print(f"🔄 Processing with standard pipeline: {pdf_path}")

    try:
        from docling.document_converter import DocumentConverter

        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False, None

        print(f"✅ Found PDF file: {pdf_path}")

        # 初始化标准DocumentConverter
        print("   Initializing DocumentConverter...")
        converter = DocumentConverter()  # 使用默认标准设置

        print("   Starting document conversion...")
        start_time = time.time()

        # 执行转换
        result = converter.convert(source=pdf_path)
        doc = result.document

        elapsed = time.time() - start_time
        print(f"✅ Conversion successful ({elapsed:.1f}s)")

        # 导出到Markdown
        print("   Exporting to Markdown...")
        markdown_content = doc.export_to_markdown()

        # 确定输出目录和文件名
        if output_dir is None:
            # 默认输出到RAG生产目录
            output_dir = Path("rag_data/rag_sources/processed/chunks")
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成输出文件名（保持简洁，适合生产环境）
        input_filename = Path(pdf_path).stem
        output_file = output_dir / f"{input_filename}_processed.md"

        # 如果文件已存在，添加时间戳避免覆盖
        if output_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"{input_filename}_processed_{timestamp}.md"

        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"   💾 Saved: {output_file}")
        print(f"   📊 Content length: {len(markdown_content)} characters")

        # 分析内容质量
        lines = markdown_content.split('\n')
        headers = [line for line in lines if line.startswith('#')]

        print(f"   📑 Total lines: {len(lines)}")
        print(f"   🏷️  Headers found: {len(headers)}")

        # 检查常见技术关键词
        key_terms = ['Bitcoin', 'blockchain', 'cryptocurrency', 'peer-to-peer', 'cryptographic',
                    'transaction', 'network', 'protocol', 'algorithm', 'hash', 'lightning',
                    'payment', 'channel', 'node', 'consensus', 'mining', 'wallet', 'signature']
        found_terms = [term for term in key_terms if term.lower() in markdown_content.lower()]
        print(f"   🔍 Key terms found: {len(found_terms)}/{len(key_terms)} - {found_terms[:5]}")

        return True, {
            'content': markdown_content,
            'output_file': str(output_file),
            'processing_time': elapsed,
            'content_length': len(markdown_content),
            'lines_count': len(lines),
            'headers_count': len(headers),
            'key_terms': found_terms
        }

    except Exception as e:
        print(f"❌ Standard processing failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False, None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Granite Docling Production: 生产环境标准文档处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument(
        '--output-dir',
        help='输出目录（默认: rag_data/rag_sources/processed/chunks）'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    # 打印工具信息
    print("🚀 Granite Docling Production - RAG Document Processor")
    print("=" * 60)
    print(f"📁 Input file: {args.pdf_file}")
    print(f"📂 Output dir: {args.output_dir or 'rag_data/rag_sources/processed/chunks'}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 处理PDF文件
    success, result = process_pdf_standard(args.pdf_file, args.output_dir)

    if success:
        print("\n" + "=" * 60)
        print("🎉 Processing completed successfully!")
        print(f"   📄 Output file: {result['output_file']}")
        print(f"   ⏱️  Processing time: {result['processing_time']:.1f} seconds")
        print(f"   📊 Content stats:")
        print(f"      - Length: {result['content_length']:,} characters")
        print(f"      - Lines: {result['lines_count']:,}")
        print(f"      - Headers: {result['headers_count']}")
        print(f"      - Key terms: {len(result['key_terms'])}")

        if args.verbose:
            print(f"\n🔍 Found key terms: {result['key_terms']}")

        # 输出适合批量处理脚本解析的结果
        print(f"\n📤 RESULT_FILE: {result['output_file']}")

        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Processing failed!")
        print("💡 Please check the PDF file path and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())