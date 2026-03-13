import React, { useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'auto';

const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState<Theme>('auto');

  useEffect(() => {
    // 初期化: 保存されたテーマまたは 'auto'
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const initialTheme = savedTheme || 'auto';
    setTheme(initialTheme);
    applyTheme(initialTheme);

    // OS設定変更のリアルタイム監視
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      const currentSavedTheme = localStorage.getItem('theme') as Theme | null;
      if (!currentSavedTheme || currentSavedTheme === 'auto') {
        applyTheme('auto');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const applyTheme = (t: Theme) => {
    const root = document.documentElement;
    if (t === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', t === 'dark');
    }
  };

  const cycleTheme = () => {
    const newTheme: Theme = 
      theme === 'auto' ? 'light' : 
      theme === 'light' ? 'dark' : 'auto';

    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  return (
    <button
      onClick={cycleTheme}
      className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-card border border-border-dim hover:border-yellow-400 transition-all focus:outline-none group shadow-sm active:scale-95"
      aria-label={`Current theme: ${theme}. Click to change.`}
    >
      <div className="relative w-5 h-5 flex items-center justify-center">
        {theme === 'light' && (
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-yellow-500 fill-current animate-in zoom-in duration-300" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 0 0 0-1.41l-1.06-1.06zm1.06-12.37a.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06a.996.996 0 0 0 0-1.41zm-12.37 12.37a.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41a.996.996 0 0 0 1.41 0l1.06-1.06a.996.996 0 0 0 0-1.41z"/></svg>
        )}
        {theme === 'dark' && (
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-indigo-400 fill-current animate-in zoom-in duration-300" viewBox="0 0 24 24"><path d="M12.1 22c4.9 0 9-4.1 9-9 0-4.7-3.9-8.7-8.6-8.9-.4 0-.8.3-.8.7v.5c0 1.1.2 2.1.6 3.1.4 1.1 1 2.1 1.7 3 1.3 1.5 3.1 2.6 5.1 3-.1.4-.2.8-.4 1.1-1.1 2.3-3.4 3.7-5.9 3.7-3.6 0-6.5-2.9-6.5-6.5 0-2.3 1.2-4.4 3-5.6.3-.2.4-.6.2-1-.2-.4-.6-.5-1-.3-2.6 1.7-4.2 4.6-4.2 7.8 0 5.2 4.2 9.4 9.4 9.4.1 0 .2 0 .3-.1z"/></svg>
        )}
        {theme === 'auto' && (
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-foreground/40 group-hover:text-yellow-400 transition-colors animate-in zoom-in duration-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
        )}
      </div>
      <span className="text-[10px] font-black uppercase tracking-[0.2em] hidden xs:block">
        {theme}
      </span>
    </button>
  );
};

export default ThemeToggle;
