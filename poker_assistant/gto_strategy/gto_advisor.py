"""
GTO策略顾问 - 将GTO策略集成到现有AI框架中
"""
from typing import Dict, List, Any, Optional, Tuple
from .gto_core import GTOCore, GTOSituation, GTOAction
from .range_manager import RangeManager
from .sizing_optimizer import SizingOptimizer, SizingContext
from .frequency_calculator import FrequencyCalculator, FrequencyContext
from .types import GTOContext, GTOResult, FrequencyResult, SizingRecommendation


class GTOAdvisor:
    """GTO策略顾问 - 桥接GTO策略和现有AI逻辑"""
    
    def __init__(self, 
                 gto_core: Optional[GTOCore] = None,
                 range_manager: Optional[RangeManager] = None,
                 sizing_optimizer: Optional[SizingOptimizer] = None,
                 frequency_calculator: Optional[FrequencyCalculator] = None):
        """
        初始化GTO顾问
        
        Args:
            gto_core: GTO核心引擎
            range_manager: 范围管理器
            sizing_optimizer: 尺度优化器
            frequency_calculator: 频率计算器
        """
        self.gto_core = gto_core or GTOCore()
        self.range_manager = range_manager or RangeManager()
        self.sizing_optimizer = sizing_optimizer or SizingOptimizer()
        self.frequency_calculator = frequency_calculator or FrequencyCalculator()
        
        # 配置参数
        self.gto_weight = 0.7  # GTO策略权重
        self.exploitative_weight = 0.3  # 剥削策略权重
        self.use_mixed_strategy = True  # 是否使用混合策略
        
        # 历史记录
        self.gto_history = []
        self.exploit_history = []
        
    def get_gto_advice(self, 
                      hole_cards: List[str],
                      community_cards: List[str],
                      street: str,
                      position: str,
                      pot_size: int,
                      stack_size: int,
                      call_amount: int,
                      valid_actions: List[Dict],
                      opponent_actions: List[Dict],
                      active_opponents: List[str]) -> Dict[str, Any]:
        """
        获取GTO策略建议（向后兼容方法）
        
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
            active_opponents: 活跃对手列表
            
        Returns:
            GTO建议字典
        """
        try:
            # 使用新的类型系统
            context = GTOContext(
                street=street,
                position=position,
                stack_size=stack_size,
                pot_size=pot_size,
                community_cards=community_cards,
                hole_cards=hole_cards,
                opponent_actions=opponent_actions,
                active_opponents=len(active_opponents),
                call_amount=call_amount,
                valid_actions=valid_actions
            )
            
            # 使用新的GTO计算方法
            gto_result = self.gto_core.calculate_gto_action_new(context)
            
            # 转换为旧的返回格式以保持兼容性
            return {
                'action': gto_result.action,
                'amount': gto_result.amount,
                'confidence': gto_result.confidence,
                'reasoning': gto_result.reasoning,
                'gto_explanation': gto_result.gto_explanation,
                'frequencies': gto_result.frequencies,
                'sizing_recommendation': {
                    'optimal_sizing': gto_result.sizing_recommendation.optimal_sizing,
                    'explanation': gto_result.sizing_recommendation.explanation,
                    'min_sizing': gto_result.sizing_recommendation.min_sizing,
                    'max_sizing': gto_result.sizing_recommendation.max_sizing
                },
                'range_analysis': gto_result.range_analysis,
                'balance_metrics': gto_result.balance_metrics,
                'exploit_opportunities': gto_result.exploit_opportunities
            }
            
        except Exception as e:
            # 回退到旧的GTO逻辑
            return self._get_gto_advice_legacy(
                hole_cards, community_cards, street, position, pot_size, stack_size,
                call_amount, valid_actions, opponent_actions, active_opponents
            )
    
    def _get_gto_advice_legacy(self, hole_cards: List[str], community_cards: List[str], 
                               street: str, position: str, pot_size: int, stack_size: int,
                               call_amount: int, valid_actions: List[Dict], 
                               opponent_actions: List[Dict], active_opponents: List[str]) -> Dict[str, Any]:
        """旧的GTO建议方法（向后兼容）"""
        # 创建GTO情境
        gto_situation = GTOSituation(
            street=street,
            position=position,
            stack_size=stack_size,
            pot_size=pot_size,
            community_cards=community_cards,
            hole_cards=hole_cards,
            opponent_actions=opponent_actions,
            active_opponents=len(active_opponents)
        )
        
        # 计算GTO行动
        gto_action = self.gto_core.calculate_gto_action(gto_situation)
        
        # 计算频率分析
        freq_context = FrequencyContext(
            street=street,
            position=position,
            hand_strength=self._estimate_hand_strength(hole_cards, community_cards),
            board_texture=self._evaluate_board_texture(community_cards),
            pot_size=pot_size,
            stack_size=stack_size,
            opponent_tendency=self._estimate_opponent_tendency(opponent_actions),
            previous_action=self._get_previous_action(opponent_actions),
            is_ip=self._has_position_advantage(position),
            num_opponents=len(active_opponents)
        )
        
        frequencies = self.frequency_calculator.calculate_optimal_frequencies(freq_context)
        
        # 计算尺度优化
        sizing_context = SizingContext(
            street=street,
            position=position,
            pot_size=pot_size,
            stack_size=stack_size,
            effective_stack=min(stack_size, stack_size - call_amount),
            board_texture=self._evaluate_board_texture(community_cards),
            hand_strength=self._estimate_hand_strength(hole_cards, community_cards),
            opponent_tendency=self._estimate_opponent_tendency(opponent_actions),
            is_ip=self._has_position_advantage(position),
            previous_action=self._get_previous_action(opponent_actions)
        )
        
        # 创建综合建议
        advice = {
            'action': gto_action.action,
            'amount': gto_action.amount,
            'confidence': self._calculate_confidence(gto_action, frequencies),
            'reasoning': self._build_gto_reasoning(gto_action, frequencies, gto_situation),
            'gto_explanation': gto_action.reasoning,
            'frequencies': frequencies,
            'sizing_recommendation': self._get_sizing_recommendation(sizing_context, gto_action.action),
            'range_analysis': self._analyze_range_fit(hole_cards, position, street),
            'balance_metrics': self._calculate_balance_metrics(),
            'exploit_opportunities': self._identify_exploit_opportunities(opponent_actions)
        }
        
        # 记录历史
        self.gto_history.append({
            'situation': gto_situation,
            'action': gto_action,
            'frequencies': frequencies
        })
        
        return advice
    
    def blend_with_exploitative(self, gto_advice: Dict[str, Any], exploitative_advice: Dict[str, Any]) -> Dict[str, Any]:
        """
        将GTO策略与剥削策略混合
        
        Args:
            gto_advice: GTO建议
            exploitative_advice: 剥削建议
            
        Returns:
            混合策略建议
        """
        # 如果任一建议缺失，返回另一个
        if not gto_advice:
            return exploitative_advice
        if not exploitative_advice:
            return gto_advice
        
        # 混合行动选择
        if gto_advice['action'] == exploitative_advice['action']:
            # 行动一致，混合金额
            blended_amount = int(
                gto_advice['amount'] * self.gto_weight + 
                exploitative_advice.get('amount', gto_advice['amount']) * self.exploitative_weight
            )
            
            return {
                'action': gto_advice['action'],
                'amount': blended_amount,
                'confidence': max(gto_advice['confidence'], exploitative_advice.get('confidence', 0.5)),
                'reasoning': f"GTO+剥削混合策略: {gto_advice['reasoning']}",
                'gto_component': gto_advice,
                'exploitative_component': exploitative_advice,
                'blend_ratio': f"GTO:{self.gto_weight:.1f}/EXP:{self.exploitative_weight:.1f}"
            }
        else:
            # 行动不一致，根据权重选择
            import random
            if random.random() < self.gto_weight:
                return gto_advice
            else:
                return exploitative_advice
    
    def get_gto_vs_exploitative_comparison(self, situation: GTOSituation) -> Dict[str, Any]:
        """
        比较GTO策略和剥削策略
        
        Args:
            situation: GTO情境
            
        Returns:
            比较分析
        """
        gto_action = self.gto_core.calculate_gto_action(situation)
        
        # 模拟剥削策略（这里应该调用现有的剥削逻辑）
        exploitative_action = self._simulate_exploitative_action(situation)
        
        return {
            'gto_action': {
                'action': gto_action.action,
                'amount': gto_action.amount,
                'reasoning': gto_action.reasoning,
                'balance_score': 0.95,  # GTO策略平衡性很高
                'exploitability': 0.1
            },
            'exploitative_action': {
                'action': exploitative_action['action'],
                'amount': exploitative_action['amount'],
                'reasoning': exploitative_action['reasoning'],
                'balance_score': 0.6,   # 剥削策略平衡性较低
                'exploitability': 0.3
            },
            'recommendation': self._recommend_strategy_type(situation)
        }
    
    def _estimate_hand_strength(self, hole_cards: List[str], community_cards: List[str]) -> float:
        """估算手牌强度"""
        # 简化实现，实际应该使用更复杂的评估
        if not hole_cards or len(hole_cards) < 2:
            return 0.0
        
        # 基于现有逻辑的简化版本
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, rank2 = card1[1], card2[1]
        
        # 对子
        if rank1 == rank2:
            ranks_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
            rank_index = ranks_order.index(rank1) if rank1 in ranks_order else 0
            return 0.5 + (rank_index / len(ranks_order)) * 0.5
        
        # 同花
        if card1[0] == card2[0]:
            return 0.6
        
        # 高牌
        high_cards = ['A', 'K', 'Q', 'J', 'T']
        if rank1 in high_cards and rank2 in high_cards:
            return 0.7
        elif rank1 in high_cards or rank2 in high_cards:
            return 0.4
        
        return 0.3
    
    def _evaluate_board_texture(self, community_cards: List[str]) -> str:
        """评估牌面纹理"""
        if not community_cards or len(community_cards) < 3:
            return 'dry'
        
        # 简化的牌面评估
        # 这里应该实现更复杂的逻辑
        return 'dynamic'
    
    def _estimate_opponent_tendency(self, opponent_actions: List[Dict]) -> float:
        """估算对手倾向"""
        if not opponent_actions:
            return 1.0
        
        aggressive_actions = 0
        total_actions = len(opponent_actions)
        
        for action in opponent_actions:
            if action.get('action') in ['raise', 'allin']:
                aggressive_actions += 1
        
        aggression_rate = aggressive_actions / total_actions if total_actions > 0 else 0.5
        return aggression_rate * 2.0  # 标准化到0-2范围
    
    def _get_previous_action(self, opponent_actions: List[Dict]) -> str:
        """获取对手上一个行动"""
        if not opponent_actions:
            return 'none'
        
        last_action = opponent_actions[-1]
        return last_action.get('action', 'none')
    
    def _has_position_advantage(self, position: str) -> bool:
        """判断是否有位置优势"""
        return position in ['BTN', 'CO', 'HJ']
    
    def _calculate_confidence(self, gto_action: GTOAction, frequencies: Dict[str, float]) -> float:
        """计算建议置信度"""
        # 基于GTO行动和频率计算置信度
        action_freq = frequencies.get(gto_action.action, 0.0)
        
        # 频率越高，置信度越高
        base_confidence = action_freq
        
        # GTO权重调整
        confidence = base_confidence * 0.8 + 0.2  # 最低20%置信度
        
        return min(1.0, max(0.2, confidence))
    
    def _build_gto_reasoning(self, gto_action: GTOAction, frequencies: Dict[str, float], situation: GTOSituation) -> str:
        """构建GTO决策理由"""
        reasoning = f"""
🎯 GTO策略分析

📊 情境分析:
• 位置: {situation.position}
• 街道: {situation.street}
• 筹码深度: {situation.stack_size}BB
• 底池大小: ${situation.pot_size}
• 活跃对手: {situation.active_opponents}

🎲 频率分析:
"""
        
        for action, freq in frequencies.items():
            percentage = freq * 100
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            reasoning += f"• {action}: {percentage:.1f}% [{bar}]\n"
        
        reasoning += f"\n💡 推荐行动: {gto_action.action.upper()}"
        if gto_action.amount > 0:
            reasoning += f" ${gto_action.amount}"
        
        reasoning += f"\n🎯 理由: {gto_action.reasoning}"
        
        return reasoning
    
    def _get_sizing_recommendation(self, sizing_context: SizingContext, action: str) -> Dict[str, Any]:
        """获取尺度建议"""
        if action == 'fold':
            return {'optimal_sizing': 0, 'explanation': '弃牌不需要下注'}
        
        optimal_sizing = self.sizing_optimizer.calculate_optimal_sizing(sizing_context, action)
        explanation = self.sizing_optimizer.get_gto_sizing_explanation(optimal_sizing, sizing_context, action)
        
        return {
            'optimal_sizing': optimal_sizing,
            'explanation': explanation,
            'min_sizing': optimal_sizing * 0.8,
            'max_sizing': optimal_sizing * 1.2
        }
    
    def _analyze_range_fit(self, hole_cards: List[str], position: str, street: str) -> Dict[str, Any]:
        """分析手牌与GTO范围的匹配度"""
        # 格式化手牌
        hand_string = self._format_hand_for_range(hole_cards)
        
        # 获取不同行动的范围
        open_range = self.range_manager.get_range_for_situation(position, 'open', street)
        defend_range = self.range_manager.get_range_for_situation(position, 'defend', street)
        
        # 分析匹配度
        open_fit = self.range_manager.is_hand_in_range(hand_string, open_range)
        defend_fit = self.range_manager.is_hand_in_range(hand_string, defend_range)
        
        return {
            'hand': hand_string,
            'position': position,
            'street': street,
            'in_open_range': open_fit,
            'in_defend_range': defend_fit,
            'range_strength': self.range_manager.get_range_strength(hand_string, open_range),
            'recommendation': self.range_manager.get_range_advice(hand_string, position, 'open', street)
        }
    
    def _calculate_balance_metrics(self) -> Dict[str, float]:
        """计算策略平衡性指标"""
        if not self.gto_history:
            return {'balance_score': 0.5, 'predictability': 0.5, 'exploitability': 0.5}
        
        # 提取历史频率
        frequencies_history = [entry['frequencies'] for entry in self.gto_history[-10:]]
        
        return self.frequency_calculator.get_balance_metrics(frequencies_history)
    
    def _identify_exploit_opportunities(self, opponent_actions: List[Dict]) -> List[str]:
        """识别剥削机会"""
        opportunities = []
        
        if not opponent_actions:
            return opportunities
        
        # 分析对手倾向
        tendency = self._estimate_opponent_tendency(opponent_actions)
        
        if tendency > 1.3:  # 对手很激进
            opportunities.append("对手过于激进，可以增加跟注范围")
            opportunities.append("对手诈唬频繁，可以考虑更多陷阱")
        
        elif tendency < 0.7:  # 对手很保守
            opportunities.append("对手过于保守，可以增加诈唬频率")
            opportunities.append("对手弃牌过多，可以扩大加注范围")
        
        # 分析具体行动模式
        recent_actions = opponent_actions[-5:]
        fold_count = sum(1 for action in recent_actions if action.get('action') == 'fold')
        
        if len(recent_actions) >= 3 and fold_count >= 2:
            opportunities.append("对手最近弃牌较多，可以增加攻击频率")
        
        return opportunities
    
    def _simulate_exploitative_action(self, situation: GTOSituation) -> Dict[str, Any]:
        """模拟剥削行动（简化版）"""
        # 这里应该调用现有的剥削逻辑
        # 现在返回一个模拟的剥削建议
        return {
            'action': 'raise',
            'amount': situation.pot_size,
            'reasoning': '基于对手历史倾向的剥削策略'
        }
    
    def _recommend_strategy_type(self, situation: GTOSituation) -> str:
        """推荐策略类型"""
        # 根据情境推荐主要使用GTO还是剥削策略
        if situation.active_opponents <= 2:  # 少人桌
            return "建议使用更多剥削策略"
        elif situation.stack_size < 50:  # 浅筹码
            return "建议偏向GTO策略"
        else:
            return "建议GTO和剥削策略混合使用"
    
    def _format_hand_for_range(self, hole_cards: List[str]) -> str:
        """将手牌格式化为范围格式"""
        if not hole_cards or len(hole_cards) < 2:
            return ""
        
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, suit1 = card1[1], card1[0]
        rank2, suit2 = card2[1], card2[0]
        
        # 排序：高牌在前
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        rank_val1 = ranks.get(rank1, 0)
        rank_val2 = ranks.get(rank2, 0)
        
        if rank_val1 > rank_val2:
            high_rank, low_rank = rank1, rank2
        elif rank_val1 < rank_val2:
            high_rank, low_rank = rank2, rank1
        else:
            # 对子
            return f"{rank1}{rank2}"
        
        # 判断是否同花
        if suit1 == suit2:
            return f"{high_rank}{low_rank}s"
        else:
            return f"{high_rank}{low_rank}o"
    
    def _fallback_gto_advice(self, error: Exception, hole_cards: List[str], position: str, street: str) -> Dict[str, Any]:
        """降级GTO建议"""
        return {
            'action': 'call',
            'amount': 0,
            'confidence': 0.3,
            'reasoning': f"GTO分析暂时不可用 ({str(error)})，使用保守策略",
            'error': str(error),
            'fallback': True
        }
    
    def update_weights(self, gto_weight: float, exploitative_weight: float):
        """更新策略权重"""
        self.gto_weight = max(0.0, min(1.0, gto_weight))
        self.exploitative_weight = max(0.0, min(1.0, exploitative_weight))
        
        # 确保权重和为1
        total = self.gto_weight + self.exploitative_weight
        if total > 0:
            self.gto_weight /= total
            self.exploitative_weight /= total
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self.gto_history:
            return {'total_hands': 0, 'avg_confidence': 0.0, 'balance_score': 0.0}
        
        total_hands = len(self.gto_history)
        avg_confidence = sum(entry['action'].frequency for entry in self.gto_history) / total_hands
        
        # 计算平衡性得分
        balance_metrics = self._calculate_balance_metrics()
        
        return {
            'total_hands': total_hands,
            'avg_confidence': avg_confidence,
            'balance_score': balance_metrics.get('balance_score', 0.0),
            'predictability': balance_metrics.get('predictability', 0.0),
            'exploitability': balance_metrics.get('exploitability', 0.0)
        }