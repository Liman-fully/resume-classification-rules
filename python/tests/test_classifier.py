#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_classifier.py — 分类规则单元测试

覆盖：主分类命中、叠加标签、兜底分类、大小写不敏感等场景。
运行：
  pytest tests/test_classifier.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest
from resume_classifier import ResumeClassifier, ClassifyResult

RULES_PATH = Path(__file__).parent.parent / "rules" / "classification_rules.json"


@pytest.fixture(scope="module")
def clf():
    return ResumeClassifier(rules_path=RULES_PATH)


# ── 主分类测试 ────────────────────────────────────────────────

class TestMainCategories:
    def test_product_manager(self, clf):
        r = clf.classify("产品经理-张三-本科-5年.pdf")
        assert r.category == "01_产品经理"
        assert r.matched_keyword == "产品经理"

    def test_ai_product_manager(self, clf):
        r = clf.classify("AI产品经理-李四-清华.pdf")
        assert r.category == "01_产品经理"
        assert r.matched_keyword == "AI产品经理"

    def test_frontend_engineer(self, clf):
        r = clf.classify("前端开发工程师-王五-3年.pdf")
        assert r.category == "02_技术研发"

    def test_backend_engineer(self, clf):
        r = clf.classify("Java后端工程师-陈六-上海.pdf")
        assert r.category == "02_技术研发"

    def test_algorithm_engineer(self, clf):
        r = clf.classify("算法工程师-NLP方向-博士.pdf")
        assert r.category == "03_AI与算法"

    def test_llm_engineer(self, clf):
        r = clf.classify("大模型工程师-AIGC-2年.pdf")
        assert r.category == "03_AI与算法"

    def test_hardware_engineer(self, clf):
        r = clf.classify("硬件工程师-芯片研发-5年.pdf")
        assert r.category == "04_硬件与电子"

    def test_data_analyst(self, clf):
        r = clf.classify("数据分析师-BI-互联网.pdf")
        assert r.category == "05_数据分析"

    def test_ui_designer(self, clf):
        r = clf.classify("UI设计师-交互设计-4年.pdf")
        assert r.category == "06_设计创意"

    def test_operations(self, clf):
        r = clf.classify("用户运营经理-私域运营.pdf")
        assert r.category == "07_运营"

    def test_new_media(self, clf):
        r = clf.classify("新媒体运营-抖音小红书-2年.pdf")
        assert r.category == "08_新媒体与内容"

    def test_marketing(self, clf):
        r = clf.classify("市场经理-品牌推广-上海.pdf")
        assert r.category == "09_市场与品牌"

    def test_sales(self, clf):
        r = clf.classify("销售经理-大客户销售-5年.pdf")
        assert r.category == "10_销售与BD")

    def test_hr(self, clf):
        r = clf.classify("HR经理-HRBP-组织发展.pdf")
        assert r.category == "12_人事HR"

    def test_finance(self, clf):
        r = clf.classify("财务总监-FP&A-上市公司.pdf")
        assert r.category == "15_财务"

    def test_legal(self, clf):
        r = clf.classify("法务经理-合同管理-知识产权.pdf")
        assert r.category == "16_法务合规"

    def test_fallback(self, clf):
        r = clf.classify("候选人简历_20240301.pdf")
        assert r.category == "99_待人工归类"
        assert r.is_fallback is True
        assert r.matched_keyword is None


# ── 叠加标签测试 ──────────────────────────────────────────────

class TestOverlayTags:
    def test_overseas_tag(self, clf):
        r = clf.classify("产品经理-Harvard毕业-留学回国.pdf")
        assert r.category == "01_产品经理"
        assert "TAG_OVERSEA" in r.tags

    def test_phd_tag(self, clf):
        r = clf.classify("算法工程师-PhD-NLP.pdf")
        assert r.category == "03_AI与算法"
        assert "TAG_PHD" in r.tags

    def test_exec_tag(self, clf):
        r = clf.classify("CTO-技术VP-15年.pdf")
        assert "TAG_EXEC" in r.tags

    def test_multiple_tags(self, clf):
        """留学生 + 高管 可同时命中"""
        r = clf.classify("CFO-Harvard-海归-上市公司.pdf")
        assert "TAG_OVERSEA" in r.tags
        assert "TAG_EXEC" in r.tags

    def test_tag_with_fallback(self, clf):
        """叠加标签可在兜底分类下同时存在"""
        r = clf.classify("Harvard留学生-无具体职位.pdf")
        assert "TAG_OVERSEA" in r.tags
        assert r.category == "99_待人工归类"


# ── 大小写不敏感测试 ──────────────────────────────────────────

class TestCaseInsensitive:
    def test_english_keyword_upper(self, clf):
        r = clf.classify("NLP Engineer-3yrs.pdf")
        assert r.category == "03_AI与算法"

    def test_english_keyword_lower(self, clf):
        r = clf.classify("nlp engineer resume.pdf")
        assert r.category == "03_AI与算法"

    def test_phd_variations(self, clf):
        r1 = clf.classify("PhD-深度学习-腾讯.pdf")
        r2 = clf.classify("phd-deep-learning.pdf")
        assert "TAG_PHD" in r1.tags
        assert "TAG_PHD" in r2.tags


# ── 批量分类测试 ──────────────────────────────────────────────

class TestBatchClassify:
    def test_batch_returns_correct_length(self, clf):
        files = [
            "产品经理-A.pdf",
            "算法工程师-B.pdf",
            "设计师-C.pdf",
            "未知候选人.pdf",
        ]
        results = clf.classify_batch(files)
        assert len(results) == 4

    def test_summary_counts(self, clf):
        files = ["产品经理-A.pdf", "产品总监-B.pdf", "算法工程师-C.pdf"]
        results = clf.classify_batch(files)
        stats = clf.summary(results)
        assert stats.get("01_产品经理", 0) == 2
        assert stats.get("03_AI与算法", 0) == 1
