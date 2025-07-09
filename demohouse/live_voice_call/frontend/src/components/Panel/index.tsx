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

  const { handleConnect } = useVoiceBotService(userParameters);
  const { currentBotSentence, currentUserSentence } = useCurrentSentence();


  const { recStart, recStop } = useAudioRecorder();

  const { logContent } = useLogContent();

  const { wsUrl, setWsUrl } = useWsUrl();
  const [draftWsUrl, setDraftWsUrl] = useState(wsUrl);
  
  const [userParameters, setUserParameters] = useState<IUserParameters>({
    question: '',
    answer: '',
    user_responds: '',
    question_stem: '',
    student_name: '',
    question_category: '',
  });

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
        <Input.TextArea
          id={'log'}
          readOnly
          className={'w-full h-[400px] text-[12px] flex flex-col-reverse'}
          value={logContent.reverse().join('\n')}
        />
      </div>
    </div>
  );
};
