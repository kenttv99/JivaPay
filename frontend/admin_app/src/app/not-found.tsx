'use client';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary">404</h1>
        <h2 className="text-3xl font-bold mb-6 text-primary">Страница не найдена</h2>
        <p className="text-secondary mb-8">
          К сожалению, запрошенная страница не существует или была перемещена.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2 border border-border rounded-md text-primary hover:bg-surface transition-colors"
          >
            Назад
          </button>
          
          <a
            href="/admin"
            className="px-6 py-2 bg-accent text-white rounded-md hover:opacity-90 transition-colors"
          >
            На главную
          </a>
        </div>
        
        <div className="mt-16 text-secondary text-sm">
          Если проблема повторяется, обратитесь к администратору
        </div>
      </div>
    </div>
  );
} 