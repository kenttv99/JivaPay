import './globals.css'; // Основные стили с Tailwind CSS
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import PermissionProviderWrapper from '@/components/providers/PermissionProviderWrapper';

const inter = Inter({ subsets: ['latin', 'cyrillic'] });

export const metadata: Metadata = {
  title: 'JivaPay - Панель администратора',
  description: 'Административная панель платежной системы JivaPay',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className={`${inter.className} bg-background text-primary`}>
        <PermissionProviderWrapper>
          {children}
        </PermissionProviderWrapper>
      </body>
    </html>
  );
}
