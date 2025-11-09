"""
策略建议引擎
为玩家提供实时的行动建议
"""
from typing import Dict, Any, List, Optional
import json
import os

from poker_assistant.llm_service.deepseek_client import DeepseekClient
from poker_assistant.llm_service.prompt_manager import PromptManager
from poker_assistant.llm_service.context_manager import ContextManager
from poker_assistant.utils.card_utils import format_cards, get_street_name, format_chips


class StrategyAdvisor:
    """策略建议引擎（支持局内上下文）"""
    
    def __init__(self, 
                 llm_client: Optional[DeepseekClient] = None,
                 prompt_manager: Optional[PromptManager] = None,
                 context_manager: Optional[ContextManager] = None):
        """
        初始化策略建议引擎
        
        Args:
            llm_client: LLM 客户端
            prompt_manager: Prompt 管理器
            context_manager: 上下文管理器（用于保留局内历史）
        """
        self.llm_client = llm_client or DeepseekClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = context_manager or ContextManager()
        
        # 当前局 ID
        self.current_round_id: Optional[str] = None
        
        # 对手建模器引用（外部传入）
        self.opponent_modeler = None
    
    def start_new_round(self, round_id: str):
        """
        开始新一局
        
        Args:
            round_id: 局号
        """
        self.current_round_id = round_id
        self.context_manager.clear_history()
    
    def set_opponent_modeler(self, opponent_modeler):
        """设置对手建模器"""
        self.opponent_modeler = opponent_modeler
    
    def get_advice(self,
                   hole_cards: List[str],
                   community_cards: List[str],
                   street: str,
                   position: str,
                   pot_size: int,
                   stack_size: int,
                   call_amount: int,
                   valid_actions: List[Dict],
                   opponent_actions: Optional[List[Dict]] = None,
                   active_opponents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取策略建议
        
        Args:
            hole_cards: 手牌
            community_cards: 公共牌
            street: 当前街道
            position: 位置
            pot_size: 底池大小
            stack_size: 筹码数量
            call_amount: 需要跟注的金额
            valid_actions: 可选行动
            opponent_actions: 对手行动历史
        
        Returns:
            建议结果字典
        """
        try:
            # 格式化数据
            hole_cards_str = format_cards(hole_cards)
            community_cards_str = format_cards(community_cards) if community_cards else "无"
            street_cn = get_street_name(street)
            
            # 格式化对手行动（传递当前底池大小用于计算下注尺度）
            if opponent_actions and len(opponent_actions) > 0:
                actions_str = self._format_opponent_actions(opponent_actions, pot_size)
            else:
                actions_str = "对手尚未行动"
            
            # 格式化可选行动
            valid_actions_str = self._format_valid_actions(valid_actions)
            
            # 添加对手建模信息
            opponent_info = ""
            if self.opponent_modeler and active_opponents:
                opponent_summaries = []
                for opp_name in active_opponents:
                    summary = self.opponent_modeler.get_opponent_summary(opp_name, detailed=True)
                    opponent_summaries.append(summary)
                if opponent_summaries:
                    opponent_info = "\n\n【对手特点】\n" + "\n".join(opponent_summaries)
            
            # 构建 prompt
            current_prompt = self.prompt_manager.format_template(
                "strategy_advice",
                hole_cards=hole_cards_str,
                community_cards=community_cards_str,
                street=street_cn,
                position=position,
                pot_size=pot_size,
                stack_size=stack_size,
                call_amount=call_amount,
                opponent_actions=actions_str,
                valid_actions=valid_actions_str
            )
            
            # 添加对手信息
            if opponent_info:
                current_prompt += opponent_info
            
            # 构建消息列表（包含局内历史）
            messages = []
            
            # 添加本局之前的建议（最近2轮 = 4条消息）
            history = list(self.context_manager.conversation_history)[-4:]
            for msg in history:
                messages.append(msg)
            
            # 如果有历史，添加上下文提示
            if history:
                context_hint = "\n\n【上下文】你在本局之前已经给出过建议，请保持策略连贯性。"
                current_prompt += context_hint
            
            # 添加当前请求
            messages.append({"role": "user", "content": current_prompt})
            
            # 调用 LLM (提升 max_tokens 到 3000)
            debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
            response = self.llm_client.chat(
                messages, 
                temperature=0.7, 
                max_tokens=3000,  # 提升到 3000
                debug=debug_mode
            )
            
            # 保存到历史
            self.context_manager.add_user_message(current_prompt)
            self.context_manager.add_assistant_message(response)
            
            # 解析响应
            advice = self._parse_response(response)
            
            # 添加原始数据
            advice["raw_response"] = response
            advice["pot_size"] = pot_size
            advice["stack_size"] = stack_size
            advice["call_amount"] = call_amount
            
            return advice
        
        except Exception as e:
            # 错误处理：返回降级建议
            return self._fallback_advice(e, valid_actions)
    
    def get_simple_advice(self,
                         hole_cards: List[str],
                         community_cards: List[str],
                         pot_size: int,
                         call_amount: int,
                         valid_actions: List[Dict]) -> str:
        """
        获取简化的文本建议（更快）
        
        Args:
            hole_cards: 手牌
            community_cards: 公共牌
            pot_size: 底池
            call_amount: 跟注金额
            valid_actions: 可选行动
        
        Returns:
            建议文本
        """
        try:
            advice = self.get_advice(
                hole_cards=hole_cards,
                community_cards=community_cards,
                street="flop",  # 默认
                position="",
                pot_size=pot_size,
                stack_size=1000,  # 默认
                call_amount=call_amount,
                valid_actions=valid_actions
            )
            
            return advice.get("reasoning", "暂无建议")
        
        except Exception as e:
            return f"获取建议时出错: {str(e)}"
    
    def _format_opponent_actions(self, actions: List[Dict], pot_size: int = 0) -> str:
        """格式化对手行动历史（包含下注尺度分析）"""
        if not actions:
            return "无"
        
        formatted = []
        for action in actions[-5:]:  # 只显示最近5个行动
            player = action.get("player", "对手")
            action_type = action.get("action", "")
            amount = action.get("amount", 0)
            
            action_cn = {
                "fold": "弃牌",
                "call": "跟注",
                "check": "过牌",
                "raise": "加注",
                "allin": "全下"
            }.get(action_type, action_type)
            
            if amount > 0:
                # 计算下注尺度（相对于底池）
                if pot_size > 0:
                    bet_to_pot_ratio = amount / pot_size
                    
                    # 描述下注尺度
                    if bet_to_pot_ratio < 0.33:
                        size_desc = "（小额下注，约1/4底池）"
                    elif bet_to_pot_ratio < 0.5:
                        size_desc = "（小额下注，约1/3底池）"
                    elif bet_to_pot_ratio < 0.75:
                        size_desc = "（中等下注，约1/2-2/3底池）"
                    elif bet_to_pot_ratio < 1.2:
                        size_desc = "（标准下注，约底池大小）"
                    elif bet_to_pot_ratio < 2.0:
                        size_desc = "（超额下注，约1.5倍底池）"
                    else:
                        size_desc = "（大额超额下注，2倍底池以上）"
                    
                    formatted.append(f"{player} {action_cn} ${amount}{size_desc}")
                else:
                    formatted.append(f"{player} {action_cn} ${amount}")
            else:
                formatted.append(f"{player} {action_cn}")
        
        return "；".join(formatted)
    
    def _format_valid_actions(self, valid_actions: List[Dict]) -> str:
        """格式化可选行动"""
        actions = []
        
        for action_info in valid_actions:
            action = action_info.get("action", "")
            
            if action == "fold":
                actions.append("弃牌")
            elif action == "call":
                amount = action_info.get("amount", 0)
                actions.append(f"跟注 ${amount}")
            elif action == "raise":
                min_amount = action_info.get("amount", {}).get("min", 0)
                max_amount = action_info.get("amount", {}).get("max", 0)
                if min_amount > 0:
                    actions.append(f"加注 ${min_amount}-${max_amount}")
        
        return " / ".join(actions)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析 AI 响应
        
        Args:
            response: AI 响应文本
        
        Returns:
            解析后的建议字典
        """
        # 尝试提取关键信息
        advice = {
            "reasoning": response,
            "recommended_action": self._extract_action(response),
            "confidence": "medium"
        }
        
        # 尝试解析 JSON（如果 AI 返回了结构化数据）
        try:
            # 查找 JSON 块
            if "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                advice.update(parsed)
        except:
            pass
        
        return advice
    
    def _extract_action(self, text: str) -> str:
        """从文本中提取推荐行动"""
        text_lower = text.lower()
        
        if "弃牌" in text or "fold" in text_lower:
            return "fold"
        elif "加注" in text or "raise" in text_lower:
            return "raise"
        elif "跟注" in text or "call" in text_lower:
            return "call"
        elif "过牌" in text or "check" in text_lower:
            return "call"  # 过牌相当于跟注0
        
        return "call"  # 默认跟注
    
    def _fallback_advice(self, error: Exception, valid_actions: List[Dict]) -> Dict[str, Any]:
        """降级建议（当 API 失败时）"""
        return {
            "reasoning": f"AI 建议暂时不可用（{str(error)}）。请根据自己的判断决定。",
            "recommended_action": "call",
            "confidence": "low",
            "error": str(error)
        }
    
    def format_advice_display(self, advice: Dict[str, Any]) -> str:
        """
        格式化建议用于显示
        
        Args:
            advice: 建议字典
        
        Returns:
            格式化的文本
        """
        lines = []
        
        # 推荐行动
        action = advice.get("recommended_action", "")
        action_cn = {
            "fold": "弃牌",
            "call": "跟注",
            "raise": "加注"
        }.get(action, action)
        
        lines.append(f"💡 推荐行动: {action_cn}")
        
        # 建议金额（如果是加注）
        if action == "raise" and "raise_amount" in advice:
            amount = advice["raise_amount"]
            lines.append(f"💰 建议金额: ${amount}")
        
        # 理由
        reasoning = advice.get("reasoning", "")
        if reasoning:
            lines.append(f"\n📝 理由:\n{reasoning}")
        
        # 胜率（如果有）
        if "win_probability" in advice:
            win_prob = advice["win_probability"]
            if isinstance(win_prob, (int, float)):
                lines.append(f"\n📊 胜率估算: {win_prob*100:.0f}%")
        
        # 风险等级（如果有）
        if "risk_level" in advice:
            risk = advice["risk_level"]
            risk_icon = {
                "low": "🟢",
                "medium": "🟡",
                "high": "🔴"
            }.get(risk, "⚪")
            lines.append(f"{risk_icon} 风险等级: {risk}")
        
        return "\n".join(lines)

