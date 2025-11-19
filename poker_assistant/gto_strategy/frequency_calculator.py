"""
频率计算器 - 基于GTO理论计算最优行动频率
"""
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FrequencyContext:
    """频率计算上下文"""
    street: str
    position: str
    hand_strength: float
    board_texture: str
    pot_size: int
    stack_size: int
    opponent_tendency: float
    previous_action: str
    is_ip: bool
    num_opponents: int


class FrequencyCalculator:
    """GTO频率计算器"""
    
    def __init__(self):
        # GTO标准频率
        self.base_frequencies = {
            'preflop': {
                'BTN': {'open': 0.50, 'fold': 0.50},
                'CO': {'open': 0.30, 'fold': 0.70},
                'HJ': {'open': 0.25, 'fold': 0.75},
                'MP': {'open': 0.20, 'fold': 0.80},
                'UTG': {'open': 0.15, 'fold': 0.85},
                'SB': {'open': 0.35, 'fold': 0.65},
                'BB': {'defend': 0.45, 'fold': 0.55}
            },
            'postflop': {
                'cbet': 0.65,  # 持续下注频率
                'vs_cbet': {
                    'call': 0.45,
                    'raise': 0.12,
                    'fold': 0.43
                },
                'double_barrel': 0.45,  # 双枪频率
                'triple_barrel': 0.30,  # 三枪频率
                'check_raise': 0.08,  # 过牌加注频率
                'probe': 0.35  # 探测下注频率
            }
        }
        
        # 牌力调整因子
        self.strength_factors = {
            'premium': {'fold': 0.1, 'call': 0.9, 'raise': 1.0},  # AA, KK, AK
            'strong': {'fold': 0.3, 'call': 0.8, 'raise': 0.9},   # 中等强牌
            'medium': {'fold': 0.5, 'call': 0.6, 'raise': 0.5},   # 中等牌
            'weak': {'fold': 0.8, 'call': 0.3, 'raise': 0.2},     # 弱牌
            'trash': {'fold': 0.95, 'call': 0.1, 'raise': 0.05}  # 垃圾牌
        }
        
        # 牌面纹理调整
        self.texture_adjustments = {
            'dry': {'aggression': 1.1, 'defense': 0.9},      # 干燥牌面更激进
            'wet': {'aggression': 0.8, 'defense': 1.2},       # 湿润牌面更谨慎
            'dynamic': {'aggression': 1.0, 'defense': 1.0},   # 动态牌面标准
            'paired': {'aggression': 0.9, 'defense': 1.1}   # 对子牌面调整
        }
        
        # 位置调整
        self.position_adjustments = {
            'BTN': {'aggression': 1.2, 'defense': 1.0},   # 按钮位更激进
            'CO': {'aggression': 1.1, 'defense': 1.0},
            'HJ': {'aggression': 1.0, 'defense': 1.0},
            'MP': {'aggression': 0.95, 'defense': 1.0},
            'UTG': {'aggression': 0.9, 'defense': 1.0},
            'SB': {'aggression': 1.0, 'defense': 0.9},   # 小盲位置劣势
            'BB': {'aggression': 0.9, 'defense': 1.1}    # 大盲需要更多防守
        }
        
    def calculate_optimal_frequencies(self, context: FrequencyContext) -> Dict[str, float]:
        """
        计算最优行动频率
        
        Args:
            context: 频率计算上下文
            
        Returns:
            各行动的最优频率
        """
        # 获取基础频率
        base_freqs = self._get_base_frequencies(context)
        
        # 应用牌力调整
        strength_adjusted = self._apply_strength_adjustments(base_freqs, context)
        
        # 应用牌面纹理调整
        texture_adjusted = self._apply_texture_adjustments(strength_adjusted, context)
        
        # 应用位置调整
        position_adjusted = self._apply_position_adjustments(texture_adjusted, context)
        
        # 应用对手倾向调整
        opponent_adjusted = self._apply_opponent_adjustments(position_adjusted, context)
        
        # 标准化频率
        normalized = self._normalize_frequencies(opponent_adjusted)
        
        return normalized
    
    def _get_base_frequencies(self, context: FrequencyContext) -> Dict[str, float]:
        """获取基础频率"""
        if context.street == 'preflop':
            return self.base_frequencies['preflop'].get(context.position, {'open': 0.20, 'fold': 0.80})
        
        # 翻牌后根据情境选择基础频率
        if context.previous_action == 'cbet':
            return {
                'call': self.base_frequencies['postflop']['vs_cbet']['call'],
                'raise': self.base_frequencies['postflop']['vs_cbet']['raise'],
                'fold': self.base_frequencies['postflop']['vs_cbet']['fold']
            }
        elif context.previous_action == 'check':
            return {
                'bet': self.base_frequencies['postflop']['probe'],
                'check': 1.0 - self.base_frequencies['postflop']['probe']
            }
        else:
            # 默认情况
            return {
                'bet': self.base_frequencies['postflop']['cbet'],
                'check': 1.0 - self.base_frequencies['postflop']['cbet']
            }
    
    def _apply_strength_adjustments(self, frequencies: Dict[str, float], context: FrequencyContext) -> Dict[str, float]:
        """应用牌力调整"""
        strength_category = self._categorize_hand_strength(context.hand_strength)
        strength_factors = self.strength_factors.get(strength_category, self.strength_factors['medium'])
        
        adjusted = frequencies.copy()
        
        for action, base_freq in frequencies.items():
            factor = strength_factors.get(action, 1.0)
            adjusted[action] = base_freq * factor
        
        return adjusted
    
    def _apply_texture_adjustments(self, frequencies: Dict[str, float], context: FrequencyContext) -> Dict[str, float]:
        """应用牌面纹理调整"""
        texture_adj = self.texture_adjustments.get(context.board_texture, self.texture_adjustments['dynamic'])
        
        adjusted = frequencies.copy()
        
        # 根据行动类型应用调整
        for action, base_freq in frequencies.items():
            if action in ['bet', 'raise']:  # 激进行动
                adjusted[action] = base_freq * texture_adj['aggression']
            elif action in ['call', 'defend']:  # 防守行动
                adjusted[action] = base_freq * texture_adj['defense']
        
        return adjusted
    
    def _apply_position_adjustments(self, frequencies: Dict[str, float], context: FrequencyContext) -> Dict[str, float]:
        """应用位置调整"""
        pos_adj = self.position_adjustments.get(context.position, self.position_adjustments['MP'])
        
        adjusted = frequencies.copy()
        
        for action, base_freq in frequencies.items():
            if action in ['bet', 'raise']:  # 激进行动
                adjusted[action] = base_freq * pos_adj['aggression']
            elif action in ['call', 'defend']:  # 防守行动
                adjusted[action] = base_freq * pos_adj['defense']
        
        return adjusted
    
    def _apply_opponent_adjustments(self, frequencies: Dict[str, float], context: FrequencyContext) -> Dict[str, float]:
        """应用对手倾向调整"""
        adjusted = frequencies.copy()
        
        # 根据对手松紧程度调整
        if context.opponent_tendency > 1.2:  # 对手很松
            # 减少诈唬，增加价值下注
            for action in ['bet', 'raise']:
                if action in adjusted:
                    adjusted[action] *= 1.1  # 更激进
            for action in ['call', 'defend']:
                if action in adjusted:
                    adjusted[action] *= 0.9  # 减少防守
        
        elif context.opponent_tendency < 0.8:  # 对手很紧
            # 增加诈唬，减少价值下注
            for action in ['bet', 'raise']:
                if action in adjusted:
                    adjusted[action] *= 0.9  # 更保守
            for action in ['call', 'defend']:
                if action in adjusted:
                    adjusted[action] *= 1.1  # 增加防守
        
        return adjusted
    
    def _normalize_frequencies(self, frequencies: Dict[str, float]) -> Dict[str, float]:
        """标准化频率"""
        total = sum(frequencies.values())
        if total <= 0:
            # 如果总和为0，平均分配
            num_actions = len(frequencies)
            return {action: 1.0 / num_actions for action in frequencies}
        
        return {action: freq / total for action, freq in frequencies.items()}
    
    def _categorize_hand_strength(self, strength: float) -> str:
        """分类手牌强度"""
        if strength >= 0.8:
            return 'premium'
        elif strength >= 0.6:
            return 'strong'
        elif strength >= 0.4:
            return 'medium'
        elif strength >= 0.2:
            return 'weak'
        else:
            return 'trash'
    
    def calculate_mixed_strategy(self, context: FrequencyContext, num_options: int = 3) -> Dict[str, float]:
        """
        计算混合策略频率
        
        Args:
            context: 上下文
            num_options: 选项数量
            
        Returns:
            混合策略频率
        """
        # 获取最优频率
        optimal_freqs = self.calculate_optimal_frequencies(context)
        
        # 添加随机性以实现混合策略
        mixed_freqs = {}
        for action, freq in optimal_freqs.items():
            # 添加±10%的随机变化
            random_factor = 0.9 + (hash(action) % 20) / 100.0
            mixed_freqs[action] = freq * random_factor
        
        return self._normalize_frequencies(mixed_freqs)
    
    def get_frequency_explanation(self, frequencies: Dict[str, float], context: FrequencyContext) -> str:
        """获取频率解释"""
        explanation = f"""
🎲 GTO频率分析

📊 情境参数:
• 位置: {context.position}
• 街道: {context.street}
• 牌力: {context.hand_strength:.2f}
• 牌面: {context.board_texture}
• 对手倾向: {context.opponent_tendency:.2f}

🎯 最优频率分布:
"""
        
        for action, freq in frequencies.items():
            percentage = freq * 100
            bar_length = int(percentage / 5)  # 每5%一个字符
            bar = "█" * bar_length + "░" * (20 - bar_length)
            explanation += f"• {action}: {percentage:.1f}% [{bar}]\n"
        
        # 添加具体建议
        explanation += "\n💡 策略建议:\n"
        
        max_action = max(frequencies.items(), key=lambda x: x[1])
        if max_action[1] > 0.6:
            explanation += f"• 主要策略: {max_action[0]} ({max_action[1]*100:.1f}%)\n"
        elif max_action[1] > 0.4:
            explanation += f"• 混合策略: 以{max_action[0]}为主 ({max_action[1]*100:.1f}%)\n"
        else:
            explanation += "• 平衡策略: 多选项混合\n"
        
        return explanation
    
    def get_balance_metrics(self, frequencies_history: List[Dict[str, float]]) -> Dict[str, float]:
        """
        计算策略平衡性指标
        
        Args:
            frequencies_history: 历史频率记录
            
        Returns:
            平衡性指标
        """
        if not frequencies_history:
            return {'balance_score': 0.0, 'predictability': 1.0, 'exploitability': 1.0}
        
        # 计算平均频率
        avg_frequencies = {}
        for action in frequencies_history[0].keys():
            avg_freq = sum(freqs.get(action, 0) for freqs in frequencies_history) / len(frequencies_history)
            avg_frequencies[action] = avg_freq
        
        # 计算平衡性得分 (越接近GTO标准越平衡)
        balance_score = 1.0 - self._calculate_deviation(avg_frequencies)
        
        # 计算可预测性 (频率变化越小越容易被预测)
        predictability = self._calculate_predictability(frequencies_history)
        
        # 计算可剥削性 (偏离GTO越多越容易被剥削)
        exploitability = self._calculate_exploitability(avg_frequencies)
        
        return {
            'balance_score': balance_score,
            'predictability': predictability,
            'exploitability': exploitability,
            'avg_frequencies': avg_frequencies
        }
    
    def _calculate_deviation(self, frequencies: Dict[str, float]) -> float:
        """计算与GTO标准的偏离度"""
        # 简化的偏离度计算
        total_deviation = 0.0
        for action, freq in frequencies.items():
            # 假设理想频率是均匀分布
            ideal_freq = 1.0 / len(frequencies)
            deviation = abs(freq - ideal_freq)
            total_deviation += deviation
        
        return min(1.0, total_deviation / 2.0)
    
    def _calculate_predictability(self, history: List[Dict[str, float]]) -> float:
        """计算可预测性"""
        if len(history) < 2:
            return 1.0
        
        # 计算频率变化的方差
        total_variance = 0.0
        for action in history[0].keys():
            action_history = [freqs.get(action, 0) for freqs in history]
            variance = self._calculate_variance(action_history)
            total_variance += variance
        
        # 方差越小越可预测
        avg_variance = total_variance / len(history[0])
        return max(0.0, 1.0 - avg_variance)
    
    def _calculate_exploitability(self, frequencies: Dict[str, float]) -> float:
        """计算可剥削性"""
        # 极端频率更容易被剥削
        max_freq = max(frequencies.values())
        min_freq = min(frequencies.values())
        
        # 频率越极端越容易被剥削
        extremity = max_freq - min_freq
        return extremity
    
    def _calculate_variance(self, values: List[float]) -> float:
        """计算方差"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance