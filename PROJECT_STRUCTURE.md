# 扑克助手项目结构文档

## 项目概述

扑克助手是一个基于Python的德州扑克AI辅助系统，集成了现代GTO（Game Theory Optimal）策略和传统AI决策算法，为玩家提供专业的扑克建议和分析。

## 项目结构

```
Poker_Assistant/
├── poker_assistant/              # 主包
│   ├── ai_analysis/              # AI分析模块
│   │   ├── board_analyzer.py     # 牌面分析器
│   │   ├── chat_agent.py         # 聊天代理
│   │   ├── opponent_analyzer.py  # 对手分析器
│   │   ├── opponent_modeler.py   # 对手建模器
│   │   ├── review_analyzer.py    # 复盘分析器
│   │   └── strategy_advisor.py   # 策略顾问
│   ├── cli/                      # 命令行界面
│   │   ├── game_renderer.py      # 游戏渲染器
│   │   └── input_handler.py      # 输入处理器
│   ├── engine/                   # 游戏引擎
│   │   ├── ai_opponent.py        # AI对手（传统）
│   │   ├── game_controller.py    # 游戏控制器
│   │   ├── game_state.py         # 游戏状态
│   │   ├── human_player.py       # 人类玩家
│   │   └── improved_ai_opponent.py # 改进AI对手（GTO集成）
│   ├── gto_strategy/             # GTO策略包
│   │   ├── types.py              # 类型定义
│   │   ├── gto_core.py           # GTO核心引擎
│   │   ├── gto_advisor.py        # GTO策略顾问
│   │   ├── frequency_calculator.py # 频率计算器
│   │   ├── sizing_optimizer.py   # 尺度优化器
│   │   └── range_manager.py      # 范围管理器
│   ├── llm_service/              # LLM服务
│   │   ├── context_manager.py    # 上下文管理器
│   │   ├── deepseek_client.py    # DeepSeek客户端
│   │   └── prompt_manager.py     # 提示管理器
│   ├── prompts/                  # 提示模板
│   │   ├── board_analysis.txt    # 牌面分析提示
│   │   ├── chat_system.txt       # 聊天系统提示
│   │   ├── opponent_analysis.txt # 对手分析提示
│   │   ├── review_analysis.txt   # 复盘分析提示
│   │   └── strategy_advice.txt   # 策略建议提示
│   └── utils/                    # 工具模块
│       ├── card_utils.py         # 牌面工具
│       ├── config.py             # 配置管理
│       └── logging.py            # 日志记录
├── tests/                        # 测试套件
│   ├── conftest.py              # 测试配置
│   ├── run_tests.py             # 测试运行器
│   ├── TESTING_GUIDE.md         # 测试规范
│   ├── unit/                    # 单元测试
│   │   ├── test_gto_strategy.py # GTO策略单元测试
│   │   └── test_ai_engine.py    # AI引擎单元测试
│   ├── integration/             # 集成测试
│   │   └── test_ai_integration.py # AI集成测试
│   └── e2e/                     # 端到端测试
│       └── test_game_flow.py    # 游戏流程测试
├── data/                        # 数据目录
│   ├── game_history/            # 游戏历史
│   └── statistics/              # 统计数据
├── myenv/                       # Python虚拟环境
├── requirements.txt             # 依赖包
├── setup.py                     # 安装脚本
└── main.py                      # 主入口
```

## 核心模块详解

### 1. GTO策略包 (`gto_strategy/`)

#### 核心组件
- **GTOCore**: 核心GTO决策引擎，基于博弈论最优策略
- **GTOAdvisor**: 策略顾问，桥接GTO引擎和AI框架
- **RangeManager**: 范围管理器，管理起手牌范围
- **SizingOptimizer**: 尺度优化器，优化下注尺度
- **FrequencyCalculator**: 频率计算器，计算混合策略频率

#### 类型系统
- **GTOContext**: GTO决策上下文
- **GTOResult**: GTO策略结果
- **FrequencyResult**: 频率分析结果
- **SizingRecommendation**: 下注尺度建议

### 2. AI引擎 (`engine/`)

#### 主要组件
- **ImprovedAIOpponentPlayer**: 改进AI对手，集成GTO策略
- **GameController**: 游戏控制器，管理游戏流程
- **HumanPlayer**: 人类玩家接口
- **GameState**: 游戏状态管理

#### 决策流程
1. 接收游戏状态和手牌信息
2. 优先使用GTO策略进行决策
3. 如GTO失败，回退到传统AI策略
4. 生成详细的思考过程
5. 返回最优决策

### 3. AI分析 (`ai_analysis/`)

#### 分析模块
- **OpponentAnalyzer**: 分析对手行为模式
- **BoardAnalyzer**: 分析牌面结构
- **StrategyAdvisor**: 提供策略建议
- **ReviewAnalyzer**: 复盘分析
- **ChatAgent**: 聊天交互

### 4. 工具模块 (`utils/`)

#### 工具类
- **CardUtils**: 牌面计算工具
- **Config**: 配置管理
- **Logging**: 统一日志记录

## 设计原则

### 1. 模块化设计
- 高内聚，低耦合
- 清晰的模块边界
- 统一的接口规范

### 2. 可扩展性
- 插件式架构
- 策略可替换
- 配置驱动

### 3. 错误处理
- 统一的错误处理机制
- 优雅的错误恢复
- 详细的错误日志

### 4. 测试覆盖
- 单元测试覆盖核心逻辑
- 集成测试验证组件协作
- 端到端测试验证完整流程

## 配置管理

### 环境变量
```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 游戏配置
GAME_INITIAL_STACK=1000
GAME_SMALL_BLIND=5
GAME_BIG_BLIND=10
GAME_MAX_ROUND=100
GAME_PLAYER_COUNT=6

# AI配置
AI_OPPONENT_DIFFICULTY=mixed
AI_ANALYSIS_LEVEL=medium
AI_AUTO_SHOW_ADVICE=true
AI_ENABLE_OPPONENT_ANALYSIS=true
AI_ENABLE_BOARD_ANALYSIS=true
AI_ENABLE_REVIEW=true
```

### 配置文件
项目使用 `.env` 文件管理本地配置，支持通过环境变量覆盖。

## 开发指南

### 1. 代码风格
- 遵循PEP 8规范
- 使用类型提示
- 编写清晰的文档字符串

### 2. 测试要求
- 新功能必须包含测试
- 修复bug必须添加回归测试
- 保持测试的可读性和可维护性

### 3. 文档要求
- 公共API必须有文档
- 复杂的算法需要详细注释
- 更新README和CHANGELOG

### 4. 提交规范
- 使用清晰的提交信息
- 关联相关的issue
- 遵循项目的提交规范

## 部署指南

### 1. 开发环境
```bash
# 克隆项目
git clone https://github.com/your-username/Poker_Assistant.git
cd Poker_Assistant

# 创建虚拟环境
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# myenv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
python tests/run_tests.py --type all

# 启动应用
python main.py
```

### 2. 生产环境
```bash
# 安装生产依赖
pip install -r requirements-prod.txt

# 设置环境变量
export DEEPSEEK_API_KEY=your_api_key
export GAME_MAX_ROUND=1000

# 运行应用
python main.py --mode production
```

## 监控和日志

### 日志级别
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志文件
- `logs/gto_engine.log`: GTO引擎日志
- `logs/ai_engine.log`: AI引擎日志
- `logs/game_engine.log`: 游戏引擎日志

### 监控指标
- 决策成功率
- GTO策略命中率
- 响应时间
- 错误率

## 故障排除

### 常见问题

1. **GTO策略失败**
   - 检查手牌格式是否正确
   - 验证游戏状态完整性
   - 查看GTO引擎日志

2. **AI决策异常**
   - 检查AI配置参数
   - 验证对手分析数据
   - 查看AI引擎日志

3. **游戏状态错误**
   - 检查PyPokerEngine版本
   - 验证游戏控制器状态
   - 查看游戏引擎日志

### 调试技巧
- 启用DEBUG日志级别
- 使用测试用例重现问题
- 检查相关的配置文件

## 贡献指南

### 如何贡献
1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request
5. 通过代码审查

### 代码审查标准
- 代码质量
- 测试覆盖
- 文档完整性
- 性能影响

## 版本历史

### v1.0.0 (当前)
- ✅ GTO策略集成
- ✅ 改进AI决策引擎
- ✅ 统一错误处理
- ✅ 完整的测试套件
- ✅ 项目结构优化

### 未来规划
- 🔄 机器学习模型集成
- 🔄 实时对手建模
- 🔄 多桌游戏支持
- 🔄 Web界面开发
- 🔄 移动端适配