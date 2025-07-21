# 双Dify客户端功能区分配置

## 🎯 配置概述

为了区分开场白和对话过程的不同功能需求，系统现在支持两个独立的Dify API密钥：

### 🔑 API密钥分配

| 功能 | API密钥 | 工作流用途 |
|------|---------|------------|
| **对话流程** | `app-JqtJdpgiEKukUAxxT8oiJR4u` | 处理学生问答、教学互动 |
| **开场白** | `app-rCIokTn1NixIujuo4M18feAW` | 生成个性化开场白 |

## 📋 配置文件修改

### backend/handler.py
```python
# 对话流程的Dify API配置
DIFY_API_KEY = "app-JqtJdpgiEKukUAxxT8oiJR4u"  # For conversation workflow
DIFY_BASE_URL = "https://api.dify.ai"

# 开场白的Dify API配置
DIFY_OPENING_API_KEY = "app-rCIokTn1NixIujuo4M18feAW"  # For opening greeting workflow
```

### VoiceBotService初始化
```python
service = VoiceBotService(
    # ... 其他配置
    dify_api_key=DIFY_API_KEY,                    # 对话流程API密钥
    dify_opening_api_key=DIFY_OPENING_API_KEY,    # 开场白API密钥
    dify_base_url=DIFY_BASE_URL,
    enable_opening=ENABLE_OPENING,
    opening_timeout=OPENING_TIMEOUT,
)
```

## 🏗️ 架构实现

### 1. 双客户端架构
```python
class VoiceBotService:
    # 对话流程客户端
    dify_client: Optional[DifyClient] = None
    
    # 开场白专用客户端
    dify_opening_client: Optional[DifyClient] = None
```

### 2. 客户端初始化
```python
async def init(self):
    # 初始化对话流程客户端
    if self.llm_provider == LLMProvider.DIFY and self.dify_api_key:
        self.dify_client = DifyClient(
            api_key=self.dify_api_key,
            base_url=self.dify_base_url
        )
    
    # 初始化开场白客户端
    if self.dify_opening_api_key:
        self.dify_opening_client = DifyClient(
            api_key=self.dify_opening_api_key,
            base_url=self.dify_base_url
        )
```

### 3. 功能调用分离
```python
# 对话流程使用 dify_client
async def _stream_dify_chat(self, text: str):
    if not self.dify_client:
        raise ValueError("Dify client not initialized")
    
    async for chunk in self.dify_client.stream_workflow_run(inputs=inputs):
        yield chunk

# 开场白使用 dify_opening_client
async def _generate_opening_text(self) -> str:
    if not self.dify_opening_client:
        return ""
    
    async for chunk in self.dify_opening_client.stream_workflow_run(inputs=inputs):
        opening_text += chunk
```

## 🔄 工作流程

### 对话流程 (app-JqtJdpgiEKukUAxxT8oiJR4u)
1. **输入参数**：
   - `question`: 题目内容
   - `answer`: 标准答案
   - `user_responds`: 学生回答
   - `question_stem`: 题目主干
   - `student_name`: 学生姓名
   - `question_category`: 题目类别

2. **处理逻辑**：学生问答处理、教学反馈、知识点解析

3. **输出**：针对学生回答的个性化教学响应

### 开场白流程 (app-rCIokTn1NixIujuo4M18feAW)
1. **输入参数**：
   - `question`: 题目内容
   - `student_name`: 学生姓名

2. **处理逻辑**：生成个性化开场白

3. **输出**：适合的开场白文本，如 "小明，现在我们来解一元二次方程哦"

## 📊 测试验证

### 连接测试结果
- ✅ 对话流程客户端连接正常
- ✅ 开场白客户端连接正常
- ✅ 两个API密钥功能独立
- ✅ 配置参数验证通过

### 功能验证
- ✅ 开场白使用专用工作流
- ✅ 对话过程使用教学工作流
- ✅ 两个功能互不干扰
- ✅ 错误处理机制完善

## 💡 使用优势

### 1. 功能专业化
- **开场白工作流**：专门优化开场白生成逻辑
- **对话工作流**：专门处理教学问答互动

### 2. 独立管理
- 不同工作流可以独立调优
- 分别监控使用情况和性能
- 独立的错误处理和日志记录

### 3. 扩展性
- 未来可以添加更多专用工作流
- 支持不同场景的专业化处理
- 便于功能模块化管理

## 🔧 配置检查

### 验证配置正确性
```bash
# 运行测试脚本
python test_dual_dify_clients.py
```

### 预期输出
```
✅ 对话流程客户端: 正常
✅ 开场白客户端: 正常
✅ 不同API密钥
✅ 配置验证通过
```

## 🚨 注意事项

### 1. API密钥管理
- 确保两个API密钥都有效
- 定期检查API配额使用情况
- 保持密钥的安全性

### 2. 错误处理
- 开场白失败时有fallback机制
- 对话客户端失败时的降级处理
- 独立的错误日志记录

### 3. 性能监控
- 分别监控两个工作流的响应时间
- 记录成功率和错误率
- 优化不同工作流的性能

## 🎉 总结

通过双Dify客户端架构，系统现在可以：

- **清晰区分**：开场白和对话功能完全独立
- **专业优化**：不同工作流针对性优化
- **稳定运行**：错误隔离，互不影响
- **便于维护**：模块化管理，易于扩展

这种架构为未来的功能扩展和性能优化提供了良好的基础。