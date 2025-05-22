'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function NotFound() {
  const router = useRouter();
  
  return (
    <div className="min-h-screen bg-[var(--jiva-background)] flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-[var(--jiva-primary)]">404</h1>
        <h2 className="text-3xl font-bold mb-6 text-[var(--jiva-text)]">Страница не найдена</h2>
        <p className="text-[var(--jiva-text-secondary)] mb-8">
          Запрашиваемая страница не существует или была перемещена
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.back()}
            className="px-6 py-2 border border-[var(--jiva-border)] rounded-md text-[var(--jiva-text)] hover:bg-[var(--jiva-background-paper)] transition-colors"
          >
            Вернуться назад
          </button>
          
          <Link
            href="/"
            className="px-6 py-2 bg-[var(--jiva-primary)] text-white rounded-md hover:bg-[var(--jiva-primary-dark)] transition-colors"
          >
            На главную
          </Link>
        </div>
      </div>
      
      <div className="mt-16 text-[var(--jiva-text-secondary)] text-sm">
        <p>Если вы считаете, что это ошибка, пожалуйста, свяжитесь с поддержкой</p>
      </div>
    </div>
  );
} 