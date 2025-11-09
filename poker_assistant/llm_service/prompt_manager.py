"""
Prompt 模板管理器
管理和加载 AI 提示词模板
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """Prompt 模板管理器"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化 Prompt 管理器
        
        Args:
            prompts_dir: Prompt 模板目录路径
        """
        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            # 默认使用项目中的 prompts 目录
            current_dir = Path(__file__).parent.parent
            self.prompts_dir = current_dir / "prompts"
        
        # 缓存加载的模板
        self._template_cache: Dict[str, str] = {}
    
    def load_template(self, template_name: str) -> str:
        """
        加载模板文件
        
        Args:
            template_name: 模板名称（不含扩展名）
        
        Returns:
            模板内容
        """
        # 检查缓存
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        # 加载文件
        template_path = self.prompts_dir / f"{template_name}.txt"
        
        if not template_path.exists():
            # 如果文件不存在，使用默认模板
            return self._get_default_template(template_name)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 缓存
            self._template_cache[template_name] = content
            return content
        
        except Exception as e:
            print(f"警告: 加载模板 {template_name} 失败: {e}")
            return self._get_default_template(template_name)
    
    def format_template(self, template_name: str, **kwargs) -> str:
        """
        格式化模板（填充参数）
        
        Args:
            template_name: 模板名称
            **kwargs: 模板参数
        
        Returns:
            格式化后的提示词
        """
        template = self.load_template(template_name)
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"警告: 模板参数缺失: {e}")
            return template
    
    def _get_default_template(self, template_name: str) -> str:
        """
        获取默认模板（当文件不存在时使用）
        
        Args:
            template_name: 模板名称
        
        Returns:
            默认模板内容
        """
        default_templates = {
            "strategy_advice": self._default_strategy_advice(),
            "opponent_analysis": self._default_opponent_analysis(),
            "board_analysis": self._default_board_analysis(),
            "review_analysis": self._default_review_analysis(),
            "chat_system": self._default_chat_system(),
        }
        
        return default_templates.get(template_name, "")
    
    def _default_strategy_advice(self) -> str:
        """默认策略建议模板"""
        return """你是一位专业的德州扑克教练。请分析以下牌局并给出建议：

【当前情况】
- 手牌: {hole_cards}
- 公共牌: {community_cards}
- 街道: {street}
- 位置: {position}
- 底池: ${pot_size}
- 你的筹码: ${stack_size}
- 需要跟注: ${call_amount}

【对手行动】
{opponent_actions}

【可选行动】
{valid_actions}

请分析：
1. 你的手牌强度
2. 当前胜率估算
3. 对手可能的范围
4. 推荐的行动（fold/call/raise）和理由
5. 如果加注，建议的金额

请以JSON格式回复：
{{
  "hand_strength": "强/中/弱",
  "win_probability": 0.65,
  "opponent_range": "...",
  "recommended_action": "call/raise/fold",
  "raise_amount": 100,
  "reasoning": "详细理由",
  "risk_level": "high/medium/low"
}}"""

    def _default_opponent_analysis(self) -> str:
        """默认对手分析模板"""
        return """你是德州扑克分析专家。请分析对手的行动：

【对手信息】
- 对手名称: {opponent_name}
- 行动: {action}
- 金额: ${amount}

【牌局情况】
- 街道: {street}
- 公共牌: {community_cards}
- 底池: ${pot_size}

【历史行动】
{opponent_history}

请分析：
1. 对手可能的手牌范围
2. 该行动的战术意图
3. 对手的打法风格（紧凶/松凶/保守等）
4. 我们的应对策略

请用简洁易懂的中文回复（100-150字）。"""

    def _default_board_analysis(self) -> str:
        """默认牌面分析模板"""
        return """请分析这个德州扑克牌面：

【牌面信息】
- 公共牌: {community_cards}
- 我的手牌: {hole_cards}
- 街道: {street}

请分析：
1. 牌面结构特征（干燥/湿润/危险）
2. 可能存在的听牌（顺子听牌/同花听牌）
3. 你当前的牌力（如果有对子、顺子等，请说明）
4. 改进的可能性（如果还有牌要发）

请用简洁的中文回复（80-120字）。"""

    def _default_review_analysis(self) -> str:
        """默认复盘分析模板"""
        return """你是德州扑克教练，请复盘这局游戏：

【对局信息】
- 回合数: {round_count}
- 最终结果: {result}
- 赢家: {winners}

【手牌】
- 你的手牌: {hole_cards}
- 最终公共牌: {community_cards}

【行动历史】
{action_history}

请提供：
1. 关键决策点分析（2-3个重要决策）
2. 哪些决策是正确的，哪些可以改进
3. 最优打法建议
4. 总体评价和学习建议

请用清晰的段落格式回复（200-300字）。"""

    def _default_chat_system(self) -> str:
        """默认聊天系统提示词"""
        return """你是一位经验丰富的德州扑克教练，名字叫"扑克AI助手"。

你的职责：
1. 回答玩家关于德州扑克的问题
2. 分析当前牌局情况
3. 提供策略建议和学习指导
4. 用通俗易懂的语言解释复杂概念

你的风格：
- 专业但不失友好
- 简洁明了，避免冗长
- 多用例子和类比
- 鼓励玩家思考

当前牌局情况（如果有）：
{game_context}

请回答玩家的问题。"""

    def get_all_templates(self) -> list:
        """
        获取所有可用的模板名称
        
        Returns:
            模板名称列表
        """
        templates = []
        
        # 从文件系统获取
        if self.prompts_dir.exists():
            for file in self.prompts_dir.glob("*.txt"):
                templates.append(file.stem)
        
        # 添加默认模板
        default_names = [
            "strategy_advice",
            "opponent_analysis", 
            "board_analysis",
            "review_analysis",
            "chat_system"
        ]
        
        for name in default_names:
            if name not in templates:
                templates.append(name)
        
        return templates
    
    def clear_cache(self):
        """清除模板缓存"""
        self._template_cache.clear()

