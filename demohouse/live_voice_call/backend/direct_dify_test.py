#!/usr/bin/env python3
"""
直接的 Dify API 测试 - 无需修改配置文件
Direct Dify API test without modifying config files
"""

import asyncio
import json
import aiohttp
import time


async def test_dify_direct(api_key: str = "app-JqtJdpgiEKukUAxxT8oiJR4u", test_inputs: dict = None):
    """
    直接测试 Dify API，无需配置文件
    """
    print("🚀 直接 Dify API 测试")
    print("=" * 50)
    print(f"📋 API 密钥: {api_key[:10]}***")
    
    # 默认测试数据
    if test_inputs is None:
        test_inputs = {
            "question": "什么是人工智能？",
            "answer": "人工智能是模拟人类智能的技术",
            "question_stem": "关于AI的基础问题",
            "student_name": "测试用户",
            "question_category": "科技",
            "user_input": "请解释一下人工智能",
            "user_responds": "请解释一下人工智能"
        }
    
    # API 请求配置
    base_url = "https://api.dify.ai"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": test_inputs,
        "response_mode": "streaming",
        "user": "direct_test_user"
    }
    
    print(f"📤 发送的数据:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            print("🔗 连接到 Dify API...")
            
            start_time = time.time()
            
            async with session.post(
                f"{base_url}/v1/workflows/run",
                json=payload
            ) as response:
                
                print(f"📊 HTTP 响应状态: {response.status}")
                print(f"📋 响应头信息: {dict(response.headers)}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ API 错误响应: {error_text}")
                    return False
                
                print("✅ 开始接收流式响应...")
                print("-" * 30)
                
                chunk_count = 0
                total_response = ""
                final_result = ""  # 保存最终的 result 内容
                
                all_raw_responses = []  # 保存所有原始响应
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    # 打印所有原始响应行
                    print(f"🔍 原始响应行: {line}")
                    all_raw_responses.append(line)
                        
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            
                            # 打印完整的解析后JSON数据
                            print(f"📦 解析后数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            
                            event_type = data.get('event', '')
                            print(f"🎯 事件类型: {event_type}")
                            
                            if event_type == 'text_chunk':
                                text = data.get('data', {}).get('text', '')
                                if text:
                                    chunk_count += 1
                                    total_response += text
                                    print(f"📝 文本块 [{chunk_count:2d}]: {text}")
                                    
                            elif event_type == 'workflow_started':
                                print("🚀 工作流开始")
                                
                            elif event_type == 'workflow_finished':
                                print("-" * 30)
                                print("🏁 工作流完成")
                                
                                # 提取最终的 result 内容
                                outputs = data.get('data', {}).get('outputs', {})
                                final_result = outputs.get('result', '')
                                print(f"🎯 最终结果(用于TTS): {final_result}")
                                break
                                
                            elif event_type == 'node_started':
                                node_id = data.get('data', {}).get('id', 'unknown')
                                node_type = data.get('data', {}).get('node_type', 'unknown')
                                print(f"🔧 节点开始: {node_type} ({node_id})")
                                
                            elif event_type == 'node_finished':
                                node_id = data.get('data', {}).get('id', 'unknown')
                                node_type = data.get('data', {}).get('node_type', 'unknown')
                                print(f"✅ 节点完成: {node_type} ({node_id})")
                                
                            elif event_type == 'error':
                                error_msg = data.get('data', {}).get('message', '未知错误')
                                print(f"❌ 工作流错误: {error_msg}")
                                return False
                                
                            else:
                                print(f"ℹ️  其他事件: {event_type}")
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️  JSON解析失败: {e}, 原始内容: {line}")
                            continue
                
                execution_time = time.time() - start_time
                
                print(f"\n📊 测试结果:")
                print(f"   ✅ 测试成功")
                print(f"   ⏱️  执行时间: {execution_time:.2f} 秒")
                print(f"   📊 流式文本块数量: {chunk_count}")
                print(f"   📝 流式文本内容: {total_response}")
                print(f"   🎯 最终结果内容(TTS用): {final_result}")
                
                # 保存结果
                result = {
                    "success": True,
                    "execution_time": execution_time,
                    "chunk_count": chunk_count,
                    "total_response": total_response,  # 流式文本内容
                    "final_result": final_result,      # 最终结果内容（用于TTS）
                    "test_inputs": test_inputs,
                    "all_raw_responses": all_raw_responses,  # 包含所有原始响应
                    "response_headers": dict(response.headers),
                    "http_status": response.status,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open('direct_dify_test_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"💾 结果已保存到: direct_dify_test_result.json")
                
                # 打印所有响应的总结
                print(f"\n📋 响应总结:")
                print(f"   📊 总响应行数: {len(all_raw_responses)}")
                print(f"   🔗 HTTP状态: {response.status}")
                print(f"   📦 响应头数量: {len(response.headers)}")
                print(f"   📝 流式文本块数量: {chunk_count}")
                print(f"   🎯 最终结果长度: {len(final_result)} 字符")
                
                # 验证结果
                if final_result:
                    print(f"   ✅ 成功获取最终结果，将用于TTS")
                else:
                    print(f"   ⚠️  未获取到最终结果")
                
                return True
                
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False


def show_usage():
    """显示使用说明"""
    print("🎯 直接 Dify API 测试工具")
    print("=" * 50)
    print("\n📋 使用方法:")
    print("1. 在命令行中运行:")
    print("   python direct_dify_test.py")
    print("\n2. 按提示输入您的 Dify API 密钥")
    print("\n3. 选择测试选项:")
    print("   - 使用默认测试数据")
    print("   - 输入自定义测试数据")
    print("\n💡 密钥格式: app-xxxxxxxxxx")


async def interactive_test():
    """交互式测试"""
    print("🔧 交互式 Dify API 测试")
    print("=" * 50)
    
    # 获取 API 密钥
    api_key = input("\n🔑 请输入您的 Dify API 密钥: ").strip()
    
    if not api_key:
        print("❌ API 密钥不能为空")
        return
    
    if not api_key.startswith("app-"):
        print("❌ API 密钥格式错误，应该以 'app-' 开头")
        return
    
    # 选择测试数据
    print("\n📋 选择测试数据:")
    print("1. 使用默认测试数据")
    print("2. 输入自定义数据")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    test_inputs = None
    
    if choice == "2":
        print("\n📝 请输入测试数据 (回车使用默认值):")
        
        question = input("问题 [什么是人工智能？]: ").strip() or "什么是人工智能？"
        answer = input("答案 [人工智能是模拟人类智能的技术]: ").strip() or "人工智能是模拟人类智能的技术"
        student_name = input("学生姓名 [测试用户]: ").strip() or "测试用户"
        category = input("问题分类 [科技]: ").strip() or "科技"
        user_input = input("用户输入 [请解释一下人工智能]: ").strip() or "请解释一下人工智能"
        
        test_inputs = {
            "question": question,
            "answer": answer,
            "question_stem": f"关于{category}的问题",
            "student_name": student_name,
            "question_category": category,
            "user_input": user_input,
            "user_responds": user_input
        }
    
    # 运行测试
    print(f"\n🚀 开始测试...")
    success = await test_dify_direct(api_key, test_inputs)
    
    if success:
        print(f"\n🎉 测试完成！Dify API 集成工作正常")
    else:
        print(f"\n😟 测试失败，请检查 API 密钥和网络连接")


async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        show_usage()
        return
    
    await interactive_test()


if __name__ == "__main__":
    asyncio.run(main())