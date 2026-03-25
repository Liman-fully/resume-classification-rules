#!/usr/bin/env python3
"""
优化效果对比测试
对比 V1 基础版 vs V2 增强版 vs Fast 高性能版
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from resume_classifier import ResumeClassifier
from resume_classifier_v2 import ResumeClassifierV2
from resume_classifier_fast import ResumeClassifierFast
import time


# 测试用例：各种类型简历
test_cases = [
    {
        "name": "技术类-Java",
        "text": """
        张三 | 5年Java后端开发经验
        技能：Java, Spring Boot, Spring Cloud, MySQL, Redis, Kafka, Docker, Kubernetes
        公司：某互联网大厂（电商行业）
        职位：高级Java开发工程师
        教育：本科，计算机科学与技术
        """
    },
    {
        "name": "技术类-Python+AI",
        "text": """
        李四 | Python开发工程师 | 3年经验
        熟悉Django、Flask框架，有机器学习项目经验
        使用过TensorFlow、PyTorch，了解深度学习算法
        不是Java开发，主要做Python和AI相关
        """
    },
    {
        "name": "产品类",
        "text": """
        王五 | 产品经理 | 4年经验
        负责电商APP功能规划和用户增长
        熟悉Axure、Figma、Sketch
        有快消品行业背景，擅长数据分析和用户研究
        """
    },
    {
        "name": "金融类",
        "text": """
        赵六 | CFA持证 | 投资经理
        5年证券行业经验，熟悉股票、基金、债券投资
        曾在基金公司担任研究员，擅长风控和合规
        管理资产规模超过10亿
        """
    },
    {
        "name": "复合背景",
        "text": """
        孙七 | 技术转产品 | 6年经验
        3年Java开发经验，熟悉后端技术栈
        3年产品经理经验，负责B端SaaS产品
        懂技术又懂业务，擅长技术产品规划
        """
    },
    {
        "name": "否定词测试",
        "text": """
        周八 | 应届毕业生
        专业是计算机科学，但没有开发经验
        非技术人员，主要从事行政和HR工作
        不具备编程能力，想做人力资源方向
        """
    }
]


def test_v1():
    """测试 V1 基础版"""
    print("\n" + "="*60)
    print("📦 V1 基础版")
    print("="*60)
    
    clf = ResumeClassifier()
    
    for case in test_cases:
        start = time.time()
        result = clf.classify(case['text'])
        elapsed = (time.time() - start) * 1000
        
        primary = result['primary']['name'] if result['primary'] else '未分类'
        industry = result['industry']['name'] if result['industry'] else '未知'
        
        print(f"\n{case['name']}:")
        print(f"  主分类: {primary}")
        print(f"  行业: {industry}")
        print(f"  耗时: {elapsed:.2f}ms")


def test_v2():
    """测试 V2 增强版"""
    print("\n" + "="*60)
    print("🚀 V2 增强版 (TF-IDF + 共现 + 否定词)")
    print("="*60)
    
    clf = ResumeClassifierV2()
    
    for case in test_cases:
        start = time.time()
        result = clf.classify(case['text'], top_k=3)
        elapsed = (time.time() - start) * 1000
        
        primary = result['primary']
        
        print(f"\n{case['name']}:")
        if primary:
            print(f"  主分类: {primary['name']} (置信度: {primary['confidence']:.2f})")
        
        if len(result['top_k']) > 1:
            top_str = ', '.join([f"{m['name']}({m['confidence']:.2f})" for m in result['top_k']])
            print(f"  Top-3: {top_str}")
        
        if result['industry']:
            print(f"  行业: {result['industry']['name']}")
        
        if result['negation_detected']:
            print(f"  ⚠️ 否定词: {', '.join(result['negation_detected'])}")
        
        print(f"  耗时: {elapsed:.2f}ms")


def test_fast():
    """测试 Fast 高性能版"""
    print("\n" + "="*60)
    print("⚡ Fast 高性能版")
    print("="*60)
    
    clf = ResumeClassifierFast()
    
    for case in test_cases:
        result = clf.classify(case['text'], top_k=3)
        
        primary = result['primary']
        
        print(f"\n{case['name']}:")
        if primary:
            print(f"  主分类: {primary['name']} (置信度: {primary['confidence']:.2f})")
        
        if result['industry']:
            print(f"  行业: {result['industry']['name']}")
        
        print(f"  匹配关键词: {result['total_matches']}个")
        print(f"  耗时: {result['elapsed_ms']}ms")


def benchmark():
    """性能对比"""
    print("\n" + "="*60)
    print("⏱️ 性能对比 (1000次分类)")
    print("="*60)
    
    test_text = test_cases[0]['text']
    
    # V1
    clf1 = ResumeClassifier()
    start = time.time()
    for _ in range(1000):
        clf1.classify(test_text)
    v1_time = (time.time() - start) * 1000
    
    # V2
    clf2 = ResumeClassifierV2()
    start = time.time()
    for _ in range(1000):
        clf2.classify(test_text)
    v2_time = (time.time() - start) * 1000
    
    # Fast
    clf3 = ResumeClassifierFast()
    start = time.time()
    for _ in range(1000):
        clf3.classify(test_text)
    fast_time = (time.time() - start) * 1000
    
    print(f"\nV1 基础版:   {v1_time:.2f}ms ({v1_time/1000:.3f}ms/次)")
    print(f"V2 增强版:   {v2_time:.2f}ms ({v2_time/1000:.3f}ms/次)")
    print(f"Fast 高性能: {fast_time:.2f}ms ({fast_time/1000:.3f}ms/次)")
    
    speedup = v1_time / fast_time
    print(f"\n🚀 Fast 比 V1 快 {speedup:.1f}x")


if __name__ == '__main__':
    print("🧪 简历分类器优化效果对比测试")
    
    test_v1()
    test_v2()
    test_fast()
    benchmark()
    
    print("\n" + "="*60)
    print("✅ 测试完成!")
    print("="*60)
