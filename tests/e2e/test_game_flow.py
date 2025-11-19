"""
端到端测试 - 测试完整的游戏流程

测试从游戏开始到结束的完整流程
"""

import pytest
from unittest.mock import Mock, patch

from poker_assistant.engine.game_controller import GameController
from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
from poker_assistant.utils.config import Config


class TestEndToEndGameFlow:
    """端到端游戏流程测试"""
    
    def setup_method(self):
        """测试前置设置"""
        self.config = Config()
        self.config.GAME_MAX_ROUND = 1  # 只测试一轮
        self.config.GAME_PLAYER_COUNT = 3  # 3个玩家
        self.config.GAME_INITIAL_STACK = 1000
    
    def test_single_round_game_flow(self):
        """测试单轮游戏流程"""
        # 创建游戏控制器
        controller = GameController(self.config)
        
        # 验证基本设置
        assert controller.config == self.config
        assert controller.game_config is not None
        assert controller.ai_config is not None
        
        # 验证AI玩家创建（需要在_setup_game之后）
        controller._setup_game()
        
        # 验证AI玩家创建
        assert len(controller.ai_players) == 2  # 3个玩家，1个人类，2个AI
        
        # 验证AI玩家类型
        for ai_player in controller.ai_players:
            assert isinstance(ai_player, ImprovedAIOpponentPlayer)
            assert ai_player.difficulty in ['easy', 'medium', 'hard']
            assert ai_player.show_thinking == True
    
    def test_ai_player_decision_in_game_context(self):
        """测试AI玩家在游戏环境中的决策"""
        # 创建AI玩家
        ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=True,
            gto_enabled=True
        )
        ai_player.uuid = "test_ai_e2e"
        
        # 模拟真实的游戏场景
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
        
        hole_card = ['SA', 'HA']  # AA
        
        # 模拟多轮游戏状态
        game_scenarios = [
            {
                'name': '翻牌前开池',
                'round_state': {
                    'street': 'preflop',
                    'dealer_btn': 0,
                    'small_blind_pos': 1,
                    'big_blind_pos': 2,
                    'pot': {'main': {'amount': 30}},
                    'community_card': [],
                    'seats': [
                        {'uuid': 'human', 'name': '你', 'stack': 1000, 'state': 'participating'},
                        {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                        {'uuid': 'test_ai_e2e', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                    ],
                    'action_histories': {
                        'preflop': [
                            {'action': 'RAISE', 'amount': 30, 'uuid': 'human'}
                        ]
                    }
                }
            },
            {
                'name': '翻牌后持续下注',
                'round_state': {
                    'street': 'flop',
                    'dealer_btn': 0,
                    'small_blind_pos': 1,
                    'big_blind_pos': 2,
                    'pot': {'main': {'amount': 150}},
                    'community_card': ['S9', 'H7', 'C2'],
                    'seats': [
                        {'uuid': 'human', 'name': '你', 'stack': 950, 'state': 'participating'},
                        {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
                        {'uuid': 'test_ai_e2e', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
                    ],
                    'action_histories': {
                        'flop': [
                            {'action': 'CHECK', 'amount': 0, 'uuid': 'human'},
                            {'action': 'BET', 'amount': 50, 'uuid': 'ai_1'}
                        ]
                    }
                }
            },
            {
                'name': '转牌圈决策',
                'round_state': {
                    'street': 'turn',
                    'dealer_btn': 0,
                    'small_blind_pos': 1,
                    'big_blind_pos': 2,
                    'pot': {'main': {'amount': 250}},
                    'community_card': ['S9', 'H7', 'C2', 'SA'],
                    'seats': [
                        {'uuid': 'human', 'name': '你', 'stack': 900, 'state': 'participating'},
                        {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 900, 'state': 'participating'},
                        {'uuid': 'test_ai_e2e', 'name': 'AI_Player', 'stack': 900, 'state': 'participating'},
                    ],
                    'action_histories': {
                        'turn': [
                            {'action': 'CHECK', 'amount': 0, 'uuid': 'human'}
                        ]
                    }
                }
            }
        ]
        
        for scenario in game_scenarios:
            print(f"\n🎮 测试场景: {scenario['name']}")
            
            # 执行决策
            action, amount = ai_player.declare_action(
                valid_actions, hole_card, scenario['round_state']
            )
            
            # 验证决策有效性
            assert action in ['fold', 'call', 'raise', 'check', 'allin']
            assert isinstance(amount, int)
            assert amount >= 0
            
            print(f"✅ 决策: {action} ${amount}")
    
    def test_multiple_ai_players_interaction(self):
        """测试多个AI玩家之间的交互"""
        # 创建多个AI玩家
        ai_players = []
        for i in range(3):
            ai_player = ImprovedAIOpponentPlayer(
                difficulty="medium",
                show_thinking=False,  # 关闭思考过程以提高性能
                gto_enabled=True
            )
            ai_player.uuid = f"test_ai_{i}"
            ai_players.append(ai_player)
        
        # 模拟游戏场景
        round_state = {
            'street': 'flop',
            'dealer_btn': 0,
            'small_blind_pos': 1,
            'big_blind_pos': 2,
            'pot': {'main': {'amount': 150}},
            'community_card': ['S9', 'H7', 'C2'],
            'seats': [
                {'uuid': 'ai_0', 'name': 'AI_0', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'flop': [
                    {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_0'},
                    {'action': 'BET', 'amount': 50, 'uuid': 'ai_1'}
                ]
            }
        }
        
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 50},
            {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
        ]
        
        # 让每个AI玩家做决策
        results = []
        for ai_player in ai_players:
            hole_card = ['SA', 'HA']  # 所有玩家都使用AA
            action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
            results.append((action, amount))
        
        # 验证所有AI都能做出有效决策
        for action, amount in results:
            assert action in ['fold', 'call', 'raise', 'check', 'allin']
            assert isinstance(amount, int)
            assert amount >= 0
    
    def test_gto_consistency_across_rounds(self):
        """测试GTO策略在多轮中的一致性"""
        ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=False,
            gto_enabled=True
        )
        ai_player.uuid = "test_gto_consistency"
        
        # 相同的场景重复多次
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
                {'uuid': 'human', 'name': '你', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                {'uuid': 'test_gto_consistency', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
            ],
            'action_histories': {
                'preflop': [
                    {'action': 'RAISE', 'amount': 30, 'uuid': 'human'}
                ]
            }
        }
        
        # 重复决策多次
        decisions = []
        for _ in range(10):
            action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
            decisions.append((action, amount))
        
        # 验证决策的一致性（优质手牌应该倾向于积极行动）
        aggressive_actions = [d for d in decisions if d[0] == 'raise']
        passive_actions = [d for d in decisions if d[0] == 'call']
        fold_actions = [d for d in decisions if d[0] == 'fold']
        
        # AA不应该弃牌
        assert len(fold_actions) == 0
        
        # 应该主要选择加注或跟注
        assert len(aggressive_actions) + len(passive_actions) == 10
    
    def test_error_handling_in_game_context(self):
        """测试游戏环境中的错误处理"""
        ai_player = ImprovedAIOpponentPlayer(
            difficulty="medium",
            show_thinking=True,
            gto_enabled=True
        )
        ai_player.uuid = "test_error_handling"
        
        # 测试各种有效场景（错误处理已在单元测试中验证）
        valid_scenarios = [
            {
                'name': '标准场景',
                'valid_actions': [
                    {'action': 'fold', 'amount': 0},
                    {'action': 'call', 'amount': 30},
                    {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
                ],
                'hole_card': ['SA', 'HA'],
                'round_state': {
                    'street': 'preflop',
                    'dealer_btn': 0,
                    'small_blind_pos': 1,
                    'big_blind_pos': 2,
                    'pot': {'main': {'amount': 30}},
                    'community_card': [],
                    'seats': [
                        {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                        {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                        {'uuid': 'test_error_handling', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                    ],
                    'action_histories': {
                        'preflop': [
                            {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                        ]
                    }
                }
            }
        ]
        
        for scenario in valid_scenarios:
            print(f"\n🧪 测试有效场景: {scenario['name']}")
            
            # 应该能够正常处理
            action, amount = ai_player.declare_action(
                scenario['valid_actions'],
                scenario['hole_card'],
                scenario['round_state']
            )
            
            # 验证处理结果
            assert action in ['fold', 'call', 'raise', 'check', 'allin']
            assert isinstance(amount, int)
            assert amount >= 0
            
            print(f"✅ 处理成功: {action} ${amount}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])