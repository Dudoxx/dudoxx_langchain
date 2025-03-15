# Server-Sent Events (SSE) Implementation

This document explains the changes made to replace Socket.IO with Server-Sent Events (SSE) for real-time progress updates in the Dudoxx Extraction system.

## Overview

The Dudoxx Extraction system now uses Server-Sent Events (SSE) instead of Socket.IO for real-time progress updates. This simplifies the architecture by:

1. Eliminating the need for a separate Socket.IO server
2. Using a standard web technology (SSE) that is built into browsers
3. Reducing dependencies and complexity
4. Providing a more direct connection between extraction requests and progress updates

## Key Changes

### Backend (API)

1. **New Progress Manager**: Added `progress_manager.py` to handle SSE connections and progress updates
2. **Request IDs**: Each extraction request now returns a unique `request_id` that is used to track progress
3. **SSE Endpoint**: Added `/api/v1/progress/{request_id}` endpoint for SSE connections
4. **Removed Socket.IO**: Removed Socket.IO server and related code
5. **Updated Requirements**: Added `sse-starlette` dependency and removed Socket.IO dependencies

### Frontend (Next.js)

1. **New SSE Client**: Added `sse.ts` to replace `socket.ts` for SSE connections
2. **Updated Components**: Updated extraction form components to use the new SSE client
3. **Request ID Handling**: Components now store the `request_id` from API responses and use it to subscribe to progress updates

## How It Works

1. When a user submits an extraction request, the API generates a unique `request_id` and returns it in the response
2. The frontend uses this `request_id` to establish an SSE connection to `/api/v1/progress/{request_id}`
3. As the extraction progresses, the API sends progress updates through the SSE connection
4. The frontend receives these updates and displays them to the user
5. When the extraction is complete, the API sends a final "completed" update

## Benefits

- **Simplified Architecture**: No need for a separate Socket.IO server
- **Reduced Dependencies**: Fewer dependencies to manage
- **Direct Connection**: Progress updates are directly linked to specific requests
- **Standard Technology**: SSE is a standard web technology supported by all modern browsers
- **Better Error Handling**: More robust error handling and recovery
- **Improved Performance**: Lower overhead and better scalability

## Usage

### Running the API Server

```bash
# Install dependencies
./install_dependencies.sh

# Run the API server
./run_servers.sh
```

### Connecting to Progress Updates (Frontend)

```typescript
import { subscribeToProgress } from '@/lib/sse';

// When you receive a request_id from an API response
const requestId = response.request_id;

// Subscribe to progress updates
const unsubscribe = subscribeToProgress(requestId, (data) => {
  console.log('Progress update:', data);
  // Update UI with progress information
});

// Unsubscribe when done
unsubscribe();
```

## Troubleshooting

- If you encounter CORS issues, make sure the API server has CORS properly configured
- If progress updates are not being received, check the browser console for connection errors
- If the API server fails to start, make sure all dependencies are installed correctly
