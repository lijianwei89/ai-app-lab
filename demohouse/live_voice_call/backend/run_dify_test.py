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
Quick test runner for Dify API integration.
This script provides a simple interface to test specific scenarios.
"""

import asyncio
import sys
from test_dify import DifyTester, TEST_CONFIG, TEST_SCENARIOS


async def quick_streaming_test():
    """Run a quick streaming test with sample data."""
    print("🚀 Quick Streaming Test")
    print("=" * 40)
    
    # Use first test scenario
    scenario = TEST_SCENARIOS[0]
    
    tester = DifyTester(TEST_CONFIG)
    result = await tester.test_streaming_workflow(scenario)
    await tester.client.close()
    
    return result


async def quick_blocking_test():
    """Run a quick blocking test with sample data."""
    print("🚀 Quick Blocking Test")
    print("=" * 40)
    
    # Use first test scenario
    scenario = TEST_SCENARIOS[0]
    
    tester = DifyTester(TEST_CONFIG)
    result = await tester.test_blocking_workflow(scenario)
    await tester.client.close()
    
    return result


async def connection_test():
    """Test basic connection to Dify API."""
    print("🚀 Connection Test")
    print("=" * 40)
    
    tester = DifyTester(TEST_CONFIG)
    success = await tester.test_connection()
    await tester.client.close()
    
    return success


def print_usage():
    """Print usage instructions."""
    print("🎯 Dify API Test Runner")
    print("\nUsage:")
    print("  python run_dify_test.py [command]")
    print("\nCommands:")
    print("  connection    - Test basic API connection")
    print("  streaming     - Run quick streaming test")
    print("  blocking      - Run quick blocking test")
    print("  full          - Run comprehensive test suite")
    print("  help          - Show this help message")
    print("\nExample:")
    print("  python run_dify_test.py streaming")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    # Check API key
    if TEST_CONFIG['api_key'] == "app-JqtJdpgiEKukUAxxT8oiJR4u":
        print("❌ Please update the API key in test_dify.py before running!")
        print("   Edit TEST_CONFIG['api_key'] with your actual Dify API key.")
        return
    
    if command == "help":
        print_usage()
        
    elif command == "connection":
        success = await connection_test()
        if success:
            print("\n✅ Connection test passed!")
        else:
            print("\n❌ Connection test failed!")
            
    elif command == "streaming":
        result = await quick_streaming_test()
        if result['success']:
            print(f"\n✅ Streaming test completed in {result['execution_time']:.2f}s")
            print(f"📊 Received {result['chunk_count']} chunks")
        else:
            print(f"\n❌ Streaming test failed: {result['error']}")
            
    elif command == "blocking":
        result = await quick_blocking_test()
        if result['success']:
            print(f"\n✅ Blocking test completed in {result['execution_time']:.2f}s")
        else:
            print(f"\n❌ Blocking test failed: {result['error']}")
            
    elif command == "full":
        # Import and run full test
        from test_dify import main as full_test
        await full_test()
        
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())