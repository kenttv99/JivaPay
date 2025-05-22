import '../styles/global.css'; // Основные стили с Tailwind CSS
import '../styles/theme.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin', 'cyrillic'] });

export const metadata: Metadata = {
  title: 'JivaPay - Панель администратора',
  description: 'Административная панель платежной системы JivaPay',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className={`${inter.className} bg-background text-[var(--jiva-text)]`}>
        {children}
      </body>
    </html>
  );
}
