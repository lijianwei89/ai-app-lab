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
  Input,
  Typography,
} from '@arco-design/web-react';

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

  const [userParameters, setUserParameters] = useState<IUserParameters>({
    question: '3+7+8中的好朋友数是什么呀',
    answer: '3、7',
    user_responds: '',
    question_stem: '学校举办传统文化节，许多担任了投壶比赛的记分员，你能帮助许多快速计算出每个人的总分吗？3+7+8= 2+8+4=',
    student_name: '果果',
    question_category: '做题',
  });

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
          <Input
            prefix={<div className={'bg-white'}>ws_url</div>}
            value={draftWsUrl}
            onChange={setDraftWsUrl}
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
          <div className="grid grid-cols-2 gap-2">
            <Input
              placeholder="question"
              value={userParameters.question}
              onChange={(value) => setUserParameters(prev => ({ ...prev, question: value }))}
            />
            <Input
              placeholder="answer"
              value={userParameters.answer}
              onChange={(value) => setUserParameters(prev => ({ ...prev, answer: value }))}
            />
            <Input
              placeholder="question_stem"
              value={userParameters.question_stem}
              onChange={(value) => setUserParameters(prev => ({ ...prev, question_stem: value }))}
            />
            <Input
              placeholder="student_name"
              value={userParameters.student_name}
              onChange={(value) => setUserParameters(prev => ({ ...prev, student_name: value }))}
            />
            <Input
              placeholder="question_category"
              value={userParameters.question_category}
              onChange={(value) => setUserParameters(prev => ({ ...prev, question_category: value }))}
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
