# 🔑 如何配置 Deepseek API Key

## 📋 快速指南

### 步骤 1: 获取 API Key

1. 访问 Deepseek 官网：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 **API Keys** 页面
4. 点击 **创建新的 API Key**
5. 复制生成的 API Key（格式类似：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`）

### 步骤 2: 配置到项目

打开项目中的 `.env` 文件，找到这一行：

```bash
DEEPSEEK_API_KEY=your_api_key_here
```

将 `your_api_key_here` 替换为你的真实 API Key：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

💡 **提示**: 确保没有多余的空格或引号。

### 步骤 3: 测试连接

运行测试脚本验证配置：

```bash
cd /Users/mac/Codinnnnng/Poker_Assistant
python3 test_phase2.py
```

如果配置正确，你会看到：

```
============================================================
🧪 Phase 2 LLM 服务集成测试
============================================================

测试 1: 配置验证             ✅ 通过
测试 2: Deepseek 客户端      ✅ 通过
...

🎉 恭喜！Phase 2 LLM 服务集成完成
```

---

## 💰 关于费用

### Deepseek 定价（非常便宜）

- Input: ~$0.0007 / 1K tokens
- Output: ~$0.002 / 1K tokens
- 平均: **~$0.001 / 1K tokens**

### 使用成本估算

| 场景 | Tokens | 费用 |
|------|--------|------|
| 一次策略建议 | ~700 | $0.0007 |
| 一局游戏（5次建议） | ~3500 | $0.0035 |
| 100局游戏 | ~350K | ~$0.35 |

💡 **非常实惠！** 充值 $5 可以玩很久。

---

## ⚙️ 完整的 .env 配置示例

```bash
# Deepseek API Configuration
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Game Configuration
GAME_INITIAL_STACK=1000
GAME_SMALL_BLIND=5
GAME_BIG_BLIND=10
GAME_MAX_ROUND=100
GAME_PLAYER_COUNT=6

# AI Configuration
AI_ANALYSIS_LEVEL=medium
AI_AUTO_SHOW_ADVICE=true
AI_ENABLE_OPPONENT_ANALYSIS=true
AI_ENABLE_BOARD_ANALYSIS=true
AI_ENABLE_REVIEW=true
AI_ENABLE_CHAT=true

# LLM Configuration
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=30

# Debug Configuration
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=logs/poker_assistant.log
```

---

## 🐛 常见问题

### Q: 提示 "未配置有效的 DEEPSEEK_API_KEY"

**A**: 检查以下几点：
1. `.env` 文件是否存在
2. API Key 是否正确粘贴（以 `sk-` 开头）
3. 是否有多余的空格或引号
4. 文件保存后是否重新运行测试

### Q: 提示 "API 连接测试失败"

**A**: 可能的原因：
1. API Key 无效或已过期
2. 网络连接问题
3. API 额度不足（需要充值）
4. Deepseek 服务暂时不可用

解决方法：
```bash
# 检查网络
ping api.deepseek.com

# 检查 API Key 格式
cat .env | grep DEEPSEEK_API_KEY

# 重新生成 API Key
# 访问 https://platform.deepseek.com/api-keys
```

### Q: 如何查看 API 使用情况？

**A**: 访问 Deepseek 控制台：
- https://platform.deepseek.com/usage

可以查看：
- 今日使用量
- 总使用量
- 余额
- 消费记录

### Q: API Key 安全吗？

**A**: `.env` 文件已被 `.gitignore` 忽略，不会被提交到 Git。
但仍需注意：
- ❌ 不要把 `.env` 文件分享给别人
- ❌ 不要把 API Key 贴在公开场合
- ✅ 定期轮换 API Key
- ✅ 设置使用额度限制

---

## ✅ 验证清单

配置完成后，确认以下几点：

- [ ] `.env` 文件中有正确的 API Key
- [ ] 运行 `python3 test_phase2.py` 全部通过
- [ ] 可以看到 AI 的回复内容
- [ ] 没有错误提示
- [ ] API 统计信息显示正常

---

## 🚀 配置完成后

恭喜！你已经完成了 Phase 2 的配置。现在可以：

1. **测试 AI 对话**
   ```bash
   python3 test_phase2.py
   ```

2. **开始 Phase 3 开发**
   - AI 策略建议
   - 对手行动分析
   - 牌面分析
   - 对局复盘
   - 自由提问

3. **或者先玩几局游戏**
   ```bash
   python3 main.py
   ```
   （Phase 1 的基础游戏依然可玩）

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 `PHASE2_COMPLETE.md` 的详细文档
2. 检查日志文件 `logs/poker_assistant.log`
3. 确保 Python 版本 >= 3.8
4. 确保所有依赖已安装：
   ```bash
   pip3 install -r requirements.txt
   ```

---

**祝你配置顺利！🎉**

配置完成后告诉我，我们可以继续开发 Phase 3 了！

