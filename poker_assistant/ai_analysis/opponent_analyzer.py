"""
对手分析引擎
分析对手行动并推测其策略
"""
from typing import Dict, Any, List, Optional

from poker_assistant.llm_service.deepseek_client import DeepseekClient
from poker_assistant.llm_service.prompt_manager import PromptManager
from poker_assistant.llm_service.context_manager import ContextManager
from poker_assistant.utils.card_utils import format_cards, get_street_name


class OpponentAnalyzer:
    """对手行动分析引擎（支持上下文）"""
    
    def __init__(self,
                 llm_client: Optional[DeepseekClient] = None,
                 prompt_manager: Optional[PromptManager] = None,
                 context_manager: Optional[ContextManager] = None):
        """
        初始化对手分析引擎
        
        Args:
            llm_client: LLM 客户端
            prompt_manager: Prompt 管理器
            context_manager: 上下文管理器
        """
        self.llm_client = llm_client or DeepseekClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = context_manager or ContextManager()
        self.opponent_modeler = None
    
    def start_new_round(self, round_id: str):
        """开始新一局"""
        self.context_manager.clear_history()
    
    def set_opponent_modeler(self, opponent_modeler):
        """设置对手建模器"""
        self.opponent_modeler = opponent_modeler
    
    def analyze_action(self,
                      opponent_name: str,
                      action: str,
                      amount: int,
                      street: str,
                      community_cards: List[str],
                      pot_size: int,
                      previous_pot: int = 0,
                      opponent_history: Optional[List[Dict]] = None) -> str:
        """
        分析对手行动
        
        Args:
            opponent_name: 对手名称
            action: 行动类型
            amount: 金额
            street: 街道
            community_cards: 公共牌
            pot_size: 当前底池
            previous_pot: 之前底池
            opponent_history: 对手历史行动
        
        Returns:
            分析文本
        """
        try:
            # 格式化数据
            action_cn = {
                "fold": "弃牌",
                "call": "跟注",
                "raise": "加注",
                "allin": "全下"
            }.get(action, action)
            
            street_cn = get_street_name(street)
            community_cards_str = format_cards(community_cards) if community_cards else "无"
            
            # 格式化历史
            history_str = self._format_history(opponent_history) if opponent_history else "暂无历史行动"
            
            # 构建 prompt
            prompt = self.prompt_manager.format_template(
                "opponent_analysis",
                opponent_name=opponent_name,
                action=action_cn,
                amount=amount,
                street=street_cn,
                community_cards=community_cards_str,
                pot_size=pot_size,
                previous_pot=previous_pot,
                opponent_history=history_str
            )
            
            # 添加对手历史信息
            import os
            if self.opponent_modeler and opponent_name:
                opponent_profile = self.opponent_modeler.get_opponent_summary(
                    opponent_name, detailed=True
                )
                prompt += f"\n\n【对手历史特点】\n{opponent_profile}"
            
            # 构建消息列表（包含历史）
            messages = []
            history = list(self.context_manager.conversation_history)[-4:]
            for msg in history:
                messages.append(msg)
            
            messages.append({"role": "user", "content": prompt})
            
            # 调用 LLM (提升 max_tokens 到 2500)
            debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
            response = self.llm_client.chat(
                messages, 
                temperature=0.7, 
                max_tokens=2500,  # 提升到 2500
                debug=debug_mode
            )
            
            # 保存到历史
            self.context_manager.add_user_message(prompt)
            self.context_manager.add_assistant_message(response)
            
            return response
        
        except Exception as e:
            return f"对手分析暂时不可用（{str(e)}）"
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化历史行动"""
        if not history:
            return "无"
        
        formatted = []
        for h in history[-5:]:  # 最近5条
            street = h.get("street", "")
            action = h.get("action", "")
            amount = h.get("amount", 0)
            
            action_cn = {
                "fold": "弃牌",
                "call": "跟注",
                "raise": "加注",
                "allin": "全下"
            }.get(action, action)
            
            street_cn = get_street_name(street)
            
            if amount > 0:
                formatted.append(f"{street_cn}: {action_cn} ${amount}")
            else:
                formatted.append(f"{street_cn}: {action_cn}")
        
        return "；".join(formatted)

