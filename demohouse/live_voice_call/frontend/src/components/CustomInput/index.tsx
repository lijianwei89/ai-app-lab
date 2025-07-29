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

import React, { forwardRef, InputHTMLAttributes } from 'react';

interface CustomInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
  inputPrefix?: React.ReactNode;
}

export const CustomInput = forwardRef<HTMLInputElement, CustomInputProps>(
  ({ label, error, fullWidth = false, inputPrefix, className = '', ...props }, ref) => {
    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${className}`}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        <div className="relative">
          {inputPrefix && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {inputPrefix}
            </div>
          )}
          <input
            ref={ref}
            {...props}
            className={`
              w-full px-3 py-2 border rounded-md shadow-sm
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
              disabled:opacity-50 disabled:cursor-not-allowed
              ${error ? 'border-red-500' : 'border-gray-300'}
              ${inputPrefix ? 'pl-16' : ''}
              ${className || ''}
            `}
          />
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}
      </div>
    );
  }
);

CustomInput.displayName = 'CustomInput';