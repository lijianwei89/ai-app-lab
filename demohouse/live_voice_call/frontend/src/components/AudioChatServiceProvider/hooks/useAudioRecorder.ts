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

import { useContext } from 'react';
import { AudioChatServiceContext } from '@/components/AudioChatServiceProvider/context';
import Recorder from 'recorder-core';
import 'recorder-core/src/extensions/waveview';
import { BIT_RATE, FRAME_SIZE, SAMPLE_RATE } from '@/constant';
import { encodeAudioOnlyRequest } from '@/utils';
import { EventType } from '@/types';
import { useLogContent } from '@/components/AudioChatServiceProvider/hooks/useLogContent';
import { useAudioChatState } from '@/components/AudioChatProvider/hooks/useAudioChatState';

export const useAudioRecorder = (onRecordStop?: () => void) => {
  const {
    serviceRef,
    waveRef,
    recorderRef,
    sendLastFrameRef,
    sendChunkRef,
    sendPcmBufferRef,
  } = useContext(AudioChatServiceContext);
  const { log } = useLogContent();
  const { setUserSpeaking } = useAudioChatState();
  const handleReset = () => {
    sendPcmBufferRef.current = new Int16Array(0);
    sendChunkRef.current = null;
    sendLastFrameRef.current = null;
  };
  const handleSend = (pcmFrame: Int16Array, isClose: boolean) => {
    if (isClose && pcmFrame.length === 0) {
      const len = sendLastFrameRef.current
        ? sendLastFrameRef.current.length
        : Math.round((SAMPLE_RATE / 1000) * 50);
      pcmFrame = new Int16Array(len);
    }
    sendLastFrameRef.current = pcmFrame;

    const blob = new Blob([pcmFrame.buffer], { type: 'audio/pcm' }); //这是裸pcm，无前44字节wav头字节wav头
    const data = encodeAudioOnlyRequest(blob);

    serviceRef.current?.sendMessage({
      event: EventType.UserAudio,
      data,
    });
    // 减少音频发送日志频率，每50次发送记录一次，或者在关闭时记录
    if (isClose || Math.random() < 0.02) {
      console.log('🎵 [ASR Debug] 发送音频数据:', {
        event: EventType.UserAudio,
        audioDataSize: data.size,
        pcmFrameLength: pcmFrame.length,
        isClose: isClose,
        timestamp: new Date().toISOString()
      });
    }
    log('send | event:' + EventType.UserAudio + ' payload: ...');
  };

  const handleProcess = (
    buffers: (Int16Array | null)[],
    bufferSampleRate: number,
    isClose: boolean,
  ) => {
    let pcm = new Int16Array(0);
    if (buffers.length > 0) {
      // 把 pcm列表（二维数组）展开成一维
      const chunk = Recorder.SampleData(
        buffers,
        bufferSampleRate,
        SAMPLE_RATE,
        sendChunkRef.current,
      );
      sendChunkRef.current = chunk;

      pcm = chunk.data;
    }

    let pcmBuffer = sendPcmBufferRef.current;
    const tmp = new Int16Array(pcmBuffer.length + pcm.length);
    tmp.set(pcmBuffer, 0);
    tmp.set(pcm, pcmBuffer.length);
    pcmBuffer = tmp;

    const chunkSize = FRAME_SIZE / (BIT_RATE / 8);

    // 按 timeSlice 切分
    while (true) {
      if (pcmBuffer.length >= chunkSize) {
        const frame = new Int16Array(pcmBuffer.subarray(0, chunkSize));
        pcmBuffer = new Int16Array(pcmBuffer.subarray(chunkSize));

        let closeVal = false;
        if (isClose && pcmBuffer.length === 0) {
          closeVal = true;
        }
        handleSend(frame, closeVal);
        if (!closeVal) continue;
      } else if (isClose) {
        const frame = new Int16Array(chunkSize);
        frame.set(pcmBuffer);
        pcmBuffer = new Int16Array(0);
        handleSend(frame, true);
      }
      break;
    }
    sendPcmBufferRef.current = pcmBuffer;
  };

  const recStart = () => {
    console.log('🎙️ [ASR Debug] ===== 开始录音，准备发送语音数据 =====');
    log('🎙️ [ASR] 开始录音');
    if (recorderRef.current) {
      recorderRef.current.close();
    }

    let clearBufferIdx = 0;

    const recorder = Recorder({
      type: 'unknown',
      onProcess: (
        buffers: (Int16Array | null)[],
        powerLevel: unknown,
        bufferDuration: unknown,
        bufferSampleRate: number,
        newBufferIdx: number,
        // asyncEnd
      ) => {
        const buffer = buffers[buffers.length - 1];
        waveRef.current &&
          waveRef.current.input(buffer, powerLevel, bufferSampleRate);
        for (let i = clearBufferIdx; i < newBufferIdx; i++) {
          buffers[i] = null;
        }
        clearBufferIdx = newBufferIdx;

        handleProcess(buffers, bufferSampleRate, false);
      },
    });

    recorder.open(
      () => {
        waveRef.current = Recorder.WaveView({
          elem: '.wave',
          width: 165,
          height: 45,
        });
        recorder.start();
        setUserSpeaking(true);
      },
      (msg: string, isUserNotAllow: boolean) => {
        console.error(
          (isUserNotAllow ? 'UserNotAllow，' : '') + '无法录音:' + msg,
        );
      },
    );

    handleReset();
    recorderRef.current = recorder;
  };

  const recStop = () => {
    console.log('🛑 [ASR Debug] ===== 停止录音，等待ASR识别结果 =====');
    log('🛑 [ASR] 停止录音，等待识别结果');
    if (!recorderRef.current) {
      return;
    }
    setUserSpeaking(false);
    recorderRef.current.close();
    handleProcess([], 0, true);
    
    // 调用回调，通知录音已停止
    onRecordStop?.();
  };

  return {
    recStart,
    recStop,
    waveRef,
  };
};
