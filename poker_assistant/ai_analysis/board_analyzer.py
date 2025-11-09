"""
牌面分析引擎
分析公共牌面结构和玩家牌力
"""
from typing import List, Optional

from poker_assistant.llm_service.deepseek_client import DeepseekClient
from poker_assistant.llm_service.prompt_manager import PromptManager
from poker_assistant.llm_service.context_manager import ContextManager
from poker_assistant.utils.card_utils import format_cards, get_street_name


class BoardAnalyzer:
    """牌面分析引擎（支持上下文）"""
    
    def __init__(self,
                 llm_client: Optional[DeepseekClient] = None,
                 prompt_manager: Optional[PromptManager] = None,
                 context_manager: Optional[ContextManager] = None):
        """
        初始化牌面分析引擎
        
        Args:
            llm_client: LLM 客户端
            prompt_manager: Prompt 管理器
            context_manager: 上下文管理器
        """
        self.llm_client = llm_client or DeepseekClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = context_manager or ContextManager()
    
    def start_new_round(self, round_id: str):
        """开始新一局"""
        self.context_manager.clear_history()
    
    def analyze_board(self,
                     community_cards: List[str],
                     hole_cards: List[str],
                     street: str) -> str:
        """
        分析牌面
        
        Args:
            community_cards: 公共牌
            hole_cards: 手牌
            street: 街道
        
        Returns:
            分析文本
        """
        try:
            # 格式化数据
            community_cards_str = format_cards(community_cards) if community_cards else "无"
            hole_cards_str = format_cards(hole_cards)
            street_cn = get_street_name(street)
            
            # 构建 prompt
            prompt = self.prompt_manager.format_template(
                "board_analysis",
                community_cards=community_cards_str,
                hole_cards=hole_cards_str,
                street=street_cn
            )
            
            # 构建消息列表（包含历史）
            import os
            messages = []
            history = list(self.context_manager.conversation_history)[-4:]
            for msg in history:
                messages.append(msg)
            
            if history:
                prompt += "\n\n【上下文】请结合之前的牌面分析，关注牌面的变化。"
            
            messages.append({"role": "user", "content": prompt})
            
            # 调用 LLM (提升 max_tokens 到 2000)
            debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
            response = self.llm_client.chat(
                messages, 
                temperature=0.7, 
                max_tokens=2000,  # 提升到 2000
                debug=debug_mode
            )
            
            # 保存到历史
            self.context_manager.add_user_message(prompt)
            self.context_manager.add_assistant_message(response)
            
            return response
        
        except Exception as e:
            return f"牌面分析暂时不可用（{str(e)}）"

