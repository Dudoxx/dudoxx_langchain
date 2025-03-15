# Dudoxx Extraction Frontend (Next.js)

A modern web interface for the Dudoxx Extraction system, built with Next.js, React, TypeScript, and Tailwind CSS.

## Features

- **Text Extraction**: Extract structured information from text using natural language queries
- **File Extraction**: Upload and extract information from various file formats (PDF, DOCX, TXT, etc.)
- **Multi-Query Extraction**: Run multiple extraction queries at once on the same document
- **Domain-Based Extraction**: Leverage specialized domains for more accurate extraction
- **Real-time Progress Updates**: Monitor extraction progress in real-time via Socket.IO
- **Dashboard**: View extraction history and statistics

## Tech Stack

- **Framework**: [Next.js 14](https://nextjs.org/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/)
- **Form Handling**: [React Hook Form](https://react-hook-form.com/)
- **Real-time Updates**: [Socket.IO](https://socket.io/)
- **HTTP Client**: [Axios](https://axios-http.com/)
- **Notifications**: [Sonner](https://sonner.emilkowal.ski/)

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn
- Dudoxx Extraction API running on port 8000
- Dudoxx Extraction Socket.IO server running on port 8001

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/dudoxx-extraction-nextjs.git
   cd dudoxx-extraction-nextjs
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create a `.env.local` file in the root directory with the following variables:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_SOCKET_URL=http://localhost:8001
   NEXT_PUBLIC_DEFAULT_API_KEY=your-api-key
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

```
dudoxx_extraction_nextjs/
├── public/              # Static assets
├── src/
│   ├── app/             # Next.js app router pages
│   ├── components/      # React components
│   │   ├── extraction/  # Extraction-related components
│   │   ├── layout/      # Layout components
│   │   └── ui/          # UI components (shadcn/ui)
│   ├── lib/             # Utility functions and services
│   └── styles/          # Global styles
├── .env.local           # Environment variables
├── next.config.js       # Next.js configuration
├── package.json         # Project dependencies
├── tailwind.config.js   # Tailwind CSS configuration
└── tsconfig.json        # TypeScript configuration
```

## API Integration

The frontend communicates with the Dudoxx Extraction API for all extraction operations. The API service is defined in `src/lib/api.ts` and handles:

- Text extraction
- File extraction
- Multi-query extraction
- API key management

## Real-time Progress Updates

Real-time progress updates are handled via Socket.IO, with the socket service defined in `src/lib/socket.ts`:

```typescript
// src/lib/socket.ts
import { io, Socket } from 'socket.io-client';
import { create } from 'zustand';

// Socket.IO connection URL from environment variable
const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8001';

// Progress update type
export type ProgressUpdate = {
  status: 'starting' | 'processing' | 'completed' | 'error';
  message: string;
  percentage?: number;
};

// Socket store type
type SocketStore = {
  socket: Socket | null;
  connected: boolean;
  progress: ProgressUpdate | null;
  connect: () => void;
  disconnect: () => void;
};

// Create socket store with Zustand
export const useSocketStore = create<SocketStore>((set, get) => ({
  socket: null,
  connected: false,
  progress: null,
  
  // Connect to Socket.IO server
  connect: () => {
    if (get().socket) return;
    
    const socket = io(SOCKET_URL);
    
    socket.on('connect', () => {
      console.log('Connected to Socket.IO server');
      set({ connected: true });
    });
    
    socket.on('progress', (data: ProgressUpdate) => {
      console.log('Progress update:', data);
      set({ progress: data });
    });
    
    socket.on('disconnect', () => {
      console.log('Disconnected from Socket.IO server');
      set({ connected: false });
    });
    
    set({ socket });
  },
  
  // Disconnect from Socket.IO server
  disconnect: () => {
    const { socket } = get();
    if (socket) {
      socket.disconnect();
      set({ socket: null, connected: false });
    }
  }
}));
```

The socket connection is initialized in the extraction components:

```typescript
// In extraction component
import { useSocketStore } from '@/lib/socket';
import { useEffect } from 'react';

export function ExtractionForm() {
  const { connect, disconnect, progress } = useSocketStore();
  
  // Connect to Socket.IO server on component mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);
  
  // Use progress updates in the UI
  return (
    <div>
      {progress && (
        <ProgressIndicator 
          status={progress.status} 
          message={progress.message} 
          percentage={progress.percentage} 
        />
      )}
      {/* Rest of the form */}
    </div>
  );
}
```

## Available Pages

- **Home** (`/`): Landing page with overview of the application
- **Extract** (`/extract`): Main extraction interface with tabs for different extraction methods
- **Dashboard** (`/dashboard`): Statistics and history of extractions

## Development

### Adding New Components

1. Create a new component in the appropriate directory
2. Import and use the component in your pages or other components

### Adding New Pages

1. Create a new page in the `src/app` directory
2. Use the `MainLayout` component to maintain consistent layout

### Styling

The project uses Tailwind CSS for styling. Customize the theme in `tailwind.config.js`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
