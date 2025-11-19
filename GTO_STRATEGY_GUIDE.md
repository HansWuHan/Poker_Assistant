# 🎯 GTO策略包使用指南

## 概述

GTO策略包为德州扑克AI助手提供了基于博弈论最优（Game Theory Optimal）理论的决策支持。该策略包保留了原有的AI逻辑，同时增加了GTO策略指导，让AI对手更加智能和难以预测。

## 🚀 快速开始

### 1. 启用GTO策略

在 `.env` 文件中配置GTO策略：

```bash
# 启用GTO策略
GTO_ENABLED=true

# 策略模式: gto_only, exploitative_only, hybrid
GTO_STRATEGY_MODE=hybrid

# GTO策略权重 (0.0-1.0)
GTO_WEIGHT=0.6

# 显示GTO分析
GTO_SHOW_ANALYSIS=true

# 使用混合策略
GTO_MIXED_STRATEGY=true
```

### 2. 运行测试

```bash
# 测试GTO策略包
python test_gto_strategy.py

# 运行GTO策略演示
python demo_gto_strategy.py
```

## 📋 核心功能

### 1. GTO核心引擎 (GTOCore)
- **翻牌前范围管理**: 基于位置的精确起手牌范围
- **翻牌后策略**: 考虑牌面纹理的最优决策
- **下注尺度优化**: 理论最优的下注大小
- **频率基础决策**: 平衡的行动频率

### 2. 范围管理器 (RangeManager)
- **位置特定范围**: BTN、CO、HJ、MP、UTG、SB、BB
- **行动分类**: 开池、3bet、4bet、防守范围
- **范围强度评估**: 手牌在范围内的相对强度
- **范围对局分析**: 范围vs范围的胜率计算

### 3. 下注尺度优化器 (SizingOptimizer)
- **情境感知尺度**: 根据筹码深度、位置、牌面调整
- **GTO标准尺度**: 1/3底池、1/2底池、2/3底池、超额下注
- **动态调整**: 基于对手倾向和牌面纹理

### 4. 频率计算器 (FrequencyCalculator)
- **最优行动频率**: 基于GTO理论的平衡频率
- **混合策略**: 避免可预测性的随机化决策
- **平衡性指标**: 策略平衡性、可预测性、可剥削性

### 5. GTO策略顾问 (GTOAdvisor)
- **综合决策引擎**: 整合所有GTO组件
- **策略混合**: GTO与剥削策略的智能混合
- **详细分析**: 提供决策的完整理论依据

## 🎮 策略模式

### 1. 纯GTO模式 (gto_only)
- 完全基于GTO理论做决策
- 最适合未知对手或高水平对局
- 保证长期不可剥削

### 2. 纯剥削模式 (exploitative_only)
- 使用原有AI逻辑，基于对手倾向
- 最适合已知对手有明显漏洞
- 最大化短期利润

### 3. 混合模式 (hybrid) - 推荐
- 结合GTO理论和对手剥削
- 默认60% GTO + 40% 剥削
- 平衡长期稳定性和短期收益

## 🧠 使用示例

### 基本使用

```python
from poker_assistant.gto_strategy import GTOAdvisor

# 创建GTO顾问
gto_advisor = GTOAdvisor()

# 获取GTO建议
advice = gto_advisor.get_gto_advice(
    hole_cards=['SA', 'HA'],      # A♠ A♥
    community_cards=[],
    street='preflop',
    position='BTN',
    pot_size=15,
    stack_size=1000,
    call_amount=0,
    valid_actions=[...],
    opponent_actions=[],
    active_opponents=['SB', 'BB']
)

print(f"建议: {advice['action']} ${advice['amount']}")
print(f"理由: {advice['reasoning']}")
```

### 高级配置

```python
# 自定义GTO权重
gto_advisor.update_weights(gto_weight=0.8, exploitative_weight=0.2)

# 设置策略模式
gto_advisor.set_strategy_mode("hybrid")

# 获取性能指标
metrics = gto_advisor.get_performance_metrics()
print(f"平衡性得分: {metrics['balance_score']}")
```

## 📊 GTO策略分析

### 翻牌前范围示例

| 位置 | 开池范围 | 范围大小 |
|------|----------|----------|
| BTN  | 50%      | 所有对子，同花A，大部分同花连牌 |
| CO   | 30%      | 对子77+，AJo+，KQo，同花连牌 |
| UTG  | 15%      | 对子88+，AQo+，同花AJ+ |

### 翻牌后策略框架

1. **持续下注 (C-Bet)**
   - 干燥牌面: 33%底池
   - 湿润牌面: 75%底池
   - 动态牌面: 55%底池

2. **面对下注**
   - 根据牌力和赔率决定跟注/加注/弃牌
   - 考虑对手范围和牌面协调性

3. **诈唬选择**
   - 有阻断效应的牌
   - 合适的牌面纹理
   - 平衡的价值诈唬比例

## 🔧 配置参数

### GTO核心参数

```python
# GTO核心参数
min_raise_factor = 2.0      # 最小加注倍数
max_raise_factor = 4.0      # 最大加注倍数
value_bet_threshold = 0.6   # 价值下注阈值
bluff_threshold = 0.3       # 诈唬阈值
```

### 频率调整因子

```python
# 位置调整
position_adjustments = {
    'BTN': {'aggression': 1.2, 'defense': 1.0},
    'BB': {'aggression': 0.9, 'defense': 1.1},
    # ...
}

# 牌面纹理调整
board_texture_adjustments = {
    'dry': {'aggression': 1.1, 'defense': 0.9},
    'wet': {'aggression': 0.8, 'defense': 1.2},
    # ...
}
```

## 🎲 实战应用

### 情境1: BTN位置拿到AA
```
位置: BTN
手牌: A♠ A♥ 
行动: 加注到 $25 (2.5BB)
理由: BTN位置AA属于超强牌，GTO推荐100%加注
```

### 情境2: BB位置面对C-Bet
```
位置: BB
手牌: K♠ Q♠
牌面: K♦ 7♣ 2♠
行动: 跟注 $30
理由: 顶对强踢脚，在干燥牌面有足够胜率跟注
```

### 情境3: CO位置诈唬
```
位置: CO
手牌: A♠ 5♠
牌面: Q♠ 8♠ 2♦
行动: 加注到 $75
理由: 有坚果同花听牌阻断，合适的诈唬候选
```

## 📈 性能指标

GTO策略包提供详细的性能分析：

- **平衡性得分**: 0-1，越接近1越平衡
- **可预测性**: 0-1，越低越难被对手预测
- **可剥削性**: 0-1，越低越难被对手剥削
- **GTO权重**: 当前GTO策略使用比例
- **历史表现**: 长期统计数据

## 🚀 高级功能

### 1. 混合策略
自动在不同行动间随机化，避免模式化：
```python
# 获取混合策略频率
mixed_frequencies = frequency_calculator.calculate_mixed_strategy(context)
```

### 2. 策略对比
比较GTO策略与剥削策略：
```python
comparison = gto_advisor.get_gto_vs_exploitative_comparison(situation)
```

### 3. 剥削机会识别
自动识别对手漏洞：
```python
opportunities = gto_advisor._identify_exploit_opportunities(opponent_actions)
```

## 💡 最佳实践

1. **新手建议**: 从混合模式开始，权重60% GTO + 40% 剥削
2. **进阶玩家**: 根据对手水平调整权重，松桌降低GTO权重
3. **高级应用**: 结合对手建模，动态调整策略参数
4. **数据分析**: 定期查看性能指标，优化策略配置

## 🔍 故障排除

### 常见问题

1. **GTO建议不合理**
   - 检查输入参数是否正确
   - 验证手牌和牌面格式
   - 调整GTO权重设置

2. **性能问题**
   - 减少复杂计算频率
   - 使用缓存机制
   - 优化策略参数

3. **策略过于保守**
   - 降低GTO权重
   - 增加剥削策略比例
   - 调整对手模型参数

## 📚 学习资源

- **GTO理论**: 博弈论在扑克中的应用
- **范围构建**: 如何构建平衡的范围
- **下注尺度**: 最优下注大小的数学原理
- **频率分析**: 混合策略的数学基础

---

**注意**: GTO策略提供理论最优框架，但实际应用中需要根据具体情境和对手特点进行调整。建议先在低风险环境中测试，逐步应用到实战对局中。