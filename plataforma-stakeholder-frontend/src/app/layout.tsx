import './globals.css';
import type { Metadata } from 'next';

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
        <ReactQueryProvider>{children}</ReactQueryProvider>
      </body>
    </html>
  );
}
