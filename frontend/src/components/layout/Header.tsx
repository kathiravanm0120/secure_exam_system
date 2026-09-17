import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, ShieldCheck, User as UserIcon } from 'lucide-react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title = 'Overview',
  subtitle = 'Security operations & CBT platform',
}) => {
  const { user, role, logout } = useAuth();

  const roleColors: Record<string, string> = {
    ADMIN: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20',
    SETTER: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    REVIEWER: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
    EXAM_OFFICER: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    CANDIDATE: 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20',
  };

  return (
    <header className="bg-white border-b border-slate-200 px-7 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
        <p className="text-xs text-slate-500 font-medium mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Role Badge */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-bold ${
            roleColors[role || 'ADMIN'] || roleColors.ADMIN
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{role}</span>
        </div>

        {/* User Info */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
          <div className="w-9 h-9 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center shadow-sm">
            {user?.name?.[0]?.toUpperCase() || <UserIcon className="w-4 h-4" />}
          </div>
          <div className="hidden sm:block">
            <div className="text-xs font-bold text-slate-900 leading-none">{user?.name}</div>
            <div className="text-[10px] text-slate-500 font-medium mt-0.5">{user?.email}</div>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          className="p-2 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
          title="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
