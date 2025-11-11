"""
输入处理器模块
处理用户输入和命令
"""
from typing import Tuple, Optional, Dict, Any, Callable
import sys


class InputHandler:
    """输入处理器"""
    
    def __init__(self, chat_callback: Optional[Callable] = None, renderer=None):
        """
        Args:
            chat_callback: 处理聊天的回调函数
            renderer: 游戏渲染器，用于显示AI分析
        """
        self.chat_callback = chat_callback
        self.renderer = renderer
        self.chat_mode = False
    
    def get_action(self, valid_actions: list, hole_card: list, 
                   round_state: dict, ai_advice_callback=None) -> Tuple[str, int]:
        """
        获取用户行动
        
        Args:
            valid_actions: 可选行动列表
            hole_card: 手牌
            round_state: 回合状态
            ai_advice_callback: AI建议回调函数，用于获取牌力分析
        
        Returns:
            (action, amount) 元组
        """
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 显示提示信息（现在包含O选项）
        self._show_action_prompt(call_action, raise_action, ai_advice_callback is not None)
        
        while True:
            try:
                user_input = input("\n> ").strip().upper()
                
                # 处理特殊命令
                if user_input == 'Q' or user_input == 'QUESTION':
                    self._handle_question_mode(hole_card, round_state)
                    continue
                
                elif user_input == 'H' or user_input == 'HELP':
                    self._show_help()
                    continue
                
                elif user_input == 'S' or user_input == 'STATUS':
                    self._show_status(round_state)
                    continue
                
                elif user_input == 'O' or user_input == 'ADVICE':
                    # 获取AI牌力分析
                    if ai_advice_callback:
                        try:
                            # 显示loading状态
                            print("\n⏳ 正在获取AI牌力分析...")
                            
                            advice = ai_advice_callback()
                            if advice:
                                # 使用renderer显示AI分析（如果有renderer）
                                if self.renderer and hasattr(self.renderer, 'render_ai_advice'):
                                    self.renderer.render_ai_advice(advice)
                                else:
                                    # 备用显示方式
                                    print(f"\n🤖 AI分析: {advice}")
                            else:
                                print("\n⚠️ 无法获取AI分析")
                        except Exception as e:
                            print(f"\n⚠️ 获取AI分析失败: {e}")
                    else:
                        print("\n⚠️ AI功能未启用")
                    continue
                
                # 处理行动
                elif user_input == 'F' or user_input == 'FOLD':
                    return fold_action['action'], fold_action['amount']
                
                elif user_input == 'C' or user_input == 'CALL':
                    return call_action['action'], call_action['amount']
                
                elif user_input == 'R' or user_input == 'RAISE':
                    if raise_action['amount']['min'] == -1:
                        print("❌ 当前不能加注")
                        continue
                    
                    amount = self._get_raise_amount(raise_action)
                    if amount is not None:
                        return raise_action['action'], amount
                
                elif user_input == 'A' or user_input == 'ALLIN':
                    if raise_action['amount']['max'] != -1:
                        return raise_action['action'], raise_action['amount']['max']
                    else:
                        print("❌ 当前不能全下")
                        continue
                
                else:
                    print("❌ 无效的输入，请输入 F/C/R/A/Q/H 或完整命令")
            
            except KeyboardInterrupt:
                print("\n")
                confirm = input("确定要退出游戏吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    sys.exit(0)
                continue
            
            except EOFError:
                print("\n游戏被中断")
                return fold_action['action'], fold_action['amount']
    
    def _show_action_prompt(self, call_action: dict, raise_action: dict, ai_enabled: bool = False):
        """显示行动提示"""
        actions = []
        actions.append("[F]弃牌")
        actions.append(f"[C]跟注(${call_action['amount']})")
        
        if raise_action['amount']['min'] != -1:
            min_raise = raise_action['amount']['min']
            max_raise = raise_action['amount']['max']
            actions.append(f"[R]加注(${min_raise}-${max_raise})")
            actions.append(f"[A]全下(${max_raise})")
        
        if ai_enabled:
            actions.append("[O]牌力分析")
        
        actions.append("[Q]提问")
        actions.append("[H]帮助")
        
        print("\n" + " | ".join(actions))
    
    def _get_raise_amount(self, raise_action: dict) -> Optional[int]:
        """获取加注金额"""
        min_raise = raise_action['amount']['min']
        max_raise = raise_action['amount']['max']
        
        print(f"\n💰 加注范围: ${min_raise} - ${max_raise}")
        print("💡 提示: 输入 'min' 最小加注, 'max' 全下, 或具体金额")
        
        while True:
            try:
                amount_input = input("加注金额: ").strip().lower()
                
                if amount_input == 'min':
                    return min_raise
                elif amount_input == 'max':
                    return max_raise
                elif amount_input == 'cancel' or amount_input == 'c':
                    return None
                else:
                    try:
                        amount = int(amount_input)
                        if min_raise <= amount <= max_raise:
                            return amount
                        else:
                            print(f"❌ 金额必须在 ${min_raise} - ${max_raise} 之间")
                    except ValueError:
                        print("❌ 请输入有效的数字、'min'、'max' 或 'cancel'")
            
            except KeyboardInterrupt:
                print("\n取消加注")
                return None
    
    def _handle_question_mode(self, hole_card: list, round_state: dict):
        """处理提问模式"""
        print("\n" + "="*60)
        print("💬 提问模式（输入问题，输入 'exit' 退出）")
        print("="*60)
        
        while True:
            try:
                question = input("\n你的问题: ").strip()
                
                if question.lower() in ['exit', 'quit', 'back', 'e']:
                    print("退出提问模式")
                    break
                
                if not question:
                    continue
                
                # 调用聊天回调
                if self.chat_callback:
                    try:
                        response = self.chat_callback(question, hole_card, round_state)
                        print(f"\n🤖 AI: {response}")
                    except Exception as e:
                        print(f"❌ 处理问题时出错: {e}")
                        print("💡 提示: AI 功能需要配置 DEEPSEEK_API_KEY")
                else:
                    print("❌ 聊天功能未启用")
                    break
            
            except KeyboardInterrupt:
                print("\n退出提问模式")
                break
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n" + "="*60)
        print("📖 帮助信息")
        print("="*60)
        print("F / FOLD    - 弃牌")
        print("C / CALL    - 跟注")
        print("R / RAISE   - 加注")
        print("A / ALLIN   - 全下")
        print("O / ADVICE  - 获取AI牌力分析")
        print("Q / QUESTION - 向 AI 提问")
        print("H / HELP    - 显示帮助")
        print("S / STATUS  - 显示状态")
        print("="*60)
    
    def _show_status(self, round_state: dict):
        """显示当前状态"""
        print("\n" + "="*60)
        print("📊 当前状态")
        print("="*60)
        print(f"街道: {round_state['street']}")
        print(f"底池: ${round_state['pot']['main']['amount']}")
        print(f"公共牌: {round_state.get('community_card', [])}")
        
        print("\n玩家状态:")
        for seat in round_state['seats']:
            status_icon = "✅" if seat['state'] == 'participating' else "❌"
            print(f"  {status_icon} {seat['name']}: ${seat['stack']} ({seat['state']})")
        print("="*60)
    
    def confirm_action(self, action: str, amount: int) -> bool:
        """
        确认行动（可选）
        
        Args:
            action: 行动类型
            amount: 金额
        
        Returns:
            是否确认
        """
        # 对于大额加注，要求确认
        if action == 'raise' and amount > 100:
            confirm = input(f"确认加注 ${amount}? (y/n): ").strip().lower()
            return confirm == 'y'
        
        return True

