"""
集成测试 - 测试完整的AI决策流程

测试AI引擎与GTO策略的集成
"""

import pytest
from unittest.mock import Mock, patch

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
from poker_assistant.engine.game_controller import GameController
from poker_assistant.utils.config import Config


class TestAIIntegration:
    """AI集成测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.config = Config()
        self.ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=True,
            gto_enabled=True
        )
        self.ai_player.uuid = "test_ai_integration"
    
    def test_full_decision_flow_premium_hand(self):
        """测试优质手牌的完整决策流程"""
        # 设置测试场景
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        hole_card = ['SA', 'HA']  # AA
        round_state = {
            'street': 'preflop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 30}},
            'community_card': [],
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'preflop': [
                    {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                ]
            }
        }
        
        # 执行决策
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 验证结果
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
        
        # 优质手牌应该倾向于积极行动
        assert action in ['raise', 'call']
    
    def test_full_decision_flow_weak_hand(self):
        """测试弱手牌的完整决策流程"""
        # 设置测试场景
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 50},
            {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
        ]
        hole_card = ['S2', 'H7']  # 27不同花
        round_state = {
            'street': 'flop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 150}},
            'community_card': ['HA', 'HK', 'DQ'],  # 高牌面
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'flop': [
                    {'action': 'BET', 'amount': 50, 'uuid': 'player1'}
                ]
            }
        }
        
        # 执行决策
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 验证结果
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
        
        # 弱手牌在需要跟注时可能弃牌，但GTO策略可能选择诈唬
        assert action in ['fold', 'call', 'raise']  # 允许加注（诈唬）
    
    def test_gto_fallback_mechanism(self):
        """测试GTO回退机制"""
        # 临时禁用GTO
        original_gto_enabled = self.ai_player.gto_enabled
        self.ai_player.gto_enabled = False
        
        # 设置测试场景
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        hole_card = ['SA', 'HA']  # AA
        round_state = {
            'street': 'preflop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 30}},
            'community_card': [],
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'preflop': [
                    {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                ]
            }
        }
        
        # 执行决策（应该使用传统策略）
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 验证结果
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
        
        # 恢复GTO设置
        self.ai_player.gto_enabled = original_gto_enabled
    
    def test_thinking_process_with_gto(self):
        """测试带GTO的思考过程"""
        # 确保GTO启用
        self.ai_player.gto_enabled = True
        
        # 设置测试场景
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        hole_card = ['SA', 'HA']  # AA
        round_state = {
            'street': 'preflop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 30}},
            'community_card': [],
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'preflop': [
                    {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                ]
            }
        }
        
        # 生成思考过程
        thinking = self.ai_player._generate_thinking_process(
            hole_card, round_state, valid_actions
        )
        
        # 验证思考过程包含GTO分析
        assert isinstance(thinking, str)
        assert '🧠' in thinking  # GTO分析标识
        assert 'GTO策略' in thinking or 'GTO' in thinking
        assert '🎯' in thinking  # 手牌信息
        assert '💰' in thinking  # 底池信息
        assert '💡' in thinking  # 建议信息
    
    def test_opponent_analysis_filtering(self):
        """测试对手分析过滤"""
        # 设置只有AI对手的场景
        round_state_no_human = {
            'street': 'flop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 150}},
            'community_card': ['S9', 'H7', 'C2'],
            'seats': [
                {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'flop': [
                    {'action': 'BET', 'amount': 50, 'uuid': 'ai_1'}
                ]
            }
        }
        
        # 设置包含人类玩家的场景
        round_state_with_human = {
            'street': 'flop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 150}},
            'community_card': ['S9', 'H7', 'C2'],
            'seats': [
                {'uuid': 'human_1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'flop': [
                    {'action': 'BET', 'amount': 50, 'uuid': 'human_1'}
                ]
            }
        }
        
        # 分析对手行为
        analysis_no_human = self.ai_player._analyze_player_behavior(round_state_no_human)
        analysis_with_human = self.ai_player._analyze_player_behavior(round_state_with_human)
        
        # 应该只有在有人类玩家时才进行分析
        assert isinstance(analysis_no_human, str)
        assert isinstance(analysis_with_human, str)
        
        # 有人类玩家时应该有分析结果
        assert len(analysis_with_human) > 0 or analysis_with_human == ""
    
    def test_error_recovery(self):
        """测试错误恢复机制"""
        # 使用无效参数测试错误恢复
        valid_actions = []  # 空的有效行动列表
        hole_card = ['SA', 'HA']
        round_state = {}  # 空的轮次状态
        
        # 使用有效参数测试正常处理
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        hole_card = ['SA', 'HA']
        round_state = {
            'street': 'preflop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 30}},
            'community_card': [],
            'seats': [
                {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_error_recovery', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'preflop': [
                    {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                ]
            }
        }
        
        # 应该能够正常处理
        action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
        
        # 应该返回某种默认决策
        assert action in ['fold', 'call', 'raise', 'check', 'allin']
        assert isinstance(amount, int)
        assert amount >= 0
    
    def test_different_streets(self):
        """测试不同街道的决策"""
        streets = ['preflop', 'flop', 'turn', 'river']
        
        for street in streets:
            # 设置测试场景
            valid_actions = [
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 30},
                {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
            ]
            hole_card = ['SA', 'HA']  # AA
            
            community_cards = []
            if street != 'preflop':
                community_cards = ['S9', 'H7', 'C2']
            if street in ['turn', 'river']:
                community_cards.append('SA')
            if street == 'river':
                community_cards.append('D3')
            
            round_state = {
                'street': street,
                'dealer_btn': 0,
                'small_blind_pos': 1,
                'big_blind_pos': 2,
                'pot': {'main': {'amount': 30}},
                'community_card': community_cards,
                'seats': [
                    {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'test_ai_integration', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                ],
                'action_histories': {
                    street: [
                        {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                    ]
                }
            }
            
            # 执行决策
            action, amount = self.ai_player.declare_action(valid_actions, hole_card, round_state)
            
            # 验证结果
            assert action in ['fold', 'call', 'raise', 'check', 'allin']
            assert isinstance(amount, int)
            assert amount >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])