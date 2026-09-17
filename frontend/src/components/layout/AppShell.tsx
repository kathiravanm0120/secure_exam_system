import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppShellProps {
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ title, subtitle, children }) => {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header title={title} subtitle={subtitle} />
        <main className="p-7 flex-1 overflow-y-auto">
          {children ? children : <Outlet />}
        </main>
      </div>
    </div>
  );
};
