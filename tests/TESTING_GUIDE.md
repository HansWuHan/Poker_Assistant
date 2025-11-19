"""
测试规范和最佳实践

定义测试编写的规范和最佳实践
"""

# 测试规范

## 测试组织结构

```
tests/
├── conftest.py              # 测试配置和共享夹具
├── run_tests.py            # 测试运行器
├── unit/                   # 单元测试
│   ├── test_gto_strategy.py
│   ├── test_ai_engine.py
│   └── ...
├── integration/            # 集成测试
│   ├── test_ai_integration.py
│   └── ...
├── e2e/                    # 端到端测试
│   ├── test_game_flow.py
│   └── ...
└── fixtures/               # 测试数据
    ├── sample_hands.json
    └── ...
```

## 测试分类

### 单元测试 (Unit Tests)
- 测试单个函数或类的功能
- 不依赖外部系统
- 运行速度快
- 使用模拟对象隔离依赖

### 集成测试 (Integration Tests)
- 测试多个组件的协作
- 可以依赖真实的外部系统
- 运行速度中等
- 验证接口兼容性

### 端到端测试 (E2E Tests)
- 测试完整的用户流程
- 尽可能接近真实环境
- 运行速度较慢
- 验证系统整体功能

## 命名规范

### 测试文件命名
- 使用 `test_` 前缀
- 使用下划线分隔单词
- 描述测试的内容
- 示例: `test_gto_strategy.py`, `test_ai_engine.py`

### 测试函数命名
- 使用 `test_` 前缀
- 使用下划线分隔单词
- 描述测试的行为和预期结果
- 示例: `test_gto_advisor_with_premium_hand()`, `test_ai_player_error_handling()`

## 测试结构

```python
def test_function_name():
    """测试描述：说明测试什么和预期结果"""
    # Arrange: 设置测试数据和环境
    
    # Act: 执行被测试的操作
    
    # Assert: 验证结果
    
    pass
```

## 测试数据

### 使用夹具 (Fixtures)
```python
@pytest.fixture
def sample_hole_cards():
    return {
        'premium': ['SA', 'HA'],      # AA
        'strong': ['SK', 'HK'],       # KK
        'medium': ['HA', 'D9'],       # A9
        'weak': ['S2', 'H7'],         # 27
    }
```

### 使用参数化测试
```python
@pytest.mark.parametrize("hole_cards,expected_action", [
    (['SA', 'HA'], 'raise'),  # AA应该加注
    (['S2', 'H7'], 'fold'),   # 27应该弃牌
])
def test_gto_decision(hole_cards, expected_action):
    # 测试实现
    pass
```

## 测试标记 (Markers)

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.e2e`: 端到端测试
- `@pytest.mark.slow`: 慢速测试
- `@pytest.mark.gto`: GTO策略相关测试
- `@pytest.mark.ai`: AI引擎相关测试

## 错误处理测试

### 测试异常情况
```python
def test_gto_advisor_with_invalid_input():
    """测试GTO顾问处理无效输入"""
    # Arrange
    advisor = GTOAdvisor()
    invalid_hole_cards = []  # 空的手牌
    
    # Act & Assert
    with pytest.raises(ValueError):
        advisor.get_gto_advice(invalid_hole_cards, ...)
```

### 测试错误恢复
```python
def test_ai_player_error_recovery():
    """测试AI玩家的错误恢复机制"""
    # Arrange
    ai_player = ImprovedAIOpponentPlayer()
    invalid_round_state = {}  # 无效的轮次状态
    
    # Act
    action, amount = ai_player.declare_action([], [], invalid_round_state)
    
    # Assert
    assert action in ['fold', 'call']  # 应该返回安全的默认决策
    assert amount >= 0
```

## 性能测试

### 测试执行时间
```python
@pytest.mark.timeout(5)  # 测试应该在5秒内完成
def test_gto_calculation_performance():
    """测试GTO计算性能"""
    # 测试实现
    pass
```

### 测试内存使用
```python
def test_ai_memory_usage():
    """测试AI内存使用"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 执行内存密集型操作
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 100 * 1024 * 1024  # 内存增加不超过100MB
```

## 测试覆盖率

### 目标覆盖率
- 单元测试: 80%+
- 集成测试: 70%+
- 端到端测试: 60%+

### 覆盖率报告
```bash
# 运行测试并生成覆盖率报告
pytest --cov=poker_assistant --cov-report=html --cov-report=term
```

## 持续集成

### 测试钩子
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=poker_assistant --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 最佳实践

### 1. 保持测试简单
- 每个测试只测试一个概念
- 使用描述性的测试名称
- 避免复杂的测试逻辑

### 2. 使用适当的断言
- 使用具体的断言而不是通用的assert
- 提供有用的错误消息
```python
assert result.action == 'raise', f"Expected raise but got {result.action}"
```

### 3. 测试边界条件
- 测试空值、零值、负值
- 测试最大值和最小值
- 测试边界情况

### 4. 保持测试独立
- 测试之间不应该有依赖关系
- 每个测试应该能够独立运行
- 使用夹具来共享设置代码

### 5. 定期维护测试
- 删除过时的测试
- 更新测试以反映代码变化
- 保持测试的可读性和可维护性