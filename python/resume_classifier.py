#!/usr/bin/env python3
"""
简历三级分类器 - 支持行业×职能×岗位分类
基于 classification_rules.json 的通用招聘分类规则体系
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class ResumeClassifier:
    """
    简历三级分类器
    
    分类层级：
    - 一级（行业）：15大类（AI/互联网、金融、医疗等）
    - 二级（职能）：22类（技术、产品、运营、销售等）
    - 三级（岗位）：1100+具体职位
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        初始化分类器
        
        Args:
            rules_path: 规则文件路径，默认为同级目录 rules/classification_rules.json
        """
        if rules_path is None:
            current_dir = Path(__file__).parent
            rules_path = current_dir.parent / "rules" / "classification_rules.json"
        
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        self._build_index()
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载分类规则"""
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_index(self):
        """构建关键词索引，加速匹配"""
        # 行业索引
        self.industry_index = {}
        for ind in self.rules.get('industries', {}).get('data', []):
            for kw in ind.get('keywords', []):
                self.industry_index[kw.lower()] = {
                    'code': ind['code'],
                    'name': ind['name'],
                    'type': 'industry'
                }
        
        # 职能索引
        self.function_index = {}
        for func in self.rules.get('functions', {}).get('data', []):
            for kw in func.get('keywords', []):
                self.function_index[kw.lower()] = {
                    'code': func['code'],
                    'name': func['name'],
                    'type': 'function'
                }
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        对简历文本进行分类
        
        Args:
            text: 简历文本内容
            
        Returns:
            {
                'primary': {'type': 'function', 'code': 'F01', 'name': 'IT互联网技术', 'confidence': 0.85},
                'industry': {'type': 'industry', 'code': 'H01', 'name': 'AI/互联网/IT', 'confidence': 0.72},
                'keywords_matched': ['java', '后端', '开发'],
                'all_matches': [...]
            }
        """
        text_lower = text.lower()
        matches = []
        
        # 匹配行业关键词
        for kw, info in self.industry_index.items():
            if kw in text_lower:
                matches.append({
                    **info,
                    'keyword': kw,
                    'confidence': self._calc_confidence(text_lower, kw)
                })
        
        # 匹配职能关键词
        for kw, info in self.function_index.items():
            if kw in text_lower:
                matches.append({
                    **info,
                    'keyword': kw,
                    'confidence': self._calc_confidence(text_lower, kw)
                })
        
        # 按置信度排序
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 确定主分类（职能优先）
        function_matches = [m for m in matches if m['type'] == 'function']
        industry_matches = [m for m in matches if m['type'] == 'industry']
        
        result = {
            'primary': function_matches[0] if function_matches else None,
            'industry': industry_matches[0] if industry_matches else None,
            'keywords_matched': [m['keyword'] for m in matches],
            'all_matches': matches[:10]  # 只保留前10个
        }
        
        return result
    
    def _calc_confidence(self, text: str, keyword: str) -> float:
        """计算匹配置信度（简化版：基于词频和位置）"""
        count = text.count(keyword)
        # 基础分 + 词频加分（上限0.3）
        base = 0.5
        freq_bonus = min(count * 0.1, 0.3)
        # 标题位置加分（简化处理：如果在开头100字符内）
        position_bonus = 0.2 if keyword in text[:200] else 0
        return min(base + freq_bonus + position_bonus, 1.0)
    
    def batch_classify(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量分类"""
        return [self.classify(t) for t in texts]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        meta = self.rules.get('_meta', {})
        return {
            'version': meta.get('version'),
            'created': meta.get('created'),
            'industries': meta.get('stats', {}).get('level1_industries'),
            'functions': meta.get('stats', {}).get('level2_functions'),
            'positions': meta.get('stats', {}).get('level3_positions'),
            'industry_keywords': len(self.industry_index),
            'function_keywords': len(self.function_index)
        }
    
    def list_categories(self) -> Dict[str, List[Dict]]:
        """列出所有分类"""
        return {
            'industries': [
                {'code': i['code'], 'name': i['name']}
                for i in self.rules.get('industries', {}).get('data', [])
            ],
            'functions': [
                {'code': f['code'], 'name': f['name']}
                for f in self.rules.get('functions', {}).get('data', [])
            ]
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简历三级分类器')
    parser.add_argument('--text', '-t', help='要分类的文本')
    parser.add_argument('--file', '-f', help='要分类的文件')
    parser.add_argument('--stats', '-s', action='store_true', help='显示规则统计')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有分类')
    
    args = parser.parse_args()
    
    classifier = ResumeClassifier()
    
    if args.stats:
        stats = classifier.get_stats()
        print("📊 规则统计")
        print(f"  版本: {stats['version']}")
        print(f"  创建时间: {stats['created']}")
        print(f"  一级行业: {stats['industries']} 个")
        print(f"  二级职能: {stats['functions']} 个")
        print(f"  三级岗位: {stats['positions']} 个")
        print(f"  行业关键词: {stats['industry_keywords']} 个")
        print(f"  职能关键词: {stats['function_keywords']} 个")
    
    elif args.list:
        cats = classifier.list_categories()
        print("\n🏢 一级行业（15个）")
        for ind in cats['industries']:
            print(f"  {ind['code']} {ind['name']}")
        
        print("\n👔 二级职能（22个）")
        for func in cats['functions']:
            print(f"  {func['code']} {func['name']}")
    
    elif args.text or args.file:
        text = args.text
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        
        result = classifier.classify(text)
        
        print("\n📝 分类结果")
        if result['primary']:
            p = result['primary']
            print(f"  主分类: {p['name']} ({p['code']}) - 置信度: {p['confidence']:.2f}")
        
        if result['industry']:
            ind = result['industry']
            print(f"  行业: {ind['name']} ({ind['code']}) - 置信度: {ind['confidence']:.2f}")
        
        if result['keywords_matched']:
            print(f"\n🔑 匹配关键词: {', '.join(result['keywords_matched'][:10])}")
    
    else:
        # 演示模式
        print("🎯 简历三级分类器 v1.0")
        print("\n示例用法:")
        print("  python resume_classifier.py --stats")
        print("  python resume_classifier.py --list")
        print("  python resume_classifier.py --text '5年Java后端开发经验，熟悉Spring Boot'")
        print("  python resume_classifier.py --file resume.txt")


if __name__ == '__main__':
    main()
