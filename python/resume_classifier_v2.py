#!/usr/bin/env python3
"""
简历三级分类器 V2 - 增强版
改进：TF-IDF权重、关键词共现、否定词检测、多标签输出
"""

import json
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter


class ResumeClassifierV2:
    """
    增强版简历三级分类器
    
    改进点：
    1. TF-IDF 权重计算
    2. 关键词共现检测
    3. 否定词过滤
    4. 多标签输出（top-k）
    5. 置信度校准
    """
    
    # 否定词表
    NEGATION_WORDS = {'非', '不是', '没有', '无', '未', '不再', '不属于', '不具备', '缺乏'}
    
    # 关键词共现权重加成
    COOCCURRENCE_BONUS = {
        # 技术类共现
        ('java', 'spring'): 0.15,
        ('java', '后端'): 0.15,
        ('python', 'django'): 0.15,
        ('python', 'flask'): 0.15,
        ('前端', 'vue'): 0.15,
        ('前端', 'react'): 0.15,
        ('算法', '机器学习'): 0.20,
        ('算法', '深度学习'): 0.20,
        ('数据', '分析'): 0.10,
        ('产品', '经理'): 0.15,
        # 金融类共现
        ('投资', '基金'): 0.15,
        ('投资', '股票'): 0.15,
        ('cfa', '金融'): 0.20,
        ('风控', '合规'): 0.15,
        # 医疗类共现
        ('临床', '医生'): 0.15,
        ('医药', '代表'): 0.15,
        # 通用共现
        ('高级', '经理'): 0.10,
        ('资深', '工程师'): 0.10,
        ('5年', '经验'): 0.10,
        ('3年', '经验'): 0.10,
    }
    
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            current_dir = Path(__file__).parent
            rules_path = current_dir.parent / "rules" / "classification_rules.json"
        
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        self._build_index()
        self._calculate_idf()
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载分类规则"""
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_index(self):
        """构建关键词索引"""
        self.industry_index = {}
        self.function_index = {}
        self.all_keywords = set()
        
        # 行业索引
        for ind in self.rules.get('industries', {}).get('data', []):
            for kw in ind.get('keywords', []):
                kw_lower = kw.lower()
                self.industry_index[kw_lower] = {
                    'code': ind['code'],
                    'name': ind['name'],
                    'type': 'industry'
                }
                self.all_keywords.add(kw_lower)
        
        # 职能索引
        for func in self.rules.get('functions', {}).get('data', []):
            for kw in func.get('keywords', []):
                kw_lower = kw.lower()
                self.function_index[kw_lower] = {
                    'code': func['code'],
                    'name': func['name'],
                    'type': 'function'
                }
                self.all_keywords.add(kw_lower)
    
    def _calculate_idf(self):
        """计算IDF（逆文档频率）"""
        # 简化版：假设每个关键词在规则中出现次数的倒数
        self.idf = {}
        for kw in self.all_keywords:
            # 计算包含该关键词的职能/行业数量
            doc_count = 0
            for func in self.rules.get('functions', {}).get('data', []):
                if kw in [k.lower() for k in func.get('keywords', [])]:
                    doc_count += 1
            for ind in self.rules.get('industries', {}).get('data', []):
                if kw in [k.lower() for k in ind.get('keywords', [])]:
                    doc_count += 1
            
            # IDF = log(总文档数 / 包含该词的文档数 + 1)
            self.idf[kw] = math.log((22 + 15) / (doc_count + 1) + 1)
    
    def classify(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        对简历文本进行分类（增强版）
        
        Args:
            text: 简历文本
            top_k: 返回前k个分类结果
            
        Returns:
            {
                'primary': {...},  # 最佳匹配
                'top_k': [...],    # top-k 分类
                'industry': {...}, # 行业
                'keywords_matched': [...],
                'negation_detected': [...]  # 检测到的否定词
            }
        """
        text_lower = text.lower()
        
        # 1. 检测否定词
        negations = self._detect_negations(text_lower)
        
        # 2. 匹配所有关键词
        matches = self._match_keywords(text_lower)
        
        # 3. 计算共现加成
        cooccurrence_bonus = self._calc_cooccurrence(text_lower, [m['keyword'] for m in matches])
        
        # 4. 计算TF-IDF权重
        word_counts = Counter(text_lower.split())
        for m in matches:
            kw = m['keyword']
            tf = word_counts.get(kw, 0) / len(word_counts) if word_counts else 0
            idf = self.idf.get(kw, 1.0)
            m['tfidf'] = tf * idf
        
        # 5. 计算综合置信度
        for m in matches:
            base_conf = self._calc_base_confidence(text_lower, m['keyword'])
            tfidf_bonus = min(m.get('tfidf', 0) * 0.5, 0.2)  # TF-IDF加成上限0.2
            cooc_bonus = cooccurrence_bonus.get(m['keyword'], 0)
            
            # 如果有否定词，降低置信度
            negation_penalty = 0.3 if any(n in text_lower[max(0, text_lower.find(m['keyword'])-20):text_lower.find(m['keyword'])] for n in self.NEGATION_WORDS) else 0
            
            m['confidence'] = min(base_conf + tfidf_bonus + cooc_bonus - negation_penalty, 1.0)
            m['confidence'] = max(m['confidence'], 0.0)  # 不低于0
        
        # 6. 按置信度排序
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 7. 分离职能和行业
        function_matches = [m for m in matches if m['type'] == 'function']
        industry_matches = [m for m in matches if m['type'] == 'industry']
        
        # 8. 组装结果
        result = {
            'primary': function_matches[0] if function_matches else None,
            'top_k': function_matches[:top_k],
            'industry': industry_matches[0] if industry_matches else None,
            'industries_top_k': industry_matches[:top_k],
            'keywords_matched': [m['keyword'] for m in matches],
            'negation_detected': negations,
            'total_matches': len(matches)
        }
        
        return result
    
    def _detect_negations(self, text: str) -> List[str]:
        """检测文本中的否定词"""
        found = []
        for neg in self.NEGATION_WORDS:
            if neg in text:
                found.append(neg)
        return found
    
    def _match_keywords(self, text: str) -> List[Dict]:
        """匹配所有关键词"""
        matches = []
        
        # 匹配行业
        for kw, info in self.industry_index.items():
            if kw in text:
                matches.append({
                    **info,
                    'keyword': kw,
                    'match_type': 'exact'
                })
        
        # 匹配职能
        for kw, info in self.function_index.items():
            if kw in text:
                matches.append({
                    **info,
                    'keyword': kw,
                    'match_type': 'exact'
                })
        
        return matches
    
    def _calc_cooccurrence(self, text: str, matched_keywords: List[str]) -> Dict[str, float]:
        """计算关键词共现加成"""
        bonus = {}
        matched_set = set(matched_keywords)
        
        for (kw1, kw2), weight in self.COOCCURRENCE_BONUS.items():
            if kw1 in matched_set and kw2 in matched_set:
                # 两个关键词都命中，给它们都加权重
                bonus[kw1] = bonus.get(kw1, 0) + weight
                bonus[kw2] = bonus.get(kw2, 0) + weight
        
        return bonus
    
    def _calc_base_confidence(self, text: str, keyword: str) -> float:
        """计算基础置信度"""
        count = text.count(keyword)
        base = 0.5
        freq_bonus = min(count * 0.1, 0.3)
        position_bonus = 0.2 if keyword in text[:200] else 0
        return min(base + freq_bonus + position_bonus, 1.0)
    
    def batch_classify(self, texts: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """批量分类"""
        return [self.classify(t, top_k) for t in texts]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取规则统计"""
        meta = self.rules.get('_meta', {})
        stats = meta.get('stats', {})
        return {
            'version': meta.get('version'),
            'created': meta.get('created'),
            'industries': stats.get('level1_industries'),
            'functions': stats.get('level2_functions'),
            'positions': stats.get('level3_positions'),
            'total_keywords': stats.get('total_keywords'),
            'keywords_per_function_avg': stats.get('keywords_per_function_avg'),
            'industry_keywords': len(self.industry_index),
            'function_keywords': len(self.function_index)
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简历三级分类器 V2（增强版）')
    parser.add_argument('--text', '-t', help='要分类的文本')
    parser.add_argument('--file', '-f', help='要分类的文件')
    parser.add_argument('--stats', '-s', action='store_true', help='显示规则统计')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有分类')
    parser.add_argument('--top-k', '-k', type=int, default=3, help='返回前k个结果')
    
    args = parser.parse_args()
    
    classifier = ResumeClassifierV2()
    
    if args.stats:
        stats = classifier.get_stats()
        print("📊 规则统计 (V2增强版)")
        print(f"  版本: {stats['version']}")
        print(f"  创建时间: {stats['created']}")
        print(f"  一级行业: {stats['industries']} 个")
        print(f"  二级职能: {stats['functions']} 个")
        print(f"  三级岗位: {stats['positions']} 个")
        print(f"  总关键词数: {stats.get('total_keywords', 'N/A')} 个")
        print(f"  平均每职能: {stats.get('keywords_per_function_avg', 'N/A')} 个")
        print(f"  行业关键词: {stats['industry_keywords']} 个")
        print(f"  职能关键词: {stats['function_keywords']} 个")
    
    elif args.list:
        # ... 省略，与v1相同
        pass
    
    elif args.text or args.file:
        text = args.text
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        
        result = classifier.classify(text, top_k=args.top_k)
        
        print("\n📝 分类结果 (V2增强版)")
        print("=" * 50)
        
        if result['primary']:
            p = result['primary']
            print(f"\n🎯 主分类: {p['name']} ({p['code']})")
            print(f"   置信度: {p['confidence']:.2f}")
            print(f"   关键词: {p['keyword']}")
        
        if result['top_k'] and len(result['top_k']) > 1:
            print(f"\n📊 Top-{args.top_k} 分类:")
            for i, m in enumerate(result['top_k'][1:], 2):
                print(f"   {i}. {m['name']} ({m['code']}) - {m['confidence']:.2f}")
        
        if result['industry']:
            ind = result['industry']
            print(f"\n🏢 行业: {ind['name']} ({ind['code']})")
            print(f"     置信度: {ind['confidence']:.2f}")
        
        if result['negation_detected']:
            print(f"\n⚠️  检测到否定词: {', '.join(result['negation_detected'])}")
        
        print(f"\n🔑 匹配关键词 ({result['total_matches']}个):")
        print(f"   {', '.join(result['keywords_matched'][:10])}")
    
    else:
        print("🎯 简历三级分类器 V2（增强版）")
        print("\n改进点:")
        print("  ✓ TF-IDF 权重计算")
        print("  ✓ 关键词共现检测")
        print("  ✓ 否定词过滤")
        print("  ✓ 多标签输出 (top-k)")
        print("\n示例用法:")
        print("  python resume_classifier_v2.py --stats")
        print("  python resume_classifier_v2.py --text 'Java开发' -k 3")


if __name__ == '__main__':
    main()
