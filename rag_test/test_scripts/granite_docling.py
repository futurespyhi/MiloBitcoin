#!/usr/bin/env python3
"""
Granite Docling: 标准文档处理工具
只使用Docling标准处理管道，接受命令行PDF文件输入
使用方法: uv run granite_docling.py <pdf_file_path>
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path


def process_pdf_standard(pdf_path):
    """使用标准处理管道处理PDF文件"""
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

        # 生成输出文件名
        input_filename = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("../test_outputs/markdown_results")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{input_filename}_standard_{timestamp}.md"

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
                    'transaction', 'network', 'protocol', 'algorithm', 'hash']
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
        description='Granite Docling: 标准文档处理工具',
        epilog='Example: uv run granite_docling.py ../test_inputs/lightning_network.pdf'
    )
    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')

    args = parser.parse_args()

    # 打印工具信息
    print("🚀 Granite Docling - Standard PDF Processing Tool")
    print("=" * 55)
    print(f"📁 Input file: {args.pdf_file}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 处理PDF文件
    success, result = process_pdf_standard(args.pdf_file)

    if success:
        print("\n" + "=" * 55)
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

        return 0
    else:
        print("\n" + "=" * 55)
        print("❌ Processing failed!")
        print("💡 Please check the PDF file path and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())