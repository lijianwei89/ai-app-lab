# 自建音色集成指南

## 当前状态
- ✅ 自建音色ID: `S_dwiOyLR61`
- ✅ 内网鉴权: `appid=200000054`, `token=bebc3b8ce075b6fd94d04407e1ed6937`
- ❌ 内网地址 `https://speech-internal.tal.com` 无法直接访问

## 集成方案

### 方案1: 直接替换现有配置（推荐）
```python
# 修改 backend/service.py:37
DEFAULT_SPEAKER = "S_dwiOyLR61"

# 修改 backend/handler.py:30-31
TTS_ACCESS_TOKEN = "bebc3b8ce075b6fd94d04407e1ed6937"
TTS_APP_ID = "200000054"
```

### 方案2: 动态配置更新
前端通过 `BotUpdateConfig` 事件动态更新：
```javascript
{
  event: 'BotUpdateConfig',
  payload: {
    speaker: 'S_dwiOyLR61'
  }
}
```

## 测试验证
创建了以下测试文件：
- `test_custom_voice.py` - 基础HTTP测试
- `test_custom_voice_volc.py` - 火山方舟客户端测试
- `test_custom_tts_simple.py` - 简单HTTP测试

## 注意事项
1. **网络环境**: 内网地址需要特定网络环境
2. **权限验证**: 确保token和appid有效
3. **音色格式**: 自建音色ID格式需匹配
4. **测试建议**: 先在内网环境验证接口可用性

## 快速集成步骤
1. 替换 `backend/handler.py` 中的TTS配置
2. 重启后端服务
3. 测试音频输出是否正常