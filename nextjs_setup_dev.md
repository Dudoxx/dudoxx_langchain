**# Next.js 15 Development Setup Guide for Dudoxx Recorder

This guide provides step-by-step instructions for setting up and developing the Dudoxx Recorder application using Next.js 15, TypeScript, Tailwind CSS, and Shadcn UI.

## Project Initialization

### Prerequisites
- Node.js 18.17 or later
- npm, yarn, or pnpm

### Creating a New Next.js 15 Project

```bash
npx create-next-app@latest dudoxx_extraction_nextjs \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --turbopack \
  --import-alias "@/*" \
  --use-npm
```

This command sets up a Next.js 15 project with:
- TypeScript support
- Tailwind CSS configuration
- ESLint for code quality
- App Router architecture
- src directory structure
- Turbopack for enhanced development experience
- Import alias for cleaner imports
- npm as the package manager

## Shadcn UI Integration

After creating the project, navigate to the project directory and install Shadcn UI:

```bash
cd dudoxx_extraction_nextjs
npx shadcn@latest init --base-color zinc --yes --force
```

This command initializes Shadcn UI with:
- Base color: Zinc
- Skips confirmation prompts
- Forces installation despite peer dependency issues
- Overwrites existing configuration

During the initialization, you may be prompted with:

```
It looks like you are using React 19.
Some packages may fail to install due to peer dependency issues in npm (see https://ui.shadcn.com/react-19).

? How would you like to proceed? › - Use arrow-keys. Return to submit.
❯   Use --force
    Use --legacy-peer-deps
```

Select `Use --force` to proceed.

Install the required UI components:

```bash
npx shadcn@latest add button card dropdown-menu select slider toggle sonner
```

During the installation, you may be prompted with:

```
It looks like you are using React 19.
Some packages may fail to install due to peer dependency issues in npm (see https://ui.shadcn.com/react-19).

? How would you like to proceed? › - Use arrow-keys. Return to submit.
❯   Use --force
    Use --legacy-peer-deps
```

Select `Use --force` to proceed.

## Environment Variables Setup

Create a `.env.local` file in the project root to store your Deepgram API key:

```bash
touch .env.local
```

Add the following content to the file:

```
add content from .env.dudoxx
```

## Project Structure

The project follows this structure:

```
dudoxx_extraction_nextjs/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── deepgram/
│   │   │       └── route.ts        # Server-side API route for Deepgram
│   │   ├── [locale]/               # Locale-based routing (en, fr)
│   │   │   └── page.tsx            # Main application page
│   │   ├── globals.css             # Global styles
│   │   └── layout.tsx              # Root layout
│   ├── components/
│   │   ├── ui/                     # Shadcn UI components
│   │   ├── recorder/
│   │   │   ├── audio-recorder.tsx  # Main recorder component
│   │   │   ├── audio-visualizer.tsx # Audio visualization
│   │   │   ├── controls.tsx        # Recording controls
│   │   │   └── audio-player.tsx    # Playback component
│   │   ├── transcription/
│   │   │   ├── transcription-display.tsx # Display transcribed text
│   │   │   └── language-selector.tsx     # Language switching
│   │   └── layout/                 # Layout components
│   ├── hooks/
│   │   ├── use-audio-recorder.ts   # Audio recording hook
│   │   ├── use-transcription.ts    # Transcription hook
│   │   └── use-language.ts         # Language switching hook
│   ├── lib/
│   │   ├── deepgram.ts             # Deepgram API utilities
│   │   └── utils.ts                # Helper functions
│   └── types/
│       └── index.ts                # TypeScript type definitions
├── public/
├── .env.local                      # Environment variables
├── next.config.js                  # Next.js configuration
├── tailwind.config.js              # Tailwind CSS configuration
├── tsconfig.json                   # TypeScript configuration
└── package.json                    # Project dependencies
```

## Audio Recording Implementation

The audio recording system uses the browser-native MediaRecorder API:

1. Install required dependencies:
```bash
npm install react-use
```

2. Create a custom hook for audio recording in `src/hooks/use-audio-recorder.ts`
3. Implement the audio visualization component in `src/components/recorder/audio-visualizer.tsx`
4. Create recording controls in `src/components/recorder/controls.tsx`

## Deepgram Integration

For real-time speech-to-text transcription:

1. Install the Deepgram SDK:
```bash
npm install @deepgram/sdk
```

2. Create the Deepgram API route in `src/app/api/deepgram/route.ts`
3. Implement the transcription hook in `src/hooks/use-transcription.ts`
4. Create the language switching mechanism in `src/hooks/use-language.ts`

## Running the Development Server

Start the development server:

```bash
npm run dev
```

The application will be available at http://localhost:3000

## Building for Production

Build the application for production:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Shadcn UI Documentation](https://ui.shadcn.com/docs)
- [Deepgram Documentation](https://developers.deepgram.com/docs)
- [MediaRecorder API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
**