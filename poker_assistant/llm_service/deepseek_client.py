"""
Deepseek API 客户端模块
使用 OpenAI 兼容接口调用 Deepseek API
"""
import os
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI


class DeepseekClient:
    """Deepseek API 客户端"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: str = "deepseek-chat",
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 timeout: int = 30):
        """
        初始化 Deepseek 客户端
        
        Args:
            api_key: API 密钥
            base_url: API 基础URL
            model: 模型名称
            temperature: 温度参数（0-2）
            max_tokens: 最大token数
            timeout: 超时时间（秒）
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # 验证 API Key
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
        
        # 初始化 OpenAI 客户端（Deepseek 兼容 OpenAI API）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
        
        # 统计信息
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def chat(self, 
             messages: List[Dict[str, str]],
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream: bool = False,
             debug: bool = False) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数（覆盖默认值）
            max_tokens: 最大token数（覆盖默认值）
            stream: 是否使用流式输出
            debug: 是否打印调试信息
        
        Returns:
            AI 回复内容
        
        Raises:
            Exception: API 调用失败
        """
        try:
            start_time = time.time()
            
            # 参数
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # 打印调试信息
            if debug:
                print("\n" + "="*70)
                print("🔍 Deepseek API 调试信息")
                print("="*70)
                print(f"📋 请求参数:")
                print(f"  Model: {self.model}")
                print(f"  Temperature: {temp}")
                print(f"  Max Tokens: {tokens}")
                print(f"  Messages 数量: {len(messages)}")
                print("\n📝 请求内容:")
                for i, msg in enumerate(messages):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    print(f"\n  Message {i+1} [{role}]:")
                    print(f"  {'-'*60}")
                    # 截取显示（如果太长）
                    if len(content) > 500:
                        print(f"  {content[:500]}...")
                        print(f"  ... (总长度: {len(content)} 字符)")
                    else:
                        print(f"  {content}")
                print("\n" + "="*70)
            
            # 调用 API
            # 添加 stop 参数为 None 确保不会提前停止
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                stream=stream,
                top_p=0.95,  # 增加输出的多样性和完整性
                frequency_penalty=0.0,  # 不惩罚重复
                presence_penalty=0.0    # 不惩罚新话题
            )
            
            # 处理响应
            if stream:
                # 流式输出（暂不支持，后续可扩展）
                content = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                return content
            else:
                # 普通输出
                content = response.choices[0].message.content
                
                # 统计信息
                self.total_requests += 1
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                finish_reason = "unknown"
                
                if hasattr(response, 'usage'):
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                    total_tokens = response.usage.total_tokens
                    self.total_tokens += total_tokens
                    
                    # Deepseek 价格（假设：$0.001/1K tokens）
                    cost = (total_tokens / 1000) * 0.001
                    self.total_cost += cost
                
                # 获取结束原因
                if hasattr(response.choices[0], 'finish_reason'):
                    finish_reason = response.choices[0].finish_reason
                
                # 计算耗时
                elapsed_time = time.time() - start_time
                
                # 打印响应调试信息
                if debug:
                    print("📤 API 响应:")
                    print(f"  耗时: {elapsed_time:.2f} 秒")
                    print(f"  Tokens 使用: {prompt_tokens} (输入) + {completion_tokens} (输出) = {total_tokens}")
                    print(f"  结束原因: {finish_reason}")
                    if finish_reason == "length":
                        print("  ⚠️  警告: 输出因达到 max_tokens 限制而截断！")
                    print(f"\n📝 响应内容 (长度: {len(content)} 字符):")
                    print(f"  {'-'*60}")
                    print(f"  {content}")
                    print("="*70 + "\n")
                
                return content
        
        except Exception as e:
            if debug:
                print(f"\n❌ API 调用失败: {str(e)}\n")
            raise Exception(f"Deepseek API 调用失败: {str(e)}")
    
    def chat_simple(self, 
                   user_message: str, 
                   system_message: Optional[str] = None) -> str:
        """
        简化的聊天接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
        
        Returns:
            AI 回复
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取使用统计
        
        Returns:
            统计信息字典
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_tokens_per_request": (
                self.total_tokens / self.total_requests 
                if self.total_requests > 0 else 0
            )
        }
    
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            是否连接成功
        """
        try:
            response = self.chat_simple(
                "你好，请回复'连接成功'",
                system_message="你是一个测试助手，只需要简短回复。"
            )
            return len(response) > 0
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False


class DeepseekError(Exception):
    """Deepseek API 错误"""
    pass


class DeepseekRateLimitError(DeepseekError):
    """速率限制错误"""
    pass


class DeepseekAuthError(DeepseekError):
    """认证错误"""
    pass


class DeepseekTimeoutError(DeepseekError):
    """超时错误"""
    pass

