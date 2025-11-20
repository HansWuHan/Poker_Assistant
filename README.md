# 🎰 德州扑克 AI 助手

一个集成 AI 大模型分析能力的德州扑克学习与练习平台。
<img width="1159" height="672" alt="image" src="https://github.com/user-attachments/assets/256d4eea-f133-41dc-8e2f-6b04cd498a12" />


## ✨ 特性

- 🎮 **6人桌真实德州扑克体验** - 基于 PyPokerEngine 的完整德州扑克引擎
- 🤖 **AI 策略建议** - 按需获取专业的 AI 牌力分析和行动建议
- 🔍 **对手行动解读** - AI 实时分析对手行为和可能的手牌范围
- 📊 **公共牌面分析** - 智能分析牌面结构和胜率
- 📝 **对局复盘** - 每局结束后的详细复盘报告
- 💬 **自由提问** - 对局中随时向 AI 提问

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Deepseek API Key

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd Poker_Assistant

# 创建虚拟环境
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# myenv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Deepseek API Key
```

### 配置 API Key

在 `.env` 文件中配置你的 Deepseek API Key：

```bash
DEEPSEEK_API_KEY=your_api_key_here
```

> 💡 如何获取 Deepseek API Key：访问 https://platform.deepseek.com/

### 运行

```bash
python main.py
```

## 🎮 使用指南

### 基础操作

- **F** - Fold (弃牌)
- **C** - Call (跟注)
- **R** - Raise (加注)
- **A** - All-in (全下)
- **O** - AI分析 (获取牌力分析)
- **Q** - Question (向 AI 提问)
- **H** - Help (显示帮助)
- **S** - Status (显示状态)

### AI 功能

#### 1. 策略建议
按 **O** 键获取AI牌力分析：
- 推荐的行动
- 建议的金额
- 详细的理由说明
- 胜率估算

#### 2. 对手分析
每个对手行动后，AI 会解读：
- 可能的手牌范围
- 行动的战术意图
- 打法风格判断
- 应对策略

#### 3. 牌面分析
公共牌发出时，AI 会分析：
- 牌面的结构特征
- 可能的听牌
- 你的牌力等级
- 改进的可能性

#### 4. 对局复盘
每局结束后，AI 提供：
- 关键决策点分析
- 错误决策标注
- 最优打法建议
- 整体表现评价

#### 5. 自由提问
按 **Q** 键可以随时向 AI 提问：
- "这个牌面我应该怎么打？"
- "对手可能拿什么牌？"
- "什么是 GTO 策略？"
- "我刚才那手牌打得对吗？"

## 📁 项目结构

```
Poker_Assistant/
├── poker_assistant/        # 主包
│   ├── engine/            # 游戏引擎
│   ├── ai_analysis/       # AI 分析模块
│   ├── llm_service/       # LLM 服务
│   ├── cli/               # 命令行界面
│   ├── data/              # 数据持久化
│   ├── utils/             # 工具函数
│   └── prompts/           # AI Prompt 模板
├── tests/                 # 测试
├── data/                  # 数据目录
├── logs/                  # 日志
└── main.py               # 主入口
```

## ⚙️ 配置

### 游戏配置

编辑 `poker_assistant/utils/config.py` 可以修改：
- 初始筹码
- 盲注大小
- 游戏回合数
- AI 对手难度

### AI 配置

可以调整：
- AI 分析详细程度
- 是否自动显示建议
- LLM 模型参数

## 🧪 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black poker_assistant/
```

## 📊 数据统计

游戏会自动记录：
- 对局历史
- 胜率统计
- 盈利/亏损
- AI 建议采纳率

数据保存在 `data/` 目录下。

## 🔧 常见问题

### Q: API 调用太慢怎么办？
A: 可以在配置中调整 AI 分析详细程度为 `low`，或者禁用部分 AI 功能。

### Q: API 调用失败？
A: 请检查：
1. API Key 是否正确配置
2. 网络连接是否正常
3. API 额度是否充足

### Q: 想要调整游戏难度？
A: 修改 `poker_assistant/utils/config.py` 中的 AI 对手配置。

## 🗺️ Roadmap

- [x] MVP 基础功能
- [ ] Web 界面
- [ ] 更高级的 AI 对手
- [ ] 多桌训练模式
- [ ] 策略库和预设
- [ ] 移动端支持

## 📄 许可

MIT License

## 🙏 致谢

- [PyPokerEngine](https://github.com/ishikota/PyPokerEngine) - 优秀的德州扑克引擎
- [Deepseek](https://www.deepseek.com/) - 强大的 AI 能力

## 📮 反馈

如有问题或建议，欢迎提 Issue 或 Pull Request！

---

**祝你玩得开心，牌技进步！🎰**


