import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Career Path Advisor — AI Career Development Assistant",
  description:
    "Upload your CV and get personalized recommendations for internships, courses, events, and a career development roadmap powered by AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body style={{ fontFamily: "'Inter', sans-serif" }}>{children}</body>
    </html>
  );
}
