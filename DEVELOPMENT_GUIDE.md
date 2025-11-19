# 开发指南

## 快速开始

### 环境设置
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

### 配置API
创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=your_api_key_here
GAME_INITIAL_STACK=1000
GAME_SMALL_BLIND=5
GAME_BIG_BLIND=10
```

## 开发流程

### 1. 功能开发
1. 创建功能分支：`git checkout -b feature/your-feature`
2. 编写代码和测试
3. 运行测试：`python tests/run_tests.py --type all`
4. 提交代码：`git commit -m "feat: your feature description"`
5. 推送分支：`git push origin feature/your-feature`
6. 创建Pull Request

### 2. 测试编写
```python
def test_your_feature():
    """测试你的功能描述"""
    # Arrange: 设置测试数据
    
    # Act: 执行操作
    
    # Assert: 验证结果
    pass
```

### 3. 代码规范
- 遵循PEP 8规范
- 使用类型提示
- 编写清晰的文档字符串
- 保持函数简短（<50行）

## 模块开发

### GTO策略开发
```python
from poker_assistant.gto_strategy import GTOCore, GTOContext

# 创建GTO上下文
context = GTOContext(
    street='preflop',
    position='BB',
    stack_size=1000,
    pot_size=30,
    community_cards=[],
    hole_cards=['SA', 'HA'],
    opponent_actions=[],
    active_opponents=1
)

# 获取GTO建议
result = gto_core.calculate_gto_action_new(context)
print(f"GTO建议: {result.action} ${result.amount}")
```

### AI引擎开发
```python
from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

# 创建AI玩家
ai_player = ImprovedAIOpponentPlayer(
    difficulty="medium",
    show_thinking=True,
    gto_enabled=True
)

# 执行决策
action, amount = ai_player.declare_action(
    valid_actions, hole_card, round_state
)
```

### 错误处理
```python
from poker_assistant.utils.logging import error_handler, PokerError

try:
    # 你的代码
    pass
except Exception as e:
    result = error_handler.handle_error(e, context="your_context")
    # 处理错误结果
```

## 调试技巧

### 1. 日志调试
```python
from poker_assistant.utils.logging import main_logger

main_logger.debug("调试信息")
main_logger.info("一般信息")
main_logger.error("错误信息")
```

### 2. 断点调试
```python
import pdb
pdb.set_trace()  # 设置断点
```

### 3. 测试调试
```bash
# 运行特定测试
python -m pytest tests/unit/test_gto_strategy.py::TestGTOCore::test_calculate_gto_action_new -v

# 调试模式运行
python -m pytest tests/unit/test_gto_strategy.py -v --pdb
```

## 性能优化

### 1. 代码优化
- 使用列表推导式代替循环
- 避免重复计算
- 使用适当的数据结构

### 2. 内存优化
- 及时释放大对象
- 使用生成器处理大数据
- 避免循环引用

### 3. 测试性能
```python
import time
import psutil

def test_performance():
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    # 你的代码
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    print(f"执行时间: {end_time - start_time:.2f}s")
    print(f"内存使用: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
```

## 部署指南

### 1. 开发环境
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行开发服务器
python main.py --mode development
```

### 2. 测试环境
```bash
# 运行所有测试
python tests/run_tests.py --type all

# 检查代码质量
flake8 poker_assistant/
mypy poker_assistant/
```

### 3. 生产环境
```bash
# 安装生产依赖
pip install -r requirements-prod.txt

# 运行生产服务器
python main.py --mode production
```

## 故障排除

### 常见问题

#### 1. 导入错误
```python
# 错误
from gto_strategy import GTOCore

# 正确
from poker_assistant.gto_strategy import GTOCore
```

#### 2. 类型错误
```python
# 错误
context = GTOContext(street=123)  # 应该是字符串

# 正确
context = GTOContext(street='preflop')
```

#### 3. 配置错误
```bash
# 确保.env文件存在
cp .env.example .env
# 编辑.env文件，填入正确的API密钥
```

### 调试工具

#### 1. 日志查看
```bash
# 查看实时日志
tail -f logs/gto_engine.log
tail -f logs/ai_engine.log
tail -f logs/game_engine.log
```

#### 2. 性能分析
```bash
# 使用cProfile进行性能分析
python -m cProfile -o profile.stats main.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

#### 3. 内存分析
```bash
# 使用memory_profiler
python -m memory_profiler main.py
```

## 贡献指南

### 1. 代码贡献
1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 运行测试确保通过
5. 提交Pull Request

### 2. 文档贡献
- 更新README.md
- 添加代码注释
- 编写使用指南
- 更新API文档

### 3. 测试贡献
- 增加测试覆盖率
- 添加边界条件测试
- 编写性能测试
- 添加集成测试

### 4. 问题报告
- 使用Issue模板
- 提供详细的复现步骤
- 包含环境信息
- 添加相关日志

## 版本发布

### 1. 版本号规范
遵循语义化版本控制（Semantic Versioning）：
- MAJOR.MINOR.PATCH
- MAJOR: 不兼容的API变更
- MINOR: 向下兼容的功能性新增
- PATCH: 向下兼容的问题修正

### 2. 发布流程
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建发布标签
4. 构建发布包
5. 发布到PyPI

### 3. 发布检查清单
- [ ] 所有测试通过
- [ ] 代码质量检查通过
- [ ] 文档已更新
- [ ] CHANGELOG.md已更新
- [ ] 版本号已更新
- [ ] 发布标签已创建