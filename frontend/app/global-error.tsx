'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col items-center justify-center p-4">
          <h2 className="text-xl font-bold mb-2">Something went wrong!</h2>
          <p className="text-sm text-gray-500 mb-4">{error.message || 'An unexpected error occurred.'}</p>
          <button
            onClick={() => reset()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
