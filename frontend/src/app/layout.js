import { Instrument_Sans, DM_Serif_Display } from "next/font/google";
import { ThemeProvider } from "@/components/ThemeProvider";
import CultureBackground from "@/components/CultureBackground";
import "./globals.css";

const instrumentSans = Instrument_Sans({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const dmSerif = DM_Serif_Display({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata = {
  title: "VaakSetu — Where Conversations Become Intelligence",
  description: "VaakSetu converts multilingual human conversations into structured intelligence and real-world actions across Healthcare, Finance, and Platform APIs.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${instrumentSans.variable} ${dmSerif.variable} antialiased min-h-screen`}>
        <ThemeProvider>
          <CultureBackground />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
