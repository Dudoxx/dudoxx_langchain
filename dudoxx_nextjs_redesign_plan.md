# Dudoxx Extraction Next.js Redesign Plan

This document outlines a comprehensive plan to modernize the Dudoxx Extraction Next.js implementation with improved components, layouts, colors, and animations.

## Current State Analysis

The current implementation uses:
- Next.js with App Router
- TailwindCSS for styling
- Radix UI components (via shadcn/ui)
- React Hook Form for form handling
- Socket.io for real-time progress updates

The UI is functional but could benefit from modern design patterns, improved visual hierarchy, and engaging animations.

## Redesign Goals

1. Create a more visually appealing and modern interface
2. Improve user experience with smooth animations and transitions
3. Enhance the layout with responsive grid systems
4. Implement a more cohesive color scheme
5. Add micro-interactions for better feedback
6. Improve accessibility and usability

## Design System Updates

### Color Palette

Update the color palette to use a more vibrant and cohesive scheme:

```tsx
// In globals.css
:root {
  --radius: 0.625rem;
  
  /* Primary colors - Vibrant blue with purple undertones */
  --primary: oklch(0.55 0.25 265);
  --primary-foreground: oklch(0.985 0 0);
  
  /* Secondary colors - Soft teal */
  --secondary: oklch(0.65 0.15 195);
  --secondary-foreground: oklch(0.985 0 0);
  
  /* Accent colors - Warm amber */
  --accent: oklch(0.75 0.18 85);
  --accent-foreground: oklch(0.15 0.01 285);
  
  /* Background and foreground */
  --background: oklch(0.98 0.005 280);
  --foreground: oklch(0.15 0.01 285);
  
  /* Card and popover */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.15 0.01 285);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.15 0.01 285);
  
  /* Muted */
  --muted: oklch(0.95 0.01 280);
  --muted-foreground: oklch(0.55 0.02 285);
  
  /* Border and input */
  --border: oklch(0.85 0.01 280);
  --input: oklch(0.85 0.01 280);
  --ring: oklch(0.55 0.25 265 / 0.3);
  
  /* Destructive */
  --destructive: oklch(0.65 0.25 25);
  --destructive-foreground: oklch(0.985 0 0);
  
  /* Chart colors */
  --chart-1: oklch(0.65 0.25 265);
  --chart-2: oklch(0.65 0.15 195);
  --chart-3: oklch(0.75 0.18 85);
  --chart-4: oklch(0.65 0.25 25);
  --chart-5: oklch(0.65 0.25 145);
}

.dark {
  --background: oklch(0.15 0.01 285);
  --foreground: oklch(0.98 0.005 280);
  
  --card: oklch(0.2 0.01 285);
  --card-foreground: oklch(0.98 0.005 280);
  --popover: oklch(0.2 0.01 285);
  --popover-foreground: oklch(0.98 0.005 280);
  
  --primary: oklch(0.75 0.25 265);
  --primary-foreground: oklch(0.15 0.01 285);
  
  --secondary: oklch(0.75 0.15 195);
  --secondary-foreground: oklch(0.15 0.01 285);
  
  --accent: oklch(0.85 0.18 85);
  --accent-foreground: oklch(0.15 0.01 285);
  
  --muted: oklch(0.25 0.01 285);
  --muted-foreground: oklch(0.75 0.02 285);
  
  --border: oklch(0.3 0.01 285);
  --input: oklch(0.3 0.01 285);
  --ring: oklch(0.75 0.25 265 / 0.3);
  
  --destructive: oklch(0.75 0.25 25);
  --destructive-foreground: oklch(0.15 0.01 285);
}
```

### Typography

Update typography to use a more modern and readable approach:

```tsx
// In layout.tsx
import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

// In globals.css
@layer base {
  :root {
    --font-sans: "Inter", system-ui, sans-serif;
    --font-mono: "JetBrains Mono", monospace;
  }
  
  html {
    font-family: var(--font-sans);
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.025em;
  }
  
  h1 {
    font-size: 3rem;
    font-weight: 800;
  }
  
  h2 {
    font-size: 2.25rem;
  }
  
  h3 {
    font-size: 1.5rem;
  }
  
  pre, code {
    font-family: var(--font-mono);
  }
}
```

### Animation Library

Add Framer Motion for advanced animations:

```bash
npm install framer-motion
```

## Component Updates

### 1. Layout Components

#### Header Component

```tsx
// src/components/layout/header.tsx
"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { usePathname } from "next/navigation";
import { FileText, BarChart3, Home, Key, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export function Header() {
  const pathname = usePathname();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);
  
  const navItems = [
    { href: "/", label: "Home", icon: Home },
    { href: "/extract", label: "Extract", icon: FileText },
    { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  ];
  
  return (
    <header 
      className={`sticky top-0 z-50 w-full backdrop-blur transition-all duration-300 ${
        isScrolled 
          ? "bg-background/95 border-b shadow-sm" 
          : "bg-background/50"
      }`}
    >
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center space-x-2">
            <motion.div 
              className="bg-primary text-primary-foreground p-1.5 rounded-md"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FileText className="h-6 w-6" />
            </motion.div>
            <span className="font-bold text-xl hidden sm:inline-block">Dudoxx Extraction</span>
          </Link>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
              >
                <motion.div
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors relative ${
                    isActive 
                      ? "text-foreground" 
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                  
                  {isActive && (
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                      layoutId="navbar-indicator"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                </motion.div>
              </Link>
            );
          })}
        </nav>
        
        <div className="flex items-center gap-2">
          <ThemeToggle />
          
          <Button 
            variant="outline" 
            size="sm" 
            className="hidden md:flex items-center gap-1.5"
          >
            <Key className="h-4 w-4" />
            <span>API Key</span>
          </Button>
          
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="md:hidden"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="container py-4 border-t">
              <nav className="flex flex-col space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href;
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex items-center gap-2 px-4 py-3 rounded-md text-sm font-medium ${
                        isActive 
                          ? "bg-primary/10 text-primary" 
                          : "text-muted-foreground hover:bg-muted hover:text-foreground"
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex items-center gap-2 mt-2 w-full justify-start px-4 py-3 h-auto"
                >
                  <Key className="h-5 w-5" />
                  <span>API Key</span>
                </Button>
              </nav>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
```

#### Footer Component

```tsx
// src/components/layout/footer.tsx
import { FileText, Github, Book, Twitter, Mail } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export function Footer() {
  const currentYear = new Date().getFullYear();
  
  const footerLinks = [
    { label: "Documentation", href: "#", icon: Book },
    { label: "GitHub", href: "#", icon: Github },
    { label: "Twitter", href: "#", icon: Twitter },
    { label: "Contact", href: "#", icon: Mail },
  ];
  
  const legalLinks = [
    { label: "Terms", href: "#" },
    { label: "Privacy", href: "#" },
    { label: "Cookies", href: "#" },
  ];
  
  return (
    <footer className="border-t py-12 md:py-16 bg-muted/50">
      <div className="container grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
        <div className="flex flex-col gap-4">
          <Link href="/" className="flex items-center gap-2 w-fit">
            <motion.div 
              className="bg-primary text-primary-foreground p-1.5 rounded-md"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <FileText className="h-5 w-5" />
            </motion.div>
            <span className="font-bold text-lg">Dudoxx Extraction</span>
          </Link>
          
          <p className="text-sm text-muted-foreground max-w-xs">
            Extract structured information from documents using advanced LLM technology.
          </p>
          
          <p className="text-sm text-muted-foreground">
            &copy; {currentYear} Dudoxx Extraction. All rights reserved.
          </p>
        </div>
        
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-medium">Product</h3>
          <nav className="flex flex-col gap-3">
            <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Home
            </Link>
            <Link href="/extract" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Extract
            </Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
          </nav>
        </div>
        
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-medium">Resources</h3>
          <nav className="flex flex-col gap-3">
            {footerLinks.map((link) => {
              const Icon = link.icon;
              
              return (
                <Link 
                  key={link.label}
                  href={link.href} 
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
        
        <div className="flex flex-col gap-4">
          <h3 className="text-sm font-medium">Legal</h3>
          <nav className="flex flex-col gap-3">
            {legalLinks.map((link) => (
              <Link 
                key={link.label}
                href={link.href} 
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>
          
          <div className="mt-4">
            <h3 className="text-sm font-medium mb-3">Subscribe to our newsletter</h3>
            <div className="flex gap-2">
              <input 
                type="email" 
                placeholder="Enter your email" 
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
              <button className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
```

#### Main Layout Component

```tsx
// src/components/layout/main-layout.tsx
import { Header } from "./header";
import { Footer } from "./footer";
import { motion } from "framer-motion";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <>
      <Header />
      <motion.main 
        className="flex-1 container py-8 md:py-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {children}
      </motion.main>
      <Footer />
    </>
  );
}
```

### 2. Home Page

```tsx
// src/app/page.tsx
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRight, FileText, Box, LayoutGrid, Check, Zap, Shield } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  const features = [
    {
      icon: FileText,
      title: "Multiple Formats",
      description: "Support for various document formats including TXT, PDF, DOCX, HTML, CSV, and Excel.",
      color: "blue",
    },
    {
      icon: Box,
      title: "Domain-Based",
      description: "Specialized domains for medical, legal, and other document types for accurate extraction.",
      color: "purple",
    },
    {
      icon: LayoutGrid,
      title: "Structured Output",
      description: "Get results in JSON, text, or other formats for easy integration with your systems.",
      color: "amber",
    },
    {
      icon: Zap,
      title: "Fast Processing",
      description: "Parallel processing for quick extraction even with large documents.",
      color: "green",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your documents are processed securely and never stored without permission.",
      color: "red",
    },
    {
      icon: Check,
      title: "High Accuracy",
      description: "Advanced LLM technology ensures high accuracy in information extraction.",
      color: "indigo",
    },
  ];
  
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };
  
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };
  
  return (
    <MainLayout>
      <div className="flex flex-col items-center justify-center space-y-16 py-12">
        {/* Hero Section */}
        <motion.div 
          className="space-y-8 text-center max-w-4xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-medium bg-muted/50">
            <span className="text-primary">New</span>
            <span className="mx-2">•</span>
            <span>Introducing parallel extraction for faster processing</span>
          </div>
          
          <h1 className="text-5xl font-bold tracking-tighter sm:text-6xl md:text-7xl">
            <span className="block">Extract Structured</span>
            <span className="block bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
              Information from Documents
            </span>
          </h1>
          
          <p className="mx-auto max-w-[700px] text-xl text-muted-foreground md:text-2xl">
            Dudoxx Extraction uses advanced LLM technology to extract structured information from various document formats.
          </p>
          
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0 justify-center">
            <Link href="/extract">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button size="lg" className="px-8 py-6 text-lg font-semibold rounded-xl shadow-lg">
                  Get Started
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </motion.div>
            </Link>
            
            <Link href="/dashboard">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button variant="outline" size="lg" className="px-8 py-6 text-lg font-semibold rounded-xl border-2">
                  View Dashboard
                </Button>
              </motion.div>
            </Link>
          </div>
        </motion.div>
        
        {/* Features Grid */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-6xl"
          variants={container}
          initial="hidden"
          animate="show"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="flex flex-col h-full space-y-4 rounded-xl p-8 bg-card shadow-lg hover:shadow-xl transition-all border"
              variants={item}
              whileHover={{ y: -5 }}
            >
              <div className={`p-4 rounded-full bg-${feature.color}-100 dark:bg-${feature.color}-900/30 w-fit`}>
                <feature.icon className={`h-6 w-6 text-${feature.color}-600 dark:text-${feature.color}-400`} />
              </div>
              
              <h3 className="text-xl font-bold">{feature.title}</h3>
              
              <p className="text-muted-foreground flex-grow">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
        
        {/* CTA Section */}
        <motion.div 
          className="w-full max-w-6xl rounded-2xl overflow-hidden shadow-xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 p-10 relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-white/10 [mask-image:linear-gradient(0deg,white,transparent)]" />
            
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="space-y-4 text-left">
                <h2 className="text-3xl font-bold">Ready to extract information?</h2>
                <p className="text-lg text-muted-foreground max-w-md">
                  Start using our powerful extraction tools today and transform your document processing workflow.
                </p>
              </div>
              
              <Link href="/extract">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button size="lg" className="px-8 py-6 text-lg font-semibold rounded-xl shadow-md">
                    Try it now
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </motion.div>
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </MainLayout>
  );
}
```

### 3. Extraction Components

#### Progress Indicator Component

```tsx
// src/components/extraction/progress-indicator.tsx
import { ProgressData } from "@/lib/socket";
import { CheckCircle, AlertCircle, Clock, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ProgressIndicatorProps {
  progress: ProgressData;
}

export function ProgressIndicator({ progress }: ProgressIndicatorProps) {
  // Calculate progress percentage
  const percentage = progress.percentage ?? 
    progress.status === "starting" ? 10 :
    progress.status === "processing" ? 50 :
    progress.status === "completed" ? 100 :
    progress.status === "error" ? 100 : 0;
  
  // Determine color based on status
  const colorClass = 
    progress.status === "completed" ? "bg-green-500" :
    progress.status === "error" ? "bg-red-500" :
    "bg-primary";
  
  // Determine icon based on status
  const StatusIcon = 
    progress.status === "completed" ? CheckCircle :
    progress.status === "error" ? AlertCircle :
    progress.status === "processing" ? ArrowRight :
    Clock;
  
  // Determine text color based on status
  const textColorClass = 
    progress.status === "completed" ? "text-green-600 dark:text-green-400" :
    progress.status === "error" ? "text-red-600 dark:text-red-400" :
    "text-primary";
  
  return (
    <motion.div 
      className="space-y-6 rounded-xl border bg-card p-6 shadow-md"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <StatusIcon className={`h-5 w-5 ${textColorClass}`} />
          </motion.div>
          <span className={`font-medium ${textColorClass}`}>{progress.message}</span>
        </div>
        <span className="text-sm font-medium">{percentage}%</span>
      </div>
      
      <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
        <motion.div 
          className={`h-full ${colorClass}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      
      <AnimatePresence mode="wait">
        {progress.status === "processing" && (
          <motion.div 
            className="flex justify-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            key="processing"
          >
            <div className="inline-flex items-center px-4 py-2 bg-primary/10 text-primary rounded-full text-sm">
              <Clock className="animate-pulse mr-2 h-4 w-4" />
              <span>Processing document...</span>
            </div>
          </motion.div>
        )}
        
        {progress.status === "completed" && (
          <motion.div 
            className="flex justify-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            key="completed"
          >
            <div className="inline-flex items-center px-4 py-2 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full text-sm">
              <CheckCircle className="mr-2 h-4 w-4" />
              <span>Extraction completed successfully</span>
            </div>
          </motion.div>
        )}
        
        {progress.status === "error" && (
          <motion.div 
            className="flex justify-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            key="error"
          >
            <div className="inline-flex items-center px-4 py-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-full text-sm">
              <AlertCircle className="mr-2 h-4 w-4" />
              <span>Extraction failed</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

#### File Extraction Form Component

```tsx
// src/components/extraction/file-extraction-form.tsx
"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { extractFromFile } from "@/lib/api";
import { FileExtractionFormData, ExtractionResponse } from "@/lib/types";
import { ExtractionResults } from "./extraction-results";
import { ProgressIndicator } from "./progress-indicator";
import { subscribeToProgress, ProgressData } from "@/lib/socket";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Upload, Sparkles, AlertCircle } from "lucide-react";

export function FileExtractionForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [results, setResults] = useState<ExtractionResponse | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  const form = useForm<Omit<FileExtractionFormData, 'file'>>({
    defaultValues: {
      query: "",
      domain: "auto",
      useParallel: false
    }
  });
  
  // Subscribe to progress updates
  useEffect(() => {
    const unsubscribe = subscribeToProgress((data) => {
      setProgress(data);
    });
    
    return () => {
      unsubscribe();
    };
  }, []);
  
  async function onSubmit(data: Omit<FileExtractionFormData, 'file'>) {
    try {
      if (!selectedFile) {
        toast.error("Please select a file to upload");
        return;
      }
      
      setIsLoading(true);
      setProgress({
        status: "starting",
        message: "Starting extraction..."
      });
      setResults(null);
      
      // Create form data for file upload
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('query', data.query);
      if (data.domain && data.domain !== "auto") formData.append('domain', data.domain);
      formData.append('use_parallel', data.useParallel ? 'true' : 'false');
      
      const response = await extractFromFile(formData);
      
      setResults(response);
      setProgress({
        status: "completed",
        message: "Extraction completed successfully"
      });
      
      toast.success("Extraction completed successfully");
    } catch (error) {
      console.error("File extraction error:", error);
      setProgress({
        status: "error",
        message: "Extraction failed"
      });
      toast.error("Extraction failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };
  
  // Handle drag events
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };
  
  // Handle drop event
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };
  
  return (
    <motion.div 
      className="space-y-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-gradient-to-r from-primary/10 via-secondary/10 to-accent/10 p-6 rounded-xl border">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/20 rounded-lg">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-bold">Extract Information from File</h2>
        </div>
        <p className="text-muted-foreground">
          Upload a document and specify what information you want to extract. Our AI will analyze the document and extract the requested information.
        </p>
      </div>
      
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="query"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Query</FormLabel>
                <FormControl>
                  <Input 
                    placeholder="E.g., Extract all parties involved in the contract" 
                    {...field} 
                    className="h-12"
                  />
                </FormControl>
                <FormDescription>
                  Describe what information you want to extract.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <div 
            className={`border-2 border-dashed rounded-xl p-8 transition-all ${
              dragActive 
                ? "border-primary bg-primary/5" 
                : "border-muted-foreground/25 hover:border-muted-foreground/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center justify-center gap-4 text-center">
              <div className="p-4 bg-muted rounded-full">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
              
              <div>
                <p className="font-medium">
                  {selectedFile ? selectedFile.name : "Drag and drop your file here"}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedFile 
                    ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB` 
                    : "Supported formats: TXT, PDF, DOCX, HTML, CSV, Excel"
                  }
                </p>
              </div>
              
              <div className="flex gap-2 items-center">
                <span className="text-sm text-muted-foreground">or</span>
                <label 
                  htmlFor="file-upload" 
                  className="cursor-pointer text-sm font-medium text-primary hover:underline"
                >
                  browse files
                </label>
                <input
                  id="file-upload"
                  type="file"
                  accept=".txt,.pdf,.docx,.doc,.html,.htm,.csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              control={form.control}
              name="domain"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Domain (Optional)</FormLabel>
                  <Select 
                    onValueChange={field.onChange} 
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="Auto-detect" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="auto">Auto-detect</SelectItem>
                      <SelectItem value="legal">Legal</SelectItem>
                      <SelectItem value="medical">Medical</SelectItem>
                      <SelectItem value="financial">Financial</SelectItem>
                      <SelectItem value="general">General</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Select a specific domain or let the system auto-detect.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="useParallel"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                  <FormControl>
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="h-4 w-4 mt-1"
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Use Parallel Extraction</FormLabel>
                    <FormDescription>
                      Process document chunks in parallel for faster extraction.
                    </FormDescription>
                  </div>
                </FormItem>
              )}
            />
          </div>
          
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button 
              type="submit" 
              disabled={isLoading || !selectedFile} 
              className="w-full h-12 text-base font-medium"
            >
              {isLoading ? (
                <>
                  <span className="mr-2">Extracting...</span>
                  <Sparkles className="h-5 w-5 animate-pulse" />
                </>
              ) : (
                <>
                  <span className="mr-2">Extract Information</span>
                  <FileText className="h-5 w-5" />
                </>
              )}
            </Button>
          </motion.div>
        </form>
      </Form>
      
      <AnimatePresence>
        {progress && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ProgressIndicator progress={progress} />
          </motion.div>
        )}
      </AnimatePresence>
      
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <ExtractionResults results={results} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

## Implementation Plan

### Phase 1: Setup and Dependencies

1. Update dependencies:
   ```bash
   npm install framer-motion @next-themes/react
   ```

2. Update color scheme and typography in globals.css

3. Create a theme toggle component:
   ```tsx
   // src/components/ui/theme-toggle.tsx
   "use client";
   
   import { useTheme } from "next-themes";
   import { Button } from "@/components/ui/button";
   import { Moon, Sun } from "lucide-react";
   import { useEffect, useState } from "react";
   import { motion, AnimatePresence } from "framer-motion";
   
   export function ThemeToggle() {
     const { theme, setTheme } = useTheme();
     const [mounted, setMounted] = useState(false);
     
     useEffect(() => {
       setMounted(true);
     }, []);
     
     if (!mounted) {
       return <Button variant="ghost" size="icon" disabled className="h-9 w-9" />;
     }
     
     return (
       <Button
         variant="ghost"
         size="icon"
         onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
         className="h-9 w-9 rounded-md"
       >
         <AnimatePresence mode="wait" initial={false}>
           {theme === "dark" ? (
             <motion.div
               key="moon"
               initial={{ opacity: 0, rotate: -90 }}
               animate={{ opacity: 1, rotate: 0 }}
               exit={{ opacity: 0, rotate: 90 }}
               transition={{ duration: 0.2 }}
             >
               <Moon className="h-5 w-5" />
               <span className="sr-only">Switch to light mode</span>
             </motion.div>
           ) : (
             <motion.div
               key="sun"
               initial={{ opacity: 0, rotate: 90 }}
               animate={{ opacity: 1, rotate: 0 }}
               exit={{ opacity: 0, rotate: -90 }}
               transition={{ duration: 0.2 }}
             >
               <Sun className="h-5 w-5" />
               <span className="sr-only">Switch to dark mode</span>
             </motion.div>
           )}
         </AnimatePresence>
       </Button>
     );
   }
   ```

### Phase 2: Layout Components

1. Update the layout.tsx file with new fonts and theme provider
2. Implement the new Header component
3. Implement the new Footer component
4. Implement the new MainLayout component

### Phase 3: Page Components

1. Update the Home page with new design and animations
2. Update the Extract page with improved layout and animations
3. Update the Dashboard page with modern grid layout and animations

### Phase 4: Extraction Components

1. Implement the improved ProgressIndicator component
2. Implement the enhanced FileExtractionForm component
3. Implement the improved TextExtractionForm component
4. Implement the enhanced ExtractionResults component

### Phase 5: Testing and Refinement

1. Test all components in both light and dark mode
2. Test responsive behavior on different screen sizes
3. Test animations and transitions
4. Optimize performance and accessibility

## Conclusion

This redesign plan focuses on creating a more modern, visually appealing, and user-friendly interface for the Dudoxx Extraction Next.js application. By implementing these changes, the application will benefit from:

1. A more cohesive and vibrant color scheme
2. Smooth animations and transitions for better user experience
3. Improved layout with responsive grid systems
4. Enhanced visual hierarchy and readability
5. Better feedback through micro-interactions
6. Improved accessibility and usability

The implementation can be done incrementally, starting with the layout components and then moving on to the page and extraction components. This approach allows for testing and refinement at each stage of the redesign process.
