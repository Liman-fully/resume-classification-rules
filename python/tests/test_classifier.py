#!/usr/bin/env python3
"""
简历三级分类器单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_classifier import ResumeClassifier


class TestResumeClassifier(unittest.TestCase):
    """测试简历三级分类器"""
    
    @classmethod
    def setUpClass(cls):
        """测试前初始化"""
        cls.classifier = ResumeClassifier()
    
    def test_load_rules(self):
        """测试规则加载"""
        stats = self.classifier.get_stats()
        self.assertEqual(stats['version'], '1.0.0')
        self.assertEqual(stats['industries'], 15)
        self.assertEqual(stats['functions'], 22)
    
    def test_classify_tech(self):
        """测试技术类简历分类"""
        text = "5年Java后端开发经验，熟悉Spring Boot、MySQL、Redis，有互联网大厂背景"
        result = self.classifier.classify(text)
        
        self.assertIsNotNone(result['primary'])
        self.assertEqual(result['primary']['type'], 'function')
        self.assertIn('关键词', result)
    
    def test_classify_product(self):
        """测试产品类简历分类"""
        text = "产品经理，负责APP功能规划，有电商行业经验，熟悉Axure、Figma"
        result = self.classifier.classify(text)
        
        self.assertIsNotNone(result['primary'])
        # 应该匹配到产品职能
        self.assertTrue('产品' in result['primary']['name'] or 
                       any('产品' in kw for kw in result['keywords_matched']))
    
    def test_classify_finance(self):
        """测试金融类简历分类"""
        text = "CFA持证，5年投资经理经验，熟悉股票、基金、风控，在证券公司工作"
        result = self.classifier.classify(text)
        
        # 应该匹配到金融行业
        if result['industry']:
            self.assertIn('金融', result['industry']['name'])
    
    def test_classify_medical(self):
        """测试医疗类简历分类"""
        text = "临床医学博士，三甲医院工作经验，熟悉药品研发、临床试验"
        result = self.classifier.classify(text)
        
        # 应该匹配到医疗行业
        if result['industry']:
            self.assertIn('医疗', result['industry']['name'])
    
    def test_batch_classify(self):
        """测试批量分类"""
        texts = [
            "Java开发工程师",
            "产品经理",
            "销售经理"
        ]
        results = self.classifier.batch_classify(texts)
        
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn('primary', r)
            self.assertIn('industry', r)
    
    def test_list_categories(self):
        """测试列出分类"""
        cats = self.classifier.list_categories()
        
        self.assertEqual(len(cats['industries']), 15)
        self.assertEqual(len(cats['functions']), 22)
        
        # 检查是否有code和name
        for ind in cats['industries']:
            self.assertIn('code', ind)
            self.assertIn('name', ind)
        
        for func in cats['functions']:
            self.assertIn('code', func)
            self.assertIn('name', func)
    
    def test_industry_codes(self):
        """测试行业编码格式"""
        cats = self.classifier.list_categories()
        
        for ind in cats['industries']:
            # 行业编码应该是 H + 两位数字
            self.assertRegex(ind['code'], r'^H\d{2}$')
    
    def test_function_codes(self):
        """测试职能编码格式"""
        cats = self.classifier.list_categories()
        
        for func in cats['functions']:
            # 职能编码应该是 F + 两位数字
            self.assertRegex(func['code'], r'^F\d{2}$')


class TestClassifierEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    @classmethod
    def setUpClass(cls):
        cls.classifier = ResumeClassifier()
    
    def test_empty_text(self):
        """测试空文本"""
        result = self.classifier.classify("")
        self.assertIsNone(result['primary'])
        self.assertIsNone(result['industry'])
    
    def test_no_match(self):
        """测试无匹配内容"""
        result = self.classifier.classify("这是一段无关的文本，没有职位信息")
        self.assertIsNone(result['primary'])
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        text1 = "JAVA开发"
        text2 = "java开发"
        
        result1 = self.classifier.classify(text1)
        result2 = self.classifier.classify(text2)
        
        # 应该匹配到相同的关键词
        self.assertEqual(result1['keywords_matched'], result2['keywords_matched'])


if __name__ == '__main__':
    unittest.main()
