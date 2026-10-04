import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import SettingsDrawer from '../components/SettingsDrawer';
import { useState } from 'react';

export default function MainLayout() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="flex h-screen bg-appBg text-primaryText overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 relative">
        <Topbar onOpenSettings={() => setIsSettingsOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <Outlet />
        </main>
        
        {/* Settings Drawer Overlay */}
        {isSettingsOpen && (
          <div 
            className="absolute inset-0 bg-black/20 z-40" 
            onClick={() => setIsSettingsOpen(false)}
          />
        )}
        
        {/* Settings Drawer */}
        <div className={`absolute top-0 right-0 h-full w-80 bg-cardBg shadow-soft-dark border-l border-cardBorder z-50 transform transition-transform duration-300 ease-in-out ${isSettingsOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          <SettingsDrawer onClose={() => setIsSettingsOpen(false)} />
        </div>
      </div>
    </div>
  );
}
