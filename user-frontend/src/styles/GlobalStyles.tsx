import { createGlobalStyle } from 'styled-components';
// 使用 React CSS-in-JS 方案

export const GlobalStyles = () => (
  <>
    <style>{`
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
          'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      @media (max-width: 768px) {
        .mobile-optimized {
          padding-left: 12px !important;
          padding-right: 12px !important;
        }
        
        .page-header h1 {
          font-size: 1.5rem !important;
        }
      }

      @media (max-width: 480px) {
        .mobile-optimized {
          padding-left: 8px !important;
          padding-right: 8px !important;
        }
        
        .page-header h1 {
          font-size: 1.25rem !important;
        }
      }

      /* 滚动条样式 */
      ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
      }

      ::-webkit-scrollbar-track {
        background: #f1f1f1;
      }

      ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 3px;
      }

      ::-webkit-scrollbar-thumb:hover {
        background: #555;
      }

      /* 动画 */
      .fade-in {
        animation: fadeIn 0.3s ease-in-out;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .slide-up {
        animation: slideUp 0.3s ease-out;
      }

      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }

      /* Loading */
      .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #1890ff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
      }

      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `}</style>
  </>
);
