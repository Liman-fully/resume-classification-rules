# 简历三级分类规则说明文档

**版本**: 3.0.0  
**更新日期**: 2026-03-25  
**适用场景**: 中文简历分类、招聘系统、AI Agent 简历解析

---

## 一、设计理念

### 1.1 为什么是三级分类？

传统简历分类往往只有职能一个维度，但实际招聘场景中，**行业背景**同样重要：

- 同样是 Java 开发，互联网行业和金融行业的要求不同
- 同样是产品经理，AI 产品和消费品的侧重点不同
- 同样是销售，医药代表和 SaaS 销售的技能树差异很大

因此，我们采用 **三级分类体系**：

```
一级（行业）：描述候选人所在/目标行业背景
  └─ 二级（职能）：描述候选人的职能方向
       └─ 三级（岗位）：具体职位名称
```

### 1.2 设计原则

| 原则 | 说明 |
|-----|------|
| **行业与职能正交** | 同一职能可以在多个行业出现（如HR存在于所有行业） |
| **分类器主逻辑** | 先职能（决定文件夹归属），行业作为附加标签（用于筛选/搜索） |
| **数据来源权威** | 基于猎聘官方15个一级行业、22个二级职能分类 |
| **跨平台通用** | JSON格式，支持任意编程语言解析 |

---

## 二、分类体系详解

### 2.1 一级行业（15个）

基于猎聘官方行业分类，覆盖中国招聘市场主流行业：

| 编码 | 行业名称 | 典型子行业 |
|-----|---------|-----------|
| H01 | AI/互联网/IT | 游戏、电商、在线教育、云计算、人工智能、区块链等 |
| H02 | 电子/通信/半导体 | 芯片、集成电路、5G、消费电子等 |
| H03 | 房地产/建筑 | 房地产开发、建筑设计、工程施工等 |
| H04 | 金融 | 银行、保险、证券、基金、信托等 |
| H05 | 消费品 | 快消、食品、日化、母婴、服装等 |
| H06 | 医疗健康 | 医院、制药、医疗器械、医美等 |
| H07 | 汽车 | 整车制造、零部件、新能源、自动驾驶等 |
| H08 | 机械/制造 | 机械制造、自动化、工业机器人等 |
| H09 | 教育培训/科研 | K12、职业教育、在线教育、科研院所等 |
| H10 | 专业服务 | 法律、会计、咨询、人力资源等 |
| H11 | 广告/传媒/文化/体育 | 广告、公关、影视、出版、体育等 |
| H12 | 生活服务 | 餐饮、酒店、旅游、美容美发等 |
| H13 | 交通/物流/贸易/零售 | 物流、快递、跨境电商、零售等 |
| H14 | 能源/化工/环保 | 石油、电力、化工、环保、新能源等 |
| H15 | 政府/非营利/其他 | 公务员、事业单位、NGO等 |

### 2.2 二级职能（22个）

基于猎聘官方职能分类：

| 编码 | 职能名称 | 典型岗位 |
|-----|---------|---------|
| F01 | IT互联网技术 | Java、Python、前端、测试、运维、算法等 |
| F02 | 电子/通信/半导体 | 硬件工程师、FPGA、射频工程师等 |
| F03 | 销售/客服 | 销售代表、客户经理、客服专员等 |
| F04 | 运营 | 用户运营、内容运营、活动运营等 |
| F05 | 人力/行政/财务/法务 | HR、行政、会计、法务等 |
| F06 | 高级管理 | CEO、CTO、VP、总监等 |
| F07 | 市场/公关/广告/会展 | 市场专员、公关经理、活动策划等 |
| F08 | 生产/制造/研发 | 生产主管、质量工程师、工艺工程师等 |
| F09 | 制药/医疗器械/医疗护理 | 医生、护士、医药代表、临床研究员等 |
| F10 | 汽车 | 汽车工程师、底盘工程师、电池工程师等 |
| F11 | 房地产/建筑/物业 | 建筑设计师、项目经理、物业经理等 |
| F12 | 金融 | 投资经理、基金经理、风控、交易员等 |
| F13 | 产品 | 产品经理、产品助理、增长产品等 |
| F14 | 设计 | UI设计师、UX设计师、平面设计师等 |
| F15 | 教育/培训 | 教师、培训师、课程顾问等 |
| F16 | 供应链/物流/采购/贸易 | 采购经理、物流专员、报关员等 |
| F17 | 生活服务/零售 | 店长、导购、美容师、厨师等 |
| F18 | 影视/媒体 | 编导、记者、摄影师、主持人等 |
| F19 | 咨询/翻译 | 咨询顾问、翻译、同声传译等 |
| F20 | 能源/环保/农业 | 环保工程师、农业技术员等 |
| F21 | 项目管理 | PM、项目助理、Scrum Master等 |
| F22 | 公务员/其他 | 公务员、军人、自由职业等 |

### 2.3 三级岗位（1100+）

三级岗位是具体职位名称，例如：

- **F01 IT互联网技术** 下包含：Java开发工程师、Python开发工程师、前端开发工程师、测试工程师、运维工程师、算法工程师、数据工程师、架构师、技术经理...
- **F13 产品** 下包含：产品经理、产品助理、增长产品经理、AI产品经理、数据产品经理、策略产品经理...

> 完整岗位列表见规则文件中的 `positions` 字段。

---

## 三、JSON 规则格式

### 3.1 文件结构

```json
{
  "_meta": {
    "version": "3.0.0",
    "created": "2026-03-19",
    "description": "...",
    "sources": ["liepin", "boss"],
    "stats": {
      "level1_industries": 15,
      "level2_functions": 22,
      "level3_positions": "1100+"
    },
    "design_principles": [...]
  },
  "industries": {
    "_note": "一级行业分类",
    "data": [...]
  },
  "functions": {
    "_note": "二级职能分类",
    "data": [...]
  }
}
```

### 3.2 行业数据结构

```json
{
  "code": "H01",
  "name": "AI/互联网/IT",
  "keywords": ["互联网", "AI", "人工智能", "IT", "软件", ...],
  "sub_industries": ["游戏", "电子商务", "云计算/大数据", ...]
}
```

### 3.3 职能数据结构

```json
{
  "code": "F01",
  "name": "IT互联网技术",
  "keywords": ["Java", "Python", "前端", "后端", "开发", ...],
  "positions": ["Java开发工程师", "Python开发工程师", ...]
}
```

---

## 四、Python 分类器使用

### 4.1 安装

```bash
git clone https://github.com/Liman-fully/resume-classification-rules.git
cd resume-classification-rules/python
```

### 4.2 基础用法

```python
from resume_classifier import ResumeClassifier

# 初始化
classifier = ResumeClassifier()

# 单条分类
result = classifier.classify("5年Java后端开发经验，熟悉Spring Boot")

print(result['primary']['name'])   # IT互联网技术
print(result['industry']['name'])  # AI/互联网/IT
print(result['keywords_matched'])  # ['java', '后端', '开发']
```

### 4.3 批量分类

```python
texts = [
    "Java开发工程师",
    "产品经理",
    "销售经理"
]

results = classifier.batch_classify(texts)
for r in results:
    print(r['primary']['name'])
```

### 4.4 命令行工具

```bash
# 查看统计
python resume_classifier.py --stats

# 列出分类
python resume_classifier.py --list

# 分类文本
python resume_classifier.py --text "Java开发工程师"

# 分类文件
python resume_classifier.py --file resume.txt
```

---

## 五、匹配算法说明

### 5.1 算法流程

```
1. 文本预处理（小写化）
2. 遍历所有行业关键词，检查是否命中
3. 遍历所有职能关键词，检查是否命中
4. 计算置信度（基于词频和位置）
5. 按置信度排序，返回最佳匹配
```

### 5.2 置信度计算

```python
def calc_confidence(text, keyword):
    base = 0.5                    # 基础分
    freq_bonus = min(count * 0.1, 0.3)   # 词频加分（上限0.3）
    position_bonus = 0.2 if in_header else 0   # 标题位置加分
    return min(base + freq_bonus + position_bonus, 1.0)
```

### 5.3 主分类逻辑

- **职能优先**：决定文件夹归属（如 "技术/"、"产品/"）
- **行业作为标签**：用于筛选/搜索（如 "只看互联网行业的技术岗"）

---

## 六、扩展与定制

### 6.1 添加新行业

编辑 `rules/classification_rules.json`：

```json
{
  "code": "H16",
  "name": "元宇宙/Web3",
  "keywords": ["元宇宙", "Web3", "NFT", "区块链游戏"],
  "sub_industries": ["虚拟现实", "数字藏品", "链游"]
}
```

### 6.2 添加新职能

```json
{
  "code": "F23",
  "name": "AI训练师",
  "keywords": ["数据标注", "模型训练", "Prompt工程"],
  "positions": ["数据标注员", "AI训练师", "Prompt工程师"]
}
```

### 6.3 在其他语言中使用

由于规则是标准 JSON，可以在任何语言中解析：

**Node.js:**
```javascript
const rules = require('./rules/classification_rules.json');

function classify(text) {
  const industries = rules.industries.data;
  const functions = rules.functions.data;
  // ... 实现匹配逻辑
}
```

**Java:**
```java
import com.fasterxml.jackson.databind.ObjectMapper;

ObjectMapper mapper = new ObjectMapper();
Map<String, Object> rules = mapper.readValue(
  new File("rules/classification_rules.json"), 
  Map.class
);
```

---

## 七、版本历史

| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| 3.0.0 | 2026-03-25 | 升级为三级分类体系（行业×职能×岗位） |
| 2.0.0 | 2026-03-18 | 二级分类（22个职能 + 3个叠加标签） |
| 1.0.0 | 2026-03-12 | 初始版本（21个基础分类） |

---

## 八、常见问题

### Q1: 为什么行业只有15个？

这是基于猎聘官方的行业分类体系。15个一级行业已经覆盖了中国招聘市场的主流领域。每个行业下还有多个子行业，实际粒度足够使用。

### Q2: 职能和行业有什么区别？

- **职能**：决定简历放在哪个文件夹（如 "技术/"、"产品/"）
- **行业**：作为附加标签，用于筛选（如 "只看互联网行业的技术岗"）

### Q3: 如何贡献新的关键词？

1. Fork 本仓库
2. 编辑 `rules/classification_rules.json`
3. 运行测试确保无破坏
4. 提交 PR

---

## 九、联系与反馈

- GitHub Issues: https://github.com/Liman-fully/resume-classification-rules/issues
- 数据来源: 猎聘 (liepin.com)、BOSS直聘 (zhipin.com)

---

*最后更新: 2026-03-25*
