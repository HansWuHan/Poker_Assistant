# 德州扑克 AI 助手 - 技术设计文档

## 📋 项目概述

### 项目名称
**Poker AI Assistant** - 基于 AI 大模型的德州扑克练习与学习平台

### 项目目标
开发一个集成 AI 分析能力的德州扑克人机对战系统，帮助玩家：
- 在实战中学习德州扑克策略
- 通过 AI 实时分析理解每个决策的深层逻辑
- 通过复盘提升扑克水平

### 核心特性
1. ✅ 6人桌德州扑克人机对战
2. ✅ AI 实时策略建议（行动前）
3. ✅ AI 对手行动解读（行动后）
4. ✅ AI 公共牌面分析
5. ✅ AI 对局复盘
6. ✅ 对局中自由提问

---

## 🛠 技术栈

### 核心依赖
```
- Python 3.8+
- PyPokerEngine: 德州扑克游戏引擎
- Deepseek API: AI 分析与建议
- python-dotenv: 环境变量管理
- rich: CLI 美化输出
- prompt_toolkit: 交互式命令行
```

### 开发工具
```
- pytest: 单元测试
- black: 代码格式化
- mypy: 类型检查
```

---

## 🏗 系统架构

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (CLI Interface)                │
│  - 游戏显示 (GameRenderer)                                   │
│  - 用户输入处理 (InputHandler)                               │
│  - AI 对话界面 (ChatInterface)                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   游戏控制层 (Game Controller)               │
│  - 游戏流程控制 (GameController)                             │
│  - 回合管理 (RoundManager)                                   │
│  - 事件处理 (EventHandler)                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   AI 分析层 (AI Analysis)                    │
│  - 策略建议引擎 (StrategyAdvisor)                            │
│  - 对手分析引擎 (OpponentAnalyzer)                           │
│  - 牌面分析引擎 (BoardAnalyzer)                              │
│  - 复盘分析引擎 (ReviewAnalyzer)                             │
│  - 自由对话引擎 (ChatAgent)                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  LLM 服务层 (LLM Service)                    │
│  - Deepseek API 客户端                                       │
│  - Prompt 模板管理                                           │
│  - 上下文管理                                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                  游戏引擎层 (Poker Engine)                   │
│  - PyPokerEngine 核心                                        │
│  - 玩家管理 (HumanPlayer, AIPlayer)                         │
│  - 游戏状态管理                                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   数据持久层 (Data Layer)                    │
│  - 游戏历史记录 (Game History)                               │
│  - 对话历史记录 (Chat History)                               │
│  - 统计数据 (Statistics)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 核心模块设计

### 1. 游戏引擎模块 (`engine/`)

#### 1.1 HumanPlayer
```python
class HumanPlayer(BasePokerPlayer):
    """人类玩家类"""
    - 接收 CLI 输入
    - 请求 AI 建议
    - 触发提问功能
```

#### 1.2 AIOpponentPlayer
```python
class AIOpponentPlayer(BasePokerPlayer):
    """AI 对手类"""
    - 基于 GTO 策略
    - 随机性模拟真实玩家
    - 支持不同难度等级
```

#### 1.3 GameState
```python
class GameState:
    """游戏状态管理"""
    - 当前回合信息
    - 历史行动记录
    - 公共牌信息
    - 底池大小
    - 玩家状态
```

---

### 2. AI 分析模块 (`ai_analysis/`)

#### 2.1 StrategyAdvisor
```python
class StrategyAdvisor:
    """策略建议引擎"""
    
    async def get_action_advice(
        self,
        hole_cards: List[str],
        community_cards: List[str],
        pot_size: int,
        stack_size: int,
        position: str,
        opponent_actions: List[Dict],
        valid_actions: List[Dict]
    ) -> AdviceResult:
        """
        生成行动建议
        
        返回:
        - 推荐行动 (fold/call/raise)
        - 建议金额
        - 理由说明
        - 胜率估算
        - 风险评估
        """
```

**Prompt 示例**:
```
你是一位专业的德州扑克教练。请分析以下牌局并给出建议：

【手牌】{hole_cards}
【公共牌】{community_cards}
【位置】{position}
【底池】{pot_size}
【筹码】{stack_size}
【对手行动】{opponent_actions}
【可选行动】{valid_actions}

请以 JSON 格式返回：
{
  "recommended_action": "call/raise/fold",
  "amount": 100,
  "reasoning": "建议理由",
  "win_probability": 0.65,
  "risk_level": "medium"
}
```

#### 2.2 OpponentAnalyzer
```python
class OpponentAnalyzer:
    """对手行动分析引擎"""
    
    async def analyze_opponent_action(
        self,
        opponent_name: str,
        action: Dict,
        game_context: GameState,
        opponent_history: List[Dict]
    ) -> AnalysisResult:
        """
        分析对手行动含义
        
        返回:
        - 可能的手牌范围
        - 行动意图分析
        - 策略类型（紧凶/松凶/保守等）
        - 应对建议
        """
```

**Prompt 示例**:
```
对手 {opponent_name} 在以下情况做出了行动，请分析：

【公共牌】{community_cards}
【底池】{pot_size}
【对手行动】{action}
【历史行动】{opponent_history}

请分析：
1. 对手可能的手牌范围
2. 该行动的战术意图
3. 对手的打法风格
4. 我们的应对策略
```

#### 2.3 BoardAnalyzer
```python
class BoardAnalyzer:
    """牌面分析引擎"""
    
    async def analyze_board(
        self,
        community_cards: List[str],
        hole_cards: List[str]
    ) -> BoardAnalysis:
        """
        分析公共牌面
        
        返回:
        - 牌面结构（干燥/湿润/危险）
        - 可能的听牌
        - 当前牌力等级
        - 改进可能性
        """
```

#### 2.4 ReviewAnalyzer
```python
class ReviewAnalyzer:
    """复盘分析引擎"""
    
    async def generate_review(
        self,
        game_history: GameHistory
    ) -> ReviewReport:
        """
        生成对局复盘报告
        
        返回:
        - 关键决策点分析
        - 错误决策标注
        - 最优打法建议
        - 整体评价
        """
```

#### 2.5 ChatAgent
```python
class ChatAgent:
    """自由对话引擎"""
    
    async def chat(
        self,
        user_question: str,
        game_context: GameState
    ) -> str:
        """
        处理用户自由提问
        
        支持问题类型:
        - 当前局面分析
        - 德州扑克知识
        - 策略讨论
        - 历史手牌回顾
        """
```

---

### 3. LLM 服务模块 (`llm_service/`)

#### 3.1 DeepseekClient
```python
class DeepseekClient:
    """Deepseek API 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用 Deepseek Chat API"""
```

#### 3.2 PromptManager
```python
class PromptManager:
    """Prompt 模板管理器"""
    
    - 加载预定义 Prompt
    - 动态参数填充
    - Prompt 版本管理
```

#### 3.3 ContextManager
```python
class ContextManager:
    """上下文管理器"""
    
    - 维护对话历史
    - 管理 Token 限制
    - 自动压缩上下文
```

---

### 4. CLI 界面模块 (`cli/`)

#### 4.1 GameRenderer
```python
class GameRenderer:
    """游戏界面渲染器"""
    
    使用 rich 库实现:
    - 牌桌布局显示
    - 玩家状态显示
    - 底池信息显示
    - 公共牌显示
    - 行动历史显示
    - AI 建议面板
```

**界面示例**:
```
╔═══════════════════════════════════════════════════════════════╗
║                    德州扑克 AI 助手                            ║
║                      Round 5 - Flop                           ║
╚═══════════════════════════════════════════════════════════════╝

                      [AI_3: $980]
                        (Fold)
            
    [AI_2: $1200]                    [AI_4: $850]
      (Call $50)                       (Raise $100)

                    💰 Pot: $350

            ┌──────────────────┐
            │  7♥  K♠  9♦      │  Community Cards
            └──────────────────┘

    [AI_1: $1100]                    [AI_5: $920]
      (Fold)                          (Call $100)

                    [YOU: $1050]
                    🃏 A♠ A♥
                    
╔═══════════════════════════════════════════════════════════════╗
║ 🤖 AI 建议                                                     ║
║ 推荐: RAISE to $250                                           ║
║ 理由: 你持有顶对，牌面较干燥，应该价值下注保护手牌             ║
║ 胜率: ~75%                                                    ║
╚═══════════════════════════════════════════════════════════════╝

[F]老德 [C]跟注 [R]加注 [A]全下 [Q]提问 > 
```

#### 4.2 InputHandler
```python
class InputHandler:
    """用户输入处理器"""
    
    - 行动输入验证
    - 金额输入处理
    - 快捷键支持
    - 提问模式切换
```

#### 4.3 ChatInterface
```python
class ChatInterface:
    """对话界面"""
    
    - 提问输入
    - 流式回复显示
    - 历史对话查看
```

---

### 5. 数据持久模块 (`data/`)

#### 5.1 GameHistory
```python
class GameHistory:
    """游戏历史记录"""
    
    保存内容:
    - 每手牌的完整信息
    - 所有玩家行动
    - AI 建议记录
    - 最终结果
```

#### 5.2 统计模块
```python
class Statistics:
    """统计数据"""
    
    - 总局数
    - 胜率
    - 盈利/亏损
    - 行动分布
    - AI 建议采纳率
```

---

## 🔄 数据流设计

### 用户行动流程

```
1. 用户轮次开始
   ↓
2. GameRenderer 显示当前状态
   ↓
3. StrategyAdvisor 生成 AI 建议 (异步)
   ↓
4. 显示 AI 建议
   ↓
5. 用户可以:
   - 选择行动
   - 按 Q 提问
   ↓
6. 执行行动
   ↓
7. 记录到 GameHistory
```

### AI 对手行动流程

```
1. AI 对手行动
   ↓
2. 行动结果显示
   ↓
3. OpponentAnalyzer 分析行动含义
   ↓
4. 显示 AI 解读
   ↓
5. 等待用户确认继续
```

### 公共牌发放流程

```
1. 发放 Flop/Turn/River
   ↓
2. BoardAnalyzer 分析牌面
   ↓
3. 显示牌面分析
   ↓
4. 继续下注轮
```

### 对局结束流程

```
1. Showdown
   ↓
2. 显示所有玩家手牌
   ↓
3. ReviewAnalyzer 生成复盘报告
   ↓
4. 显示复盘报告
   ↓
5. 保存历史记录
   ↓
6. 更新统计数据
```

---

## 🗂 项目文件结构

```
Poker_Assistant/
├── .env                          # 环境变量（API Key）
├── .env.example                  # 环境变量模板
├── .gitignore
├── README.md                     # 用户文档
├── DESIGN.md                     # 本设计文档
├── requirements.txt              # Python 依赖
├── setup.py                      # 安装配置
│
├── poker_assistant/              # 主包
│   ├── __init__.py
│   │
│   ├── engine/                   # 游戏引擎模块
│   │   ├── __init__.py
│   │   ├── human_player.py      # 人类玩家
│   │   ├── ai_opponent.py       # AI 对手
│   │   ├── game_controller.py   # 游戏控制器
│   │   └── game_state.py        # 游戏状态
│   │
│   ├── ai_analysis/              # AI 分析模块
│   │   ├── __init__.py
│   │   ├── strategy_advisor.py  # 策略建议
│   │   ├── opponent_analyzer.py # 对手分析
│   │   ├── board_analyzer.py    # 牌面分析
│   │   ├── review_analyzer.py   # 复盘分析
│   │   └── chat_agent.py        # 对话代理
│   │
│   ├── llm_service/              # LLM 服务模块
│   │   ├── __init__.py
│   │   ├── deepseek_client.py   # Deepseek 客户端
│   │   ├── prompt_manager.py    # Prompt 管理
│   │   └── context_manager.py   # 上下文管理
│   │
│   ├── cli/                      # CLI 界面模块
│   │   ├── __init__.py
│   │   ├── game_renderer.py     # 游戏渲染
│   │   ├── input_handler.py     # 输入处理
│   │   └── chat_interface.py    # 对话界面
│   │
│   ├── data/                     # 数据持久模块
│   │   ├── __init__.py
│   │   ├── game_history.py      # 游戏历史
│   │   └── statistics.py        # 统计数据
│   │
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── card_utils.py        # 扑克牌工具
│   │   ├── probability.py       # 概率计算
│   │   └── config.py            # 配置管理
│   │
│   └── prompts/                  # Prompt 模板
│       ├── strategy_advice.txt
│       ├── opponent_analysis.txt
│       ├── board_analysis.txt
│       ├── review_analysis.txt
│       └── chat_system.txt
│
├── tests/                        # 测试
│   ├── __init__.py
│   ├── test_engine/
│   ├── test_ai_analysis/
│   ├── test_llm_service/
│   └── test_utils/
│
├── data/                         # 数据目录
│   ├── game_history/            # 游戏记录
│   └── statistics/              # 统计数据
│
├── logs/                         # 日志
│   └── .gitkeep
│
└── main.py                       # 主入口
```

---

## 🎮 游戏配置

### 默认配置
```python
GAME_CONFIG = {
    "max_round": 100,              # 最大回合数
    "initial_stack": 1000,         # 初始筹码
    "small_blind": 5,              # 小盲注
    "big_blind": 10,               # 大盲注
    "ante": 0,                     # 底注
    "player_count": 6,             # 玩家数量
    "ai_opponents": 5,             # AI 对手数量
}

AI_CONFIG = {
    "enable_strategy_advice": True,      # 启用策略建议
    "enable_opponent_analysis": True,    # 启用对手分析
    "enable_board_analysis": True,       # 启用牌面分析
    "enable_review": True,               # 启用复盘
    "enable_chat": True,                 # 启用自由提问
    "auto_show_advice": True,            # 自动显示建议
    "analysis_detail_level": "medium",   # 分析详细程度
}

LLM_CONFIG = {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 30,
}
```

---

## 🔐 环境变量配置

### .env.example
```bash
# Deepseek API Configuration
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Game Configuration
GAME_INITIAL_STACK=1000
GAME_SMALL_BLIND=5
GAME_BIG_BLIND=10

# AI Configuration
AI_ANALYSIS_LEVEL=medium  # low/medium/high

# Debug
DEBUG=False
LOG_LEVEL=INFO
```

---

## 🚀 开发计划

### Phase 1: 基础框架 (3-4天)
- [x] 项目结构搭建
- [ ] PyPokerEngine 集成
- [ ] 基础 CLI 界面
- [ ] HumanPlayer 和 AIOpponentPlayer 实现
- [ ] GameController 实现
- [ ] 基础游戏流程跑通

**验收标准**: 能够进行 6 人桌基础游戏，无 AI 分析功能

### Phase 2: LLM 服务集成 (2-3天)
- [ ] Deepseek API 客户端
- [ ] Prompt 模板设计
- [ ] PromptManager 实现
- [ ] ContextManager 实现
- [ ] API 调用测试

**验收标准**: 能够成功调用 Deepseek API 并获得合理回复

### Phase 3: AI 分析功能 (4-5天)
- [ ] StrategyAdvisor 实现
- [ ] OpponentAnalyzer 实现
- [ ] BoardAnalyzer 实现
- [ ] ReviewAnalyzer 实现
- [ ] 各模块 Prompt 优化

**验收标准**: 四大 AI 分析功能均可用且返回高质量建议

### Phase 4: 对话功能 (2天)
- [ ] ChatAgent 实现
- [ ] ChatInterface 实现
- [ ] 对话历史管理
- [ ] 上下文注入

**验收标准**: 能够在游戏中随时提问并获得合理回答

### Phase 5: 数据持久化 (2天)
- [ ] GameHistory 实现
- [ ] Statistics 实现
- [ ] JSON 序列化/反序列化
- [ ] 历史查询功能

**验收标准**: 游戏记录能够保存和查询

### Phase 6: 界面优化 (2-3天)
- [ ] Rich 美化
- [ ] 动画效果
- [ ] 快捷键优化
- [ ] 错误处理
- [ ] 用户体验优化

**验收标准**: 界面美观、操作流畅

### Phase 7: 测试与文档 (2天)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 用户文档
- [ ] API 文档
- [ ] 示例代码

**验收标准**: 测试覆盖率 > 70%，文档完整

---

## 📊 关键技术点

### 1. 异步处理
```python
# AI 分析可能耗时较长，使用异步避免阻塞
async def get_ai_advice():
    advice = await strategy_advisor.get_action_advice(...)
    return advice
```

### 2. 错误处理
```python
# API 调用失败时的降级策略
try:
    advice = await llm_client.get_advice(...)
except APIError:
    advice = fallback_rule_based_advice()  # 使用规则引擎
```

### 3. Token 管理
```python
# 控制上下文长度，避免超出 Token 限制
context = context_manager.compress_context(
    game_history, 
    max_tokens=6000
)
```

### 4. 缓存优化
```python
# 对相似牌面的分析结果进行缓存
@lru_cache(maxsize=1000)
def analyze_board(community_cards, hole_cards):
    ...
```

---

## 🧪 测试策略

### 单元测试
- 每个模块独立测试
- Mock LLM API 调用
- 覆盖边界情况

### 集成测试
- 完整游戏流程测试
- AI 分析功能测试
- 数据持久化测试

### 性能测试
- API 调用延迟
- 内存使用
- 响应时间

---

## 📈 后续扩展方向

### MVP 之后可以考虑的功能
1. **Web 界面**: 使用 FastAPI + React
2. **多语言支持**: 英文界面
3. **高级 AI 对手**: 基于 CFR/Deep Learning 的 AI
4. **多桌训练**: 同时进行多局游戏
5. **策略库**: 预设不同打法风格
6. **社区功能**: 分享对局、讨论策略
7. **移动端**: iOS/Android App
8. **语音交互**: 语音提问和语音播报

---

## 🎯 成功标准

### MVP 完成标准
1. ✅ 能够稳定运行 6 人桌游戏
2. ✅ AI 建议准确率 > 70%（通过专家评估）
3. ✅ 平均 API 响应时间 < 5 秒
4. ✅ 界面清晰易用，无重大 Bug
5. ✅ 支持完整的游戏流程和所有 AI 功能

### 用户体验标准
1. ✅ 新手能够在 5 分钟内开始游戏
2. ✅ AI 建议通俗易懂
3. ✅ 游戏流畅不卡顿
4. ✅ 错误提示友好

---

## 💡 技术风险与应对

### 风险 1: API 调用延迟
**影响**: 用户等待时间过长  
**应对**: 
- 异步处理 + 加载动画
- 缓存常见场景分析
- 提供"跳过 AI 建议"选项

### 风险 2: API 成本
**影响**: 频繁调用成本高  
**应对**:
- 使用更便宜的模型（Deepseek 已经很便宜）
- 优化 Prompt 减少 Token
- 可选的分析详细程度

### 风险 3: AI 建议质量
**影响**: 建议不准确影响用户体验  
**应对**:
- Prompt 工程优化
- 多轮测试和调整
- 提供反馈机制

### 风险 4: 并发性能
**影响**: 多个 AI 分析同时进行时卡顿  
**应对**:
- 合理的异步队列
- 优先级控制（用户行动建议 > 对手分析）

---

## 📝 总结

本设计文档提供了德州扑克 AI 助手的完整技术方案，包括：
- ✅ 清晰的分层架构
- ✅ 详细的模块设计
- ✅ 完整的数据流
- ✅ 可执行的开发计划
- ✅ 风险评估和应对

**预计总开发时间**: 15-20 天完成 MVP

**下一步**: 等待确认后开始 Phase 1 开发

---

*Document Version: 1.0*  
*Last Updated: 2025-11-08*  
*Author: AI Assistant*


