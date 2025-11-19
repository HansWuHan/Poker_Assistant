"""
GTO策略单元测试

测试GTO策略包的核心功能
"""

import pytest
from unittest.mock import Mock, patch

from poker_assistant.gto_strategy import (
    GTOCore, GTOAdvisor, RangeManager, SizingOptimizer, FrequencyCalculator,
    GTOContext, GTOResult, FrequencyResult, SizingRecommendation
)
from poker_assistant.gto_strategy.types import ActionType, Position, Street


class TestGTOCore:
    """GTO核心引擎测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.gto_core = GTOCore()
        self.test_context = GTOContext(
            street='preflop',
            position='BB',
            stack_size=1000,
            pot_size=30,
            community_cards=[],
            hole_cards=['SA', 'HA'],
            opponent_actions=[{'action': 'raise', 'amount': 30}],
            active_opponents=1,
            call_amount=30,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 30},
                {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
            ]
        )
    
    def test_gto_core_initialization(self):
        """测试GTO核心初始化"""
        assert self.gto_core is not None
        assert hasattr(self.gto_core, 'preflop_ranges')
        assert hasattr(self.gto_core, 'postflop_strategies')
        assert hasattr(self.gto_core, 'sizing_charts')
    
    def test_calculate_gto_action_new_with_premium_hand(self):
        """测试新类型系统的GTO决策 - 优质手牌"""
        result = self.gto_core.calculate_gto_action_new(self.test_context)
        
        assert isinstance(result, GTOResult)
        assert result.action in ['fold', 'call', 'raise']
        assert 0 <= result.confidence <= 1
        assert result.amount >= 0
        # 检查是否包含相关信息
        assert 'BB' in result.reasoning or '防守' in result.reasoning
    
    def test_calculate_gto_action_new_with_weak_hand(self):
        """测试新类型系统的GTO决策 - 弱手牌"""
        weak_context = GTOContext(
            street='preflop',
            position='BB',
            stack_size=1000,
            pot_size=30,
            community_cards=[],
            hole_cards=['S2', 'H7'],  # 27不同花
            opponent_actions=[{'action': 'raise', 'amount': 30}],
            active_opponents=1,
            call_amount=30,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 30},
                {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
            ]
        )
        
        result = self.gto_core.calculate_gto_action_new(weak_context)
        
        assert isinstance(result, GTOResult)
        assert result.action in ['fold', 'call', 'raise']
        # 弱牌应该有较高的弃牌频率
        assert result.frequencies.get('fold', 0) >= 0.2  # 至少20%弃牌频率
    
    def test_frequency_calculation_new(self):
        """测试新频率计算方法"""
        result = self.gto_core._calculate_action_frequencies_new(self.test_context)
        
        assert isinstance(result, FrequencyResult)
        assert isinstance(result.action_frequencies, dict)
        assert len(result.action_frequencies) > 0
        
        # 验证频率总和（AA应该是强牌，主要加注）
        total_freq = sum(result.action_frequencies.values())
        assert 0.9 <= total_freq <= 1.1  # 允许小的舍入误差
        
        # AA应该有合理的加注频率（考虑位置调整）
        assert result.action_frequencies.get('raise', 0) >= 0.2  # 至少20%加注频率
    
    def test_sizing_recommendation_new(self):
        """测试新尺度建议方法"""
        result = self.gto_core._calculate_sizing_recommendation_new(self.test_context)
        
        assert isinstance(result, SizingRecommendation)
        assert result.optimal_sizing > 0
        assert result.min_sizing <= result.optimal_sizing
        assert result.max_sizing >= result.optimal_sizing
        assert result.sizing_type in ['value', 'bluff', 'mixed', 'probe']
    
    def test_range_analysis_new(self):
        """测试新范围分析方法"""
        result = self.gto_core._analyze_range_new(self.test_context)
        
        assert isinstance(result, dict)
        assert 'hand' in result
        assert 'position' in result
        assert 'in_open_range' in result
        assert 'range_strength' in result
        assert 'recommendation' in result
        
        # AA应该在开池范围内
        assert result['in_open_range'] is True
        assert result['range_strength'] > 0.9
    
    def test_fallback_gto_result_new(self):
        """测试新回退GTO结果"""
        result = self.gto_core._fallback_gto_result_new(self.test_context)
        
        assert isinstance(result, GTOResult)
        assert result.action == 'call'  # 回退到跟注
        assert result.confidence == 0.5  # 中等置信度
        assert '回退' in result.reasoning or '保守' in result.reasoning


class TestGTOAdvisor:
    """GTO顾问测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.advisor = GTOAdvisor()
        self.test_hole_cards = ['SA', 'HA']
        self.test_community_cards = []
        self.test_street = 'preflop'
        self.test_position = 'BB'
        self.test_pot_size = 30
        self.test_stack_size = 1000
        self.test_call_amount = 30
        self.test_valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        self.test_opponent_actions = [{'action': 'raise', 'amount': 30}]
        self.test_active_opponents = ['Player1']
    
    def test_gto_advisor_initialization(self):
        """测试GTO顾问初始化"""
        assert self.advisor is not None
        assert hasattr(self.advisor, 'gto_core')
        assert hasattr(self.advisor, 'range_manager')
        assert hasattr(self.advisor, 'sizing_optimizer')
        assert hasattr(self.advisor, 'frequency_calculator')
    
    def test_get_gto_advice_with_premium_hand(self):
        """测试获取GTO建议 - 优质手牌"""
        advice = self.advisor.get_gto_advice(
            hole_cards=self.test_hole_cards,
            community_cards=self.test_community_cards,
            street=self.test_street,
            position=self.test_position,
            pot_size=self.test_pot_size,
            stack_size=self.test_stack_size,
            call_amount=self.test_call_amount,
            valid_actions=self.test_valid_actions,
            opponent_actions=self.test_opponent_actions,
            active_opponents=self.test_active_opponents
        )
        
        assert isinstance(advice, dict)
        assert 'action' in advice
        assert 'amount' in advice
        assert 'confidence' in advice
        assert 'frequencies' in advice
        assert 'sizing_recommendation' in advice
        
        # 验证行动有效性
        assert advice['action'] in ['fold', 'call', 'raise']
        assert 0 <= advice['confidence'] <= 1
    
    def test_get_gto_advice_error_handling(self):
        """测试GTO建议的错误处理"""
        # 使用无效参数测试错误处理
        advice = self.advisor.get_gto_advice(
            hole_cards=[],  # 空的手牌
            community_cards=self.test_community_cards,
            street=self.test_street,
            position=self.test_position,
            pot_size=self.test_pot_size,
            stack_size=self.test_stack_size,
            call_amount=self.test_call_amount,
            valid_actions=self.test_valid_actions,
            opponent_actions=self.test_opponent_actions,
            active_opponents=self.test_active_opponents
        )
        
        # 应该返回回退建议
        assert isinstance(advice, dict)
        assert 'action' in advice
        assert advice['action'] in ['fold', 'call', 'raise']
    
    def test_blend_with_exploitative(self):
        """测试GTO与剥削策略混合"""
        gto_advice = {
            'action': 'raise',
            'amount': 90,
            'confidence': 0.8,
            'frequencies': {'raise': 0.7, 'call': 0.2, 'fold': 0.1}
        }
        
        exploitative_advice = {
            'action': 'call',
            'amount': 30,
            'confidence': 0.6,
            'reason': 'opponent_tight'
        }
        
        blended = self.advisor.blend_with_exploitative(gto_advice, exploitative_advice)
        
        assert isinstance(blended, dict)
        assert 'action' in blended
        assert 'confidence' in blended
        # 混合后的置信度应该在两者之间
        assert 0.6 <= blended['confidence'] <= 0.8


class TestRangeManager:
    """范围管理器测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.range_manager = RangeManager()
    
    def test_range_manager_initialization(self):
        """测试范围管理器初始化"""
        assert self.range_manager is not None
        assert hasattr(self.range_manager, 'preflop_ranges')
        assert hasattr(self.range_manager, 'postflop_ranges')
    
    def test_get_preflop_range(self):
        """测试获取翻牌前范围"""
        btn_range = self.range_manager.get_preflop_range('BTN', 'open')
        
        assert isinstance(btn_range, set)
        assert len(btn_range) > 0
        # 按钮位置应该有较宽的开池范围
        assert len(btn_range) > 50
        
        # 检查是否包含优质手牌
        assert 'AA' in btn_range
        assert 'KK' in btn_range
        assert 'AKs' in btn_range
    
    def test_is_hand_in_range(self):
        """测试手牌是否在范围内"""
        # AA应该在按钮开池范围内
        assert self.range_manager.is_hand_in_range_by_position('AA', 'BTN', 'open') is True
        
        # 27不同花应该不在按钮开池范围内
        assert self.range_manager.is_hand_in_range_by_position('72o', 'BTN', 'open') is False


class TestSizingOptimizer:
    """尺度优化器测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.sizing_optimizer = SizingOptimizer()
    
    def test_sizing_optimizer_initialization(self):
        """测试尺度优化器初始化"""
        assert self.sizing_optimizer is not None
        assert hasattr(self.sizing_optimizer, 'standard_sizings')
    
    def test_calculate_optimal_sizing(self):
        """测试计算最优尺度"""
        from poker_assistant.gto_strategy.sizing_optimizer import SizingContext
        
        context = SizingContext(
            street='flop',
            position='BTN',
            pot_size=100,
            stack_size=1000,
            effective_stack=950,
            board_texture='dry',
            hand_strength=0.8,
            opponent_tendency=0.2,  # passive
            is_ip=True,
            previous_action='check'
        )
        
        sizing = self.sizing_optimizer.calculate_optimal_sizing(context, 'value_bet')
        
        assert isinstance(sizing, (int, float))
        assert sizing > 0
        assert sizing <= 5.0  # 合理的尺度范围


class TestFrequencyCalculator:
    """频率计算器测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.frequency_calculator = FrequencyCalculator()
    
    def test_frequency_calculator_initialization(self):
        """测试频率计算器初始化"""
        assert self.frequency_calculator is not None
        assert hasattr(self.frequency_calculator, 'base_frequencies')
    
    def test_calculate_optimal_frequencies(self):
        """测试计算最优频率"""
        from poker_assistant.gto_strategy.frequency_calculator import FrequencyContext
        
        context = FrequencyContext(
            street='flop',
            position='BTN',
            hand_strength=0.7,
            board_texture='dry',
            pot_size=100,
            stack_size=1000,
            opponent_tendency=0.5,  # neutral
            previous_action='check',
            is_ip=True,
            num_opponents=1
        )
        
        frequencies = self.frequency_calculator.calculate_optimal_frequencies(context)
        
        assert isinstance(frequencies, dict)
        assert len(frequencies) > 0
        
        # 验证频率总和
        total_freq = sum(frequencies.values())
        assert 0.9 <= total_freq <= 1.1  # 允许小的舍入误差
        
        # 检查是否包含主要行动
        expected_actions = ['fold', 'call', 'raise', 'check', 'bet']
        for action in frequencies:
            assert action in expected_actions


class TestGTOTypes:
    """GTO类型定义测试"""
    
    def test_gto_context_creation(self):
        """测试GTO上下文创建"""
        context = GTOContext(
            street='preflop',
            position='BB',
            stack_size=1000,
            pot_size=30,
            community_cards=[],
            hole_cards=['SA', 'HA'],
            opponent_actions=[],
            active_opponents=1
        )
        
        assert context.street == 'preflop'
        assert context.position == 'BB'
        assert context.stack_size == 1000
        assert context.pot_size == 30
    
    def test_gto_result_creation(self):
        """测试GTO结果创建"""
        sizing_rec = SizingRecommendation(
            optimal_sizing=2.5,
            min_sizing=2.0,
            max_sizing=3.0,
            explanation="Test sizing",
            sizing_type='value'
        )
        
        result = GTOResult(
            action='raise',
            amount=75,
            confidence=0.8,
            reasoning="Test reasoning",
            gto_explanation="Test GTO explanation",
            frequencies={'raise': 0.7, 'call': 0.3},
            sizing_recommendation=sizing_rec,
            range_analysis={'hand': 'AA', 'position': 'BB'},
            balance_metrics={'balance_score': 0.8},
            exploit_opportunities=[]
        )
        
        assert result.action == 'raise'
        assert result.amount == 75
        assert result.confidence == 0.8
        assert result.sizing_recommendation.optimal_sizing == 2.5
    
    def test_frequency_result_methods(self):
        """测试频率结果方法"""
        freq_result = FrequencyResult(
            action_frequencies={'raise': 0.5, 'call': 0.3, 'fold': 0.2},
            mixed_strategy={'raise': 0.5, 'call': 0.3, 'fold': 0.2},
            equilibrium_deviation=0.1,
            confidence_level=0.8
        )
        
        # 测试主要行动获取
        primary_action = freq_result.get_primary_action()
        assert primary_action == 'raise'
        
        # 测试行动概率获取
        raise_prob = freq_result.get_action_probability('raise')
        assert raise_prob == 0.5
        
        fold_prob = freq_result.get_action_probability('fold')
        assert fold_prob == 0.2
    
    def test_sizing_recommendation_methods(self):
        """测试尺度建议方法"""
        sizing_rec = SizingRecommendation(
            optimal_sizing=2.5,
            min_sizing=2.0,
            max_sizing=3.0,
            explanation="Test sizing",
            sizing_type='value'
        )
        
        # 测试绝对金额计算
        pot_size = 100
        absolute_amount = sizing_rec.get_absolute_amount(pot_size)
        assert absolute_amount == 250  # 2.5 * 100
        
        # 测试尺度有效性
        assert sizing_rec.is_valid_sizing(250, pot_size) is True
        assert sizing_rec.is_valid_sizing(150, pot_size) is False  # 低于最小值
        assert sizing_rec.is_valid_sizing(350, pot_size) is False  # 高于最大值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])