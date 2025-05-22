import './globals.css';
import type { Metadata } from 'next';
import { Toaster } from 'sonner';
import { ReactQueryProvider } from '@/providers/react-query-provider';

export const metadata: Metadata = {
  title: 'Plataforma Stakeholders',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          {children}
          <Toaster richColors />
        </ReactQueryProvider>
      </body>
    </html>
  );
}
