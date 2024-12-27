import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ToastContextProvider } from "@/components/ui/toast-context";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WhatsApp Summary Bot",
  description: "Configure WhatsApp group message summaries",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ToastContextProvider>
          {children}
        </ToastContextProvider>
      </body>
    </html>
  );
}
