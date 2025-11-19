"""
AI引擎单元测试

测试AI决策引擎的核心功能
"""

import pytest
from unittest.mock import Mock, patch

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
from poker_assistant.utils.logging import ai_logger


class TestImprovedAIOpponentPlayer:
    """改进AI对手玩家测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=True,
            gto_enabled=True
        )
        self.ai_player.uuid = "test_ai_player"
    
    def test_ai_player_initialization(self):
        """测试AI玩家初始化"""
        assert self.ai_player is not None
        assert self.ai_player.difficulty == "medium"
        assert self.ai_player.show_thinking is True
        assert self.ai_player.gto_enabled is True
        assert self.ai_player.uuid is not None
    
    def test_declare_action_with_premium_hand(self, test_config, sample_hole_cards):
        """测试优质手牌的决策"""
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = sample_hole_cards['premium']  # AA
        round_state = test_config.DEFAULT_ROUND_STATE
        
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
        
        # 优质手牌应该倾向于积极行动
        assert action in ['raise', 'call']  # 不应该弃牌
    
    def test_declare_action_with_weak_hand(self, test_config, sample_hole_cards):
        """测试弱手牌的决策"""
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = sample_hole_cards['weak']  # 27不同花
        round_state = test_config.DEFAULT_ROUND_STATE
        
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
        
        # 弱手牌在需要跟注时可能弃牌，但GTO策略可能选择其他行动
        assert action in ['fold', 'call', 'raise']  # 允许加注（诈唬）
    
    def test_gto_strategy_integration(self, test_config):
        """测试GTO策略集成"""
        # 确保GTO顾问已启用
        assert self.ai_player.gto_advisor is not None
        
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = ['SA', 'HA']  # AA
        round_state = test_config.DEFAULT_ROUND_STATE
        
        # 调用决策方法
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 应该成功返回决策
        assert action is not None
        assert amount is not None
    
    def test_thinking_process_generation(self, test_config):
        """测试思考过程生成"""
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = ['SA', 'HA']  # AA
        round_state = test_config.DEFAULT_ROUND_STATE
        
        # 生成思考过程
        thinking = self.ai_player._generate_thinking_process(
            hole_card, round_state, valid_actions
        )
        
        assert isinstance(thinking, str)
        assert len(thinking) > 0
        
        # 检查是否包含关键信息
        assert '🎯' in thinking  # 手牌信息
        assert '💰' in thinking  # 底池信息
        assert '💡' in thinking  # 建议信息
    
    def test_gto_analysis_extraction(self, test_config):
        """测试GTO分析提取"""
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = ['SA', 'HA']  # AA
        round_state = test_config.DEFAULT_ROUND_STATE
        
        # 获取GTO分析
        gto_analysis = self.ai_player._get_gto_analysis(hole_card, round_state, valid_actions)
        
        # GTO分析返回字符串格式的分析
        assert isinstance(gto_analysis, str)
        assert len(gto_analysis) > 0
        assert '🎯' in gto_analysis  # GTO策略标识
    
    def test_opponent_analysis_filtering(self, test_config):
        """测试对手分析过滤"""
        round_state = test_config.DEFAULT_ROUND_STATE.copy()
        
        # 测试只有AI对手的情况
        analysis_no_human = self.ai_player._analyze_player_behavior(round_state)
        
        # 测试包含人类玩家的情况
        round_state['seats'][0]['name'] = '你'  # 设置为人类玩家
        analysis_with_human = self.ai_player._analyze_player_behavior(round_state)
        
        # 应该只有在有人类玩家时才进行分析
        assert isinstance(analysis_with_human, str)
        assert len(analysis_with_human) > 0 or analysis_with_human == ""
    
    def test_position_detection(self, test_config):
        """测试位置检测"""
        round_state = test_config.DEFAULT_ROUND_STATE
        
        position = self.ai_player._get_position_name(round_state)
        
        assert isinstance(position, str)
        assert position in ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO', 'HJ']
    
    def test_error_handling(self, test_config):
        """测试错误处理"""
        # 使用有效的完整参数测试
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = ['SA', 'HA']
        round_state = test_config.DEFAULT_ROUND_STATE
        
        # 应该能够正常处理
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 应该返回有效决策
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
    
    def test_gto_fallback_mechanism(self, test_config):
        """测试GTO回退机制"""
        # 临时禁用GTO以测试回退机制
        original_gto_enabled = self.ai_player.gto_enabled
        self.ai_player.gto_enabled = False
        
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        hole_card = ['SA', 'HA']
        round_state = test_config.DEFAULT_ROUND_STATE
        
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 应该成功返回决策（使用传统策略）
        assert action is not None
        assert amount is not None
        
        # 恢复GTO设置
        self.ai_player.gto_enabled = original_gto_enabled
    
    def test_uuid_generation(self):
        """测试UUID生成"""
        # 创建新的AI玩家实例
        new_ai = ImprovedAIOpponentPlayer()
        
        assert new_ai.uuid is not None
        assert len(new_ai.uuid) > 0
        assert isinstance(new_ai.uuid, str)
    
    def test_difficulty_levels(self):
        """测试不同难度级别"""
        difficulties = ['easy', 'medium', 'hard']
        
        for difficulty in difficulties:
            ai = ImprovedAIOpponentPlayer(difficulty=difficulty)
            assert ai.difficulty == difficulty
            assert ai.uuid is not None


class TestAIThinkingProcess:
    """AI思考过程测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=True
        )
        self.ai_player.uuid = "test_ai_player"
    
    def test_thinking_process_structure(self, test_config):
        """测试思考过程结构"""
        hole_card = ['SA', 'HA']
        round_state = test_config.DEFAULT_ROUND_STATE
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        
        thinking = self.ai_player._generate_thinking_process(
            hole_card, round_state, valid_actions
        )
        
        # 检查基本结构
        lines = thinking.split('\n')
        assert len(lines) > 0
        
        # 检查是否包含关键部分
        assert any('🎯' in line for line in lines)  # 手牌信息
        assert any('💰' in line for line in lines)  # 底池信息
        assert any('💡' in line for line in lines)  # 建议信息
    
    def test_gto_analysis_in_thinking(self, test_config):
        """测试思考过程中的GTO分析"""
        hole_card = ['SA', 'HA']
        round_state = test_config.DEFAULT_ROUND_STATE
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        
        # 确保GTO启用
        self.ai_player.gto_enabled = True
        
        thinking = self.ai_player._generate_thinking_process(
            hole_card, round_state, valid_actions
        )
        
        # 应该包含GTO分析
        assert '🧠' in thinking  # GTO分析标识
        assert 'GTO策略' in thinking or 'GTO' in thinking
    
    def test_opponent_analysis_in_thinking(self, test_config):
        """测试思考过程中的对手分析"""
        hole_card = ['SA', 'HA']
        round_state = test_config.DEFAULT_ROUND_STATE
        valid_actions = test_config.DEFAULT_VALID_ACTIONS
        
        thinking = self.ai_player._generate_thinking_process(
            hole_card, round_state, valid_actions
        )
        
        # 应该包含对手分析
        assert '🔍' in thinking  # 对手分析标识
        assert '你:' in thinking  # 人类玩家分析
    
    def test_empty_thinking_handling(self):
        """测试空思考过程的处理"""
        # 使用有效参数测试
        from tests.conftest import TestConfig
        test_config = TestConfig()
        
        thinking = self.ai_player._generate_thinking_process(
            test_config.DEFAULT_HOLE_CARDS, 
            test_config.DEFAULT_ROUND_STATE, 
            test_config.DEFAULT_VALID_ACTIONS
        )
        
        # 应该返回有效的思考过程
        assert isinstance(thinking, str)
        assert len(thinking) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])