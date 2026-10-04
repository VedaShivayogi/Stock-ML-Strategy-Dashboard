import { NavLink } from 'react-router-dom';
import { Home, BarChart2, Star, Wallet, Users, User, Phone, LogOut } from 'lucide-react';
import { cn } from '../lib/utils';

export default function Sidebar() {
  return (
    <aside className="w-64 flex-shrink-0 bg-cardBg border-r border-cardBorder hidden md:flex flex-col h-full z-10">
      <div className="h-16 flex items-center px-6 border-b border-cardBorder">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-logoAccent flex items-center justify-center transform rotate-45">
            <span className="text-white font-bold -rotate-45 text-sm">S</span>
          </div>
          <span className="text-xl font-bold font-inter tracking-tight">Stockin</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 px-4 flex flex-col gap-8">
        <div>
          <p className="px-2 text-xs font-semibold text-secondaryText uppercase tracking-wider mb-2">Menu</p>
          <nav className="space-y-1">
            <NavItem to="/dashboard" icon={Home} label="Dashboard" />
            {/* The following are just placeholder pages as per requirements, we may not implement all of them fully if not requested */}
            <NavItem to="/stocks" icon={BarChart2} label="Stocks" />
            <NavItem to="/favorites" icon={Star} label="Favorites" />
            <NavItem to="/wallet" icon={Wallet} label="Wallet" />
          </nav>
        </div>

        <div>
          <p className="px-2 text-xs font-semibold text-secondaryText uppercase tracking-wider mb-2">Account</p>
          <nav className="space-y-1">
            <NavItem to="/community" icon={Users} label="Our community" />
            <NavItem to="/profile" icon={User} label="Profile" />
            <NavItem to="/contact" icon={Phone} label="Contact us" />
          </nav>
        </div>
        
        <div>
          <p className="px-2 text-xs font-semibold text-secondaryText uppercase tracking-wider mb-2">Analysis</p>
          <nav className="space-y-1">
            <NavItem to="/risk" icon={BarChart2} label="Risk Analysis" />
            <NavItem to="/explain" icon={Star} label="Explainability" />
          </nav>
        </div>
      </div>

      <div className="p-4 border-t border-cardBorder">
        <button className="flex items-center gap-3 px-2 py-2 w-full text-secondaryText hover:text-negativeRed hover:bg-negativeRed/10 rounded-btn transition-colors">
          <LogOut size={20} />
          <span className="font-medium text-sm">Logout</span>
        </button>
      </div>
    </aside>
  );
}

function NavItem({ to, icon: Icon, label }: { to: string, icon: any, label: string }) {
  return (
    <NavLink 
      to={to} 
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-2 py-2 rounded-btn text-sm font-medium transition-colors",
        isActive 
          ? "bg-primaryBlue/10 text-primaryBlue" 
          : "text-secondaryText hover:text-primaryText hover:bg-cardBorder/50"
      )}
    >
      <Icon size={20} />
      {label}
    </NavLink>
  );
}
