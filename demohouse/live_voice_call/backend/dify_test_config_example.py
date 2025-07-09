#!/usr/bin/env python3
"""
Dify 测试配置示例文件
请复制此文件并根据您的实际情况进行配置
"""

# ===== Dify API 配置 =====
DIFY_CONFIG = {
    # 步骤 1: 将此处替换为您的实际 Dify API 密钥
    # 在 Dify 控制台中创建应用后可以获得 API 密钥
    "api_key": "app-你的实际Dify密钥",
    
    # 步骤 2: 确认 Dify API 服务器地址
    # 如果您使用的是自部署的 Dify 实例，请修改此 URL
    "base_url": "https://api.dify.ai",
    
    # 步骤 3: 设置测试用户 ID（可以保持默认）
    "user_id": "test_user_voice_call"
}

# ===== 测试选项 =====
TEST_OPTIONS = {
    # 是否启用详细日志输出
    "verbose_logging": True,
    
    # 测试超时时间（秒）
    "timeout": 30,
    
    # 是否保存测试结果到文件
    "save_results": True,
    
    # 结果文件保存目录
    "results_dir": "./test_results/"
}

# ===== 自定义测试数据 =====
CUSTOM_TEST_SCENARIOS = [
    {
        "name": "自定义场景1",
        "description": "根据您的业务需求定制的测试场景",
        "inputs": {
            "question": "您的自定义问题",
            "answer": "预期答案",
            "question_stem": "问题主干",
            "student_name": "测试学生",
            "question_category": "科目分类",
            "user_input": "用户实际输入的内容",
            "user_responds": "ASR 识别的用户语音内容"
        }
    }
]

# ===== 配置验证函数 =====
def validate_config():
    """验证配置是否正确"""
    errors = []
    
    if DIFY_CONFIG["api_key"] == "app-你的实际Dify密钥":
        errors.append("❌ 请设置您的实际 Dify API 密钥")
    
    if not DIFY_CONFIG["api_key"].startswith("app-"):
        errors.append("❌ Dify API 密钥格式错误，应该以 'app-' 开头")
    
    if not DIFY_CONFIG["base_url"].startswith("http"):
        errors.append("❌ base_url 格式错误，应该是完整的 HTTP URL")
    
    return errors

# ===== 使用说明 =====
USAGE_INSTRUCTIONS = """
🔧 配置步骤:

1. 获取 Dify API 密钥:
   - 登录您的 Dify 控制台
   - 创建或选择一个应用
   - 在应用设置中找到 API 密钥
   - 复制以 'app-' 开头的密钥

2. 更新配置:
   - 将 DIFY_CONFIG["api_key"] 替换为您的实际密钥
   - 如果使用自部署 Dify，请更新 base_url

3. 运行测试:
   python dify_standalone_test.py connection    # 测试连接
   python dify_standalone_test.py scenario 0    # 测试单个场景
   python dify_standalone_test.py all           # 测试所有场景

4. 检查结果:
   - 控制台会显示实时输出
   - 测试结果会保存为 JSON 文件
   - 检查生成的 dify_test_result_*.json 文件
"""

if __name__ == "__main__":
    print("📋 Dify 测试配置示例")
    print("=" * 50)
    
    # 验证当前配置
    errors = validate_config()
    if errors:
        print("⚠️  配置问题:")
        for error in errors:
            print(f"   {error}")
    else:
        print("✅ 配置验证通过")
    
    print(USAGE_INSTRUCTIONS)