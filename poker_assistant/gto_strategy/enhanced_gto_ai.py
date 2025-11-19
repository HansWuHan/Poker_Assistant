"""
GTO增强版AI对手 - 集成GTO策略的改进AI
保留原有逻辑，增加GTO策略指导
"""
import random
from typing import Dict, List, Any, Optional, Tuple

# 导入现有AI逻辑
try:
    from pypokerengine.players import BasePokerPlayer
except ImportError:
    # 如果pypokerengine不可用，创建一个基类
    class BasePokerPlayer:
        def __init__(self):
            self.uuid = None
        
        def declare_action(self, valid_actions, hole_card, round_state):
            pass

# 导入GTO策略包
from poker_assistant.gto_strategy import GTOAdvisor, GTOSituation
from poker_assistant.gto_strategy.gto_core import GTOAction

# 导入现有AI逻辑（复制关键部分以保持兼容性）
class EnhancedGTOAIOpponentPlayer(BasePokerPlayer):
    """
    GTO增强版AI对手 - 结合GTO策略和现有AI逻辑
    
    特点：
    1. 保留原有AI逻辑作为基础
    2. 集成GTO策略指导
    3. 支持策略混合和权重调整
    4. 提供详细的GTO分析
    """
    
    def __init__(self, difficulty: str = "medium", shared_hole_cards: dict = None, 
                 show_thinking: bool = True, gto_enabled: bool = True, 
                 gto_weight: float = 0.6, strategy_mode: str = "hybrid"):
        """
        初始化GTO增强AI
        
        Args:
            difficulty: 难度级别 (easy, medium, hard)
            shared_hole_cards: 共享底牌字典
            show_thinking: 是否显示思考过程
            gto_enabled: 是否启用GTO策略
            gto_weight: GTO策略权重 (0-1)
            strategy_mode: 策略模式 (gto_only, exploitative_only, hybrid)
        """
        super().__init__()
        self.difficulty = difficulty
        self.action_history = []
        self.round_count = 0
        self.hole_cards = []
        self.shared_hole_cards = shared_hole_cards
        self.show_thinking = show_thinking
        self.gto_enabled = gto_enabled
        self.gto_weight = gto_weight
        self.strategy_mode = strategy_mode
        
        # GTO策略顾问
        if self.gto_enabled:
            self.gto_advisor = GTOAdvisor()
        else:
            self.gto_advisor = None
        
        # 对手建模数据
        self.opponent_stats = {}
        self.table_dynamics = {
            'avg_pot_size': 0,
            'aggression_level': 'normal',
            'recent_raises': 0
        }
        
        # GTO分析结果缓存
        self.last_gto_analysis = None
        
    def declare_action(self, valid_actions, hole_card, round_state):
        """决定下一步行动 - 集成GTO策略"""
        import time
        
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 更新桌面动态
        self._update_table_dynamics(round_state)
        
        # 生成思考过程（如果开启显示）
        if self.show_thinking:
            self._display_thinking_process(hole_card, round_state, valid_actions)
        else:
            # 即使关闭思考显示，也添加1秒延时让AI决策更自然
            time.sleep(1)
        
        # 根据策略模式选择决策方式
        if self.strategy_mode == "gto_only" and self.gto_enabled:
            # 纯GTO策略
            action, amount = self._gto_based_strategy(fold_action, call_action, raise_action, 
                                                   hole_card, round_state)
        elif self.strategy_mode == "exploitative_only":
            # 纯剥削策略（使用原有逻辑）
            action, amount = self._exploitative_strategy(fold_action, call_action, raise_action, 
                                                        hole_card, round_state)
        else:
            # 混合策略（默认）
            action, amount = self._hybrid_strategy(fold_action, call_action, raise_action, 
                                                  hole_card, round_state)
        
        return action, amount
    
    def _gto_based_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """基于GTO的策略决策"""
        if not self.gto_advisor:
            return self._exploitative_strategy(fold_action, call_action, raise_action, 
                                             hole_card, round_state)
        
        try:
            # 获取当前情境信息
            position = self._get_position_name(round_state)
            street = round_state['street']
            pot_size = round_state['pot']['main']['amount']
            stack_size = self._get_my_stack(round_state)
            call_amount = call_action['amount']
            
            # 获取对手行动历史
            opponent_actions = self._extract_opponent_actions(round_state)
            active_opponents = self._get_active_opponents(round_state)
            
            # 获取GTO建议
            gto_advice = self.gto_advisor.get_gto_advice(
                hole_cards=hole_card,
                community_cards=round_state.get('community_card', []),
                street=street,
                position=position,
                pot_size=pot_size,
                stack_size=stack_size,
                call_amount=call_amount,
                valid_actions=[fold_action, call_action, raise_action],
                opponent_actions=opponent_actions,
                active_opponents=active_opponents
            )
            
            # 缓存GTO分析
            self.last_gto_analysis = gto_advice
            
            # 应用GTO建议
            return self._apply_gto_advice(gto_advice, fold_action, call_action, raise_action)
            
        except Exception as e:
            # GTO分析失败，回退到剥削策略
            print(f"GTO分析失败: {e}")
            return self._exploitative_strategy(fold_action, call_action, raise_action, 
                                             hole_card, round_state)
    
    def _exploitative_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """剥削策略（使用原有逻辑）"""
        # 根据难度选择原有策略
        if self.difficulty == "easy":
            return self._improved_easy_strategy(fold_action, call_action, raise_action, 
                                            hole_card, round_state)
        elif self.difficulty == "hard":
            return self._improved_hard_strategy(fold_action, call_action, raise_action, 
                                             hole_card, round_state)
        else:  # medium
            return self._improved_medium_strategy(fold_action, call_action, raise_action, 
                                               hole_card, round_state)
    
    def _hybrid_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """混合策略 - 结合GTO和剥削策略"""
        # 获取剥削策略建议
        exploitative_action, exploitative_amount = self._exploitative_strategy(
            fold_action, call_action, raise_action, hole_card, round_state)
        
        # 如果GTO未启用，直接使用剥削策略
        if not self.gto_enabled or not self.gto_advisor:
            return exploitative_action, exploitative_amount
        
        try:
            # 获取GTO建议
            gto_advice = self._gto_based_strategy(fold_action, call_action, raise_action, 
                                               hole_card, round_state)
            
            if gto_advice and isinstance(gto_advice, tuple):
                gto_action, gto_amount = gto_advice
                
                # 创建剥削建议字典
                exploitative_advice = {
                    'action': exploitative_action,
                    'amount': exploitative_amount,
                    'reasoning': f'基于{self.difficulty}难度剥削策略'
                }
                
                # 创建GTO建议字典
                gto_advice_dict = {
                    'action': gto_action,
                    'amount': gto_amount,
                    'reasoning': '基于GTO理论的最优策略'
                }
                
                # 混合策略
                blended_advice = self.gto_advisor.blend_with_exploitative(
                    gto_advice_dict, exploitative_advice)
                
                return blended_advice['action'], blended_advice['amount']
            
        except Exception as e:
            print(f"混合策略失败: {e}")
        
        # 混合失败，回退到剥削策略
        return exploitative_action, exploitative_amount
    
    def _display_thinking_process(self, hole_card, round_state, valid_actions):
        """显示思考过程 - 包含GTO分析"""
        import time
        
        print()
        # 获取AI玩家名字
        ai_name = "AI"
        for seat in round_state.get('seats', []):
            if seat.get('uuid') == self.uuid:
                ai_name = seat.get('name', 'AI')
                break
        
        print(f"🤖 {ai_name} 思考中...")
        time.sleep(1)
        
        # 生成GTO分析（如果启用）
        gto_analysis = ""
        if self.gto_enabled and self.gto_advisor:
            try:
                # 获取当前情境
                position = self._get_position_name(round_state)
                street = round_state['street']
                pot_size = round_state['pot']['main']['amount']
                stack_size = self._get_my_stack(round_state)
                call_amount = valid_actions[1]['amount']
                
                opponent_actions = self._extract_opponent_actions(round_state)
                active_opponents = self._get_active_opponents(round_state)
                
                # 获取GTO建议
                gto_advice = self.gto_advisor.get_gto_advice(
                    hole_cards=hole_card,
                    community_cards=round_state.get('community_card', []),
                    street=street,
                    position=position,
                    pot_size=pot_size,
                    stack_size=stack_size,
                    call_amount=call_amount,
                    valid_actions=valid_actions,
                    opponent_actions=opponent_actions,
                    active_opponents=active_opponents
                )
                
                if gto_advice:
                    gto_analysis = self._format_gto_analysis(gto_advice)
                    
            except Exception as e:
                gto_analysis = f"GTO分析暂时不可用 ({str(e)})"
        
        # 生成传统分析
        traditional_analysis = self._generate_traditional_thinking(hole_card, round_state, valid_actions)
        
        # 显示综合分析
        if gto_analysis:
            print("🔍 GTO策略分析:")
            print(gto_analysis)
            print()
        
        print("🧠 传统策略分析:")
        print(traditional_analysis)
        
        time.sleep(1)  # 给玩家时间阅读分析
    
    def _format_gto_analysis(self, gto_advice: Dict[str, Any]) -> str:
        """格式化GTO分析结果"""
        lines = []
        
        # 主要建议
        action = gto_advice.get('action', 'unknown')
        amount = gto_advice.get('amount', 0)
        confidence = gto_advice.get('confidence', 0.0)
        
        action_names = {'fold': '弃牌', 'call': '跟注', 'raise': '加注'}
        action_cn = action_names.get(action, action)
        
        lines.append(f"💡 GTO推荐: {action_cn}")
        if amount > 0:
            lines.append(f"💰 建议金额: ${amount}")
        lines.append(f"🎯 置信度: {confidence*100:.0f}%")
        
        # 频率分析
        frequencies = gto_advice.get('frequencies', {})
        if frequencies:
            lines.append("📊 行动频率:")
            for action, freq in frequencies.items():
                lines.append(f"  • {action}: {freq*100:.1f}%")
        
        # 范围分析
        range_analysis = gto_advice.get('range_analysis', {})
        if range_analysis:
            in_range = range_analysis.get('in_open_range', False)
            range_strength = range_analysis.get('range_strength', 0.0)
            lines.append(f"🎴 范围匹配: {'✅' if in_range else '❌'} (强度: {range_strength*100:.0f}%)")
        
        return "\n".join(lines)
    
    def _generate_traditional_thinking(self, hole_card, round_state, valid_actions):
        """生成传统策略分析"""
        # 这里可以重用原有AI的思考过程生成逻辑
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        call_amount = valid_actions[1]['amount']
        
        # 基础牌力评估
        hand_strength = self._evaluate_hand_strength(hole_card, round_state.get('community_card', []))
        
        thinking_steps = []
        
        # 精简版思考过程
        if street == 'preflop':
            card_desc = self._describe_hole_cards(hole_card)
            formatted_cards = self._format_hole_cards_display(hole_card)
            position = self._get_position_name(round_state)
            thinking_steps.append(f"🎯 {formatted_cards} ({card_desc}) - {position}")
        else:
            hand_desc = self._describe_hand_strength(hole_card, round_state.get('community_card', []))
            formatted_cards = self._format_hole_cards_display(hole_card)
            thinking_steps.append(f"🎯 {hand_desc} {formatted_cards}")
        
        # 底池信息
        if call_amount > 0 and pot > 0:
            pot_odds = call_amount / (pot + call_amount)
            thinking_steps.append(f"💰 底池${pot}，跟注${call_amount}，赔率{pot_odds:.1%}")
        
        # 对手分析
        active_opponents = self._get_active_opponents(round_state)
        if active_opponents > 0:
            hand_guess = self._guess_opponent_hands(round_state, street)
            if hand_guess:
                thinking_steps.append(f"🔍 {hand_guess}")
        
        # 决策建议
        if hand_strength >= 0.7:
            thinking_steps.append("💡 强牌，考虑价值下注")
        elif hand_strength >= 0.4:
            thinking_steps.append("💡 中等牌力，谨慎行动")
        else:
            thinking_steps.append("💡 弱牌，考虑弃牌")
        
        return "\n".join(thinking_steps)
    
    def _apply_gto_advice(self, gto_advice: Dict[str, Any], fold_action, call_action, raise_action):
        """应用GTO建议到具体行动"""
        if not gto_advice:
            return self._exploitative_strategy(fold_action, call_action, raise_action, 
                                             [], {})  # 降级处理
        
        recommended_action = gto_advice.get('action', 'call')
        recommended_amount = gto_advice.get('amount', 0)
        
        # 根据建议行动类型选择
        if recommended_action == 'fold':
            return fold_action['action'], fold_action['amount']
        
        elif recommended_action == 'call':
            return call_action['action'], call_action['amount']
        
        elif recommended_action == 'raise':
            # 确保金额在允许范围内
            min_raise = raise_action['amount']['min'] if isinstance(raise_action['amount'], dict) else 0
            max_raise = raise_action['amount']['max'] if isinstance(raise_action['amount'], dict) else 100000
            
            # 调整推荐金额到允许范围
            if recommended_amount < min_raise:
                recommended_amount = min_raise
            elif recommended_amount > max_raise:
                recommended_amount = max_raise
            
            return raise_action['action'], recommended_amount
        
        # 默认返回跟注
        return call_action['action'], call_action['amount']
    
    # 辅助方法（从原有AI复制）
    def _get_position_name(self, round_state):
        """获取位置名称"""
        for idx, seat in enumerate(round_state['seats']):
            if seat.get('uuid') == self.uuid:
                # 简化位置识别
                dealer_btn = round_state.get('dealer_btn', 0)
                total_players = len([s for s in round_state['seats'] if s.get('stack', 0) > 0])
                
                if total_players == 2:
                    return "BTN" if idx == dealer_btn else "BB"
                else:
                    if idx == dealer_btn:
                        return "BTN"
                    elif (idx - dealer_btn) % total_players == 1:
                        return "SB"
                    elif (idx - dealer_btn) % total_players == 2:
                        return "BB"
                    else:
                        return "MP"
        return "MP"
    
    def _extract_opponent_actions(self, round_state):
        """提取对手行动历史"""
        opponent_actions = []
        action_histories = round_state.get('action_histories', {})
        
        for street, actions in action_histories.items():
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get('uuid') != self.uuid:
                        opponent_actions.append(action)
        
        return opponent_actions
    
    def _get_active_opponents(self, round_state):
        """获取活跃对手数量"""
        seats = round_state.get('seats', [])
        return sum(1 for seat in seats 
                   if seat.get('stack', 0) > 0 
                   and seat.get('uuid') != self.uuid 
                   and seat.get('state', 'participating') == 'participating')
    
    def _get_my_stack(self, round_state):
        """获取我的筹码"""
        for seat in round_state['seats']:
            if seat.get('uuid') == self.uuid:
                return seat.get('stack', 0)
        return 0
    
    def _update_table_dynamics(self, round_state):
        """更新桌面动态"""
        # 实现桌面动态更新逻辑
        pass
    
    def _evaluate_hand_strength(self, hole_card, community_card):
        """评估手牌强度"""
        # 简化实现
        return 0.5
    
    def _describe_hole_cards(self, hole_card):
        """描述手牌"""
        if not hole_card or len(hole_card) < 2:
            return "无效手牌"
        
        # 简化的手牌描述
        card1, card2 = hole_card[0], hole_card[1]
        rank1, rank2 = card1[1], card2[1]
        
        if rank1 == rank2:
            return f"对子 {rank1}{rank2}"
        elif card1[0] == card2[0]:
            return "同花"
        else:
            return "不同花"
    
    def _format_hole_cards_display(self, hole_card):
        """格式化手牌显示"""
        if not hole_card or len(hole_card) < 2:
            return ""
        
        return f"{hole_card[0]} {hole_card[1]}"
    
    def _describe_hand_strength(self, strength, hole_card, community_card):
        """描述牌力"""
        if strength >= 0.8:
            return "极强牌力"
        elif strength >= 0.6:
            return "强牌"
        elif strength >= 0.4:
            return "中等牌力"
        elif strength >= 0.2:
            return "弱牌"
        else:
            return "极弱牌力"
    
    def _guess_opponent_hands(self, round_state, street):
        """猜测对手手牌"""
        # 简化实现
        active_opponents = self._get_active_opponents(round_state)
        if active_opponents == 0:
            return ""
        
        return f"{active_opponents}个活跃对手"
    
    # 原有策略方法（简化版本）
    def _improved_easy_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """简单策略"""
        # 简化的简单策略实现
        import random
        
        hand_strength = self._evaluate_hand_strength(hole_card, round_state.get('community_card', []))
        
        if hand_strength >= 0.6:
            if raise_action['amount']['min'] != -1:
                return raise_action['action'], max(raise_action['amount']['min'], 20)
            else:
                return call_action['action'], call_action['amount']
        elif hand_strength >= 0.3:
            if call_action['amount'] == 0:
                return call_action['action'], call_action['amount']
            else:
                return fold_action['action'], fold_action['amount']
        else:
            return fold_action['action'], fold_action['amount']
    
    def _improved_medium_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """中等策略"""
        # 简化的中等策略实现
        import random
        
        hand_strength = self._evaluate_hand_strength(hole_card, round_state.get('community_card', []))
        
        if hand_strength >= 0.7:
            if raise_action['amount']['min'] != -1 and random.random() < 0.7:
                return raise_action['action'], max(raise_action['amount']['min'], 30)
            else:
                return call_action['action'], call_action['amount']
        elif hand_strength >= 0.4:
            if call_action['amount'] == 0:
                return call_action['action'], call_action['amount']
            elif random.random() < 0.5:
                return call_action['action'], call_action['amount']
            else:
                return fold_action['action'], fold_action['amount']
        else:
            return fold_action['action'], fold_action['amount']
    
    def _improved_hard_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """困难策略"""
        # 简化的困难策略实现
        import random
        
        hand_strength = self._evaluate_hand_strength(hole_card, round_state.get('community_card', []))
        
        if hand_strength >= 0.8:
            if raise_action['amount']['min'] != -1 and random.random() < 0.8:
                return raise_action['action'], max(raise_action['amount']['min'], 40)
            else:
                return call_action['action'], call_action['amount']
        elif hand_strength >= 0.5:
            if call_action['amount'] == 0:
                return call_action['action'], call_action['amount']
            elif random.random() < 0.7:
                return call_action['action'], call_action['amount']
            else:
                return fold_action['action'], fold_action['amount']
        else:
            return fold_action['action'], fold_action['amount']
    
    # 消息处理方法（保持兼容性）
    def receive_game_start_message(self, game_info):
        self.round_count = 0
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_count = round_count
        self.hole_cards = hole_card
        
        # 修复：将底牌记录到共享字典中
        if self.shared_hole_cards is not None:
            self.shared_hole_cards[self.uuid] = hole_card
    
    def receive_street_start_message(self, street, round_state):
        pass
    
    def receive_game_update_message(self, action, round_state):
        pass
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
    
    # 配置方法
    def set_gto_weight(self, weight: float):
        """设置GTO策略权重"""
        self.gto_weight = max(0.0, min(1.0, weight))
    
    def set_strategy_mode(self, mode: str):
        """设置策略模式"""
        if mode in ["gto_only", "exploitative_only", "hybrid"]:
            self.strategy_mode = mode
    
    def enable_gto(self, enabled: bool):
        """启用/禁用GTO策略"""
        self.gto_enabled = enabled
        if enabled and not self.gto_advisor:
            self.gto_advisor = GTOAdvisor()
        elif not enabled and self.gto_advisor:
            self.gto_advisor = None
    
    def get_gto_metrics(self) -> Dict[str, Any]:
        """获取GTO策略使用指标"""
        if not self.gto_advisor:
            return {'gto_enabled': False}
        
        return {
            'gto_enabled': self.gto_enabled,
            'strategy_mode': self.strategy_mode,
            'gto_weight': self.gto_weight,
            'performance_metrics': self.gto_advisor.get_performance_metrics() if self.gto_advisor else {}
        }