#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License. 

"""
Standalone test script for Dify API integration.
This script tests the Dify client functionality independently from the voice call system.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any
from dify_client import DifyClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Test Configuration
TEST_CONFIG = {
    # TODO: Replace with your actual Dify API key
    "api_key": "app-JqtJdpgiEKukUAxxT8oiJR4u",
    "base_url": "https://api.dify.ai",
    "user_id": "test_user_001"
}

# Test Data Sets
TEST_SCENARIOS = [
    {
        "name": "Basic Conversation Test",
        "description": "Test basic conversation with LLM parameters",
        "inputs": {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "question_stem": "Geography question about European capitals",
            "student_name": "Alice",
            "question_category": "Geography",
            "user_input": "Tell me about the capital of France",
            "user_responds": "Tell me about the capital of France",
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there! How can I help you today?"}
            ]
        }
    },
    {
        "name": "Educational Scenario",
        "description": "Test educational conversation scenario",
        "inputs": {
            "question": "Explain photosynthesis",
            "answer": "Photosynthesis is the process by which plants convert sunlight into energy",
            "question_stem": "Biology question about plant processes",
            "student_name": "Bob",
            "question_category": "Biology",
            "user_input": "Can you explain how plants make their food?",
            "user_responds": "Can you explain how plants make their food?",
            "conversation_history": [
                {"role": "user", "content": "I want to learn about biology"},
                {"role": "assistant", "content": "Great! Biology is fascinating. What would you like to know?"}
            ]
        }
    },
    {
        "name": "Math Problem Test",
        "description": "Test mathematical problem solving",
        "inputs": {
            "question": "Solve: 2x + 5 = 13",
            "answer": "x = 4",
            "question_stem": "Linear algebra equation solving",
            "student_name": "Carol",
            "question_category": "Mathematics",
            "user_input": "Help me solve this equation: 2x + 5 = 13",
            "user_responds": "Help me solve this equation: 2x + 5 = 13",
            "conversation_history": [
                {"role": "user", "content": "I need help with math"},
                {"role": "assistant", "content": "I'd be happy to help you with math! What problem are you working on?"}
            ]
        }
    },
    {
        "name": "Empty Parameters Test",
        "description": "Test with minimal parameters",
        "inputs": {
            "user_input": "Hello, how are you?",
            "user_responds": "Hello, how are you?",
            "conversation_history": []
        }
    }
]


class DifyTester:
    """Comprehensive tester for Dify API integration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the tester with configuration."""
        self.config = config
        self.client = DifyClient(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        self.results = []
    
    async def test_streaming_workflow(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test streaming workflow execution."""
        print(f"\n🔄 Testing Streaming Mode: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Inputs: {json.dumps(scenario['inputs'], indent=2)}")
        
        result = {
            "scenario": scenario['name'],
            "mode": "streaming",
            "success": False,
            "response_chunks": [],
            "total_response": "",
            "error": None,
            "execution_time": 0,
            "chunk_count": 0
        }
        
        start_time = time.time()
        
        try:
            print("\n📡 Starting streaming request...")
            async for chunk in self.client.stream_workflow(
                inputs=scenario['inputs'],
                user_id=self.config['user_id']
            ):
                result['response_chunks'].append(chunk)
                result['total_response'] += chunk
                result['chunk_count'] += 1
                print(f"📝 Chunk {result['chunk_count']}: {chunk}")
            
            result['success'] = True
            result['execution_time'] = time.time() - start_time
            
            print(f"\n✅ Streaming test completed successfully!")
            print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
            print(f"📊 Total chunks received: {result['chunk_count']}")
            print(f"📄 Complete response: {result['total_response']}")
            
        except Exception as e:
            result['error'] = str(e)
            result['execution_time'] = time.time() - start_time
            print(f"\n❌ Streaming test failed: {str(e)}")
        
        return result
    
    async def test_blocking_workflow(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test blocking workflow execution."""
        print(f"\n🔄 Testing Blocking Mode: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Inputs: {json.dumps(scenario['inputs'], indent=2)}")
        
        result = {
            "scenario": scenario['name'],
            "mode": "blocking",
            "success": False,
            "response": None,
            "error": None,
            "execution_time": 0
        }
        
        start_time = time.time()
        
        try:
            print("\n📡 Starting blocking request...")
            response = await self.client.run_workflow(
                inputs=scenario['inputs'],
                user_id=self.config['user_id']
            )
            
            result['response'] = response
            result['success'] = True
            result['execution_time'] = time.time() - start_time
            
            print(f"\n✅ Blocking test completed successfully!")
            print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
            print(f"📄 Response: {json.dumps(response, indent=2)}")
            
        except Exception as e:
            result['error'] = str(e)
            result['execution_time'] = time.time() - start_time
            print(f"\n❌ Blocking test failed: {str(e)}")
        
        return result
    
    async def test_connection(self) -> bool:
        """Test basic connection to Dify API."""
        print("\n🔗 Testing Dify API Connection...")
        
        try:
            # Simple test with minimal inputs
            test_inputs = {"user_input": "Connection test"}
            
            async for chunk in self.client.stream_workflow(
                inputs=test_inputs,
                user_id="connection_test"
            ):
                print(f"✅ Connection successful! Received: {chunk}")
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("🚀 Starting Dify API Comprehensive Test Suite")
        print("=" * 60)
        
        # Test connection first
        connection_ok = await self.test_connection()
        if not connection_ok:
            print("\n❌ Connection test failed. Please check your API key and network.")
            return
        
        # Run all test scenarios
        for scenario in TEST_SCENARIOS:
            print("\n" + "=" * 60)
            
            # Test streaming mode
            streaming_result = await self.test_streaming_workflow(scenario)
            self.results.append(streaming_result)
            
            # Wait a bit between tests
            await asyncio.sleep(1)
            
            # Test blocking mode
            blocking_result = await self.test_blocking_workflow(scenario)
            self.results.append(blocking_result)
            
            # Wait between scenarios
            await asyncio.sleep(2)
        
        # Generate test summary
        await self.generate_test_summary()
        
        # Cleanup
        await self.client.close()
    
    async def generate_test_summary(self):
        """Generate and display test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['scenario']} ({result['mode']}) - {result['execution_time']:.2f}s")
            if not result['success']:
                print(f"   Error: {result['error']}")
        
        # Performance analysis
        successful_results = [r for r in self.results if r['success']]
        if successful_results:
            avg_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)
            print(f"\n⏱️  Average execution time: {avg_time:.2f} seconds")
        
        # Save results to file
        with open('dify_test_results.json', 'w') as f:
            json.dump({
                'config': self.config,
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (successful_tests/total_tests)*100
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"\n📁 Test results saved to: dify_test_results.json")


async def main():
    """Main test runner."""
    print("🎯 Dify API Integration Test")
    print("This script will test the Dify API integration with various scenarios.")
    print("\n⚠️  IMPORTANT: Make sure to update the API key in TEST_CONFIG before running!")
    
    # Check if API key is still placeholder
    if TEST_CONFIG['api_key'] == "app-JqtJdpgiEKukUAxxT8oiJR4u":
        print("\n❌ Please update the API key in TEST_CONFIG before running the test!")
        print("   Update TEST_CONFIG['api_key'] with your actual Dify API key.")
        return
    
    print(f"\n🔧 Configuration:")
    print(f"   API Key: {TEST_CONFIG['api_key'][:10]}***")
    print(f"   Base URL: {TEST_CONFIG['base_url']}")
    print(f"   User ID: {TEST_CONFIG['user_id']}")
    
    # Initialize and run tester
    tester = DifyTester(TEST_CONFIG)
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())