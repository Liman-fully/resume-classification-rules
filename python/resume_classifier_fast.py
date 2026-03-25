#!/usr/bin/env python3
"""
简历三级分类器 Fast - 高性能版
使用 Aho-Corasick 算法实现 O(n) 单次扫描匹配
"""

import json
import math
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

# 尝试导入 pyahocorasick，如果没有则使用回退方案
try:
    import ahocorasick
    HAS_AHOCORASICK = True
except ImportError:
    HAS_AHOCORASICK = False
    print("⚠️  pyahocorasick 未安装，使用回退方案（性能较低）")
    print("   安装: pip install pyahocorasick")


class AhoCorasickMatcher:
    """Aho-Corasick 多模式匹配器"""
    
    def __init__(self):
        self.automaton = None
        self.pattern_info = {}
    
    def build(self, patterns: Dict[str, Dict]):
        """构建自动机"""
        if not HAS_AHOCORASICK:
            # 回退方案：简单字典
            self.patterns = patterns
            return
        
        self.automaton = ahocorasick.Automaton()
        
        for pattern, info in patterns.items():
            self.automaton.add_word(pattern, (pattern, info))
        
        self.automaton.make_automaton()
    
    def search(self, text: str) -> List[Tuple[str, Dict, int]]:
        """
        搜索所有匹配
        返回: [(matched_text, info, end_position), ...]
        """
        if not HAS_AHOCORASICK:
            # 回退方案：逐个匹配
            results = []
            text_lower = text.lower()
            for pattern, info in self.patterns.items():
                pos = text_lower.find(pattern)
                while pos != -1:
                    results.append((pattern, info, pos + len(pattern)))
                    pos = text_lower.find(pattern, pos + 1)
            return results
        
        results = []
        for end_index, (pattern, info) in self.automaton.iter(text.lower()):
            results.append((pattern, info, end_index))
        return results


class ResumeClassifierFast:
    """
    高性能简历三级分类器
    
    性能优化：
    1. Aho-Corasick O(n) 单次扫描
    2. 预计算 IDF
    3. 缓存分词结果
    """
    
    NEGATION_WORDS = {'非', '不是', '没有', '无', '未', '不再', '不属于', '不具备', '缺乏'}
    
    COOCCURRENCE_BONUS = {
        ('java', 'spring'): 0.15,
        ('java', '后端'): 0.15,
        ('python', 'django'): 0.15,
        ('python', 'flask'): 0.15,
        ('前端', 'vue'): 0.15,
        ('前端', 'react'): 0.15,
        ('算法', '机器学习'): 0.20,
        ('算法', '深度学习'): 0.20,
        ('产品', '经理'): 0.15,
        ('投资', '基金'): 0.15,
        ('cfa', '金融'): 0.20,
        ('高级', '经理'): 0.10,
        ('资深', '工程师'): 0.10,
        ('5年', '经验'): 0.10,
    }
    
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            current_dir = Path(__file__).parent
            rules_path = current_dir.parent / "rules" / "classification_rules.json"
        
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        self._build_matcher()
        self._calculate_idf()
    
    def _load_rules(self) -> Dict[str, Any]:
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_matcher(self):
        """构建 Aho-Corasick 匹配器"""
        patterns = {}
        
        # 添加行业关键词
        for ind in self.rules.get('industries', {}).get('data', []):
            for kw in ind.get('keywords', []):
                patterns[kw.lower()] = {
                    'code': ind['code'],
                    'name': ind['name'],
                    'type': 'industry'
                }
        
        # 添加职能关键词
        for func in self.rules.get('functions', {}).get('data', []):
            for kw in func.get('keywords', []):
                patterns[kw.lower()] = {
                    'code': func['code'],
                    'name': func['name'],
                    'type': 'function'
                }
        
        self.matcher = AhoCorasickMatcher()
        self.matcher.build(patterns)
        self.pattern_count = len(patterns)
    
    def _calculate_idf(self):
        """预计算 IDF"""
        self.idf = {}
        all_keywords = set()
        
        for func in self.rules.get('functions', {}).get('data', []):
            all_keywords.update(k.lower() for k in func.get('keywords', []))
        for ind in self.rules.get('industries', {}).get('data', []):
            all_keywords.update(k.lower() for k in ind.get('keywords', []))
        
        for kw in all_keywords:
            doc_count = 0
            for func in self.rules.get('functions', {}).get('data', []):
                if kw in [k.lower() for k in func.get('keywords', [])]:
                    doc_count += 1
            for ind in self.rules.get('industries', {}).get('data', []):
                if kw in [k.lower() for k in ind.get('keywords', [])]:
                    doc_count += 1
            
            self.idf[kw] = math.log((22 + 15) / (doc_count + 1) + 1)
    
    def classify(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """高性能分类"""
        start_time = time.time()
        text_lower = text.lower()
        
        # 1. Aho-Corasick 单次扫描匹配所有关键词
        matches_raw = self.matcher.search(text_lower)
        
        # 2. 去重并统计
        match_dict = {}
        for pattern, info, end_pos in matches_raw:
            if pattern not in match_dict:
                match_dict[pattern] = {
                    **info,
                    'keyword': pattern,
                    'count': 0,
                    'positions': []
                }
            match_dict[pattern]['count'] += 1
            match_dict[pattern]['positions'].append(end_pos - len(pattern))
        
        # 3. 计算置信度
        word_counts = Counter(text_lower.split())
        matches = []
        
        for pattern, data in match_dict.items():
            # 基础置信度
            base_conf = 0.5 + min(data['count'] * 0.1, 0.3)
            if any(pos < 200 for pos in data['positions']):
                base_conf += 0.2
            
            # TF-IDF
            tf = word_counts.get(pattern, 0) / len(word_counts) if word_counts else 0
            tfidf_bonus = min(tf * self.idf.get(pattern, 1.0) * 0.5, 0.2)
            
            # 否定词检测
            negation_penalty = 0
            for pos in data['positions']:
                context = text_lower[max(0, pos-20):pos]
                if any(n in context for n in self.NEGATION_WORDS):
                    negation_penalty = 0.3
                    break
            
            data['confidence'] = min(max(base_conf + tfidf_bonus - negation_penalty, 0.0), 1.0)
            matches.append(data)
        
        # 4. 共现加成
        matched_keywords = set(m['keyword'] for m in matches)
        for (kw1, kw2), weight in self.COOCCURRENCE_BONUS.items():
            if kw1 in matched_keywords and kw2 in matched_keywords:
                for m in matches:
                    if m['keyword'] in (kw1, kw2):
                        m['confidence'] = min(m['confidence'] + weight, 1.0)
        
        # 5. 排序并分离
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        function_matches = [m for m in matches if m['type'] == 'function']
        industry_matches = [m for m in matches if m['type'] == 'industry']
        
        elapsed = time.time() - start_time
        
        return {
            'primary': function_matches[0] if function_matches else None,
            'top_k': function_matches[:top_k],
            'industry': industry_matches[0] if industry_matches else None,
            'industries_top_k': industry_matches[:top_k],
            'keywords_matched': [m['keyword'] for m in matches],
            'total_matches': len(matches),
            'elapsed_ms': round(elapsed * 1000, 2)
        }
    
    def batch_classify(self, texts: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """批量分类"""
        return [self.classify(t, top_k) for t in texts]
    
    def benchmark(self, texts: List[str], iterations: int = 100) -> Dict:
        """性能测试"""
        import time
        
        # 预热
        for _ in range(10):
            for text in texts:
                self.classify(text)
        
        # 正式测试
        start = time.time()
        for _ in range(iterations):
            for text in texts:
                self.classify(text)
        elapsed = time.time() - start
        
        total_calls = iterations * len(texts)
        avg_time = (elapsed / total_calls) * 1000
        
        return {
            'total_calls': total_calls,
            'total_time_ms': round(elapsed * 1000, 2),
            'avg_time_ms': round(avg_time, 3),
            'throughput_per_sec': round(total_calls / elapsed, 1)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='简历三级分类器 Fast（高性能版）')
    parser.add_argument('--text', '-t', help='要分类的文本')
    parser.add_argument('--file', '-f', help='要分类的文件')
    parser.add_argument('--benchmark', '-b', action='store_true', help='性能测试')
    parser.add_argument('--top-k', '-k', type=int, default=3, help='返回前k个结果')
    
    args = parser.parse_args()
    
    print("🚀 初始化高性能分类器...")
    if HAS_AHOCORASICK:
        print("   ✓ 使用 Aho-Corasick 算法 (O(n) 单次扫描)")
    else:
        print("   ⚠️ 使用回退方案 (O(n×m) 多次扫描)")
    
    classifier = ResumeClassifierFast()
    print(f"   ✓ 加载 {classifier.pattern_count} 个关键词模式\n")
    
    if args.benchmark:
        print("⏱️  运行性能测试...")
        test_texts = [
            "5年Java后端开发经验，熟悉Spring Boot、MySQL、Redis",
            "产品经理，负责电商APP功能规划，有快消品行业经验",
            "CFA持证，投资经理，熟悉股票、基金、风控",
            "HRBP，互联网大厂背景，擅长招聘和人才发展"
        ]
        result = classifier.benchmark(test_texts, iterations=100)
        print(f"\n📊 性能测试结果:")
        print(f"   总调用次数: {result['total_calls']}")
        print(f"   总耗时: {result['total_time_ms']} ms")
        print(f"   平均单次: {result['avg_time_ms']} ms")
        print(f"   吞吐量: {result['throughput_per_sec']} 次/秒")
    
    elif args.text or args.file:
        text = args.text
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        
        result = classifier.classify(text, top_k=args.top_k)
        
        print("\n📝 分类结果")
        print("=" * 50)
        
        if result['primary']:
            p = result['primary']
            print(f"\n🎯 主分类: {p['name']} ({p['code']})")
            print(f"   置信度: {p['confidence']:.2f}")
        
        if result['top_k'] and len(result['top_k']) > 1:
            print(f"\n📊 Top-{args.top_k}:")
            for i, m in enumerate(result['top_k'][1:], 2):
                print(f"   {i}. {m['name']} ({m['code']}) - {m['confidence']:.2f}")
        
        if result['industry']:
            ind = result['industry']
            print(f"\n🏢 行业: {ind['name']} ({ind['code']}) - {ind['confidence']:.2f}")
        
        print(f"\n⚡ 处理耗时: {result['elapsed_ms']} ms")
        print(f"🔑 匹配关键词: {result['total_matches']} 个")
    
    else:
        print("🎯 简历三级分类器 Fast（高性能版）")
        print("\n示例:")
        print("  python resume_classifier_fast.py --benchmark")
        print("  python resume_classifier_fast.py --text 'Java开发' -k 3")


if __name__ == '__main__':
    main()
