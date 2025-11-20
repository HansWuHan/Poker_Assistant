"""
对手建模模块 - 专门用于分析对手行为和预测手牌范围
"""

class OpponentModeler:
    """对手建模器 - 分析对手行为模式"""
    
    def __init__(self, player_uuid):
        self.player_uuid = player_uuid
        self.opponent_stats = {}  # 存储对手统计数据
    
    def is_heads_up(self, round_state):
        """判断是否进入单挑场景（heads-up）"""
        active_count = self._get_active_opponents(round_state)
        return active_count == 1

    def _get_active_opponents(self, round_state):
        """获取活跃对手数量（排除已弃牌玩家和自己）"""
        seats = round_state.get('seats', [])
        active_opponents = []
        
        for seat in seats:
            if (seat.get('stack', 0) > 0 
                and seat.get('uuid') != self.player_uuid 
                and seat.get('state', 'participating') == 'participating'):
                active_opponents.append(seat.get('name', 'Unknown'))
        
        # 清理调试输出，保持界面整洁
        return len(active_opponents)

    def analyze_heads_up_opponent_with_count(self, round_state, active_opponent_count):
        """接收主类的活跃对手数，避免重复计算"""
        if active_opponent_count != 1:
            return None
        
        return self._analyze_heads_up_opponent_internal(round_state)
    
    def analyze_heads_up_opponent(self, round_state):
        """单挑对手建模：分析下注频率、激进程度、摊牌倾向"""
        if not self.is_heads_up(round_state):
            return None
        
        return self._analyze_heads_up_opponent_internal(round_state)
    
    def _analyze_heads_up_opponent_internal(self, round_state):
        """内部实现：单挑对手建模"""
        
        # 获取对手UUID（单挑时只有一个对手）
        opponent_uuid = None
        for seat in round_state.get('seats', []):
            if seat.get('uuid') != self.player_uuid and seat.get('state') == 'participating':
                opponent_uuid = seat['uuid']
                break
        
        if not opponent_uuid:
            return None
        
        # 统计对手行为
        action_histories = round_state.get('action_histories', {})
        total_actions = 0
        aggressive_actions = 0
        call_actions = 0
        fold_actions = 0
        
        for street, actions in action_histories.items():
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get('uuid') == opponent_uuid:
                        action_type = action.get('action', '').lower()
                        amount = action.get('amount', 0)
                        
                        # 排除盲注
                        if street == 'preflop' and amount <= 20 and action_type in ['call', 'raise']:
                            continue
                        
                        total_actions += 1
                        if action_type in ['raise', 'bet']:
                            aggressive_actions += 1
                        elif action_type == 'call':
                            call_actions += 1
                        elif action_type == 'fold':
                            fold_actions += 1
        
        if total_actions == 0:
            return {
                'aggression_factor': 0.5,
                'fold_rate': 0.3,
                'tendency': 'unknown',
                'description': '对手数据不足，使用默认策略'
            }
        
        # 计算激进程度
        aggression_factor = aggressive_actions / total_actions
        fold_rate = fold_actions / total_actions
        
        # 判断对手类型
        if aggression_factor > 0.6:
            tendency = 'very_aggressive'
            description = '对手非常激进，频繁加注，建议收紧范围，多用强牌反击'
        elif aggression_factor > 0.4:
            tendency = 'aggressive'
            description = '对手激进，喜欢主导底池，建议谨慎对抗'
        elif aggression_factor < 0.2:
            tendency = 'very_passive'
            description = '对手非常保守，很少加注，可以多偷盲，价值下注更薄'
        elif aggression_factor < 0.3:
            tendency = 'passive'
            description = '对手保守，多为跟注，可以大胆价值下注'
        else:
            tendency = 'balanced'
            description = '对手平衡型，建议标准策略应对'
        
        return {
            'aggression_factor': aggression_factor,
            'fold_rate': fold_rate,
            'tendency': tendency,
            'description': description,
            'total_actions': total_actions,
            'aggressive_actions': aggressive_actions
        }

    def predict_opponent_range_heads_up(self, round_state, opponent_analysis):
        """单挑场景：预测对手手牌范围"""
        if not opponent_analysis:
            return "对手范围：标准范围（数据不足）"
        
        street = round_state['street']
        action_histories = round_state.get('action_histories', {})
        current_street_actions = action_histories.get(street, [])
        
        # 获取对手当前街道的行动
        opponent_current_action = None
        for action in current_street_actions:
            if isinstance(action, dict) and action.get('uuid') != self.player_uuid:
                action_type = action.get('action', '').lower()
                amount = action.get('amount', 0)
                # 排除盲注
                if not (street == 'preflop' and amount <= 20):
                    opponent_current_action = {'type': action_type, 'amount': amount}
        
        # 基于对手类型和当前行动预测范围
        tendency = opponent_analysis['tendency']
        
        if street == 'preflop':
            if tendency == 'very_aggressive':
                if opponent_current_action and opponent_current_action['type'] == 'raise':
                    if opponent_current_action['amount'] > 100:
                        return "对手范围：强牌（AA,KK,AK）或频繁诈唬"
                    else:
                        return "对手范围：较宽，可能包含KQ,AJ,中等对子"
                else:
                    return "对手范围：较宽，可能包含同花连牌，高牌"
            elif tendency == 'very_passive':
                if opponent_current_action and opponent_current_action['type'] == 'raise':
                    return "对手范围：极强牌（AA,KK,QQ,AK），保守玩家加注就是强牌"
                else:
                    return "对手范围：中等强度（对子，高牌），很少诈唬"
            else:
                return "对手范围：标准起手牌范围，中等强度"
        
        else:  # 翻牌后
            pot = round_state['pot']['main']['amount']
            if opponent_current_action:
                action_type = opponent_current_action['type']
                amount = opponent_current_action['amount']
                
                if tendency == 'very_aggressive':
                    if action_type == 'bet' and amount > pot * 0.7:
                        return "对手可能：强牌（顶对+）或大额诈唬"
                    elif action_type == 'raise':
                        return "对手可能：强牌或标准诈唬，激进玩家范围较宽"
                    else:
                        return "对手可能：中等牌力，跟注范围较宽"
                elif tendency == 'very_passive':
                    if action_type == 'raise':
                        return "对手可能：极强牌（两对+），保守玩家加注很少诈唬"
                    elif action_type == 'bet':
                        return "对手可能：成牌（对子+），很少纯诈唬"
                    else:
                        return "对手可能：边缘牌或听牌，谨慎跟注"
                else:
                    return "对手范围：标准成牌范围，结合牌面分析"
            else:
                return "对手尚未行动，范围较宽"
        
        return "对手范围：标准范围"