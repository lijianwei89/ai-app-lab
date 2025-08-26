#!/usr/bin/env python3
import asyncio
import csv
import time
import httpx

API_KEY = "app-nxb7ZW4Uy9DZmeEMoE2ibTDY"
BASE_URL = "https://api.dify.ai"

async def test_file(csv_path):
    print(f"🚀 开始测试: {csv_path}")
    results = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cases = list(reader)
    
    print(f"📊 共 {len(cases)} 条测试")
    
    for i, row in enumerate(cases, 1):
        print(f"\r🧪 测试 {i}/{len(cases)}: {row['user_input'][:20]}...", end="")
        
        payload = {
            "query": row['user_input'],
            "inputs": {"user_input": row['user_input']},
            "response_mode": "blocking",
            "user": row['session_id'] or f"test-{i}",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(f"{BASE_URL}/v1/chat-messages", 
                                    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
                                    json=payload)
                
                if r.status_code == 200:
                    row['response'] = r.json().get('answer', '').strip()
                    row['status'] = 'success'
                else:
                    row['response'] = f"Error {r.status_code}"
                    row['status'] = 'failed'
                    
        except Exception as e:
            row['response'] = str(e)
            row['status'] = 'error'
            
        results.append(row)
        await asyncio.sleep(0.5)
    
    output = f"test_results_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    with open(output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['session_id','turn','user_input','category','response','status'])
        writer.writeheader()
        writer.writerows(results)
    
    success = sum(1 for r in results if r['status'] == 'success')
    print(f"\n✅ 完成! 成功 {success}/{len(results)}, 结果保存在: {output}")

if __name__ == "__main__":
    asyncio.run(test_file('aipet_testset_short_coherent.csv'))