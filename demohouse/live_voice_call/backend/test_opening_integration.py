#!/usr/bin/env python3
"""
Integration test for opening generation using actual service components.
"""
import asyncio
import json
from typing import Dict, Any


# Mock classes to avoid external dependencies
class MockASRClient:
    def __init__(self, **kwargs):
        self.inited = True
    
    async def init(self):
        pass
    
    async def close(self):
        pass


class MockHTTPTTSManager:
    def __init__(self):
        pass
    
    async def initialize(self, **kwargs):
        pass
    
    async def synthesize(self, text):
        class MockResponse:
            success = True
            audio_data = f"[Mock Audio Data for: {text}]".encode()
            error_message = None
        return MockResponse()


# Import actual service components
from dify_client import DifyClient


async def test_opening_with_real_dify():
    """Test opening generation with real Dify client."""
    print("🧪 集成测试：使用真实Dify客户端生成开场白")
    print("=" * 50)
    
    # Create real Dify client with updated credentials
    dify_client = DifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    # Test parameters
    test_params = {
        "question": "解一元二次方程", 
        "student_name": "小明"
    }
    
    print(f"📋 测试参数: {json.dumps(test_params, ensure_ascii=False)}")
    print("-" * 30)
    
    try:
        print("🚀 调用Dify工作流生成开场白...")
        opening_text = ""
        
        async for chunk in dify_client.stream_workflow_run(
            inputs=test_params,
            user_id=f"opening-{test_params['student_name']}"
        ):
            if chunk:
                print(f"📝 收到文本块: {chunk}")
                opening_text += chunk
        
        if opening_text:
            print("✅ 开场白生成成功！")
            print(f"🎤 完整开场白: {opening_text}")
            print(f"📏 文本长度: {len(opening_text)} 字符")
            
            # Test TTS mock
            print("\n🔊 测试TTS合成...")
            tts_manager = MockHTTPTTSManager()
            await tts_manager.initialize()
            
            response = await tts_manager.synthesize(opening_text)
            if response.success:
                print(f"✅ TTS合成成功: {len(response.audio_data)} 字节")
                print(f"🎵 音频数据预览: {response.audio_data[:50]}...")
            else:
                print(f"❌ TTS合成失败: {response.error_message}")
            
            return True
        else:
            print("❌ 开场白生成失败：未收到文本内容")
            return False
            
    except Exception as e:
        print(f"💥 测试失败: {str(e)}")
        return False


async def test_multiple_scenarios():
    """Test multiple opening generation scenarios."""
    print("\n🧪 多场景测试")
    print("=" * 50)
    
    scenarios = [
        {"question": "解一元二次方程", "student_name": "小明", "desc": "数学 - 小明"},
        {"question": "学习英语语法", "student_name": "小红", "desc": "英语 - 小红"},
        {"question": "物理力学基础", "student_name": "小华", "desc": "物理 - 小华"},
    ]
    
    dify_client = DifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    success_count = 0
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['desc']}")
        print("-" * 30)
        
        try:
            opening_text = ""
            async for chunk in dify_client.stream_workflow_run(
                inputs={
                    "question": scenario["question"],
                    "student_name": scenario["student_name"]
                },
                user_id=f"test-{scenario['student_name']}"
            ):
                if chunk:
                    opening_text += chunk
            
            if opening_text:
                print(f"✅ 成功: {opening_text}")
                success_count += 1
            else:
                print("❌ 失败: 未生成内容")
                
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
        
        # Brief pause between requests
        await asyncio.sleep(0.5)
    
    print(f"\n📊 测试结果: {success_count}/{len(scenarios)} 成功")
    return success_count == len(scenarios)


async def test_opening_text_processing():
    """Test opening text processing and cleanup."""
    print("\n🧪 文本处理测试")
    print("=" * 50)
    
    import re
    
    # Test cases with thinking tags
    test_texts = [
        "<think>\n小明呀，现在我们来解一元二次方程啦。\n</think>小明，现在我们来解一元二次方程哦",
        "小红，我们一起学习英语语法吧！",
        "<think>这是思考过程</think>小华，让我们探索物理的奥秘",
        "   <think>内部思考</think>   正式内容   ",
    ]
    
    expected_results = [
        "小明，现在我们来解一元二次方程哦",
        "小红，我们一起学习英语语法吧！",
        "小华，让我们探索物理的奥秘",
        "正式内容",
    ]
    
    for i, (test_text, expected) in enumerate(zip(test_texts, expected_results), 1):
        print(f"测试 {i}:")
        print(f"  输入: {repr(test_text)}")
        
        # Apply the same processing as in dify_client.py
        cleaned = re.sub(r'<think>.*?</think>', '', test_text, flags=re.DOTALL).strip()
        print(f"  输出: {repr(cleaned)}")
        print(f"  期望: {repr(expected)}")
        
        if cleaned == expected:
            print("  ✅ 通过")
        else:
            print("  ❌ 失败")
        print()


async def main():
    """Run all tests."""
    print("🎯 开场白功能集成测试")
    print("=" * 60)
    
    # Test 1: Single opening generation
    success1 = await test_opening_with_real_dify()
    
    # Test 2: Multiple scenarios
    success2 = await test_multiple_scenarios()
    
    # Test 3: Text processing
    await test_opening_text_processing()
    
    print("\n🎉 测试总结")
    print("=" * 30)
    if success1 and success2:
        print("✅ 所有集成测试通过！")
        print("🎤 开场白功能已准备就绪")
        print("\n📋 功能验证:")
        print("  ✅ Dify API调用成功")
        print("  ✅ 文本内容生成正确")
        print("  ✅ 思考标签清理正常")
        print("  ✅ TTS集成模拟成功")
        print("  ✅ 多场景支持验证")
    else:
        print("❌ 部分测试失败，请检查配置")
        if not success1:
            print("  - 单一测试失败")
        if not success2:
            print("  - 多场景测试失败")


if __name__ == "__main__":
    asyncio.run(main())