#!/usr/bin/env python3
"""
Phase 2: Bitcoin白皮书CLI处理测试
使用Granite Docling CLI命令进行处理
"""

import subprocess
import os
import time
from datetime import datetime

def test_bitcoin_cli_processing():
    """使用CLI命令处理Bitcoin白皮书"""
    print("📄 Processing Bitcoin whitepaper with CLI...")

    pdf_path = "../test_inputs/bitcoin.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return False

    print(f"✅ Found Bitcoin PDF: {pdf_path}")

    # 创建输出目录
    os.makedirs("../test_outputs/docling_results", exist_ok=True)
    os.makedirs("../test_outputs/markdown_results", exist_ok=True)

    results = {}

    # Test 1: 标准Markdown输出
    print("\n🔄 Test 1: Converting to Markdown with Granite...")
    try:
        cmd = [
            "docling",
            "--to", "md",
            "--pipeline", "vlm",
            "--vlm-model", "granite_docling",
            pdf_path
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Markdown conversion successful ({elapsed:.1f}s)")

            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_file = f"../test_outputs/markdown_results/bitcoin_{timestamp}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)

            print(f"   💾 Saved to: {md_file}")
            print(f"   📊 Output length: {len(result.stdout)} characters")
            results['markdown'] = {'success': True, 'length': len(result.stdout), 'file': md_file}
        else:
            print(f"❌ Markdown conversion failed")
            print(f"   Error: {result.stderr}")
            results['markdown'] = {'success': False, 'error': result.stderr}

    except subprocess.TimeoutExpired:
        print("❌ Markdown conversion timed out")
        results['markdown'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Markdown conversion error: {e}")
        results['markdown'] = {'success': False, 'error': str(e)}

    # Test 2: HTML + Layout可视化
    print("\n🔄 Test 2: Converting to HTML with layout...")
    try:
        cmd = [
            "docling",
            "--to", "html_split_page",
            "--show-layout",
            "--pipeline", "vlm",
            "--vlm-model", "granite_docling",
            pdf_path
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ HTML conversion successful ({elapsed:.1f}s)")

            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = f"../test_outputs/docling_results/bitcoin_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)

            print(f"   💾 Saved to: {html_file}")
            print(f"   📊 Output length: {len(result.stdout)} characters")
            results['html_layout'] = {'success': True, 'length': len(result.stdout), 'file': html_file}
        else:
            print(f"❌ HTML conversion failed")
            print(f"   Error: {result.stderr}")
            results['html_layout'] = {'success': False, 'error': result.stderr}

    except subprocess.TimeoutExpired:
        print("❌ HTML conversion timed out")
        results['html_layout'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ HTML conversion error: {e}")
        results['html_layout'] = {'success': False, 'error': str(e)}

    # Test 3: 双格式输出 (HTML + MD)
    print("\n🔄 Test 3: Converting to both HTML and Markdown...")
    try:
        cmd = [
            "docling",
            "--to", "html",
            "--to", "md",
            "--pipeline", "vlm",
            "--vlm-model", "granite_docling",
            pdf_path
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Dual format conversion successful ({elapsed:.1f}s)")

            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dual_file = f"../test_outputs/docling_results/bitcoin_dual_{timestamp}.txt"
            with open(dual_file, 'w', encoding='utf-8') as f:
                f.write("=== DUAL FORMAT OUTPUT ===\n")
                f.write(result.stdout)

            print(f"   💾 Saved to: {dual_file}")
            print(f"   📊 Output length: {len(result.stdout)} characters")
            results['dual_format'] = {'success': True, 'length': len(result.stdout), 'file': dual_file}
        else:
            print(f"❌ Dual format conversion failed")
            print(f"   Error: {result.stderr}")
            results['dual_format'] = {'success': False, 'error': result.stderr}

    except subprocess.TimeoutExpired:
        print("❌ Dual format conversion timed out")
        results['dual_format'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Dual format conversion error: {e}")
        results['dual_format'] = {'success': False, 'error': str(e)}

    return results

def analyze_cli_results(results):
    """分析CLI结果"""
    print("\n🔍 Analyzing CLI conversion results...")

    analysis = {}

    for test_name, result in results.items():
        if result['success']:
            print(f"✅ {test_name}: Success")
            if 'file' in result:
                # 检查生成的文件内容
                try:
                    with open(result['file'], 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查关键内容
                    key_terms = ['Bitcoin', 'Satoshi Nakamoto', 'blockchain', 'peer-to-peer']
                    found_terms = [term for term in key_terms if term in content]

                    print(f"   📊 Content length: {len(content)} chars")
                    print(f"   🔍 Key terms found: {found_terms}")

                    analysis[test_name] = {
                        'length': len(content),
                        'key_terms': found_terms,
                        'key_term_count': len(found_terms)
                    }

                except Exception as e:
                    print(f"   ⚠️ Could not analyze file: {e}")
        else:
            print(f"❌ {test_name}: Failed - {result.get('error', 'Unknown error')}")

    return analysis

def generate_phase2_cli_report():
    """生成Phase 2 CLI测试报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print(f"\n📊 Phase 2 Bitcoin CLI Processing Report")
    print(f"=" * 55)
    print(f"Test time: {timestamp}")
    print(f"Method: Docling CLI with Granite VLM")
    print(f"Target: Bitcoin whitepaper")

    # 执行CLI测试
    print(f"\n{'='*15} GRANITE CLI PROCESSING {'='*15}")
    cli_results = test_bitcoin_cli_processing()

    # 分析结果
    analysis = analyze_cli_results(cli_results)

    # 生成总结
    print(f"\n{'='*20} SUMMARY {'='*20}")

    successful_tests = sum(1 for r in cli_results.values() if r['success'])
    total_tests = len(cli_results)

    print(f"Successful conversions: {successful_tests}/{total_tests}")

    for test_name, result in cli_results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{test_name:15}: {status}")

    # 质量评估
    if successful_tests > 0:
        print(f"\n📈 Quality Assessment:")
        for test_name, info in analysis.items():
            print(f"  {test_name}: {info['key_term_count']}/4 key terms found")

    success = successful_tests >= 2  # 至少2个测试成功

    if success:
        print("🎉 Bitcoin CLI processing successful!")
        print("💡 Ready for Lightning Network processing")
    else:
        print("⚠️ Bitcoin CLI processing needs attention")

    return success, cli_results

if __name__ == "__main__":
    print("🚀 Starting Phase 2: Bitcoin CLI Processing with Granite")
    print("=" * 65)

    success, results = generate_phase2_cli_report()

    # 保存报告
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    status = "SUCCESS" if success else "FAILED"

    report_file = f"../test_reports/phase2_bitcoin_cli_{timestamp}_{status}.txt"
    try:
        with open(report_file, "w") as f:
            f.write(f"Phase 2 Bitcoin CLI Processing: {status}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Method: Docling CLI + Granite VLM\n")
            f.write(f"Results: {len([r for r in results.values() if r['success']])}/{len(results)} successful\n")
        print(f"\n📝 Report saved to: {report_file}")
    except Exception as e:
        print(f"⚠️ Could not save report: {e}")

    print(f"\n🎯 Next: Run this script to test Granite Docling CLI!")