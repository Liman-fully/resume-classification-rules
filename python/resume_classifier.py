#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume_classifier.py — 简历分类规则引擎

基于 classification_rules.json 实现的轻量级分类器。
支持：
  - 主分类（互斥，first_match）
  - 横切叠加标签（TAG_OVERSEA / TAG_PHD / TAG_EXEC，可同时命中多个）
  - dry_run 预览模式
  - 自定义规则路径（环境变量 / 参数传入）

使用方式：
  from resume_classifier import ResumeClassifier
  clf = ResumeClassifier()
  result = clf.classify("产品经理-张三-本科-北京.pdf")
  print(result.category)   # "01_产品经理"
  print(result.tags)       # []
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── 默认规则文件路径 ──────────────────────────────────────────
_DEFAULT_RULES_PATH = Path(__file__).parent.parent / "rules" / "classification_rules.json"


# ── 数据类 ────────────────────────────────────────────────────

@dataclass
class ClassifyResult:
    """单条简历分类结果。"""
    filename: str
    category: str                    # 主分类 ID，如 "01_产品经理"
    category_name: str               # 主分类名称
    matched_keyword: Optional[str]   # 触发主分类的关键词，None 表示兜底
    tags: list[str] = field(default_factory=list)   # 命中的叠加标签 ID 列表
    tag_names: list[str] = field(default_factory=list)

    @property
    def is_fallback(self) -> bool:
        return self.matched_keyword is None

    def __str__(self) -> str:
        tag_str = f"  标签：{', '.join(self.tag_names)}" if self.tag_names else ""
        kw_str = f"  触发词：{self.matched_keyword}" if self.matched_keyword else "  （兜底）"
        return f"{self.filename}\n  → {self.category_name}{kw_str}{tag_str}"


# ── 分类器 ────────────────────────────────────────────────────

class ResumeClassifier:
    """
    基于 JSON 规则的简历分类器。

    Args:
        rules_path: 规则文件路径，默认读取包目录下的 classification_rules.json
        rules_dict: 直接传入规则字典（优先级高于 rules_path）
    """

    def __init__(
        self,
        rules_path: str | Path | None = None,
        rules_dict: dict | None = None,
    ) -> None:
        if rules_dict is not None:
            self._rules = rules_dict
        else:
            path = Path(rules_path) if rules_path else Path(
                os.environ.get("RESUME_RULES_PATH", str(_DEFAULT_RULES_PATH))
            )
            with open(path, encoding="utf-8") as f:
                self._rules = json.load(f)

        self._config = self._rules.get("config", {})
        self._case_insensitive = self._config.get("match_mode", "case_insensitive") == "case_insensitive"
        self._fallback = self._config.get("fallback_category", "99_待人工归类")
        self._categories = self._rules.get("categories", [])
        self._overlay_tags = self._rules.get("overlay_tags", [])

    # ── 公开 API ─────────────────────────────────────────────

    def classify(self, filename: str) -> ClassifyResult:
        """
        对单个文件名进行分类。

        Args:
            filename: 简历文件名（含扩展名），如 "产品经理-张三.pdf"

        Returns:
            ClassifyResult
        """
        name = filename.lower() if self._case_insensitive else filename

        # 1. 匹配叠加标签（不互斥，全部命中）
        matched_tags, matched_tag_names = self._match_overlay_tags(name)

        # 2. 匹配主分类（命中即停）
        category_id, category_name, keyword = self._match_category(name)

        return ClassifyResult(
            filename=filename,
            category=category_id,
            category_name=category_name,
            matched_keyword=keyword,
            tags=matched_tags,
            tag_names=matched_tag_names,
        )

    def classify_batch(self, filenames: list[str]) -> list[ClassifyResult]:
        """批量分类，返回结果列表。"""
        return [self.classify(f) for f in filenames]

    def get_categories(self) -> list[dict]:
        """返回所有主分类定义。"""
        return self._categories

    def get_overlay_tags(self) -> list[dict]:
        """返回所有叠加标签定义。"""
        return self._overlay_tags

    def summary(self, results: list[ClassifyResult]) -> dict[str, int]:
        """统计各分类数量。"""
        stats: dict[str, int] = {}
        for r in results:
            stats[r.category] = stats.get(r.category, 0) + 1
        return dict(sorted(stats.items()))

    # ── 内部方法 ─────────────────────────────────────────────

    def _match_overlay_tags(self, name_lower: str) -> tuple[list[str], list[str]]:
        ids, names = [], []
        for tag in self._overlay_tags:
            for kw in tag.get("keywords", []):
                if (kw.lower() if self._case_insensitive else kw) in name_lower:
                    ids.append(tag["id"])
                    names.append(tag["name"])
                    break  # 每个 tag 只加一次
        return ids, names

    def _match_category(self, name_lower: str) -> tuple[str, str, Optional[str]]:
        # 按 order 排序后依次匹配
        for cat in sorted(self._categories, key=lambda c: c.get("order", 999)):
            for kw in cat.get("keywords", []):
                if (kw.lower() if self._case_insensitive else kw) in name_lower:
                    return cat["id"], cat["name"], kw
        # 兜底
        fallback_name = next(
            (c["name"] for c in self._categories if c["id"] == self._fallback),
            self._fallback,
        )
        return self._fallback, fallback_name, None


# ── 命令行入口 ────────────────────────────────────────────────

def main() -> None:
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="简历分类工具 —— 根据文件名关键词自动归类",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python resume_classifier.py "产品经理-张三-本科-北京.pdf"
  python resume_classifier.py *.pdf
  python resume_classifier.py --rules /path/to/rules.json *.pdf
        """,
    )
    parser.add_argument("filenames", nargs="+", help="简历文件名列表")
    parser.add_argument("--rules", help="自定义规则文件路径")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args()

    clf = ResumeClassifier(rules_path=args.rules)
    results = clf.classify_batch(args.filenames)

    if args.json:
        output = [
            {
                "filename": r.filename,
                "category": r.category,
                "category_name": r.category_name,
                "matched_keyword": r.matched_keyword,
                "tags": r.tags,
                "tag_names": r.tag_names,
                "is_fallback": r.is_fallback,
            }
            for r in results
        ]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(r)
        print()
        print("── 统计 ──")
        for cat, count in clf.summary(results).items():
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
