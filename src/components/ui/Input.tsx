import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  suffix?: React.ReactNode;
}

const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder = '',
  value,
  onChange,
  error = '',
  suffix,
  className = '',
  disabled = false,
  ...props
}) => {
  return (
    <div className="w-full">
      <div className="relative">
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={`
            w-full h-10 px-3 rounded border
            ${error ? 'border-red-500' : 'border-[#d9d9d9]'}
            focus:outline-none focus:border-[#1890ff] focus:ring-1 focus:ring-[#1890ff]
            disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
            transition-all duration-200
            ${suffix ? 'pr-10' : ''}
            ${className}
          `}
          {...props}
        />
        {suffix && (
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