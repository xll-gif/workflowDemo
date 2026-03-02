import React, { useState } from 'react';

interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'onBlur'> {
  error?: string;
  suffix?: React.ReactNode;
  showPasswordToggle?: boolean;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
}

const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder = '',
  value,
  onChange,
  onBlur,
  error = '',
  suffix,
  showPasswordToggle = false,
  className = '',
  disabled = false,
  name,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const inputType = showPasswordToggle ? (showPassword ? 'text' : 'password') : type;

  return (
    <div className="w-full">
      <div className="relative">
        <input
          type={inputType}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          disabled={disabled}
          name={name}
          className={`
            w-full h-10 px-3 rounded border
            ${error ? 'border-red-500' : 'border-[#d9d9d9]'}
            focus:outline-none focus:border-[#1890ff] focus:ring-1 focus:ring-[#1890ff]
            disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
            transition-all duration-200
            ${suffix || showPasswordToggle ? 'pr-10' : ''}
            ${className}
          `}
          {...props}
        />
        {showPasswordToggle && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            {showPassword ? '👁️' : '🙈'}
          </button>
        )}
        {suffix && !showPasswordToggle && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {suffix}
          </div>
        )}
      </div>
      {error && (
        <p className="text-red-500 text-xs mt-1">{error}</p>
      )}
    </div>
  );
};

export default Input;
