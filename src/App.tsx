import React from 'react';
import LoginPage from './components/pages/LoginPage';

const App: React.FC = () => {
  // 从布局规范获取背景色，必须使用此方式设置根背景
  const backgroundColor = '#ffffff'; // layout.colors.background

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor }}
    >
      <LoginPage />
    </div>
  );
};

export default App;
