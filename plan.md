# Trading Agent v2 全面重做计划

## 变更总览（基于用户7条意见）

### 核心架构变更
1. **个股分析模式简化**：从"快速(默认)/深度/九维"三模式 → "超级深度(默认)/快速(用户明确要求)"两模式
2. **深度框架融合**：九维工作流 + 12维分析 → 融合为"超级深度分析框架"（统一更高维度）
3. **新增数据源**：wencai-skills（同花顺问财SkillHub），与mx-skills形成双引擎
4. **配额策略放松**：各skill独立额度，去掉所有小心翼翼的限制
5. **新增文件**：references/analysis-method.md（六维快速分析框架）

### 双引擎分工设计

#### mx-skills（东方财富）— 独立150次/天/每个skill
- mx-data: 实时行情、K线、财务、资金流向
- mx-search: 新闻、公告、研报搜索
- mx-xuangu: 多条件选股
- mx-moni: 模拟持仓/买卖
- mx-zixuan: 自选股管理

#### wencai-skills（同花顺）— 独立100次/天/每个skill
**mx-skills做不到，wencai独有（主力使用）**：
- 研报搜索：主流投研机构深度研报、投资评级、目标价
- 行业数据查询：行业估值、财务、盈利、板块排名、产业链
- 公司经营数据查询：主营构成、客户、供应商、重大合同
- 机构研究与评级查询：ESG、业绩预测、券商金股、信用评级
- 宏观数据查询：GDP、CPI、PPI、利率、汇率、社融
- 公司股东股本查询：股东户数、前十大股东、实控人、筹码分布
- 事件数据查询：业绩预告、增发、解禁、调研、监管函

**mx-skills也能做，wencai作为退级选项**：
- 行情数据查询（mx-data退级选项）
- 财务数据查询（mx-data退级选项）
- 新闻搜索（mx-search退级选项）
- 公告搜索（mx-search退级选项）
- 问财选A股（mx-xuangu退级选项）
- 模拟炒股（mx-moni退级选项）

#### 本地数据（baostock，永远首选）
5201只A股Parquet，秒级查询，无额度限制

### 文件改造清单

| 文件 | 操作 | 变更内容 |
|------|------|---------|
| AGENTS.md | 重做 | 个股分析两模式/融合深度框架/双引擎数据分工/去掉配额限制 |
| SOUL.md | 重做 | 去掉配额相关内容/弹性区更新/深度框架更新 |
| TOOLS.md | 重做 | 双引擎完整skill清单/分工降级链/去掉配额限制/增加wencai安装配置 |
| BOOTSTRAP.md | 重做 | 更新能力导航/快捷指令表/两模式说明 |
| METACOGNITION.md | 重做 | 去掉配额相关触发器/更新深度模式识别 |
| FAILURE_PROTOCOL.md | 重做 | 去掉配额相关降级链/更新故障分类 |
| USER.md | 重做 | 去掉成本敏感/更新风格参数 |
| IDENTITY.md | 保留 | 不变 |
| ADAPTIVE_CONSTRAINTS.md | 保留 | 不变 |
| HEARTBEAT.md | 保留 | 不变 |
| references/analysis-method.md | 新增 | 六维快速分析框架 |
| references/deep-dive-workflow.md | 重做 | 九维+12维融合为超级深度框架 |

## 执行阶段

### Stage 1: 引用文件创建（并行）
- A1: 创建 references/analysis-method.md（六维快速框架）
- A2: 创建 references/deep-dive-workflow.md（融合超级深度框架）

### Stage 2: 配置文件重做（并行）
- B1: 重做 AGENTS.md
- B2: 重做 TOOLS.md（含wencai配置）
- B3: 重做 SOUL.md
- B4: 重做 BOOTSTRAP.md
- B5: 重做 METACOGNITION.md
- B6: 重做 FAILURE_PROTOCOL.md
- B7: 重做 USER.md

### Stage 3: 文章重做
基于全新配置体系重新撰写分析文章

### Stage 4: 格式化输出
转为docx
