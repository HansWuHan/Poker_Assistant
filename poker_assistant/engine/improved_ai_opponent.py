"""
改进的AI对手策略 - 解决过度激进问题
"""
import random
try:
    from pypokerengine.players import BasePokerPlayer
except ImportError:
    # 如果pypokerengine不可用，创建一个基类
    class BasePokerPlayer:
        def __init__(self):
            self.uuid = None
        
        def declare_action(self, valid_actions, hole_card, round_state):
            pass


class ImprovedAIOpponentPlayer(BasePokerPlayer):
    """
    改进的AI对手玩家 - 带思考过程显示
    """
    
    def __init__(self, difficulty: str = "medium", shared_hole_cards: dict = None, 
                 show_thinking: bool = True):
        super().__init__()
        self.difficulty = difficulty
        self.action_history = []
        self.round_count = 0
        self.hole_cards = []
        self.shared_hole_cards = shared_hole_cards
        self.show_thinking = show_thinking  # 是否显示思考过程
        
        # 对手建模数据
        self.opponent_stats = {}
        self.table_dynamics = {
            'avg_pot_size': 0,
            'aggression_level': 'normal',
            'recent_raises': 0
        }
    
    def declare_action(self, valid_actions, hole_card, round_state):
        """决定下一步行动"""
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 更新桌面动态
        self._update_table_dynamics(round_state)
        
        # 生成思考过程（如果开启显示）
        if self.show_thinking:
            thinking_process = self._generate_thinking_process(
                hole_card, round_state, valid_actions
            )
            self._display_thinking(thinking_process)
        
        # 根据难度选择策略
        if self.difficulty == "easy":
            action, amount = self._improved_easy_strategy(fold_action, call_action, raise_action, 
                                                         hole_card, round_state)
        elif self.difficulty == "hard":
            action, amount = self._improved_hard_strategy(fold_action, call_action, raise_action,
                                                         hole_card, round_state)
        else:  # medium
            action, amount = self._improved_medium_strategy(fold_action, call_action, raise_action,
                                                           hole_card, round_state)
        
        # 显示最终决策（如果开启显示）
        if self.show_thinking:
            self._display_decision(action, amount, hole_card, round_state)
        
        return action, amount
    
    def _generate_thinking_process(self, hole_card, round_state, valid_actions):
        """生成思考过程"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        call_amount = valid_actions[1]['amount']
        
        # 基础牌力评估
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        thinking_steps = []
        
        # 步骤1: 手牌评估
        if street == 'preflop':
            card_desc = self._describe_hole_cards(hole_card)
            thinking_steps.append(f"🎯 手牌评估: {card_desc}")
        else:
            hand_desc = self._describe_hand_strength(hand_strength, hole_card, round_state.get('community_card', []))
            thinking_steps.append(f"🎯 牌力评估: {hand_desc}")
        
        # 步骤2: 位置分析
        position = self._get_my_position(round_state)
        position_desc = self._describe_position(position, len([p for p in round_state['seats'] if p['stack'] > 0]))
        thinking_steps.append(f"📍 位置分析: {position_desc}")
        
        # 步骤3: 底池赔率
        if call_amount > 0 and pot > 0:
            pot_odds = call_amount / (pot + call_amount)
            odds_desc = f"底池${pot}，需要跟注${call_amount}，赔率{pot_odds:.1%}"
            thinking_steps.append(f"💰 {odds_desc}")
        
        # 步骤4: 对手分析
        opponent_desc = self._analyze_opponents_simple(round_state)
        if opponent_desc:
            thinking_steps.append(f"👥 对手分析: {opponent_desc}")
        
        # 步骤5: 决策建议
        if hand_strength >= 0.7:
            thinking_steps.append("💡 建议: 强牌，考虑价值下注")
        elif hand_strength >= 0.4:
            thinking_steps.append("💡 建议: 中等牌力，谨慎行动")
        else:
            thinking_steps.append("💡 建议: 弱牌，考虑弃牌")
        
        return "\n".join(thinking_steps)
    
    def _display_thinking(self, thinking_text):
        """显示思考过程"""
        if thinking_text:
            print(f"\n🤖 AI思考过程:")
            print(f"{thinking_text}")
            print("-" * 40)
    
    def _display_decision(self, action, amount, hole_card, round_state):
        """显示最终决策"""
        action_names = {
            'fold': '🚫 弃牌',
            'call': '✅ 跟注',
            'raise': '📈 加注'
        }
        
        action_text = action_names.get(action, action)
        if amount > 0:
            print(f"🎯 最终决策: {action_text} ${amount}")
        else:
            print(f"🎯 最终决策: {action_text}")
        print("=" * 40)
    
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
    
    def _analyze_opponents_simple(self, round_state):
        """简单分析对手"""
        seats = round_state['seats']
        active_opponents = sum(1 for seat in seats if seat['stack'] > 0 and seat['uuid'] != self.uuid)
        
        if active_opponents == 0:
            return ""
        
        return f"{active_opponents}个活跃对手"
    
    def _improved_easy_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的简单策略 - 更精细的决策"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        if street == 'preflop':
            # 翻牌前更精细的起手牌要求
            if adjusted_strength >= 0.85:
                # 超强牌（AA, KK, AK等）
                if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                    # 根据筹码深度调整下注大小
                    if my_stack > pot * 20:  # 深筹码
                        amount = max(raise_action['amount']['min'], int(pot * 0.8))
                    else:  # 浅筹码
                        amount = max(raise_action['amount']['min'], int(pot * 0.6))
                    return raise_action['action'], amount
                elif random.random() < 0.2:  # 20%概率慢打
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.7:
                # 强牌但非超强
                if call_action['amount'] <= pot * 0.15 and random.random() < 0.8:
                    return call_action['action'], call_action['amount']
                elif raise_action['amount']['min'] != -1 and random.random() < 0.3:
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.5:
                # 中等牌力
                if call_action['amount'] <= pot * 0.08 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:  # 免费看牌
                    return call_action['action'], call_action['amount']
                # 偶尔偷盲（10%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.05 and 
                      random.random() < 0.1):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌力和公共牌协调性综合判断
            board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
            
            # 调整牌力评估
            effective_strength = adjusted_strength
            if board_coordination > 0.7:  # 协调的牌面
                effective_strength *= 0.9  # 降低牌力评估
            elif board_coordination < 0.3:  # 不协调的牌面
                effective_strength *= 1.1  # 提高牌力评估
            
            if effective_strength >= 0.8:
                # 强牌，价值下注
                if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                    bet_size = self._calculate_value_bet_size(hand_strength, pot, raise_action)
                    return raise_action['action'], bet_size
                elif random.random() < 0.8:  # 80%概率至少跟注
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.55:
                # 中等强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.4:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif pot_odds <= 0.3 and hand_strength >= 0.45:  # 赔率合适
                    if random.random() < 0.7:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and 
                      random.random() < 0.2 and pot_odds <= 0.25):  # 偶尔半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.4))
                    return raise_action['action'], amount
                
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.35:
                # 边缘牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.15 and hand_strength >= 0.25:  # 赔率很好才跟注
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.1 and 
                      pot_odds <= 0.2):  # 10%概率诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.35))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 极低概率诈唬（8%）
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.08 and 
                      pot_odds <= 0.25):
                    amount = max(raise_action['amount']['min'], int(pot * 0.3))
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _improved_medium_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的中等策略 - 更智能的对手建模和情境判断"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 对手倾向
        opponent_tendency = self._analyze_opponent_tendency(round_state)
        
        # 公共牌协调性
        board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor * opponent_tendency
        
        # 根据牌面调整牌力评估
        if street != 'preflop':
            if board_coordination > 0.7:  # 协调牌面，降低牌力
                adjusted_strength *= 0.85
            elif board_coordination < 0.3:  # 不协调牌面，提高牌力
                adjusted_strength *= 1.15
        
        if street == 'preflop':
            # 基于位置和对手倾向调整起手牌要求
            if adjusted_strength >= 0.8:
                # 超强牌
                if opponent_tendency > 1.2:  # 对手激进
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        # 深筹码时更大加注
                        if my_stack > pot * 15:
                            amount = max(raise_action['amount']['min'], int(pot * 0.9))
                        else:
                            amount = max(raise_action['amount']['min'], int(pot * 0.7))
                        return raise_action['action'], amount
                else:  # 对手保守
                    if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                        amount = max(raise_action['amount']['min'], int(pot * 0.6))
                        return raise_action['action'], amount
                
                # 偶尔慢打
                if random.random() < 0.2:
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.65:
                # 强牌
                if call_action['amount'] <= pot * 0.12 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.4 and 
                      opponent_tendency < 1.1):  # 对保守对手加注
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.5:
                # 中等牌力
                if (call_action['amount'] <= pot * 0.08 and 
                    (position_factor >= 1.0 or opponent_tendency < 1.0)):
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      position_factor >= 1.1):  # 位置好时偶尔偷盲
                    amount = max(raise_action['amount']['min'], int(pot * 0.4))
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 位置好时偶尔偷盲（8%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.04 and 
                      random.random() < 0.08):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌面纹理和对手类型调整策略
            effective_strength = adjusted_strength
            
            if effective_strength >= 0.8:
                # 超强牌
                if opponent_tendency > 1.2:  # 对手激进，可以大注
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.1, pot, raise_action)
                        return raise_action['action'], bet_size
                else:  # 对手保守，标准价值下注
                    if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength, pot, raise_action)
                        return raise_action['action'], bet_size
                
                # 80%概率至少跟注
                if random.random() < 0.8:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.6:
                # 强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.25 and hand_strength >= 0.5:  # 赔率合适
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.35 and hand_strength >= 0.55 and 
                      opponent_tendency < 1.0):  # 对保守对手放宽
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.3 and 
                      pot_odds <= 0.3):  # 半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.55))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.4:
                # 中等牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.35:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.25 and hand_strength >= 0.4 and 
                      position_factor >= 1.0):  # 位置好
                    if random.random() < 0.8:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.2 and 
                      pot_odds <= 0.25 and position_factor >= 1.05):  # 位置好时半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.45))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.25:
                # 边缘牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.15 and hand_strength >= 0.25:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      pot_odds <= 0.2 and opponent_tendency > 1.1):  # 对激进对手诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.4))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 对激进对手偶尔诈唬（12%）
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.12 and 
                      opponent_tendency > 1.2 and pot_odds <= 0.2):
                    amount = max(raise_action['amount']['min'], int(pot * 0.35))
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _improved_hard_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的困难策略 - 最智能的决策"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 对手倾向
        opponent_tendency = self._analyze_opponent_tendency(round_state)
        
        # 公共牌协调性
        board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor * opponent_tendency
        
        # 根据牌面调整牌力评估
        if street != 'preflop':
            if board_coordination > 0.7:  # 协调牌面，降低牌力
                adjusted_strength *= 0.8
            elif board_coordination < 0.3:  # 不协调牌面，提高牌力
                adjusted_strength *= 1.2
        
        if street == 'preflop':
            # 基于位置和对手倾向调整起手牌要求
            if adjusted_strength >= 0.85:
                # 超强牌
                if opponent_tendency > 1.3:  # 对手很激进
                    if random.random() < 0.8 and raise_action['amount']['min'] != -1:
                        # 深筹码时更大加注
                        if my_stack > pot * 12:
                            amount = max(raise_action['amount']['min'], int(pot * 1.0))
                        else:
                            amount = max(raise_action['amount']['min'], int(pot * 0.8))
                        return raise_action['action'], amount
                else:  # 对手保守
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        amount = max(raise_action['amount']['min'], int(pot * 0.7))
                        return raise_action['action'], amount
                
                # 偶尔慢打
                if random.random() < 0.15:
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.7:
                # 强牌
                if call_action['amount'] <= pot * 0.15 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.5 and 
                      opponent_tendency < 1.1):  # 对保守对手加注
                    amount = max(raise_action['amount']['min'], int(pot * 0.6))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.55:
                # 中等牌力
                if (call_action['amount'] <= pot * 0.1 and 
                    (position_factor >= 1.0 or opponent_tendency < 1.0)):
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.25 and 
                      position_factor >= 1.1):  # 位置好时偷盲
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 位置好时偶尔偷盲（12%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.05 and 
                      random.random() < 0.12):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌面纹理和对手类型调整策略
            effective_strength = adjusted_strength
            
            if effective_strength >= 0.85:
                # 超强牌
                if opponent_tendency > 1.3:  # 对手很激进
                    if random.random() < 0.8 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.2, pot, raise_action)
                        return raise_action['action'], bet_size
                else:  # 对手保守
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.1, pot, raise_action)
                        return raise_action['action'], bet_size
                
                # 85%概率至少跟注
                if random.random() < 0.85:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.65:
                # 强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.3 and hand_strength >= 0.55:  # 赔率合适
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.4 and hand_strength >= 0.6 and 
                      opponent_tendency < 1.0):  # 对保守对手放宽
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.4 and 
                      pot_odds <= 0.35):  # 半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.65))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.45:
                # 中等牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.25 and hand_strength >= 0.4:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.3 and hand_strength >= 0.45 and 
                      position_factor >= 1.0):  # 位置好
                    if random.random() < 0.8:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.3 and 
                      pot_odds <= 0.3 and position_factor >= 1.05):  # 位置好时半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.55))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.3:
                # 边缘牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.3:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.2 and 
                      pot_odds <= 0.25 and opponent_tendency > 1.2):  # 对激进对手诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 对激进对手偶尔诈唬（15%）
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      opponent_tendency > 1.2 and pot_odds <= 0.25):
                    amount = max(raise_action['amount']['min'], int(pot * 0.45))
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _evaluate_real_hand_strength(self, hole_card, community_card):
        """评估真实牌力（0-1）"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 基础牌力评估
        base_strength = self._evaluate_hand_simple(hole_card, community_card)
        
        # 如果有公共牌，进行更精确评估
        if community_card and len(community_card) >= 3:
            # 这里可以集成更复杂的牌力评估
            # 现在简化处理：根据公共牌调整评估
            board_coordination = self._assess_board_coordination(community_card)
            
            # 协调的公共牌降低牌力（更危险）
            if board_coordination > 0.7:
                base_strength *= 0.85
            elif board_coordination < 0.3:
                base_strength *= 1.1
        
        return min(1.0, base_strength)
    
    def _get_position_factor(self, round_state):
        """获取位置因子"""
        my_position = self._get_my_position(round_state)
        dealer_btn = round_state['dealer_btn']
        total_players = len([p for p in round_state['seats'] if p['stack'] > 0])
        
        # 位置评估（越靠后越好）
        if my_position == dealer_btn:
            return 1.15  # BTN位置最佳
        elif (my_position - dealer_btn) % total_players <= 2:
            return 1.05  # 靠后位置
        else:
            return 0.95  # 靠前位置
    
    def _analyze_opponent_tendency(self, round_state):
        """分析对手倾向（更智能）"""
        action_histories = round_state.get('action_histories', {})
        
        total_actions = 0
        aggressive_actions = 0
        call_actions = 0
        fold_actions = 0
        
        # 分析所有街道的行动
        for street_actions in action_histories.values():
            if isinstance(street_actions, list):
                for action in street_actions:
                    if isinstance(action, dict) and 'action' in action:
                        # 只统计其他玩家的行动
                        if action.get('uuid') != self.uuid:
                            total_actions += 1
                            action_type = action['action'].lower()
                            
                            if action_type in ['raise', 'allin']:
                                aggressive_actions += 1
                            elif action_type == 'call':
                                call_actions += 1
                            elif action_type == 'fold':
                                fold_actions += 1
        
        if total_actions == 0:
            return 1.0
        
        # 计算激进因子（0-1）
        aggression_factor = aggressive_actions / total_actions if total_actions > 0 else 0.5
        
        # 计算弃牌率
        fold_rate = fold_actions / total_actions if total_actions > 0 else 0
        
        # 根据对手类型返回调整因子
        if aggression_factor > 0.5:  # 非常激进
            return 0.85  # 更谨慎
        elif aggression_factor > 0.35:  # 激进
            return 0.9
        elif aggression_factor < 0.15:  # 非常保守
            return 1.2  # 可以更激进
        elif aggression_factor < 0.25:  # 保守
            return 1.1
        else:  # 正常
            return 1.0
    
    def _calculate_value_bet_size(self, hand_strength, pot, raise_action):
        """计算价值下注大小（更智能）"""
        min_raise = raise_action['amount']['min']
        max_raise = raise_action['amount']['max']
        
        # 根据牌力决定下注比例
        if hand_strength >= 0.9:  # 极强牌
            bet_ratio = random.uniform(0.8, 1.0)
        elif hand_strength >= 0.8:  # 强牌
            bet_ratio = random.uniform(0.65, 0.85)
        elif hand_strength >= 0.65:  # 中等强牌
            bet_ratio = random.uniform(0.5, 0.7)
        elif hand_strength >= 0.5:  # 中等牌
            bet_ratio = random.uniform(0.4, 0.6)
        else:  # 边缘牌
            bet_ratio = random.uniform(0.3, 0.5)
        
        bet_size = int(pot * bet_ratio)
        
        # 确保在合理范围内
        if bet_size < min_raise:
            return min_raise
        elif bet_size > max_raise:
            return max_raise
        else:
            return bet_size
    
    def _has_showdown_value(self, hand_strength, round_state):
        """判断是否有摊牌价值"""
        # 简化判断：牌力超过阈值且有希望赢
        return hand_strength >= 0.3
    
    def _get_my_stack(self, round_state):
        """获取我的筹码量"""
        for seat in round_state['seats']:
            if seat['uuid'] == self.uuid:
                return seat.get('stack', 0)
        return 0
    
    def _assess_board_coordination(self, community_card):
        """评估公共牌协调性（更精确）"""
        if not community_card or len(community_card) < 3:
            return 0.5
        
        # 评估顺子可能性
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = []
        for card in community_card:
            rank = card[1]
            card_ranks.append(ranks.get(rank, 0))
        
        card_ranks.sort()
        
        # 检查顺子可能性
        straight_danger = 0
        for i in range(len(card_ranks) - 2):
            if card_ranks[i+2] - card_ranks[i] <= 4:  # 3张牌在5个连续等级内
                straight_danger += 0.2
        
        # 检查同花可能性
        suit_counts = {}
        for card in community_card:
            suit = card[0]
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        flush_danger = max(suit_counts.values()) / len(community_card) if suit_counts else 0
        
        # 综合评估：0.0-1.0，越高表示牌面越协调（越危险）
        coordination = min(1.0, (straight_danger + flush_danger) / 2)
        
        return coordination
    
    def _update_table_dynamics(self, round_state):
        """更新桌面动态"""
        # 统计最近的加注情况
        street = round_state['street']
        action_histories = round_state.get('action_histories', {})
        
        if street in action_histories:
            recent_raises = sum(1 for action in action_histories[street] 
                              if action.get('action', '').lower() == 'raise')
            self.table_dynamics['recent_raises'] = recent_raises
    
    def _get_my_position(self, round_state):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == self.uuid:
                return idx
        return 0
    
    def _evaluate_hand_simple(self, hole_card, community_card):
        """保留原有的简单评估作为基础"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 提取点数
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card1_rank = ranks.get(hole_card[0][1], 0)
        card2_rank = ranks.get(hole_card[1][1], 0)
        
        # 是否对子
        is_pair = (card1_rank == card2_rank)
        
        # 是否同花
        is_suited = (hole_card[0][0] == hole_card[1][0])
        
        # 高牌
        high_card = max(card1_rank, card2_rank)
        low_card = min(card1_rank, card2_rank)
        
        # 基础评分
        score = 0.0
        
        if is_pair:
            # 对子
            score = 0.5 + (card1_rank / 28.0)  # AA=1.0, 22=0.54
        else:
            # 非对子
            score = (high_card + low_card) / 28.0
            
            # 同花加成
            if is_suited:
                score += 0.1
            
            # 连牌加成
            if abs(card1_rank - card2_rank) <= 3:
                score += 0.05
            
            # 高牌加成
            if high_card >= 12:  # Q 或更大
                score += 0.1
        
        return min(1.0, score)
    
    # 保留原有的消息处理方法
    def receive_game_start_message(self, game_info):
        self.round_count = 0
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_count = round_count
        self.hole_cards = hole_card
        
        # 修复：将底牌记录到共享字典中，用于摊牌显示
        if self.shared_hole_cards is not None:
            self.shared_hole_cards[self.uuid] = hole_card
    
    def receive_street_start_message(self, street, round_state):
        pass
    
    def receive_game_update_message(self, action, round_state):
        pass
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        pass