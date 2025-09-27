#!/usr/bin/env python3
"""
Phase 1: Granite Docling Basic Functionality Verification
测试环境验证和基础功能检查
"""

import sys
import time
import traceback
from datetime import datetime

def test_imports():
    """测试基础导入和依赖"""
    print("🔍 Testing imports...")

    try:
        # 基础导入测试
        import torch
        print(f"✅ PyTorch: {torch.__version__}")

        # CUDA检查
        cuda_available = torch.cuda.is_available()
        print(f"✅ CUDA available: {cuda_available}")
        if cuda_available:
            print(f"   GPU device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")

        # Docling导入测试
        import docling
        print(f"✅ Docling imported successfully")

        # 检查Docling版本
        try:
            print(f"   Docling version: {docling.__version__}")
        except AttributeError:
            print("   Docling version: Unknown")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_granite_model_loading():
    """测试Granite Docling模型加载"""
    print("\n🧠 Testing Granite Docling model loading...")

    try:
        from docling.vlm.granite_docling import GraniteDocling
        print("✅ GraniteDocling class imported")

        # 尝试初始化模型
        print("   Initializing Granite model...")
        model = GraniteDocling()
        print("✅ Granite Docling model initialized successfully")

        # 检查模型设备
        device = next(model.model.parameters()).device
        print(f"   Model device: {device}")

        return True, model

    except ImportError as e:
        print(f"❌ GraniteDocling import error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return False, None

def test_docling_converter():
    """测试Docling转换器"""
    print("\n⚙️ Testing Docling converter...")

    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import ConversionInput
        print("✅ DocumentConverter imported")

        # 初始化转换器
        converter = DocumentConverter()
        print("✅ DocumentConverter initialized")

        return True, converter

    except ImportError as e:
        print(f"❌ DocumentConverter import error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ DocumentConverter initialization error: {e}")
        return False, None

def test_gpu_memory():
    """测试GPU内存状态"""
    print("\n🔧 Testing GPU memory...")

    try:
        import torch
        if torch.cuda.is_available():
            # 获取GPU内存信息
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            cached = torch.cuda.memory_reserved(0) / (1024**3)

            print(f"✅ GPU Memory Status:")
            print(f"   Total: {total_memory:.1f} GB")
            print(f"   Allocated: {allocated:.1f} GB")
            print(f"   Cached: {cached:.1f} GB")
            print(f"   Available: {total_memory - cached:.1f} GB")

            return True
        else:
            print("❌ CUDA not available")
            return False

    except Exception as e:
        print(f"❌ GPU memory check error: {e}")
        return False

def generate_phase1_report():
    """生成Phase 1测试报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print(f"\n📊 Phase 1 Basic Verification Report")
    print(f"=" * 50)
    print(f"Test time: {timestamp}")
    print(f"Environment: milo_rag conda environment")

    # 执行所有测试
    results = {}

    # Test 1: 基础导入
    print(f"\n{'='*20} TEST 1: IMPORTS {'='*20}")
    results['imports'] = test_imports()

    # Test 2: 模型加载
    print(f"\n{'='*20} TEST 2: MODEL LOADING {'='*20}")
    model_success, model = test_granite_model_loading()
    results['model_loading'] = model_success

    # Test 3: 转换器
    print(f"\n{'='*20} TEST 3: CONVERTER {'='*20}")
    converter_success, converter = test_docling_converter()
    results['converter'] = converter_success

    # Test 4: GPU内存
    print(f"\n{'='*20} TEST 4: GPU MEMORY {'='*20}")
    results['gpu_memory'] = test_gpu_memory()

    # 总结报告
    print(f"\n{'='*20} SUMMARY {'='*20}")
    passed = sum(results.values())
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready for Phase 2.")
        return True, model, converter
    else:
        print("⚠️  Some tests failed. Check environment setup.")
        return False, None, None

if __name__ == "__main__":
    print("🚀 Starting Phase 1: Basic Functionality Verification")
    print("=" * 60)

    success, model, converter = generate_phase1_report()

    # 保存测试结果
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    status = "SUCCESS" if success else "FAILED"

    # 简单的结果记录
    with open(f"../test_reports/phase1_basic_verification_{timestamp}_{status}.txt", "w") as f:
        f.write(f"Phase 1 Basic Verification: {status}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Environment: milo_rag\n")

    sys.exit(0 if success else 1)