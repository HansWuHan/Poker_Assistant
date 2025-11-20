"""
改进的AI对手 - 模块化重构版
只保留核心入口逻辑，其他功能迁移到专用模块
"""
import random
import time

try:
    from pypokerengine.players import BasePokerPlayer
except ImportError:
    # 如果pypokerengine不可用，创建一个基类
    class BasePokerPlayer:
        def __init__(self):
            self.uuid = None
        
        def declare_action(self, valid_actions, hole_card, round_state):
            pass

# 导入模块化组件
try:
    from .opponent_model import OpponentModeler
    from .thinking_generator import ThinkingGenerator
    from .ai_utils import AIUtils
except ImportError:
    # 如果模块化导入失败，创建空类
    OpponentModeler = None
    ThinkingGenerator = None
    AIUtils = None

# 导入GTO策略组件
try:
    from ..gto_strategy.gto_advisor import GTOAdvisor
    from ..gto_strategy.gto_core import GTOSituation
    GTO_AVAILABLE = True
except ImportError:
    GTO_AVAILABLE = False
    GTOAdvisor = None
    GTOSituation = None


class ImprovedAIOpponentPlayer(BasePokerPlayer):
    """
    改进的AI对手玩家 - 模块化重构版
    """
    
    def __init__(self, difficulty: str = "medium", shared_hole_cards: dict = None, 
                 show_thinking: bool = True, gto_enabled: bool = True):
        super().__init__()
        self.difficulty = difficulty
        self.action_history = []
        self.round_count = 0
        self.hole_cards = []
        self.shared_hole_cards = shared_hole_cards
        self.show_thinking = show_thinking
        self.gto_enabled = gto_enabled
        
        # 确保有uuid属性
        if not hasattr(self, 'uuid') or self.uuid is None:
            import uuid as uuid_module
            self.uuid = str(uuid_module.uuid4())
        
        # 初始化模块化组件
        self.opponent_modeler = OpponentModeler(self.uuid) if OpponentModeler else None
        self.thinking_generator = ThinkingGenerator(self.uuid) if ThinkingGenerator else None
        self.ai_utils = AIUtils()
        
        # GTO策略组件
        self.gto_advisor = None
        if GTO_AVAILABLE and gto_enabled:
            try:
                self.gto_advisor = GTOAdvisor()
            except Exception:
                self.gto_advisor = None
        
        # 桌面动态数据
        self.table_dynamics = {
            'avg_pot_size': 0,
            'aggression_level': 'normal',
            'recent_raises': 0
        }
    
    def declare_action(self, valid_actions, hole_card, round_state):
        """决定下一步行动 - 模块化入口"""
        import time
        
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 更新桌面动态
        self._update_table_dynamics(round_state)
        
        # 优先使用GTO策略（如果启用且可用）
        gto_action = None
        gto_success = False
        gto_result = None
        
        if self.gto_enabled and self.gto_advisor:
            try:
                gto_action = self._get_gto_advice(valid_actions, hole_card, round_state)
                if gto_action:
                    gto_success = True
                    # 获取GTO结果用于思考过程
                    gto_result = self._get_raw_gto_result(hole_card, round_state, valid_actions)
            except Exception as e:
                print(f"GTO策略失败，使用传统策略: {e}")
        
        # 生成思考过程（如果开启显示）
        if self.show_thinking:
            self._display_thinking_process(hole_card, round_state, valid_actions, gto_result)
        else:
            # 即使关闭思考显示，也添加1秒延时让AI决策更自然
            time.sleep(1)
        
        # 返回GTO决策或回退到传统策略
        if gto_success and gto_action:
            return gto_action
        
        # 根据难度选择传统策略
        if self.difficulty == "easy":
            return self._easy_strategy(fold_action, call_action, raise_action, hole_card, round_state)
        elif self.difficulty == "hard":
            return self._hard_strategy(fold_action, call_action, raise_action, hole_card, round_state)
        else:  # medium
            return self._medium_strategy(fold_action, call_action, raise_action, hole_card, round_state)
    
    def _display_thinking_process(self, hole_card, round_state, valid_actions, gto_result):
        """显示思考过程 - 模块化版本"""
        print()
        
        # 获取AI玩家名字
        ai_name = "AI"
        for seat in round_state.get('seats', []):
            if seat.get('uuid') == self.uuid:
                ai_name = seat.get('name', 'AI')
                break
        print(f"🤖 {ai_name} 思考中...")
        
        # 等待2秒
        import time
        time.sleep(2)
        
        # 获取最终决策
        final_action = self._get_final_action(hole_card, round_state, valid_actions)
        
        # 使用思考生成器生成内容
        if self.thinking_generator:
            heads_up_analysis = None
            
            # 获取正确位置信息和单挑状态
            if self.opponent_modeler:
                is_heads_up = self.opponent_modeler.is_heads_up(round_state)
                active_opponents = self._get_active_opponents_debug(round_state)
                my_position = self._get_my_position_debug(round_state)
            
            if self.opponent_modeler and self.opponent_modeler.is_heads_up(round_state):
                heads_up_analysis = self.opponent_modeler.analyze_heads_up_opponent(round_state)
            
            # 获取正确位置信息
            my_position = self._get_my_position_debug(round_state)
            
            # 统一单挑检测：主类已经计算过，直接使用结果
            is_heads_up = (active_opponents == 1)
            
            # 确保获取单挑分析数据（使用主类的活跃对手数）
            if is_heads_up and self.opponent_modeler:
                # 直接告诉对手建模模块活跃对手数，避免重复计算
                heads_up_analysis = self.opponent_modeler.analyze_heads_up_opponent_with_count(round_state, active_opponents)
            
            thinking_text = self.thinking_generator.generate_thinking_from_action(
                final_action, hole_card, round_state, valid_actions, gto_result, heads_up_analysis, my_position, is_heads_up
            )
            print(thinking_text)
    
    def _get_final_action(self, hole_card, round_state, valid_actions):
        """获取最终决策（用于思考过程）"""
        # 优先使用GTO策略
        if self.gto_enabled and self.gto_advisor:
            try:
                gto_action = self._get_gto_advice(valid_actions, hole_card, round_state)
                if gto_action:
                    return gto_action
            except Exception:
                pass
        
        # 回退到传统策略
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        if self.difficulty == "easy":
            return self._easy_strategy(fold_action, call_action, raise_action, hole_card, round_state)
        elif self.difficulty == "hard":
            return self._hard_strategy(fold_action, call_action, raise_action, hole_card, round_state)
        else:
            return self._medium_strategy(fold_action, call_action, raise_action, hole_card, round_state)
    
    def _easy_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """简化版简单策略"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 基础牌力评估
        hand_strength = self.ai_utils.evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        if street == 'preflop':
            if hand_strength >= 0.8:
                # 超强牌
                if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                    amount = max(raise_action['amount']['min'], int(pot * 0.6))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif hand_strength >= 0.6:
                # 强牌
                if call_action['amount'] <= pot * 0.15:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        else:
            # 翻牌后简化逻辑
            if hand_strength >= 0.7:
                if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif hand_strength >= 0.4:
                if call_action['amount'] <= pot * 0.2:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
    
    def _medium_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """简化版中等策略 - 包含单挑对手建模"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 基础牌力评估
        hand_strength = self.ai_utils.evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self.ai_utils.get_position_factor(round_state, self.uuid)
        
        # 调整后的牌力
        adjusted_strength = hand_strength * position_factor
        
        # 单挑场景：根据对手建模调整策略
        if self.opponent_modeler and self.opponent_modeler.is_heads_up(round_state):
            heads_up_analysis = self.opponent_modeler.analyze_heads_up_opponent(round_state)
            if heads_up_analysis:
                tendency = heads_up_analysis['tendency']
                
                # 根据对手类型调整策略
                if tendency == 'very_aggressive':
                    adjusted_strength *= 0.9  # 对手激进，收紧范围
                elif tendency == 'very_passive':
                    adjusted_strength *= 1.1  # 对手保守，放宽范围
                elif tendency == 'aggressive':
                    adjusted_strength *= 0.95
                elif tendency == 'passive':
                    adjusted_strength *= 1.05
        
        # 根据前位下注金额调整策略
        previous_bets = self._get_previous_bets(round_state)
        max_previous_bet = max(previous_bets) if previous_bets else 0
        
        if max_previous_bet > pot * 0.5:
            adjusted_strength *= 0.85
        elif max_previous_bet < pot * 0.1 and max_previous_bet > 0:
            adjusted_strength *= 1.15
        
        # 翻牌后根据牌面协调性调整
        if street != 'preflop':
            board_coordination = self.ai_utils.assess_board_coordination(round_state.get('community_card', []))
            if board_coordination > 0.7:
                adjusted_strength *= 0.85
            elif board_coordination < 0.3:
                adjusted_strength *= 1.15
        
        # 决策逻辑
        if street == 'preflop':
            if adjusted_strength >= 0.8:
                # 超强牌
                if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                    amount = max(raise_action['amount']['min'], int(pot * 0.7))
                    return raise_action['action'], amount
                return call_action['action'], call_action['amount']
            elif adjusted_strength >= 0.6:
                # 强牌
                if call_action['amount'] <= pot * 0.12:
                    return call_action['action'], call_action['amount']
                elif raise_action['amount']['min'] != -1 and random.random() < 0.4:
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            elif adjusted_strength >= 0.4:
                # 中等牌力
                if call_action['amount'] <= pot * 0.08:
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        else:
            # 翻牌后决策
            if adjusted_strength >= 0.8:
                # 强牌，价值下注
                if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                    bet_size = self._calculate_value_bet_size(adjusted_strength, pot, raise_action)
                    return raise_action['action'], bet_size
                return call_action['action'], call_action['amount']
            elif adjusted_strength >= 0.5:
                # 中等强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                if pot_odds <= 0.25:
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
    
    def _hard_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """简化版困难策略"""
        # 困难策略使用更精细的参数
        return self._medium_strategy(fold_action, call_action, raise_action, hole_card, round_state)
    
    def _get_previous_bets(self, round_state):
        """获取前面玩家的下注金额（排除盲注）"""
        action_histories = round_state.get('action_histories', {})
        street = round_state['street']
        previous_bets = []

        if street in action_histories:
            for action in action_histories[street]:
                if isinstance(action, dict) and action.get('action') in ['raise', 'bet']:
                    amount = action.get('amount', 0)
                    # 排除盲注（金额<=20且是preflop）
                    if not (street == 'preflop' and amount <= 20):
                        previous_bets.append(amount)

        return previous_bets
    
    def _calculate_value_bet_size(self, hand_strength, pot, raise_action):
        """计算价值下注大小（简化版）"""
        min_raise = raise_action['amount']['min']
        max_raise = raise_action['amount']['max']
        
        # 根据牌力决定下注比例
        if hand_strength >= 0.9:
            bet_ratio = 0.8
        elif hand_strength >= 0.8:
            bet_ratio = 0.7
        elif hand_strength >= 0.6:
            bet_ratio = 0.6
        else:
            bet_ratio = 0.5
        
        bet_size = int(pot * bet_ratio)
        
        # 确保在允许范围内
        if bet_size < min_raise:
            return min_raise
        elif bet_size > max_raise:
            return max_raise
        else:
            return bet_size
    
    def _get_gto_advice(self, valid_actions, hole_card, round_state):
        """获取GTO策略建议（简化版）"""
        if not self.gto_advisor:
            return None
        
        try:
            # 准备GTO需要的参数
            street = round_state['street']
            position = self._get_position_name(round_state)
            stack_size = self._get_my_stack(round_state)
            pot_size = round_state['pot']['main']['amount']
            community_cards = round_state.get('community_card', [])
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 获取GTO建议
            gto_result = self.gto_advisor.get_gto_advice(
                hole_cards=hole_card,
                community_cards=community_cards,
                street=street,
                position=position,
                pot_size=pot_size,
                stack_size=stack_size,
                call_amount=call_amount,
                valid_actions=valid_actions,
                opponent_actions=[],  # 简化版，暂时传入空列表
                active_opponents=[]  # 简化版，暂时传入空列表
            )
            
            if gto_result:
                # 转换GTO建议为行动
                action_type = gto_result['action']
                amount = gto_result.get('amount', 0)
                
                # 映射到可用行动
                if action_type == 'fold':
                    fold_action = next((a for a in valid_actions if a['action'] == 'fold'), None)
                    if fold_action:
                        return fold_action['action'], fold_action['amount']
                
                elif action_type == 'call':
                    call_action = next((a for a in valid_actions if a['action'] == 'call'), None)
                    if call_action:
                        return call_action['action'], call_action['amount']
                
                elif action_type == 'raise':
                    raise_action = next((a for a in valid_actions if a['action'] == 'raise'), None)
                    if raise_action and raise_action['amount']['min'] != -1:
                        gto_amount = max(amount, raise_action['amount']['min'])
                        gto_amount = min(gto_amount, raise_action['amount']['max'])
                        return raise_action['action'], int(gto_amount)
            
            return None
            
        except Exception as e:
            print(f"GTO策略获取失败: {e}")
            return None
    
    def _get_raw_gto_result(self, hole_card, round_state, valid_actions):
        """获取原始GTO结果，用于思考过程分析"""
        if not self.gto_advisor:
            return None
        
        try:
            # 准备GTO需要的参数
            street = round_state['street']
            position = self._get_position_name(round_state)
            stack_size = self._get_my_stack(round_state)
            pot_size = round_state['pot']['main']['amount']
            community_cards = round_state.get('community_card', [])
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 获取GTO建议
            return self.gto_advisor.get_gto_advice(
                hole_cards=hole_card,
                community_cards=community_cards,
                street=street,
                position=position,
                pot_size=pot_size,
                stack_size=stack_size,
                call_amount=call_amount,
                valid_actions=valid_actions,
                opponent_actions=[],  # 简化版，暂时传入空列表
                active_opponents=[]  # 简化版，暂时传入空列表
            )
            
        except Exception as e:
            return None
    
    def _get_position_name(self, round_state):
        """获取位置名称"""
        position_idx = self._get_my_position(round_state)
        total_players = len([s for s in round_state['seats'] if s['stack'] > 0])
        
        if total_players <= 2:
            return "BTN" if position_idx == 0 else "BB"
        
        dealer_btn = round_state['dealer_btn']
        
        if position_idx == dealer_btn:
            return "BTN"
        elif position_idx == (dealer_btn - 1) % len(round_state['seats']):
            return "CO"
        elif position_idx == (dealer_btn - 2) % len(round_state['seats']):
            return "HJ"
        else:
            return "MP"
    
    def _get_my_position(self, round_state):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == self.uuid:
                return idx
        return 0
    
    def _get_my_stack(self, round_state):
        """获取我的筹码量"""
        for seat in round_state['seats']:
            if seat['uuid'] == self.uuid:
                return seat.get('stack', 0)
        return 0
    
    def _get_active_opponents_debug(self, round_state):
        """获取活跃对手数量（清理版）"""
        seats = round_state.get('seats', [])
        active_opponents = []
        
        for seat in seats:
            if (seat.get('stack', 0) > 0 
                and seat.get('uuid') != self.uuid 
                and seat.get('state', 'participating') == 'participating'):
                active_opponents.append({
                    'name': seat.get('name', 'Unknown'),
                    'uuid': seat.get('uuid', ''),
                    'stack': seat.get('stack', 0)
                })
        
        return len(active_opponents)
    
    def _get_my_position_debug(self, round_state):
        """获取我的位置（6人桌标准）"""
        dealer_btn = round_state.get('dealer_btn', 0)
        small_blind_pos = round_state.get('small_blind_pos', 1)
        big_blind_pos = round_state.get('big_blind_pos', 2)
        
        my_pos = 0
        for idx, seat in enumerate(round_state.get('seats', [])):
            if seat.get('uuid') == self.uuid:
                my_pos = idx
                break
        
        total_players = len([s for s in round_state.get('seats', []) if s.get('stack', 0) > 0])
        
        # 正确位置判断（6人桌）
        if total_players <= 2:
            pos_name = "按钮位" if my_pos == dealer_btn else "大盲位"
        else:
            # 计算相对位置（从庄家开始顺时针）
            relative_pos = (my_pos - dealer_btn) % total_players
            
            if relative_pos == 0:
                pos_name = "按钮位"
            elif relative_pos == 1:
                pos_name = "小盲位"
            elif relative_pos == 2:
                pos_name = "大盲位"
            elif relative_pos == 3:
                pos_name = "UTG(枪口位)"
            elif relative_pos == 4:
                pos_name = "HJ(劫持位)"
            else:  # relative_pos == 5
                pos_name = "CO(关煞位)"
        
        return pos_name
    
    def _update_table_dynamics(self, round_state):
        """更新桌面动态"""
        street = round_state['street']
        action_histories = round_state.get('action_histories', {})
        
        if street in action_histories:
            recent_raises = sum(1 for action in action_histories[street] 
                              if action.get('action', '').lower() == 'raise')
            self.table_dynamics['recent_raises'] = recent_raises
    
    # 实现pypokerengine要求的接口方法
    def receive_game_start_message(self, game_info):
        """接收游戏开始消息"""
        pass
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        """接收回合开始消息"""
        self.hole_cards = hole_card
        self.round_count = round_count
    
    def receive_street_start_message(self, street, round_state):
        """接收街道开始消息"""
        pass
    
    def receive_game_update_message(self, action, round_state):
        """接收游戏更新消息"""
        pass
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        """接收回合结果消息"""
        pass