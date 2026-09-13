import "./globals.css";

export const metadata = {
  title: "NER Landslide Intelligence",
  description: "AI-powered landslide risk intelligence and early warning platform for India's North Eastern Region",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
