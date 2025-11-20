"""
思考过程生成器 - 专门用于生成AI的思考内容
"""

class ThinkingGenerator:
    """思考过程生成器"""
    
    def __init__(self, player_uuid):
        self.player_uuid = player_uuid
    
    def generate_thinking_from_action(self, action_result, hole_card, round_state, valid_actions, 
                                    gto_result=None, heads_up_analysis=None, my_position_name=None, is_heads_up=None):
        """基于实际决策结果生成思考过程"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        call_amount = valid_actions[1]['amount']
        
        # 基础牌力评估
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        thinking_steps = []
        
        # 手牌信息展示
        if street == 'preflop':
            card_desc = self._describe_hole_cards(hole_card)
            formatted_cards = self._format_hole_cards_display(hole_card)
            # 使用传入的正确位置，避免重复判断
            if my_position_name:
                position_desc = my_position_name
            else:
                # 备用方案：自己计算
                position = self._get_my_position(round_state)
                position_desc = self._describe_position(position, len([p for p in round_state['seats'] if p['stack'] > 0]))
            thinking_steps.append(f"🎯 {formatted_cards} ({card_desc}) - {position_desc}")
        else:
            hand_desc = self._describe_hand_strength(hand_strength, hole_card, round_state.get('community_card', []))
            formatted_cards = self._format_hole_cards_display(hole_card)
            thinking_steps.append(f"🎯 {hand_desc} {formatted_cards}")
        
        # 单挑场景：展示对手建模和范围预测
        # 使用传入的单挑状态，避免重复计算
        if is_heads_up:
            if heads_up_analysis:
                thinking_steps.append(f"🎯 单挑分析: {heads_up_analysis['description']}")
                
                # 预测对手范围
                range_prediction = self._predict_opponent_range_heads_up(round_state, heads_up_analysis)
                if range_prediction:
                    thinking_steps.append(f"🔍 {range_prediction}")
            else:
                thinking_steps.append("🎯 单挑场景: 对手数据不足，使用标准策略")
        
        # 基于实际决策生成GTO分析
        if action_result:
            action = action_result[0]  # fold, call, raise
            amount = action_result[1] if len(action_result) > 1 else 0
            
            # 获取GTO结果用于频率分析
            if gto_result:
                frequencies = gto_result.get('frequencies', {})
                
                # 显示实际决策和频率
                confidence = frequencies.get(action, 0) if frequencies else 0
                
                # 显示GTO策略行
                action_text = {
                    'fold': '🚫 弃牌',
                    'call': '✅ 跟注', 
                    'raise': '📈 加注'
                }.get(action, action)
                
                thinking_steps.append(f"🧠 GTO策略: {action_text} ${int(amount)} (置信度: {confidence:.0%})")
                
                # 显示频率分布
                if frequencies:
                    freq_parts = []
                    for action_type, freq in frequencies.items():
                        if freq > 0.01:  # 只显示大于1%的频率
                            bar_length = int(freq * 20)  # 20个字符的进度条
                            bar = "█" * bar_length + "░" * (20 - bar_length)
                            freq_parts.append(f"{action_type}: {freq:.0%} [{bar}]")
                    if freq_parts:
                        thinking_steps.append(f"📊 频率分布: {' | '.join(freq_parts)}")
                
                # 底池信息
                if call_amount > 0 and pot > 0:
                    pot_odds = call_amount / (pot + call_amount)
                    thinking_steps.append(f"💰 底池${pot}，跟注${call_amount}，赔率{pot_odds:.1%}")
                
                # 基于实际决策给出合理建议
                if action == 'fold' and confidence < 0.3:
                    thinking_steps.append("💡 GTO建议: 低概率但合理的弃牌选择")
                elif action == 'call' and confidence > 0.4:
                    thinking_steps.append("💡 GTO建议: 基于频率分析的合理跟注")
                elif action == 'raise' and confidence > 0.4:
                    thinking_steps.append("💡 GTO建议: 基于频率分析的积极进攻")
                else:
                    # 混合策略的情况
                    if action == 'fold':
                        thinking_steps.append("💡 GTO建议: 混合策略中的弃牌选择")
                    elif action == 'call':
                        thinking_steps.append("💡 GTO建议: 混合策略中的跟注选择")
                    elif action == 'raise':
                        thinking_steps.append("💡 GTO建议: 混合策略中的加注选择")
            else:
                # 没有GTO数据，使用传统逻辑
                if action == 'fold':
                    thinking_steps.append("💡 GTO建议: 放弃底池，保存筹码")
                elif action == 'call':
                    thinking_steps.append("💡 GTO建议: 控制底池，谨慎跟注")
                elif action == 'raise':
                    thinking_steps.append("💡 GTO建议: 积极进攻，价值下注")
        
        return "\n".join(thinking_steps)
    
    # 以下是需要的基础函数，后续可以进一步抽象
    def _evaluate_real_hand_strength(self, hole_card, community_card):
        """评估真实牌力（简化版）"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 这里应该调用更复杂的评估函数，暂时简化
        return 0.5  # 默认值
    
    def _describe_hole_cards(self, hole_card):
        """描述手牌"""
        if not hole_card or len(hole_card) < 2:
            return "无效手牌"
        
        # 提取牌面信息
        card1, card2 = hole_card[0], hole_card[1]
        rank1, rank2 = card1[1], card2[1]
        suit1, suit2 = card1[0], card2[0]
        
        # 是否对子
        if rank1 == rank2:
            rank_names = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T'}
            rank_name = rank_names.get(rank1, rank1)
            return f"对子 {rank_name}{rank_name}"
        
        # 是否同花
        suited = "同花" if suit1 == suit2 else "不同花"
        
        # 高牌
        ranks = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        
        high_card = max(ranks.get(rank1, 0), ranks.get(rank2, 0))
        low_card = min(ranks.get(rank1, 0), ranks.get(rank2, 0))
        
        # 连牌判断
        gap = high_card - low_card
        if gap == 1:
            connector = "连牌"
        elif gap <= 3:
            connector = "近似连牌"
        else:
            connector = "不连牌"
        
        return f"{suited} {connector}"
    
    def _format_hole_cards_display(self, hole_card):
        """格式化手牌显示 - 恢复Unicode花色符号"""
        if not hole_card or len(hole_card) < 2:
            return ""
        
        # 导入卡片工具函数（如果可用）
        try:
            from poker_assistant.utils.card_utils import format_card, get_card_color
            
            # 格式化两张牌
            card1 = format_card(hole_card[0])
            card2 = format_card(hole_card[1])
            
            # 返回格式化字符串（使用Unicode符号）
            return f"{card1} {card2}"
            
        except ImportError:
            # 如果无法导入，使用简单格式
            return f"{hole_card[0]} {hole_card[1]}"
    
    def _get_my_position(self, round_state):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == self.player_uuid:
                return idx
        return 0
    
    def _describe_position(self, position, total_players):
        """描述位置"""
        if total_players <= 2:
            return "单挑位置"
        
        if position == 0:
            return "按钮位(最佳)"
        elif position == 1:
            return "小盲位"
        elif position == 2:
            return "大盲位"
        elif position >= total_players - 2:
            return "靠后位置"
        else:
            return "靠前位置"
    
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
    
    def _is_heads_up(self, round_state):
        """判断是否单挑"""
        seats = round_state.get('seats', [])
        active_count = sum(1 for seat in seats 
                          if seat.get('stack', 0) > 0 
                          and seat.get('uuid') != self.player_uuid 
                          and seat.get('state', 'participating') == 'participating')
        return active_count == 1
    
    def _predict_opponent_range_heads_up(self, round_state, opponent_analysis):
        """预测对手范围（简化版）"""
        if not opponent_analysis:
            return "对手范围：标准范围"
        
        return f"对手倾向：{opponent_analysis['description']}"  # 简化版