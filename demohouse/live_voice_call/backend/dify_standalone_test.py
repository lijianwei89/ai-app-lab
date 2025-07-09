#!/usr/bin/env python3
"""
独立的 Dify API 测试脚本，不依赖其他模块
Standalone Dify API test script without external dependencies
"""

import asyncio
import json
import logging
import time
import uuid
import aiohttp
from typing import Dict, Any, AsyncIterable, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===== 测试配置 =====
TEST_CONFIG = {
    # TODO: 请将此处替换为您的实际 Dify API 密钥
    "api_key": "app-JqtJdpgiEKukUAxxT8oiJR4u",  # 替换为您的实际密钥
    "base_url": "https://api.dify.ai",
    "user_id": "test_user_001"
}

# ===== 简化版 Dify 客户端 =====
class SimpleDifyClient:
    """简化版的 Dify 客户端，用于独立测试"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def stream_workflow(self, inputs: Dict[str, Any], user_id: str = None) -> AsyncIterable[str]:
        """执行流式工作流"""
        if user_id is None:
            user_id = str(uuid.uuid4())
            
        session = await self._get_session()
        
        payload = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user_id
        }
        
        print(f"📡 发送请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        try:
            async with session.post(
                f"{self.base_url}/v1/workflows/run",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Dify API 错误 {response.status}: {error_text}")
                
                print("✅ 开始接收流式响应...")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                        
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            event_type = data.get('event', '')
                            
                            if event_type == 'text_chunk':
                                text = data.get('data', {}).get('text', '')
                                if text:
                                    yield text
                                    
                            elif event_type == 'workflow_finished':
                                print("🏁 工作流完成")
                                break
                                
                            elif event_type == 'error':
                                error_msg = data.get('data', {}).get('message', '未知错误')
                                raise Exception(f"Dify 工作流错误: {error_msg}")
                                
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            print(f"❌ API 错误: {str(e)}")
            raise

# ===== 测试场景数据 =====
TEST_SCENARIOS = [
    {
        "name": "基础对话测试",
        "description": "测试带有完整 LLM 参数的基础对话",
        "inputs": {
            "question": "法国的首都是什么？",
            "answer": "巴黎",
            "question_stem": "关于欧洲首都的地理问题",
            "student_name": "小明",
            "question_category": "地理",
            "user_input": "请告诉我法国的首都",
            "user_responds": "请告诉我法国的首都",
            "conversation_history": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！我能为你做什么？"}
            ]
        }
    },
    {
        "name": "教育场景测试",
        "description": "测试教育对话场景",
        "inputs": {
            "question": "解释光合作用",
            "answer": "光合作用是植物将阳光转化为能量的过程",
            "question_stem": "关于植物过程的生物学问题",
            "student_name": "小红",
            "question_category": "生物学",
            "user_input": "你能解释一下植物是如何制造食物的吗？",
            "user_responds": "你能解释一下植物是如何制造食物的吗？"
        }
    },
    {
        "name": "数学问题测试",
        "description": "测试数学问题解答",
        "inputs": {
            "question": "解方程：2x + 5 = 13",
            "answer": "x = 4",
            "question_stem": "一元一次方程求解",
            "student_name": "小华",
            "question_category": "数学",
            "user_input": "帮我解这个方程：2x + 5 = 13",
            "user_responds": "帮我解这个方程：2x + 5 = 13"
        }
    },
    {
        "name": "最小参数测试",
        "description": "只使用必需参数的测试",
        "inputs": {
            "user_input": "你好，你怎么样？",
            "user_responds": "你好，你怎么样？"
        }
    }
]

# ===== 测试函数 =====
async def test_connection():
    """测试连接"""
    print("🔗 测试 Dify API 连接...")
    
    if TEST_CONFIG['api_key'] == "app-JqtJdpgiEKukUAxxT8oiJR4u":
        print("❌ 请先更新 TEST_CONFIG 中的 API 密钥！")
        return False
    
    client = SimpleDifyClient(
        api_key=TEST_CONFIG['api_key'],
        base_url=TEST_CONFIG['base_url']
    )
    
    try:
        test_inputs = {"user_input": "连接测试"}
        
        async for chunk in client.stream_workflow(
            inputs=test_inputs,
            user_id="connection_test"
        ):
            print(f"✅ 连接成功！收到响应: {chunk}")
            await client.close()
            return True
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        await client.close()
        return False

async def test_streaming_scenario(scenario_index: int = 0):
    """测试指定场景的流式响应"""
    if scenario_index >= len(TEST_SCENARIOS):
        print(f"❌ 场景索引 {scenario_index} 超出范围，最大索引为 {len(TEST_SCENARIOS)-1}")
        return
    
    scenario = TEST_SCENARIOS[scenario_index]
    
    print(f"\n🚀 测试场景: {scenario['name']}")
    print(f"📝 描述: {scenario['description']}")
    print(f"📋 输入参数: {json.dumps(scenario['inputs'], indent=2, ensure_ascii=False)}")
    
    if TEST_CONFIG['api_key'] == "app-JqtJdpgiEKukUAxxT8oiJR4u":
        print("❌ 请先更新 TEST_CONFIG 中的 API 密钥！")
        return
    
    client = SimpleDifyClient(
        api_key=TEST_CONFIG['api_key'],
        base_url=TEST_CONFIG['base_url']
    )
    
    start_time = time.time()
    chunk_count = 0
    total_response = ""
    
    try:
        print("\n📡 开始流式请求...")
        
        async for chunk in client.stream_workflow(
            inputs=scenario['inputs'],
            user_id=TEST_CONFIG['user_id']
        ):
            chunk_count += 1
            total_response += chunk
            print(f"📝 第 {chunk_count} 块: {chunk}")
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ 流式测试完成！")
        print(f"⏱️  执行时间: {execution_time:.2f} 秒")
        print(f"📊 总共收到 {chunk_count} 个数据块")
        print(f"📄 完整响应: {total_response}")
        
        # 保存结果
        result = {
            "scenario": scenario['name'],
            "success": True,
            "execution_time": execution_time,
            "chunk_count": chunk_count,
            "total_response": total_response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(f'dify_test_result_{scenario_index}.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 测试结果已保存到: dify_test_result_{scenario_index}.json")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        
        # 保存错误结果
        error_result = {
            "scenario": scenario['name'],
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(f'dify_test_error_{scenario_index}.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    finally:
        await client.close()

async def test_all_scenarios():
    """测试所有场景"""
    print("🎯 开始完整测试套件")
    print("=" * 50)
    
    # 先测试连接
    connection_ok = await test_connection()
    if not connection_ok:
        print("\n❌ 连接测试失败，请检查 API 密钥和网络连接")
        return
    
    # 测试每个场景
    for i, scenario in enumerate(TEST_SCENARIOS):
        print(f"\n{'='*50}")
        print(f"测试场景 {i+1}/{len(TEST_SCENARIOS)}")
        await test_streaming_scenario(i)
        
        # 场景间等待
        if i < len(TEST_SCENARIOS) - 1:
            print("⏳ 等待 2 秒后继续下一个测试...")
            await asyncio.sleep(2)
    
    print(f"\n🏁 所有测试完成！")

def show_usage():
    """显示使用说明"""
    print("🎯 Dify API 独立测试工具")
    print("=" * 50)
    print("\n📋 使用方法:")
    print("python dify_standalone_test.py [命令]")
    print("\n📝 可用命令:")
    print("  connection  - 测试 API 连接")
    print("  scenario N  - 测试第 N 个场景 (0-3)")
    print("  all         - 测试所有场景")
    print("  show        - 显示所有测试场景")
    print("  help        - 显示此帮助信息")
    print("\n💡 示例:")
    print("  python dify_standalone_test.py connection")
    print("  python dify_standalone_test.py scenario 0")
    print("  python dify_standalone_test.py all")
    
    print(f"\n⚠️  重要提醒:")
    print("请先在脚本中更新 TEST_CONFIG['api_key'] 为您的实际 Dify API 密钥！")

def show_scenarios():
    """显示所有测试场景"""
    print("📋 可用测试场景:")
    print("=" * 50)
    
    for i, scenario in enumerate(TEST_SCENARIOS):
        print(f"\n{i}. {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        
        # 显示主要参数
        inputs = scenario['inputs']
        if 'question' in inputs:
            print(f"   ❓ 问题: {inputs['question']}")
        if 'student_name' in inputs:
            print(f"   👤 学生: {inputs['student_name']}")
        if 'question_category' in inputs:
            print(f"   📚 类别: {inputs['question_category']}")

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_usage()
    elif command == "show":
        show_scenarios()
    elif command == "connection":
        await test_connection()
    elif command == "scenario":
        if len(sys.argv) < 3:
            print("❌ 请指定场景编号，例如: python dify_standalone_test.py scenario 0")
            show_scenarios()
            return
        try:
            scenario_index = int(sys.argv[2])
            await test_streaming_scenario(scenario_index)
        except ValueError:
            print("❌ 场景编号必须是数字")
    elif command == "all":
        await test_all_scenarios()
    else:
        print(f"❌ 未知命令: {command}")
        show_usage()

if __name__ == "__main__":
    asyncio.run(main())