"""
下注尺度优化器 - 基于GTO理论优化下注尺度
"""
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SizingContext:
    """下注尺度上下文"""
    street: str  # preflop, flop, turn, river
    position: str  # BTN, SB, BB, UTG, etc.
    pot_size: int
    stack_size: int
    effective_stack: int
    board_texture: str  # dry, wet, dynamic
    hand_strength: float  # 0-1
    opponent_tendency: float  # 对手倾向
    is_ip: bool  # 是否有位置优势
    previous_action: str  # 之前的行动
    

class SizingOptimizer:
    """GTO下注尺度优化器"""
    
    def __init__(self):
        # GTO标准尺度
        self.standard_sizings = {
            'preflop': {
                'open': 2.5,  # 2.5BB
                '3bet': 3.5,  # 3.5倍加注
                '4bet': 2.2,  # 2.2倍3bet
                '5bet': 1.0   # 全下
            },
            'postflop': {
                'value_bet': {
                    'thin': 0.5,      # 薄价值下注
                    'standard': 0.75, # 标准价值下注
                    'big': 1.0,       # 大价值下注
                    'overbet': 1.25   # 超额下注
                },
                'bluff': {
                    'small': 0.33,    # 小诈唬
                    'standard': 0.75, # 标准诈唬
                    'big': 1.0,       # 大诈唬
                    'overbet': 1.25   # 超额诈唬
                },
                'probe': {
                    'small': 0.4,     # 探测下注
                    'standard': 0.65
                }
            }
        }
        
        # 情境调整因子
        self.context_factors = {
            'position': {
                'BTN': 1.1,  # 按钮位可以更激进
                'CO': 1.05,
                'HJ': 1.0,
                'MP': 0.95,
                'UTG': 0.9,
                'SB': 0.95,  # 小盲位置劣势
                'BB': 0.9    # 大盲位置最差
            },
            'board_texture': {
                'dry': 0.85,      # 干燥牌面小尺度
                'wet': 1.15,      # 湿润牌面大尺度
                'dynamic': 1.0,   # 动态牌面标准尺度
                'paired': 0.9     # 对子牌面小尺度
            },
            'stack_depth': {
                'shallow': 0.8,   # 浅筹码保守
                'medium': 1.0,    # 中等筹码标准
                'deep': 1.2       # 深筹码可以更激进
            },
            'opponent_tendency': {
                'tight': 1.1,     # 紧的对手可以更大下注
                'loose': 0.9,     # 松的对手小尺度
                'aggressive': 1.0, # 激进的对手标准尺度
                'passive': 1.05   # 被动的对手可以稍大
            }
        }
        
    def calculate_optimal_sizing(self, context: SizingContext, action_type: str) -> float:
        """
        计算最优下注尺度
        
        Args:
            context: 下注上下文
            action_type: 行动类型 ('value_bet', 'bluff', 'probe')
            
        Returns:
            最优尺度 (作为底池比例)
        """
        # 基础尺度
        base_sizing = self._get_base_sizing(context.street, action_type, context.hand_strength)
        
        # 应用情境调整
        adjusted_sizing = self._apply_context_adjustments(base_sizing, context, action_type)
        
        # 应用边界约束
        final_sizing = self._apply_constraints(adjusted_sizing, context, action_type)
        
        return final_sizing
    
    def _get_base_sizing(self, street: str, action_type: str, hand_strength: float) -> float:
        """获取基础尺度"""
        if street == 'preflop':
            return self.standard_sizings['preflop'].get(action_type, 2.5)
        
        # 翻牌后根据牌力和行动类型选择
        postflop_sizings = self.standard_sizings['postflop']
        
        if action_type == 'value_bet':
            if hand_strength >= 0.8:
                return postflop_sizings['value_bet']['big']
            elif hand_strength >= 0.65:
                return postflop_sizings['value_bet']['standard']
            elif hand_strength >= 0.5:
                return postflop_sizings['value_bet']['thin']
            else:
                return postflop_sizings['value_bet']['standard']
        
        elif action_type == 'bluff':
            # 诈唬通常使用标准尺度以保持平衡
            return postflop_sizings['bluff']['standard']
        
        elif action_type == 'probe':
            return postflop_sizings['probe']['standard']
        
        return 0.75  # 默认标准尺度
    
    def _apply_context_adjustments(self, base_sizing: float, context: SizingContext, action_type: str) -> float:
        """应用情境调整"""
        adjusted = base_sizing
        
        # 位置调整
        position_factor = self.context_factors['position'].get(context.position, 1.0)
        adjusted *= position_factor
        
        # 牌面纹理调整
        texture_factor = self.context_factors['board_texture'].get(context.board_texture, 1.0)
        adjusted *= texture_factor
        
        # 筹码深度调整
        stack_depth = self._classify_stack_depth(context.effective_stack, context.pot_size)
        stack_factor = self.context_factors['stack_depth'].get(stack_depth, 1.0)
        adjusted *= stack_factor
        
        # 对手倾向调整
        opponent_tendency = self._classify_opponent_tendency(context.opponent_tendency)
        opponent_factor = self.context_factors['opponent_tendency'].get(opponent_tendency, 1.0)
        adjusted *= opponent_factor
        
        return adjusted
    
    def _apply_constraints(self, sizing: float, context: SizingContext, action_type: str) -> float:
        """应用约束条件"""
        # 最小尺度约束
        min_sizing = self._get_min_sizing(context, action_type)
        
        # 最大尺度约束
        max_sizing = self._get_max_sizing(context, action_type)
        
        # 筹码约束
        max_possible = context.effective_stack / context.pot_size if context.pot_size > 0 else 100
        
        # 应用所有约束
        final_sizing = max(min_sizing, min(sizing, max_sizing, max_possible))
        
        return final_sizing
    
    def _get_min_sizing(self, context: SizingContext, action_type: str) -> float:
        """获取最小尺度"""
        if context.street == 'preflop':
            return 2.0  # 翻牌前最少2BB
        
        # 翻牌后最小尺度
        if action_type == 'value_bet':
            return 0.33  # 价值下注最少1/3底池
        elif action_type == 'bluff':
            return 0.5   # 诈唬最少半池
        else:
            return 0.33  # 其他最少1/3底池
    
    def _get_max_sizing(self, context: SizingContext, action_type: str) -> float:
        """获取最大尺度"""
        if context.street == 'preflop':
            # 翻牌前根据筹码深度
            if context.effective_stack < 50:  # 浅筹码
                return min(4.0, context.effective_stack / context.pot_size * 0.8)
            else:
                return 4.0  # 深筹码最多4倍
        
        # 翻牌后最大尺度
        if action_type == 'value_bet':
            return 2.0  # 价值下注最多2倍底池
        elif action_type == 'bluff':
            return 1.25  # 诈唬最多1.25倍底池
        else:
            return 1.5   # 其他最多1.5倍底池
    
    def _classify_stack_depth(self, effective_stack: int, pot_size: int) -> str:
        """分类筹码深度"""
        if pot_size == 0:
            return 'medium'
        
        stack_to_pot = effective_stack / pot_size
        
        if stack_to_pot < 8:
            return 'shallow'
        elif stack_to_pot > 20:
            return 'deep'
        else:
            return 'medium'
    
    def _classify_opponent_tendency(self, tendency: float) -> str:
        """分类对手倾向"""
        if tendency > 1.3:
            return 'loose'
        elif tendency < 0.8:
            return 'tight'
        elif tendency > 1.1:
            return 'aggressive'
        else:
            return 'passive'
    
    def calculate_sizing_for_street(self, street: str, context: SizingContext) -> Dict[str, float]:
        """
        计算整条街的各种下注尺度
        
        Args:
            street: 街道
            context: 上下文
            
        Returns:
            各种行动的推荐尺度
        """
        return {
            'value_bet': self.calculate_optimal_sizing(context, 'value_bet'),
            'bluff': self.calculate_optimal_sizing(context, 'bluff'),
            'probe': self.calculate_optimal_sizing(context, 'probe'),
            'check_back': 0.0  # 过牌是0
        }
    
    def get_gto_sizing_explanation(self, sizing: float, context: SizingContext, action_type: str) -> str:
        """获取GTO尺度的解释"""
        pot_percentage = sizing * 100
        
        explanation = f"""
💰 GTO下注尺度分析

📊 基础参数:
• 底池大小: ${context.pot_size}
• 有效筹码: ${context.effective_stack}  
• 位置: {context.position}
• 牌面: {context.board_texture}
• 牌力: {context.hand_strength:.2f}

🎯 推荐尺度: {pot_percentage:.0f}% 底池 (${int(context.pot_size * sizing)})

🔍 尺度分析:
"""
        
        if sizing <= 0.4:
            explanation += "• 小额下注 (≤40%): 适用于薄价值或探测"
        elif sizing <= 0.7:
            explanation += "• 标准下注 (40-70%): 平衡的价值下注和诈唬"
        elif sizing <= 1.0:
            explanation += "• 大额下注 (70-100%): 强价值牌或高胜率诈唬"
        else:
            explanation += "• 超额下注 (>100%): 极化范围，极强牌或纯诈唬"
        
        explanation += f"\n\n📈 情境调整:"
        
        # 解释各种调整
        if context.board_texture == 'wet':
            explanation += "\n• 湿润牌面: 尺度增加15% (保护强牌)"
        elif context.board_texture == 'dry':
            explanation += "\n• 干燥牌面: 尺度减少15% (节省筹码)"
        
        if context.position == 'BTN':
            explanation += "\n• 按钮位置: 尺度增加10% (位置优势)"
        elif context.position == 'BB':
            explanation += "\n• 大盲位置: 尺度减少10% (位置劣势)"
        
        stack_depth = self._classify_stack_depth(context.effective_stack, context.pot_size)
        if stack_depth == 'deep':
            explanation += "\n• 深筹码: 尺度增加20% (筹码充足)"
        elif stack_depth == 'shallow':
            explanation += "\n• 浅筹码: 尺度减少20% (保护筹码)"
        
        return explanation