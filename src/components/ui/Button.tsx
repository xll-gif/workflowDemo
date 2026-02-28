import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  children,
  loading = false,
  disabled = false,
  className = '',
  ...props
}) => {
  return (
    <button
      className={`
        bg-[#1890ff] hover:bg-[#40a9ff] active:bg-[#096dd9]
        text-white font-medium rounded
        transition-all duration-200
        disabled:bg-[#91d5ff] disabled:cursor-not-allowed
        flex items-center justify-center
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
      ) : null}
      {children}
    </button>
  );
};

export default Button;