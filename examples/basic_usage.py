#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
examples/basic_usage.py — 快速上手示例
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from resume_classifier import ResumeClassifier

# ── 初始化（自动读取 rules/classification_rules.json）──────────
clf = ResumeClassifier()

print("=" * 60)
print("示例 1：单文件分类")
print("=" * 60)
samples = [
    "产品经理-张三-本科-5年-北京.pdf",
    "算法工程师-NLP方向-PhD-腾讯.pdf",
    "CFO-Harvard-海归-上市公司.pdf",
    "小红书运营-内容创作-2年.pdf",
    "设计师-候选人.pdf",  # 触发兜底
]
for fname in samples:
    r = clf.classify(fname)
    tag_str = f" | 标签: {', '.join(r.tag_names)}" if r.tag_names else ""
    kw_str = f"  触发词: 【{r.matched_keyword}】" if r.matched_keyword else "  （兜底分类）"
    print(f"\n📄 {fname}")
    print(f"   → {r.category_name}{tag_str}")
    print(f"  {kw_str}")

print()
print("=" * 60)
print("示例 2：批量分类 + 统计")
print("=" * 60)
filenames = [
    "前端开发工程师-Vue-React-3年.pdf",
    "后端工程师-Java-微服务.pdf",
    "产品总监-SaaS产品-8年.pdf",
    "UI设计师-移动端-B端.pdf",
    "数据分析师-SQL-Python.pdf",
    "市场经理-品牌营销-5年.pdf",
    "销售总监-大客户-10年.pdf",
    "HRBP-组织发展-500强.pdf",
    "项目经理-PMP-敏捷.pdf",
    "财务经理-FP&A-CPA.pdf",
    "法务专员-合同管理.pdf",
    "候选人简历_未知职位.pdf",  # 兜底
]

results = clf.classify_batch(filenames)
print(f"\n共处理 {len(results)} 份简历\n")
print("分类统计：")
for cat, count in clf.summary(results).items():
    bar = "█" * count
    print(f"  {cat:20s} {bar} ({count})")

print()
print("=" * 60)
print("示例 3：筛选留学生候选人")
print("=" * 60)
mixed = [
    "产品经理-MIT毕业-留学回国.pdf",
    "算法工程师-Stanford-PhD.pdf",
    "市场经理-国内背景.pdf",
    "销售VP-Cambridge-海归.pdf",
]
results = clf.classify_batch(mixed)
overseas = [r for r in results if "TAG_OVERSEA" in r.tags]
print(f"\n共 {len(mixed)} 份，海归候选人 {len(overseas)} 份：")
for r in overseas:
    print(f"  ✓ {r.filename} → {r.category_name}")
