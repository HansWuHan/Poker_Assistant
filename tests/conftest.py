"""
测试配置和工具模块

提供测试所需的通用工具、夹具和配置
"""

import pytest
import sys
import os
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestConfig:
    """测试配置类"""
    
    # 默认测试手牌
    DEFAULT_HOLE_CARDS = ['SA', 'HA']  # 不同花AA
    DEFAULT_COMMUNITY_CARDS = ['S9', 'H7', 'C2']  # 顶对牌面
    
    # 默认测试场景
    DEFAULT_ROUND_STATE = {
        'street': 'flop',
        'dealer_btn': 0,
        'small_blind_pos': 1,
        'big_blind_pos': 2,
        'pot': {'main': {'amount': 150}},
        'community_card': DEFAULT_COMMUNITY_CARDS,
        'seats': [
            {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
        ],
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                {'action': 'BET', 'amount': 50, 'uuid': 'player2'}
            ]
        }
    }
    
    DEFAULT_VALID_ACTIONS = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
    ]


class MockPyPokerEngine:
    """模拟PyPokerEngine环境"""
    
    @staticmethod
    def create_mock_player(uuid: str = "test_player", name: str = "TestPlayer"):
        """创建模拟玩家"""
        player = Mock()
        player.uuid = uuid
        player.name = name
        player.stack = 1000
        player.state = "participating"
        return player
    
    @staticmethod
    def create_mock_round_state(street: str = "flop", pot_size: int = 150) -> Dict[str, Any]:
        """创建模拟游戏状态"""
        return {
            'street': street,
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': pot_size}},
            'community_card': TestConfig.DEFAULT_COMMUNITY_CARDS,
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                street: [
                    {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                    {'action': 'BET', 'amount': 50, 'uuid': 'player2'}
                ]
            }
        }


class TestHelpers:
    """测试辅助函数"""
    
    @staticmethod
    def assert_gto_result_valid(result: Dict[str, Any]) -> None:
        """验证GTO结果的有效性"""
        assert isinstance(result, dict), "GTO结果必须是字典"
        assert 'action' in result, "GTO结果必须包含action字段"
        assert 'amount' in result, "GTO结果必须包含amount字段"
        assert 'confidence' in result, "GTO结果必须包含confidence字段"
        assert result['action'] in ['fold', 'call', 'raise', 'check', 'allin'], f"无效的行动: {result['action']}"
        assert 0 <= result['confidence'] <= 1, f"置信度必须在0-1之间: {result['confidence']}"
        
        if 'frequencies' in result:
            frequencies = result['frequencies']
            assert isinstance(frequencies, dict), "频率必须是字典"
            total_freq = sum(frequencies.values())
            assert 0.9 <= total_freq <= 1.1, f"频率总和应该接近1: {total_freq}"
    
    @staticmethod
    def assert_ai_thinking_valid(thinking_text: str) -> None:
        """验证AI思考过程的有效性"""
        assert isinstance(thinking_text, str), "思考过程必须是字符串"
        assert len(thinking_text) > 0, "思考过程不能为空"
        
        # 检查是否包含关键信息
        key_indicators = ['🎯', '💰', '💡', '🧠', '📊']
        has_indicator = any(indicator in thinking_text for indicator in key_indicators)
        assert has_indicator, "思考过程应该包含表情符号指示器"


@pytest.fixture
def test_config():
    """测试配置夹具"""
    return TestConfig()


@pytest.fixture
def mock_pypokerengine():
    """模拟PyPokerEngine夹具"""
    return MockPyPokerEngine()


@pytest.fixture
def sample_hole_cards():
    """示例手牌夹具"""
    return {
        'premium': ['SA', 'HA'],      # AA
        'strong': ['SK', 'HK'],       # KK
        'medium': ['HA', 'D9'],       # A9
        'weak': ['S2', 'H7'],         # 27
        'suited_connectors': ['S7', 'S6'],  # 76s
        'pocket_pair': ['C5', 'D5']   # 55
    }


@pytest.fixture
def sample_boards():
    """示例牌面夹具"""
    return {
        'dry_flop': ['S9', 'H7', 'C2'],
        'wet_flop': ['SJ', 'HT', 'C9'],
        'paired_flop': ['SA', 'HA', 'D7'],
        'monotone_flop': ['SA', 'SK', 'SQ'],
        'turn_card': ['SA'],
        'river_card': ['D3']
    }


@pytest.fixture
def sample_positions():
    """示例位置夹具"""
    return ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO', 'HJ']


# 测试标记
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "gto: marks tests as GTO-related tests"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests as AI-related tests"
    )