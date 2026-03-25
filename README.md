# 简历职能分类规则 Skills 包

[![Version](https://img.shields.io/badge/version-3.0.0-blue)](https://github.com/Liman-fully/resume-classification-rules)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**可复用的中文简历三级分类体系** —— 行业 × 职能 × 岗位

---

## 目录结构

```
resume-classification-rules/
├── rules/
│   ├── classification_rules.json         # ⭐ 核心规则（三级分类）
│   └── classification_rules.schema.json  # JSON Schema（编辑器智能提示）
├── python/
│   ├── resume_classifier.py              # Python 分类器实现
│   └── tests/test_classifier.py          # 单元测试
├── examples/basic_usage.py               # 快速上手示例
├── docs/RULES_GUIDE.md                   # 完整规则说明文档
└── README.md
```

---

## 三级分类体系

| 层级 | 数量 | 说明 | 编码 |
|-----|------|------|------|
| **一级（行业）** | 15个 | AI/互联网、金融、医疗、汽车等 | H01-H15 |
| **二级（职能）** | 22个 | 技术、产品、运营、销售等 | F01-F22 |
| **三级（岗位）** | 1100+ | 具体职位名称 | 内嵌在职能中 |

### 15个一级行业

| 编码 | 行业名称 | 子行业数 |
|-----|---------|---------|
| H01 | AI/互联网/IT | 19 |
| H02 | 电子/通信/半导体 | 4 |
| H03 | 房地产/建筑 | 8 |
| H04 | 金融 | 9 |
| H05 | 消费品 | 11 |
| H06 | 医疗健康 | 10 |
| H07 | 汽车 | 8 |
| H08 | 机械/制造 | 9 |
| H09 | 教育培训/科研 | 7 |
| H10 | 专业服务 | 6 |
| H11 | 广告/传媒/文化/体育 | 7 |
| H12 | 生活服务 | 8 |
| H13 | 交通/物流/贸易/零售 | 8 |
| H14 | 能源/化工/环保 | 7 |
| H15 | 政府/非营利/其他 | 5 |

### 22个二级职能

| 编码 | 职能名称 |
|-----|---------|
| F01 | IT互联网技术 |
| F02 | 电子/通信/半导体 |
| F03 | 销售/客服 |
| F04 | 运营 |
| F05 | 人力/行政/财务/法务 |
| F06 | 高级管理 |
| F07 | 市场/公关/广告/会展 |
| F08 | 生产/制造/研发 |
| F09 | 制药/医疗器械/医疗护理 |
| F10 | 汽车 |
| F11 | 房地产/建筑/物业 |
| F12 | 金融 |
| F13 | 产品 |
| F14 | 设计 |
| F15 | 教育/培训 |
| F16 | 供应链/物流/采购/贸易 |
| F17 | 生活服务/零售 |
| F18 | 影视/媒体 |
| F19 | 咨询/翻译 |
| F20 | 能源/环保/农业 |
| F21 | 项目管理 |
| F22 | 公务员/其他 |

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Liman-fully/resume-classification-rules.git
cd resume-classification-rules
```

### 2. 运行示例

```bash
cd python
python resume_classifier.py --stats      # 查看规则统计
python resume_classifier.py --list       # 列出所有分类
python resume_classifier.py --text "Java开发工程师"  # 单条分类
```

### 3. Python API 使用

```python
from resume_classifier import ResumeClassifier

# 初始化
classifier = ResumeClassifier()

# 单条分类
result = classifier.classify("5年Java后端开发经验，熟悉Spring Boot")
print(result['primary']['name'])   # IT互联网技术
print(result['industry']['name'])  # AI/互联网/IT

# 批量分类
texts = ["Java开发", "产品经理", "销售经理"]
results = classifier.batch_classify(texts)
```

---

## 数据来源

- **猎聘** (liepin) - 2026-03-16 实时抓取
- **BOSS直聘** (boss) - 2026-03-16 实时抓取

---

## 设计原则

1. **行业与职能正交**：同一职能可以在多个行业出现（如HR存在于所有行业）
2. **分类器主逻辑**：先职能（决定文件夹归属），行业作为附加标签（用于筛选/搜索）
3. **数据来源权威**：基于猎聘官方15个一级行业、22个二级职能分类
4. **跨平台通用**：JSON格式，支持 Python/Node.js/Java/Go 等任意语言

---

## 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 3.0.0 | 2026-03-25 | 升级为三级分类体系（行业×职能×岗位） |
| 2.0.0 | 2026-03-18 | 二级分类（职能+叠加标签） |
| 1.0.0 | 2026-03-12 | 初始版本 |

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 贡献

欢迎提交 Issue 和 PR！详见 [docs/RULES_GUIDE.md](docs/RULES_GUIDE.md) 贡献指南。
