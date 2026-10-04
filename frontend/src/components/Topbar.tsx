import { Search, Mail, Bell, Moon, Sun, Settings } from 'lucide-react';
import { useState } from 'react';

export default function Topbar({ onOpenSettings }: { onOpenSettings: () => void }) {
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));

  const toggleDark = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.theme = 'light';
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.theme = 'dark';
      setIsDark(true);
    }
  };

  return (
    <header className="h-16 px-4 md:px-6 flex items-center justify-between border-b border-cardBorder bg-cardBg shrink-0">
      <div className="flex-1 flex items-center">
        <div className="relative w-full max-w-md hidden md:block">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-secondaryText" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-cardBorder rounded-btn leading-5 bg-appBg text-primaryText placeholder-secondaryText focus:outline-none focus:ring-1 focus:ring-primaryBlue focus:border-primaryBlue sm:text-sm"
            placeholder="Search a ticker, e.g. SPY"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-secondaryText hover:text-primaryText transition-colors">
          <Mail className="h-5 w-5" />
        </button>
        <button className="text-secondaryText hover:text-primaryText transition-colors">
          <Bell className="h-5 w-5" />
        </button>
        <button onClick={toggleDark} className="text-secondaryText hover:text-primaryText transition-colors">
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
        <button onClick={onOpenSettings} className="text-secondaryText hover:text-primaryText transition-colors">
          <Settings className="h-5 w-5" />
        </button>
        
        <div className="h-8 w-px bg-cardBorder mx-1" />
        
        <div className="flex items-center gap-3 cursor-pointer">
          <img 
            className="h-8 w-8 rounded-full bg-gray-300" 
            src="https://api.dicebear.com/7.x/notionists/svg?seed=Felix&backgroundColor=e8eaee" 
            alt="User avatar" 
          />
          <div className="hidden md:block text-sm">
            <p className="font-medium text-primaryText">Evan Morrison</p>
            <p className="text-xs text-secondaryText">evan@example.com</p>
          </div>
        </div>
      </div>
    </header>
  );
}
