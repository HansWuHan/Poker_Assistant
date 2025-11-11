"""
人类玩家模块
处理人类玩家的输入和行动
"""
from typing import Tuple, Optional, Callable
from pypokerengine.players import BasePokerPlayer


class HumanPlayer(BasePokerPlayer):
    """
    人类玩家类
    通过回调函数从 CLI 获取用户输入
    """
    
    def __init__(self, 
                 input_callback: Optional[Callable] = None,
                 display_callback: Optional[Callable] = None):
        """
        Args:
            input_callback: 获取用户输入的回调函数
            display_callback: 显示信息的回调函数
        """
        super().__init__()
        self.input_callback = input_callback
        self.display_callback = display_callback
        self.hole_cards = []
        self.round_count = 0
        
    def declare_action(self, valid_actions, hole_card, round_state) -> Tuple[str, int]:
        """
        决定下一步行动（通过用户输入）
        
        Args:
            valid_actions: 可选行动列表
            hole_card: 手牌
            round_state: 回合状态
        
        Returns:
            (action, amount) 元组
        """
        self.hole_cards = hole_card
        
        # 如果有输入回调，使用回调获取输入
        if self.input_callback:
            try:
                action, amount = self.input_callback(valid_actions, hole_card, round_state)
                return action, amount
            except Exception as e:
                print(f"获取输入时出错: {e}")
                # 默认跟注
                call_action = valid_actions[1]
                return call_action['action'], call_action['amount']
        
        # 如果没有回调，使用命令行输入（备用方案）
        return self._get_action_from_console(valid_actions, hole_card, round_state)
    
    def _get_action_from_console(self, valid_actions, hole_card, round_state) -> Tuple[str, int]:
        """
        从命令行获取行动（备用方案）
        """
        print("\n" + "="*60)
        print(f"你的手牌: {hole_card}")
        print(f"公共牌: {round_state.get('community_card', [])}")
        print(f"底池: ${round_state['pot']['main']['amount']}")
        print("="*60)
        
        # 显示可选行动
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        print("\n可选行动:")
        print(f"1. [F]弃牌 (Fold)")
        print(f"2. [C]跟注 (Call) - ${call_action['amount']}")
        
        if raise_action['amount']['min'] != -1:
            print(f"3. [R]加注 (Raise) - ${raise_action['amount']['min']} ~ ${raise_action['amount']['max']}")
        
        # 获取用户输入
        while True:
            try:
                choice = input("\n请选择行动 (F/C/R): ").strip().upper()
                
                if choice == 'F':
                    return fold_action['action'], fold_action['amount']
                
                elif choice == 'C':
                    return call_action['action'], call_action['amount']
                
                elif choice == 'R':
                    if raise_action['amount']['min'] == -1:
                        print("当前不能加注，请选择其他行动")
                        continue
                    
                    min_raise = raise_action['amount']['min']
                    max_raise = raise_action['amount']['max']
                    
                    # 显示加注规则信息
                    round_state = self.game_state.round_state if hasattr(self.game_state, 'round_state') else None
                    if round_state and min_raise > 0:
                        street = round_state.get('street', 'preflop')
                        action_histories = round_state.get('action_histories', {})
                        
                        if street in action_histories:
                            max_previous_raise = 0
                            for action in action_histories[street]:
                                if action.get('action', '').upper() == 'RAISE':
                                    amount = action.get('amount', 0)
                                    max_previous_raise = max(max_previous_raise, amount)
                            
                            if max_previous_raise > 0:
                                required_min = max_previous_raise * 2
                                print(f"📏 加注规则: 必须至少为之前最大加注(${max_previous_raise})的一倍")
                                print(f"📊 理论最小: ${required_min} (实际最小: ${min_raise})")
                    
                    amount_input = input(f"请输入加注金额 ({min_raise}-{max_raise}): ").strip()
                    
                    try:
                        amount = int(amount_input)
                        if min_raise <= amount <= max_raise:
                            return raise_action['action'], amount
                        else:
                            print(f"金额必须在 {min_raise} 到 {max_raise} 之间")
                    except ValueError:
                        print("请输入有效的数字")
                
                else:
                    print("无效的选择，请输入 F, C 或 R")
            
            except KeyboardInterrupt:
                print("\n\n游戏被中断")
                return fold_action['action'], fold_action['amount']
    
    def receive_game_start_message(self, game_info):
        """接收游戏开始消息"""
        self.round_count = 0
        if self.display_callback:
            try:
                self.display_callback("game_start", game_info)
            except Exception as e:
                print(f"显示回调出错: {e}")
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        """接收回合开始消息"""
        self.round_count = round_count
        self.hole_cards = hole_card
        if self.display_callback:
            try:
                self.display_callback("round_start", {
                    "round_count": round_count,
                    "hole_card": hole_card,
                    "seats": seats
                })
            except Exception as e:
                print(f"显示回调出错: {e}")
    
    def receive_street_start_message(self, street, round_state):
        """接收街道开始消息"""
        if self.display_callback:
            try:
                self.display_callback("street_start", {
                    "street": street,
                    "round_state": round_state
                })
            except Exception as e:
                print(f"显示回调出错: {e}")
    
    def receive_game_update_message(self, action, round_state):
        """接收游戏更新消息（其他玩家的行动）"""
        if self.display_callback:
            try:
                self.display_callback("game_update", {
                    "action": action,
                    "round_state": round_state
                })
            except Exception as e:
                print(f"显示回调出错: {e}")
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        """接收回合结果消息"""
        if self.display_callback:
            try:
                self.display_callback("round_result", {
                    "winners": winners,
                    "hand_info": hand_info,
                    "round_state": round_state
                })
            except Exception as e:
                print(f"显示回调出错: {e}")

