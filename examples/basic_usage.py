#!/usr/bin/env python3
"""
简历三级分类器 - 基础用法示例
"""

import sys
from pathlib import Path

# 添加 python 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from resume_classifier import ResumeClassifier


def main():
    # 初始化分类器
    print("🚀 初始化简历三级分类器...\n")
    classifier = ResumeClassifier()
    
    # 显示规则统计
    stats = classifier.get_stats()
    print("📊 规则统计")
    print(f"  版本: {stats['version']}")
    print(f"  创建时间: {stats['created']}")
    print(f"  一级行业: {stats['industries']} 个")
    print(f"  二级职能: {stats['functions']} 个")
    print(f"  三级岗位: {stats['positions']} 个")
    print(f"  行业关键词: {stats['industry_keywords']} 个")
    print(f"  职能关键词: {stats['function_keywords']} 个\n")
    
    # 列出所有分类
    cats = classifier.list_categories()
    print("🏢 一级行业（15个）")
    for ind in cats['industries'][:5]:
        print(f"  {ind['code']} {ind['name']}")
    print("  ...")
    
    print("\n👔 二级职能（22个）")
    for func in cats['functions'][:5]:
        print(f"  {func['code']} {func['name']}")
    print("  ...\n")
    
    # 示例1：技术类简历
    print("=" * 50)
    print("示例1：技术类简历")
    print("=" * 50)
    text1 = """
    张三 | 5年Java后端开发经验
    技能：Java, Spring Boot, MySQL, Redis, Kafka, Docker
    公司：某互联网大厂（AI/互联网/IT行业）
    职位：高级Java开发工程师
    """
    result1 = classifier.classify(text1)
    print(f"\n文本: {text1[:50]}...")
    if result1['primary']:
        print(f"主分类: {result1['primary']['name']} ({result1['primary']['code']})")
    if result1['industry']:
        print(f"行业: {result1['industry']['name']} ({result1['industry']['code']})")
    print(f"匹配关键词: {', '.join(result1['keywords_matched'][:5])}")
    
    # 示例2：产品类简历
    print("\n" + "=" * 50)
    print("示例2：产品类简历")
    print("=" * 50)
    text2 = """
    李四 | 产品经理 | 3年经验
    负责电商APP功能规划，熟悉Axure、Figma
    有快消品行业背景，擅长用户增长
    """
    result2 = classifier.classify(text2)
    print(f"\n文本: {text2[:50]}...")
    if result2['primary']:
        print(f"主分类: {result2['primary']['name']} ({result2['primary']['code']})")
    if result2['industry']:
        print(f"行业: {result2['industry']['name']} ({result2['industry']['code']})")
    print(f"匹配关键词: {', '.join(result2['keywords_matched'][:5])}")
    
    # 示例3：金融类简历
    print("\n" + "=" * 50)
    print("示例3：金融类简历")
    print("=" * 50)
    text3 = """
    王五 | CFA持证 | 投资经理
    5年证券行业经验，熟悉股票、基金、风控
    曾在基金公司担任研究员
    """
    result3 = classifier.classify(text3)
    print(f"\n文本: {text3[:50]}...")
    if result3['primary']:
        print(f"主分类: {result3['primary']['name']} ({result3['primary']['code']})")
    if result3['industry']:
        print(f"行业: {result3['industry']['name']} ({result3['industry']['code']})")
    print(f"匹配关键词: {', '.join(result3['keywords_matched'][:5])}")
    
    # 示例4：批量分类
    print("\n" + "=" * 50)
    print("示例4：批量分类")
    print("=" * 50)
    texts = [
        "Java开发工程师，熟悉Spring Boot",
        "产品经理，负责APP规划",
        "销售经理，有快消品经验",
        "HRBP，互联网大厂背景"
    ]
    results = classifier.batch_classify(texts)
    
    for i, (text, result) in enumerate(zip(texts, results), 1):
        primary = result['primary']['name'] if result['primary'] else '未分类'
        industry = result['industry']['name'] if result['industry'] else '未知'
        print(f"{i}. {text[:20]}... -> 职能: {primary}, 行业: {industry}")
    
    print("\n✅ 示例运行完成！")


if __name__ == '__main__':
    main()
