// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// Licensed under the 【火山方舟】原型应用软件自用许可协议
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at 
//     https://www.volcengine.com/docs/82379/1433703
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License. 

import {
  Button,
  Descriptions,
  Select,
  Typography,
} from '@arco-design/web-react';
import { CustomInput } from '@/components/CustomInput';

const { Option } = Select;

import { useAudioChatState } from '@/components/AudioChatProvider/hooks/useAudioChatState';

import { useLogContent } from '@/components/AudioChatServiceProvider/hooks/useLogContent';
import { useAudioRecorder } from '@/components/AudioChatServiceProvider/hooks/useAudioRecorder';
import { useVoiceBotService } from '@/components/AudioChatServiceProvider/hooks/useVoiceBotService';
import { useCurrentSentence } from '@/components/AudioChatServiceProvider/hooks/useCurrentSentence';
import { useWsUrl } from '@/components/AudioChatServiceProvider/hooks/useWsUrl';
import { useState } from 'react';
import { IUserParameters } from '@/types';

export const Panel = () => {
  const {
    wsConnected,

    botSpeaking,

    userSpeaking,

    botAudioPlaying,
  } = useAudioChatState();

  // 预设参数分组
  const defaultPresetParameters = {
    '数学-好朋友数': {
      question: '3+7+8中的好朋友数是什么呀',
      answer: '3、7',
      user_responds: '',
      question_stem: '学校举办传统文化节，许多担任了投壶比赛的记分员，你能帮助许多快速计算出每个人的总分吗？3+7+8= 2+8+4=',
      student_name: '果果',
      question_category: '做题',
    },
  };

  const [presetParameters, setPresetParameters] = useState<Record<string, IUserParameters>>(() => {
    const savedPresets = localStorage.getItem('userParameterPresets');
    return savedPresets ? JSON.parse(savedPresets) : defaultPresetParameters;
  });
  const [selectedPreset, setSelectedPreset] = useState<string>('数学-好朋友数');
  const [userParameters, setUserParameters] = useState<IUserParameters>(
    () => {
      const savedPresets = localStorage.getItem('userParameterPresets');
      const presets = savedPresets ? JSON.parse(savedPresets) : defaultPresetParameters;
      return presets['数学-好朋友数'];
    }
  );
  
  // 计算自定义预设数量（排除默认预设）
  const getCustomPresetCount = () => {
    const defaultKeys = Object.keys(defaultPresetParameters);
    return Object.keys(presetParameters).filter(key => !defaultKeys.includes(key)).length;
  };
  
  // 处理预设参数选择变化
  const handlePresetChange = (value: string) => {
    setSelectedPreset(value);
    setUserParameters(presetParameters[value]);
  };
  
  // 保存当前参数为新预设
  const saveCurrentAsPreset = () => {
    // 检查是否已达到最大自定义预设数量
    if (getCustomPresetCount() >= 10) {
      alert('最多只能创建10个自定义预设！');
      return;
    }
    
    const presetName = prompt('请输入预设名称:');
    if (presetName) {
      // 检查预设名称是否已存在
      if (presetParameters[presetName]) {
        const confirmOverwrite = confirm(`预设 "${presetName}" 已存在，是否覆盖?`);
        if (!confirmOverwrite) return;
      }
      
      const newPresets = {
        ...presetParameters,
        [presetName]: userParameters
      };
      setPresetParameters(newPresets);
      localStorage.setItem('userParameterPresets', JSON.stringify(newPresets));
      setSelectedPreset(presetName);
      alert(`预设 "${presetName}" 已保存`);
    }
  };
  
  // 重命名当前预设
  const renameCurrentPreset = () => {
    // 检查是否是默认预设
    if (Object.keys(defaultPresetParameters).includes(selectedPreset)) {
      alert('不能重命名默认预设！');
      return;
    }
    
    const newName = prompt('请输入新的预设名称:', selectedPreset);
    if (newName && newName !== selectedPreset) {
      // 检查新名称是否已存在
      if (presetParameters[newName]) {
        alert(`预设 "${newName}" 已存在！`);
        return;
      }
      
      // 重命名预设
      const newPresets = { ...presetParameters };
      newPresets[newName] = newPresets[selectedPreset];
      delete newPresets[selectedPreset];
      
      setPresetParameters(newPresets);
      localStorage.setItem('userParameterPresets', JSON.stringify(newPresets));
      setSelectedPreset(newName);
      alert(`预设已重命名为 "${newName}"`);
    }
  };
  
  // 删除当前预设
  const deleteCurrentPreset = () => {
    // 检查是否是默认预设
    if (Object.keys(defaultPresetParameters).includes(selectedPreset)) {
      alert('不能删除默认预设！');
      return;
    }
    
    const confirmDelete = confirm(`确定要删除预设 "${selectedPreset}" 吗?`);
    if (confirmDelete) {
      const newPresets = { ...presetParameters };
      delete newPresets[selectedPreset];
      
      setPresetParameters(newPresets);
      localStorage.setItem('userParameterPresets', JSON.stringify(newPresets));
      
      // 选择第一个预设作为默认选择
      const firstPreset = Object.keys(newPresets)[0];
      setSelectedPreset(firstPreset);
      setUserParameters(newPresets[firstPreset]);
      alert(`预设 "${selectedPreset}" 已删除`);
    }
  };
  
  // 更新参数时同时更新当前预设
  const updateUserParameters = (updater: (prev: IUserParameters) => IUserParameters) => {
    const updatedParams = updater(userParameters);
    setUserParameters(updatedParams);
    
    // 如果当前选择的预设与当前参数不匹配，则设置为自定义
    const currentPreset = Object.keys(presetParameters).find(
      key => JSON.stringify(presetParameters[key]) === JSON.stringify(updatedParams)
    );
    
    if (!currentPreset && selectedPreset !== '自定义') {
      // 参数已被修改，设置为自定义
      const newPresets = {
        ...presetParameters,
        '自定义': updatedParams
      };
      setPresetParameters(newPresets);
      localStorage.setItem('userParameterPresets', JSON.stringify(newPresets));
      setSelectedPreset('自定义');
    }
  };
  
  // 修改单个参数的处理函数
  const handleParameterChange = (field: keyof IUserParameters, value: string) => {
    updateUserParameters(prev => ({ ...prev, [field]: value }));
  };

  const { handleConnect, handleOpeningGreeting } = useVoiceBotService(userParameters);
  const { currentBotSentence, currentUserSentence } = useCurrentSentence();

  const { recStart, recStop } = useAudioRecorder();

  const { logContent } = useLogContent();

  const { wsUrl, setWsUrl } = useWsUrl();
  const [draftWsUrl, setDraftWsUrl] = useState(wsUrl);

  return (
    <div className={'flex flex-col gap-4'}>
      <div className={'w-[650px] flex flex-col gap-4'}>
        <div className={'flex gap-2'}>
          <CustomInput
            inputPrefix={<div className={'bg-white'}>ws_url</div>}
            value={draftWsUrl}
            onChange={(e) => setDraftWsUrl(e.target.value)}
          />
          <Button
            onClick={() => {
              setWsUrl(draftWsUrl);
              handleConnect();
            }}
          >
            连接
          </Button>
          <Button 
            disabled={!wsConnected} 
            onClick={handleOpeningGreeting}
            type="primary"
          >
            开场白
          </Button>
          <Button disabled={!wsConnected} onClick={recStart}>
            打电话
          </Button>
          <Button disabled={!wsConnected} onClick={recStop}>
            挂断
          </Button>
        </div>
        <Descriptions
          border
          data={[
            { label: '正在收听用户语音', value: userSpeaking ? '是' : '否' },
            { label: '正在输出回答', value: botSpeaking ? '是' : '否' },
            { label: '正在播放语音', value: botAudioPlaying ? '是' : '否' },
          ]}
        />
        <Descriptions
          column={1}
          border
          data={[
            {
              label: 'User 语音识别结果',
              value: (
                <Typography.Ellipsis className={'w-[400px]'} showTooltip>
                  {currentUserSentence}
                </Typography.Ellipsis>
              ),
            },
            {
              label: 'Bot 语音文本',
              value: (
                <Typography.Ellipsis
                  expandable={false}
                  rows={2}
                  className={'w-[400px]'}
                  showTooltip
                >
                  {currentBotSentence}
                </Typography.Ellipsis>
              ),
            },
          ]}
        />
        <div className="flex flex-col gap-2">
          <div className="font-semibold">用户参数设置</div>
          <div className="flex gap-2 items-center">
            <Select
              className="flex-1"
              placeholder="选择参数预设"
              value={selectedPreset}
              onChange={handlePresetChange}
            >
              {Object.keys(presetParameters).map(key => (
                <Option key={key} value={key}>
                  {key}
                </Option>
              ))}
            </Select>
            <Button onClick={saveCurrentAsPreset}>+</Button>
            <Button onClick={renameCurrentPreset} disabled={Object.keys(defaultPresetParameters).includes(selectedPreset)}>重命名</Button>
            <Button onClick={deleteCurrentPreset} disabled={Object.keys(defaultPresetParameters).includes(selectedPreset)}>删除</Button>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <CustomInput
              placeholder="question"
              value={userParameters.question}
              onChange={(e) => handleParameterChange('question', e.target.value)}
            />
            <CustomInput
              placeholder="answer"
              value={userParameters.answer}
              onChange={(e) => handleParameterChange('answer', e.target.value)}
            />
            <CustomInput
              placeholder="question_stem"
              value={userParameters.question_stem}
              onChange={(e) => handleParameterChange('question_stem', e.target.value)}
            />
            <CustomInput
              placeholder="student_name"
              value={userParameters.student_name}
              onChange={(e) => handleParameterChange('student_name', e.target.value)}
            />
            <CustomInput
              placeholder="question_category"
              value={userParameters.question_category}
              onChange={(e) => handleParameterChange('question_category', e.target.value)}
            />
          </div>
        </div>
        <div className="mb-2 text-xs text-gray-600">
          <div className="font-semibold mb-1">日志说明:</div>
          <div className="flex flex-wrap gap-4">
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-100 border-l-2 border-blue-600"></div>Dify请求</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-green-100 border-l-2 border-green-600"></div>Dify成功响应</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-red-100 border-l-2 border-red-600"></div>Dify错误响应</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-100 border-l-2 border-yellow-600"></div>用户参数</span>
          </div>
        </div>
        <div className={'w-full h-[400px] text-[12px] flex flex-col-reverse border border-gray-300 rounded-md p-2 overflow-y-auto bg-white'}>
          {logContent.slice().reverse().map((line, index) => {
            // 检查是否为Dify相关日志
            const isDifyRequest = line.includes('[DIFY_REQUEST]');
            const isDifyResponse = line.includes('[DIFY_RESPONSE]');
            const isDifySuccess = isDifyResponse && line.includes('| SUCCESS |');
            const isDifyError = isDifyResponse && line.includes('| ERROR |');
            
            let className = 'mb-1 font-mono';
            let style = {};
            
            if (isDifyRequest) {
              className += ' bg-blue-100 text-blue-800 p-1 rounded';
              style = { borderLeft: '4px solid #3b82f6' };
            } else if (isDifySuccess) {
              className += ' bg-green-100 text-green-800 p-1 rounded';
              style = { borderLeft: '4px solid #10b981' };
            } else if (isDifyError) {
              className += ' bg-red-100 text-red-800 p-1 rounded';
              style = { borderLeft: '4px solid #ef4444' };
            } else if (line.includes('UserParameters') || line.includes('[USER_PARAMS]')) {
              className += ' bg-yellow-100 text-yellow-800 p-1 rounded';
              style = { borderLeft: '4px solid #f59e0b' };
            }
            
            return (
              <div key={index} className={className} style={style}>
                <pre className="whitespace-pre-wrap break-words text-xs">{line}</pre>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
