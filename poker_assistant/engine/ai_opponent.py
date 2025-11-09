"""
AI 对手玩家模块
实现基于规则的 AI 对手
"""
import random
from pypokerengine.players import BasePokerPlayer


class AIOpponentPlayer(BasePokerPlayer):
    """
    AI 对手玩家
    基于简单策略的 AI，提供多种难度级别
    """
    
    def __init__(self, difficulty: str = "medium", shared_hole_cards: dict = None):
        """
        Args:
            difficulty: 难度级别 ('easy', 'medium', 'hard')
            shared_hole_cards: 共享字典，用于记录底牌
        """
        super().__init__()
        self.difficulty = difficulty
        self.action_history = []
        self.round_count = 0
        self.hole_cards = []  # 保存底牌用于摊牌展示
        self.shared_hole_cards = shared_hole_cards  # 共享底牌字典
        
    def declare_action(self, valid_actions, hole_card, round_state):
        """
        决定下一步行动
        
        Args:
            valid_actions: 可选行动列表 [fold, call, raise]
            hole_card: 手牌
            round_state: 回合状态
        
        Returns:
            (action, amount) 元组
        """
        # 获取可选行动
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 根据难度选择策略
        if self.difficulty == "easy":
            action, amount = self._easy_strategy(fold_action, call_action, raise_action, 
                                                 hole_card, round_state)
        elif self.difficulty == "hard":
            action, amount = self._hard_strategy(fold_action, call_action, raise_action,
                                                hole_card, round_state)
        else:  # medium
            action, amount = self._medium_strategy(fold_action, call_action, raise_action,
                                                  hole_card, round_state)
        
        return action, amount
    
    def _easy_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """简单策略 - 保守玩法"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 评估手牌强度（简单版）
        hand_strength = self._evaluate_hand_simple(hole_card, round_state.get('community_card', []))
        
        # 翻牌前
        if street == 'preflop':
            if hand_strength >= 0.7:
                # 好牌，70% 加注，30% 跟注
                if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                    amount = raise_action['amount']['min']
                    return raise_action['action'], amount
                else:
                    return call_action['action'], call_action['amount']
            elif hand_strength >= 0.4:
                # 中等牌，跟注
                return call_action['action'], call_action['amount']
            else:
                # 差牌，80% 弃牌，20% 跟注（诈唬）
                if random.random() < 0.8:
                    return fold_action['action'], fold_action['amount']
                else:
                    return call_action['action'], call_action['amount']
        
        # 翻牌后
        else:
            if hand_strength >= 0.6:
                # 强牌，加注或跟注
                if random.random() < 0.5 and raise_action['amount']['min'] != -1:
                    amount = raise_action['amount']['min']
                    return raise_action['action'], amount
                else:
                    return call_action['action'], call_action['amount']
            elif hand_strength >= 0.3:
                # 中等牌，跟注
                return call_action['action'], call_action['amount']
            else:
                # 差牌，弃牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
    
    def _medium_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """中等策略 - 平衡玩法"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        hand_strength = self._evaluate_hand_simple(hole_card, round_state.get('community_card', []))
        
        # 位置因素
        dealer_btn = round_state['dealer_btn']
        my_position = self._get_my_position(round_state)
        position_factor = 1.0 if my_position > dealer_btn else 0.9
        
        # 调整后的手牌强度
        adjusted_strength = hand_strength * position_factor
        
        if street == 'preflop':
            if adjusted_strength >= 0.75:
                # 强牌，加注
                if raise_action['amount']['min'] != -1:
                    # 加注 2.5-3 倍大盲
                    amount = min(raise_action['amount']['max'], 
                               max(raise_action['amount']['min'], pot // 3))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif adjusted_strength >= 0.5:
                # 中等偏强，跟注或小加注
                if random.random() < 0.3 and raise_action['amount']['min'] != -1:
                    amount = raise_action['amount']['min']
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif adjusted_strength >= 0.3:
                # 中等牌，跟注
                if call_action['amount'] <= pot // 4:  # 如果代价不大
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
            else:
                # 差牌，弃牌
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            if adjusted_strength >= 0.7:
                # 强牌，价值下注
                if raise_action['amount']['min'] != -1:
                    # 下注 50%-75% 底池
                    bet_size = int(pot * random.uniform(0.5, 0.75))
                    amount = min(raise_action['amount']['max'],
                               max(raise_action['amount']['min'], bet_size))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif adjusted_strength >= 0.4:
                # 中等牌，跟注或过牌
                if call_action['amount'] == 0:
                    return call_action['action'], 0
                elif call_action['amount'] <= pot // 3:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
            else:
                # 差牌，弃牌或诈唬
                if call_action['amount'] == 0:
                    # 免费看牌
                    return call_action['action'], 0
                elif random.random() < 0.15:  # 15% 概率诈唬
                    if raise_action['amount']['min'] != -1:
                        amount = min(raise_action['amount']['max'],
                                   int(pot * 0.6))
                        return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _hard_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """困难策略 - 激进玩法"""
        # 继承中等策略，但更激进
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        hand_strength = self._evaluate_hand_simple(hole_card, round_state.get('community_card', []))
        
        # 位置和对手数量因素
        my_position = self._get_my_position(round_state)
        active_players = len([p for p in round_state['seats'] if p['state'] != 'folded'])
        
        # 更激进的策略
        if street == 'preflop':
            if hand_strength >= 0.65:
                # 强牌，大加注
                if raise_action['amount']['min'] != -1:
                    amount = min(raise_action['amount']['max'],
                               max(raise_action['amount']['min'], pot // 2))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif hand_strength >= 0.4:
                # 中等牌，混合策略
                if random.random() < 0.5 and raise_action['amount']['min'] != -1:
                    amount = raise_action['amount']['min']
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif hand_strength >= 0.25:
                # 边缘牌，看价格
                if call_action['amount'] <= pot // 5:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                # 差牌，弃牌
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            if hand_strength >= 0.65:
                # 强牌，价值下注
                if raise_action['amount']['min'] != -1:
                    bet_size = int(pot * random.uniform(0.6, 0.9))
                    amount = min(raise_action['amount']['max'],
                               max(raise_action['amount']['min'], bet_size))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif hand_strength >= 0.35:
                # 中等牌
                if call_action['amount'] <= pot // 2:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                # 差牌，诈唬或弃牌
                if call_action['amount'] == 0:
                    # 免费看牌或诈唬
                    if random.random() < 0.3 and raise_action['amount']['min'] != -1:
                        amount = int(pot * 0.5)
                        amount = min(raise_action['amount']['max'],
                                   max(raise_action['amount']['min'], amount))
                        return raise_action['action'], amount
                    return call_action['action'], 0
                return fold_action['action'], fold_action['amount']
    
    def _evaluate_hand_simple(self, hole_card, community_card):
        """
        简单的手牌评估（返回 0-1 之间的值）
        """
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
    
    def _get_my_position(self, round_state):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == self.uuid:
                return idx
        return 0
    
    def receive_game_start_message(self, game_info):
        """接收游戏开始消息"""
        self.round_count = 0
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        """接收回合开始消息"""
        self.round_count = round_count
        self.hole_cards = hole_card  # 保存底牌
        
        # 写入共享字典（用于摊牌展示）
        if self.shared_hole_cards is not None:
            self.shared_hole_cards[self.uuid] = hole_card
    
    def receive_street_start_message(self, street, round_state):
        """接收街道开始消息"""
        pass
    
    def receive_game_update_message(self, action, round_state):
        """接收游戏更新消息"""
        self.action_history.append(action)
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        """接收回合结果消息"""
        pass

