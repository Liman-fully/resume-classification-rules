# 简历分类规则 Skills 包

> **一套可复用的中文简历职能分类规则**，适用于招聘工具开发、简历管理系统、AI 简历解析后处理流程。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](rules/classification_rules.json)

---

## 这是什么

这是从 [resume-dedup](https://github.com/Liman-fully/resume-dedup) 项目中提取的核心分类规则，**单独打包为独立 Skills 包**，方便：

- 🔌 直接集成到任何简历处理工具
- 🤖 作为 AI Agent 的知识库或工具函数
- 🧩 社区开发者贡献和扩展规则
- 📚 学习如何设计可维护的规则引擎

---

## 快速上手

### 方式一：Python（推荐）

```bash
git clone https://github.com/Liman-fully/resume-classification-rules.git
cd resume-classification-rules
python examples/basic_usage.py
```

```python
from python.resume_classifier import ResumeClassifier

clf = ResumeClassifier()
result = clf.classify("产品经理-张三-本科-5年-北京.pdf")

print(result.category)       # "01_产品经理"
print(result.category_name)  # "产品经理"
print(result.matched_keyword)# "产品经理"
print(result.tags)           # [] (无叠加标签)
```

### 方式二：命令行

```bash
# 单文件
python python/resume_classifier.py "算法工程师-PhD-NLP.pdf"

# 批量
python python/resume_classifier.py *.pdf

# JSON 输出
python python/resume_classifier.py --json "产品经理-MIT-海归.pdf"
```

### 方式三：直接使用 JSON 规则

规则文件位于 `rules/classification_rules.json`，可被任何语言读取：

```javascript
// JavaScript / Node.js
const rules = require('./rules/classification_rules.json');

function classify(filename) {
  const name = filename.toLowerCase();
  for (const cat of rules.categories) {
    for (const kw of cat.keywords) {
      if (name.includes(kw.toLowerCase())) {
        return { category: cat.id, name: cat.name, keyword: kw };
      }
    }
  }
  return { category: rules.config.fallback_category };
}
```

---

## 规则体系

### 两层架构

```
第一层 — 叠加标签（可同时命中多个，不互斥）
  ★留学生/海归 (TAG_OVERSEA)  → 海外院校/海归关键词
  ★博士/博士后 (TAG_PHD)      → PhD / 博士后等
  ★高级管理    (TAG_EXEC)     → CEO/CTO/VP 等 C 级

第二层 — 主分类（互斥，命中即停）
  01 产品经理    02 技术研发    03 AI与算法    04 硬件与电子
  05 数据分析    06 设计创意    07 运营        08 新媒体与内容
  09 市场与品牌  10 销售与BD    11 客户服务    12 人事HR
  13 项目管理    14 行政        15 财务        16 法务合规
  17 采购与供应链 18 培训教育   19 金融        20 医疗健康
  21 其他职能    99 待人工归类（兜底）
```

### 分类效果示例

| 文件名 | 主分类 | 叠加标签 |
|--------|--------|---------|
| `产品经理-张三-本科-北京.pdf` | 01_产品经理 | — |
| `算法工程师-PhD-NLP.pdf` | 03_AI与算法 | ★博士/博士后 |
| `CFO-Harvard-海归.pdf` | 15_财务 | ★留学生/海归 + ★高级管理 |
| `前端开发-Vue-React-3年.pdf` | 02_技术研发 | — |
| `候选人简历_未知.pdf` | 99_待人工归类 | — |

---

## 目录结构

```
resume-classification-rules/
├── rules/
│   ├── classification_rules.json         # 规则主文件（核心）
│   └── classification_rules.schema.json  # JSON Schema（编辑器提示）
├── python/
│   ├── resume_classifier.py              # Python 分类器实现
│   └── tests/
│       └── test_classifier.py            # 单元测试
├── examples/
│   └── basic_usage.py                    # 快速上手示例
├── docs/
│   └── RULES_GUIDE.md                    # 完整规则说明文档
└── README.md
```

---

## 规则说明

详细的规则设计理念、分类边界说明、扩展方法和常见问题，请阅读：

📖 [**docs/RULES_GUIDE.md**](docs/RULES_GUIDE.md)

---

## 运行测试

```bash
cd resume-classification-rules
pytest python/tests/ -v
```

---

## 贡献规则

有新的职位词需要覆盖？欢迎提 PR！

1. 编辑 `rules/classification_rules.json`，在对应分类的 `keywords` 中追加
2. 在 `python/tests/test_classifier.py` 添加测试用例
3. `pytest` 全绿后提交 PR

详细流程见 [docs/RULES_GUIDE.md#贡献指南](docs/RULES_GUIDE.md#10-贡献指南)。

---

## 与主项目的关系

本包是从以下项目中提取的独立模块：

| 项目 | 说明 |
|-----|-----|
| [resume-dedup](https://github.com/Liman-fully/resume-dedup) | 简历去重工具（使用本规则进行归类） |
| [resume-toolkit](https://github.com/Liman-fully/resume-toolkit) | 简历整理工具套件 |

本规则包可单独使用，也可作为上述工具的规则来源。

---

## License

MIT © [Liman](https://github.com/Liman-fully)
