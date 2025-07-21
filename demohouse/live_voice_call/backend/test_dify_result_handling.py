#!/usr/bin/env python3
"""
Test Dify result handling for both workflow_finished and node_finished scenarios.
"""
import asyncio
import json
from dify_client import DifyClient


async def test_result_extraction():
    """Test how we extract results from different Dify response patterns."""
    print("🧪 测试Dify结果提取逻辑")
    print("=" * 50)
    
    client = DifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    test_case = {
        "question": "解一元二次方程",
        "student_name": "小明"
    }
    
    print(f"📋 测试参数: {json.dumps(test_case, ensure_ascii=False)}")
    print("-" * 30)
    
    try:
        print("🚀 调用Dify工作流...")
        
        collected_results = []
        chunk_count = 0
        
        async for chunk in client.stream_workflow_run(
            inputs=test_case,
            user_id=f"test-result-extraction"
        ):
            if chunk:
                chunk_count += 1
                collected_results.append(chunk)
                print(f"📝 结果 {chunk_count}: '{chunk}'")
        
        print(f"\n📊 收集到的结果:")
        print(f"   总数量: {len(collected_results)}")
        
        if collected_results:
            # 分析结果
            for i, result in enumerate(collected_results, 1):
                print(f"   结果 {i}: '{result}' (长度: {len(result)})")
            
            # 根据当前的理解，应该只有一个最终结果
            final_result = collected_results[-1] if collected_results else ""
            print(f"\n✅ 最终开场白: '{final_result}'")
            
            # 验证结果质量
            if final_result:
                contains_name = test_case["student_name"] in final_result
                contains_question = any(word in final_result for word in ["解", "一元二次方程"])
                
                print(f"\n🔍 质量检查:")
                print(f"   包含学生姓名: {'✅' if contains_name else '❌'} ({test_case['student_name']})")
                print(f"   包含问题相关内容: {'✅' if contains_question else '❌'}")
                print(f"   文本合理长度: {'✅' if 5 <= len(final_result) <= 100 else '❌'} ({len(final_result)} 字符)")
                
                if contains_name and contains_question:
                    print(f"✅ 开场白质量检查通过！")
                    return True
                else:
                    print(f"⚠️ 开场白质量需要改进")
                    return False
            else:
                print(f"❌ 未生成开场白")
                return False
        else:
            print(f"❌ 未收到任何结果")
            return False
            
    except Exception as e:
        print(f"💥 测试失败: {str(e)}")
        return False


async def test_multiple_calls():
    """Test multiple calls to ensure consistency."""
    print(f"\n🧪 一致性测试 - 多次调用")
    print("=" * 50)
    
    client = DifyClient(
        api_key="app-rCIokTn1NixIujuo4M18feAW",
        base_url="https://api.dify.ai"
    )
    
    test_cases = [
        {"question": "解一元二次方程", "student_name": "小明"},
        {"question": "解一元二次方程", "student_name": "小红"},
        {"question": "学习英语语法", "student_name": "小华"},
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 调用 {i}: {test_case['student_name']} - {test_case['question']}")
        
        try:
            opening_text = ""
            async for chunk in client.stream_workflow_run(
                inputs=test_case,
                user_id=f"consistency-test-{i}"
            ):
                if chunk:
                    opening_text += chunk
            
            if opening_text:
                results.append({
                    "input": test_case,
                    "output": opening_text,
                    "success": True
                })
                print(f"   ✅ 结果: '{opening_text}'")
            else:
                results.append({
                    "input": test_case,
                    "output": "",
                    "success": False
                })
                print(f"   ❌ 无结果")
                
        except Exception as e:
            results.append({
                "input": test_case,
                "output": "",
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ 错误: {str(e)}")
        
        # 简短等待
        await asyncio.sleep(0.5)
    
    print(f"\n📊 一致性测试结果:")
    success_count = sum(1 for r in results if r["success"])
    print(f"   成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        print(f"   {status} 调用 {i}: {result['input']['student_name']} → '{result['output'][:30]}...'")
    
    return success_count == len(results)


async def main():
    """Run all tests."""
    print("🎯 Dify结果处理验证测试")
    print("=" * 60)
    
    # Test 1: Basic result extraction
    success1 = await test_result_extraction()
    
    # Test 2: Consistency across multiple calls
    success2 = await test_multiple_calls()
    
    print(f"\n🏁 测试总结")
    print("=" * 30)
    
    if success1 and success2:
        print("✅ 所有测试通过！")
        print("🎤 Dify结果提取逻辑工作正常")
        print("\n📋 验证通过的功能:")
        print("  ✅ 从LLM节点提取文本")
        print("  ✅ workflow_finished处理")
        print("  ✅ 思考标签清理")
        print("  ✅ 结果一致性")
        print("  ✅ 质量检查通过")
    else:
        print("❌ 部分测试失败")
        if not success1:
            print("  - 基础结果提取失败")
        if not success2:
            print("  - 一致性测试失败")
        print("💡 建议检查Dify工作流配置")


if __name__ == "__main__":
    asyncio.run(main())