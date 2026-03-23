import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/Sidebar';
import { AuthProvider } from '@/context/AuthContext';


const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AISec Intelligence Platform',
  description: 'AI-Powered Security Operations and Governance',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <div className="flex min-h-screen bg-[#05070b]">
            <Sidebar />
            <main className="flex-1 pl-64 min-h-screen">

            <header className="h-16 border-b glass flex items-center px-8 justify-between sticky top-0 z-40">
              <div className="flex items-center gap-4">
                <h1 className="font-semibold text-lg text-slate-200">System Dashboard</h1>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-xs font-medium text-slate-300">Backend Connected</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600"></div>
              </div>
            </header>
            <div className="p-8">
              {children}
            </div>
          </main>
        </div>
        </AuthProvider>
      </body>

    </html>
  );
}
