"""
AI工具函数模块 - 牌力评估、位置判断等基础功能
"""

class AIUtils:
    """AI工具类"""
    
    @staticmethod
    def evaluate_real_hand_strength(hole_card, community_card):
        """评估真实牌力（0-1）"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 基础牌力评估（仅基于手牌）
        base_strength = AIUtils.evaluate_hand_simple(hole_card, community_card)
        
        # 如果有公共牌，进行更精确评估
        if community_card and len(community_card) >= 3:
            # 评估实际牌力，而不是仅仅基于手牌
            actual_strength = AIUtils.evaluate_actual_hand_strength(hole_card, community_card)
            
            # 如果实际牌力远低于基础牌力，说明高牌被高估了
            if actual_strength < base_strength * 0.7:
                return actual_strength
            
            # 考虑公共牌协调性
            board_coordination = AIUtils.assess_board_coordination(community_card)
            
            # 协调的公共牌降低牌力（更危险）
            if board_coordination > 0.7:
                actual_strength *= 0.85
            elif board_coordination < 0.3:
                actual_strength *= 1.1
            
            return min(1.0, actual_strength)
        
        return min(1.0, base_strength)
    
    @staticmethod
    def evaluate_hand_simple(hole_card, community_card):
        """简单牌力评估"""
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
        
        # 基础牌力计算
        high_card = max(card1_rank, card2_rank)
        
        if is_pair:
            # 对子牌力：对子越大越强
            return min(1.0, 0.3 + (high_card / 14.0) * 0.7)
        
        # 高牌牌力
        strength = 0.0
        if high_card >= 12:  # Q以上
            strength = 0.25
        elif high_card >= 10:  # T以上
            strength = 0.2
        else:
            strength = 0.15
        
        # 同花加分
        if is_suited:
            strength += 0.05
        
        # 连牌加分
        gap = abs(card1_rank - card2_rank)
        if gap == 1:  # 连牌
            strength += 0.05
        elif gap <= 3:  # 近似连牌
            strength += 0.02
        
        return min(1.0, strength)
    
    @staticmethod
    def evaluate_actual_hand_strength(hole_card, community_card):
        """评估实际牌力（考虑公共牌后的真实强度）"""
        if not hole_card or len(hole_card) < 2 or not community_card or len(community_card) < 3:
            return AIUtils.evaluate_hand_simple(hole_card, community_card)
        
        # 合并所有牌
        all_cards = hole_card + community_card
        
        # 评估实际牌力
        actual_strength = AIUtils.assess_hand_strength(all_cards)
        
        return actual_strength
    
    @staticmethod
    def assess_hand_strength(all_cards):
        """评估手牌强度（基于所有牌）"""
        if len(all_cards) < 5:
            return AIUtils.evaluate_hand_simple(all_cards[:2], all_cards[2:])
        
        # 提取点数和花色
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = []
        card_suits = []
        
        for card in all_cards:
            rank = card[1]
            suit = card[0]
            card_ranks.append(ranks.get(rank, 0))
            card_suits.append(suit)
        
        # 统计每个点数和花色的数量
        rank_counts = {}
        suit_counts = {}
        
        for rank in card_ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        for suit in card_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # 评估牌力
        strength = 0.0
        
        # 1. 检查同花
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        if max_suit_count >= 5:
            strength = 0.8  # 同花
        elif max_suit_count == 4:
            strength = 0.3  # 4张同花
        elif max_suit_count == 3:
            strength = 0.1  # 3张同花
        
        # 2. 检查顺子可能性
        unique_ranks = sorted(set(card_ranks))
        straight_potential = 0
        
        for i in range(len(unique_ranks) - 2):
            if unique_ranks[i+2] - unique_ranks[i] <= 4:
                straight_potential += 0.1
        
        strength += min(0.3, straight_potential)
        
        # 3. 检查对子和三条
        max_rank_count = max(rank_counts.values()) if rank_counts else 0
        if max_rank_count >= 3:
            strength = max(strength, 0.7)  # 三条
        elif max_rank_count == 2:
            # 计算对子数量
            pair_count = sum(1 for count in rank_counts.values() if count == 2)
            if pair_count >= 2:
                strength = max(strength, 0.6)  # 两对
            else:
                strength = max(strength, 0.4)  # 一对
        
        # 4. 高牌评估（如果没有其他牌力）
        if strength < 0.2:
            # 评估高牌强度
            high_cards = sorted(card_ranks, reverse=True)[:3]  # 取最高的3张牌
            avg_high_card = sum(high_cards) / len(high_cards)
            
            # 高牌强度（基于平均高牌点数）
            if avg_high_card >= 12:  # Q以上
                strength = 0.25
            elif avg_high_card >= 10:  # T以上
                strength = 0.2
            else:
                strength = 0.15
        
        return min(1.0, strength)
    
    @staticmethod
    def assess_board_coordination(community_card):
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
    
    @staticmethod
    def get_position_factor(round_state, player_uuid):
        """获取位置因子"""
        my_position = AIUtils.get_my_position(round_state, player_uuid)
        dealer_btn = round_state['dealer_btn']
        total_players = len([s for s in round_state['seats'] if s['stack'] > 0])
        
        # 位置评估（越靠后越好）
        if my_position == dealer_btn:
            return 1.15  # BTN位置最佳
        elif (my_position - dealer_btn) % total_players <= 2:
            return 1.05  # 靠后位置
        else:
            return 0.95  # 靠前位置
    
    @staticmethod
    def get_my_position(round_state, player_uuid):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == player_uuid:
                return idx
        return 0
    
    @staticmethod
    def format_action(action, amount):
        """格式化行动显示"""
        action_names = {
            'fold': '🚫 弃牌',
            'call': '✅ 跟注',
            'raise': '📈 加注'
        }
        
        action_text = action_names.get(action, action)
        if amount > 0:
            return f"{action_text} ${int(amount)}"
        else:
            return action_text