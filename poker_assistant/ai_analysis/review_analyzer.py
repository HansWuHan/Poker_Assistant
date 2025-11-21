"""
复盘分析引擎
对已结束的对局进行深度分析
"""
from typing import Dict, Any, List, Optional

from poker_assistant.llm_service.deepseek_client import DeepseekClient
from poker_assistant.llm_service.prompt_manager import PromptManager
from poker_assistant.utils.card_utils import format_cards


class ReviewAnalyzer:
    """复盘分析引擎"""
    
    def __init__(self,
                 llm_client: Optional[DeepseekClient] = None,
                 prompt_manager: Optional[PromptManager] = None):
        """
        初始化复盘分析引擎
        
        Args:
            llm_client: LLM 客户端
            prompt_manager: Prompt 管理器
        """
        self.llm_client = llm_client or DeepseekClient()
        self.prompt_manager = prompt_manager or PromptManager()
    
    def generate_review(self,
                       round_count: int,
                       hole_cards: List[str],
                       community_cards: List[str],
                       action_history: List[Dict],
                       winners: List[Dict],
                       hand_info: List[Dict],
                       final_pot: int) -> str:
        """
        生成复盘报告
        
        Args:
            round_count: 回合数
            hole_cards: 你的手牌
            community_cards: 最终公共牌
            action_history: 行动历史
            winners: 赢家信息
            hand_info: 手牌信息
            final_pot: 最终底池
        
        Returns:
            复盘报告文本
        """
        try:
            # 格式化数据
            hole_cards_str = format_cards(hole_cards)
            community_cards_str = format_cards(community_cards)
            
            # 格式化赢家
            winners_str = ", ".join([w.get("name", "未知") for w in winners])
            
            # 判断结果
            you_won = any("你" in w.get("name", "") for w in winners)
            result = "胜利" if you_won else "失败"
            
            # 格式化行动历史
            history_str = self._format_action_history(action_history)
            
            # 格式化手牌信息
            hand_info_str = self._format_hand_info(hand_info)
            
            # 构建 prompt - 使用GTO优化版模板
            prompt = self.prompt_manager.format_template(
                "review_analysis_gto",
                round_count=round_count,
                result=result,
                winners=winners_str,
                hole_cards=hole_cards_str,
                community_cards=community_cards_str,
                final_pot=final_pot,
                action_history=history_str,
                hand_info=hand_info_str
            )
            
            # 调用 LLM
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.chat(
                messages, 
                temperature=0.7, 
                max_tokens=1000
            )
            
            return response
        
        except Exception as e:
            return f"复盘分析暂时不可用（{str(e)}）"
    
    def _format_action_history(self, history: List[Dict]) -> str:
        """格式化行动历史"""
        if not history:
            return "无行动记录"
        
        formatted = []
        current_street = ""
        
        for h in history:
            street = h.get("street", "")
            player = h.get("player_name", "")
            action = h.get("action", "")
            amount = h.get("amount", 0)
            
            # 街道标题
            if street != current_street:
                current_street = street
                street_names = {
                    "preflop": "【翻牌前】",
                    "flop": "【翻牌】",
                    "turn": "【转牌】",
                    "river": "【河牌】"
                }
                formatted.append(street_names.get(street, f"【{street}】"))
            
            # 行动
            action_cn = {
                "fold": "弃牌",
                "call": "跟注",
                "raise": "加注",
                "allin": "全下"
            }.get(action, action)
            
            if amount > 0:
                formatted.append(f"  {player}: {action_cn} ${amount}")
            else:
                formatted.append(f"  {player}: {action_cn}")
        
        return "\n".join(formatted)
    
    def _format_hand_info(self, hand_info: List[Dict]) -> str:
        """格式化手牌信息"""
        if not hand_info:
            return "无手牌信息"
        
        formatted = []
        for info in hand_info:
            name = info.get("name", "未知")
            hand = info.get("hand", {})
            hand_type = hand.get("hand", {}).get("hand", "未知")
            
            # 手牌类型中文化
            hand_names = {
                "highcard": "高牌",
                "onepair": "一对",
                "twopair": "两对",
                "threecard": "三条",
                "straight": "顺子",
                "flush": "同花",
                "fullhouse": "葫芦",
                "fourcard": "四条",
                "straightflush": "同花顺"
            }
            hand_type_cn = hand_names.get(hand_type, hand_type)
            
            formatted.append(f"{name}: {hand_type_cn}")
        
        return "；".join(formatted)

