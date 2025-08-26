#!/usr/bin/env python3
"""
多轮对话测试脚本
支持session_id相同的对话上下文保持
"""
import asyncio
import csv
import json
import time
import httpx
from typing import List, Dict, Any
from collections import defaultdict

API_KEY = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
BASE_URL = "https://api.dify.ai"

class MultiTurnTester:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        
    def load_test_cases(self, csv_path: str) -> Dict[str, List[Dict[str, str]]]:
        """按session_id分组加载测试用例"""
        sessions = defaultdict(list)
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                session_id = row['session_id']
                sessions[session_id].append({
                    'session_id': session_id,
                    'turn': int(row['turn']),
                    'user_input': row['user_input'],
                    'category': row['category'],
                    'response': ''
                })
        
        # 按turn排序
        for session_id in sessions:
            sessions[session_id].sort(key=lambda x: x['turn'])
            
        return dict(sessions)
    
    async def test_session(self, session_id: str, turns: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """测试一个完整的对话session - 获取并使用conversation_id维持上下文"""
        print(f"🎯 测试会话 {session_id} ({len(turns)}轮)")
        
        results = []
        conversation_id = None
        
        for i, turn_data in enumerate(turns):
            print(f"  🗣️ 第{turn_data['turn']}轮: {turn_data['user_input'][:30]}...")
            
            payload = {
                "query": turn_data['user_input'],
                "inputs": {"user_input": turn_data['user_input']},
                "response_mode": "blocking",
                "user": session_id
            }
            
            # 从第二轮开始使用conversation_id
            if conversation_id and i > 0:
                payload["conversation_id"] = conversation_id
                print(f"    📱 使用对话ID: {conversation_id}")
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self.base_url}/v1/chat-messages",
                        headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        turn_data['response'] = data.get('answer', '').strip()
                        turn_data['status'] = 'success'
                        
                        # 记录第一轮返回的conversation_id
                        if i == 0:
                            conversation_id = data.get('conversation_id', '')
                            if conversation_id:
                                print(f"    📱 获取对话ID: {conversation_id}")
                    else:
                        turn_data['response'] = f"Error {response.status_code}: {response.text}"
                        turn_data['status'] = 'failed'
                        
            except Exception as e:
                turn_data['response'] = str(e)
                turn_data['status'] = 'error'
            
            results.append(turn_data)
            await asyncio.sleep(0.5)  # 避免请求过快
            
        return results
    
    async def run_multi_turn_test(self, csv_path: str) -> None:
        """运行多轮对话测试"""
        print("🚀 开始多轮对话上下文测试...")
        
        # 加载并分组测试用例
        sessions = self.load_test_cases(csv_path)
        total_sessions = len(sessions)
        total_turns = sum(len(turns) for turns in sessions.values())
        
        print(f"📊 共 {total_sessions} 个会话，{total_turns} 轮对话")
        
        all_results = []
        success_count = 0
        
        for i, (session_id, turns) in enumerate(sessions.items(), 1):
            print(f"\n📱 处理会话 {i}/{total_sessions}: {session_id}")
            
            session_results = await self.test_session(session_id, turns)
            all_results.extend(session_results)
            
            # 统计成功数
            session_success = sum(1 for r in session_results if r['status'] == 'success')
            success_count += session_success
            
            print(f"✅ 会话 {session_id} 完成: {session_success}/{len(turns)} 成功")
        
        # 保存结果
        output_path = f"multi_turn_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'session_id', 'turn', 'user_input', 'category', 'response', 'status'
            ])
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\n🎉 测试完成!")
        print(f"📈 总成功率: {success_count}/{total_turns}")
        print(f"📄 详细结果: {output_path}")
        
        # 分析会话连贯性
        self.analyze_coherence(all_results)
    
    def analyze_coherence(self, results: List[Dict[str, str]]) -> None:
        """分析对话连贯性"""
        sessions = defaultdict(list)
        for result in results:
            sessions[result['session_id']].append(result)
        
        print("\n🔍 连贯性分析:")
        for session_id, turns in sessions.items():
            if len(turns) > 1:
                print(f"  💬 会话 {session_id}: {len(turns)} 轮对话")
                for turn in turns:
                    print(f"    {turn['turn']}. {turn['user_input'][:40]}... → {turn['response'][:40]}...")

async def main():
    """主函数"""
    tester = MultiTurnTester(API_KEY, BASE_URL)
    await tester.run_multi_turn_test('aipet_testset_short_coherent.csv')

if __name__ == "__main__":
    asyncio.run(main())