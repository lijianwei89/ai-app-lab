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

import { useContext, useRef } from 'react';
import { AudioChatServiceContext } from '@/components/AudioChatServiceProvider/context';

export const useLogContent = () => {
  const { logContent, setLogContent } = useContext(AudioChatServiceContext);
  const throttleMapRef = useRef<Map<string, { count: number; lastTime: number }>>(new Map());

  const log = (v: string) => {
    // 检查是否为需要节流的UserAudio日志
    if (v.includes('event:UserAudio')) {
      const key = 'UserAudio';
      const now = Date.now();
      const throttleInfo = throttleMapRef.current.get(key) || { count: 0, lastTime: 0 };
      
      // 每秒最多显示一条UserAudio日志
      if (now - throttleInfo.lastTime < 1000) {
        throttleInfo.count++;
        throttleMapRef.current.set(key, throttleInfo);
        return;
      }
      
      // 显示节流的日志，包含累计次数
      const message = throttleInfo.count > 0 
        ? `${v} (${throttleInfo.count + 1} frames sent)`
        : v;
      
      throttleMapRef.current.set(key, { count: 0, lastTime: now });
      
      setLogContent(prevState => [
        ...prevState,
        `[${new Date().toLocaleTimeString()}]\t${message}`,
      ]);
      return;
    }

    // 其他日志正常显示
    setLogContent(prevState => [
      ...prevState,
      `[${new Date().toLocaleTimeString()}]\t${v}`,
    ]);
  };
  return {
    logContent,
    log,
  };
};
