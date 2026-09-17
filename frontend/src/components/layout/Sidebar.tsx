import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  PlusSquare,
  CheckSquare,
  Award,
  ShieldAlert,
  Search,
  Database,
  Building2,
  Lock,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['ADMIN', 'SETTER', 'REVIEWER', 'EXAM_OFFICER'] },
    { label: 'Questions', path: '/questions', icon: FileText, roles: ['ADMIN', 'SETTER', 'REVIEWER'] },
    { label: 'Create Question', path: '/questions/create', icon: PlusSquare, roles: ['ADMIN', 'SETTER'] },
    { label: 'Review Queue', path: '/review', icon: CheckSquare, roles: ['ADMIN', 'REVIEWER'] },
    { label: 'Exams & Release', path: '/exams', icon: Award, roles: ['ADMIN', 'EXAM_OFFICER'] },
    { label: 'Candidate CBT', path: '/cbt', icon: Lock, roles: ['ADMIN', 'CANDIDATE'] },
    { label: 'Leak Investigation', path: '/investigation', icon: Search, roles: ['ADMIN', 'EXAM_OFFICER'] },
    { label: 'Security Center', path: '/security', icon: ShieldAlert, roles: ['ADMIN'] },
    { label: 'Blockchain Ledger', path: '/blockchain', icon: Database, roles: ['ADMIN'] },
    { label: 'Centres & Devices', path: '/centres', icon: Building2, roles: ['ADMIN'] },
  ];

  const visibleNav = navItems.filter((item) => role && item.roles.includes(role));

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col border-r border-slate-800 min-h-screen">
      {/* Brand Logo Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black flex items-center justify-center text-lg shadow-lg shadow-blue-500/20">
          SE
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-tight text-white leading-none">Secure Exam</h1>
          <span className="text-[11px] text-slate-400 font-medium">Control Platform</span>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="p-3 space-y-1 flex-1">
        {visibleNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Security Architecture Footnote */}
      <div className="p-4 m-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-[11px] text-slate-400 leading-relaxed">
        <strong className="text-slate-200 block mb-1">Defense-In-Depth</strong>
        AES-256-GCM envelope encryption, SHA-256 fingerprinting, and audit ledger tracking.
      </div>
    </aside>
  );
};
