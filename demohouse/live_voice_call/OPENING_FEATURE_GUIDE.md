# 开场白功能使用指南

## 功能概述

开场白功能根据用户输入的问题（question）和学生姓名（student_name），通过Dify工作流动态生成个性化的开场白，并以语音形式播放给用户。

## 功能特性

### 1. 智能内容生成
- 基于Dify工作流，根据问题和学生姓名动态生成个性化开场白
- 支持多种教学场景和问题类型
- 自然语言处理，生成符合教学情境的开场白

### 2. 语音合成
- 使用HTTP TTS服务将开场白文本转换为语音
- 支持多种语音类型和集群配置
- 与现有TTS配置保持一致

### 3. 状态管理
- 新增`Opening`状态，确保开场白播放期间用户输入被正确处理
- 防止重复播放开场白
- 与现有`Idle`和`InProgress`状态无缝集成

## 配置参数

### 后端配置（handler.py）
```python
# 开场白功能配置
ENABLE_OPENING = True      # 是否启用开场白功能
OPENING_TIMEOUT = 5        # 开场白生成超时时间（秒）
```

### 服务配置（VoiceBotService）
```python
service = VoiceBotService(
    # ... 其他配置
    enable_opening=ENABLE_OPENING,    # 启用开场白
    opening_timeout=OPENING_TIMEOUT,  # 超时配置
)
```

## 使用流程

### 1. 参数配置
客户端通过`UserParameters`事件发送必要参数：
```json
{
  "event": "UserParameters",
  "payload": {
    "question": "解一元二次方程",
    "student_name": "小明",
    "answer": "...",
    "user_responds": "...",
    "question_stem": "...",
    "question_category": "..."
  }
}
```

### 2. 触发条件
开场白在以下条件都满足时自动触发：
- `enable_opening = True`
- `opening_generated = False`（未生成过开场白）
- `current_question`不为空
- `current_student_name`不为空
- `state == "Idle"`

### 3. 事件流程
1. **OpeningStart事件** - 开场白生成开始
```json
{
  "event": "OpeningStart",
  "payload": {
    "question": "解一元二次方程",
    "student_name": "小明"
  }
}
```

2. **TTS事件序列** - 标准TTS事件流
```json
{
  "event": "TTSSentenceStart",
  "payload": {
    "sentence": "你好小明，我是你的学习助手乔青青..."
  }
}
```

3. **OpeningDone事件** - 开场白播放完成
```json
{
  "event": "OpeningDone",
  "payload": {
    "success": true,
    "error": null
  }
}
```

## Dify工作流配置

### 输入参数
开场白工作流需要支持以下输入参数：
- `question` (string): 教学问题/场景
- `student_name` (string): 学生姓名

### 输出要求
- 工作流应返回适合的开场白文本
- 文本应该自然、友好，符合教学场景
- 建议包含对学生的称呼和问题的简要介绍

### 示例输出
```text
你好小明，我是你的学习助手乔青青。今天我们一起来学习解一元二次方程，这是一个很有趣的数学问题。让我们一步一步来解决它吧！
```

## 错误处理

### 1. Dify调用失败
- 自动使用默认开场白模板
- 记录错误日志
- 发送`OpeningDone`事件，`success=false`

### 2. TTS转换失败
- 返回空音频数据
- 记录错误日志
- 继续后续流程

### 3. 网络超时
- 基于`opening_timeout`配置自动超时
- 使用默认开场白作为后备方案

## 前端集成

### 事件监听
```javascript
// 监听开场白相关事件
websocket.onmessage = (event) => {
  const data = parseWebSocketEvent(event.data);
  
  switch (data.event) {
    case 'OpeningStart':
      console.log('开场白生成开始:', data.payload);
      // 可以显示加载状态
      break;
      
    case 'OpeningDone':
      console.log('开场白播放完成:', data.payload);
      if (data.payload.success) {
        // 开场白成功播放
      } else {
        // 处理错误情况
        console.error('开场白错误:', data.payload.error);
      }
      break;
  }
};
```

### 状态管理
```javascript
// 在开场白期间禁用用户输入
if (botState === 'Opening') {
  // 禁用录音按钮
  // 显示"正在播放开场白"提示
}
```

## 调试和监控

### 日志关键词
- `[OPENING]` - 开场白相关日志
- `[PARAM_RECEIVED]` - 参数接收日志
- `[DIFY_REQUEST]` - Dify API请求日志
- `[HTTP_TTS]` - TTS合成日志

### 常见问题排查
1. **开场白未触发**
   - 检查`enable_opening`配置
   - 确认`question`和`student_name`参数是否正确传递
   - 验证服务状态是否为`Idle`

2. **开场白重复播放**
   - 检查`opening_generated`标志是否正确设置
   - 确认服务重启后状态重置

3. **Dify调用失败**
   - 检查API密钥和工作流配置
   - 验证网络连接和超时设置

## 最佳实践

1. **合理设置超时时间** - 建议5-10秒，平衡响应速度和稳定性
2. **优化开场白内容** - 保持简洁友好，避免过长的开场白
3. **错误处理** - 确保有合适的fallback机制
4. **性能监控** - 监控开场白生成耗时和成功率
5. **用户体验** - 提供清晰的视觉反馈，让用户了解当前状态

## 版本兼容性

此功能与现有的语音对话系统完全兼容，不会影响：
- 现有的对话流程
- ASR语音识别
- TTS语音合成
- LLM对话生成

开场白功能作为可选功能，可以通过配置随时启用或禁用。