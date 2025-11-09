"""
对话代理
处理用户的自由提问
"""
from typing import Dict, Any, List, Optional

from poker_assistant.llm_service.deepseek_client import DeepseekClient
from poker_assistant.llm_service.prompt_manager import PromptManager
from poker_assistant.llm_service.context_manager import ContextManager


class ChatAgent:
    """AI 对话代理"""
    
    def __init__(self,
                 llm_client: Optional[DeepseekClient] = None,
                 prompt_manager: Optional[PromptManager] = None,
                 context_manager: Optional[ContextManager] = None):
        """
        初始化对话代理
        
        Args:
            llm_client: LLM 客户端
            prompt_manager: Prompt 管理器
            context_manager: 上下文管理器
        """
        self.llm_client = llm_client or DeepseekClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = context_manager or ContextManager()
        
        # 初始化系统提示词
        self._init_system_prompt()
    
    def _init_system_prompt(self):
        """初始化系统提示词"""
        system_prompt = self.prompt_manager.load_template("chat_system")
        # 暂时不添加游戏上下文，等用户提问时动态添加
        self.context_manager.add_system_message(system_prompt)
    
    def chat(self, 
             user_question: str,
             game_context: Optional[Dict[str, Any]] = None) -> str:
        """
        与用户对话
        
        Args:
            user_question: 用户问题
            game_context: 游戏上下文（可选）
        
        Returns:
            AI 回复
        """
        try:
            # 更新游戏上下文（如果提供）
            if game_context:
                self.context_manager.update_game_context(game_context)
            
            # 获取上下文字符串
            context_str = self.context_manager.get_game_context_string()
            
            # 构建完整的系统提示（包含游戏上下文）
            system_template = self.prompt_manager.load_template("chat_system")
            system_prompt = system_template.format(game_context=context_str)
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史对话（最近3轮）
            history = list(self.context_manager.conversation_history)[-6:]  # 3轮 = 6条消息
            for msg in history:
                if msg["role"] != "system":  # 不重复添加system消息
                    messages.append(msg)
            
            # 添加当前问题
            messages.append({"role": "user", "content": user_question})
            
            # 调用 LLM
            response = self.llm_client.chat(messages, temperature=0.8, max_tokens=800)
            
            # 保存到历史
            self.context_manager.add_user_message(user_question)
            self.context_manager.add_assistant_message(response)
            
            return response
        
        except Exception as e:
            return f"抱歉，暂时无法回答你的问题（{str(e)}）。请稍后再试。"
    
    def clear_history(self):
        """清除对话历史"""
        self.context_manager.clear_history()
        self._init_system_prompt()
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        return self.context_manager.get_summary()

