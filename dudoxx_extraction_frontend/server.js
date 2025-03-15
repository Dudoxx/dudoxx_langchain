/**
 * Dudoxx Extraction Frontend Server
 * 
 * This server provides a web interface for the Dudoxx Extraction API.
 * It handles authentication, session management, and proxies requests to the API.
 */

require('dotenv').config();
const express = require('express');
const session = require('express-session');
const flash = require('connect-flash');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const axios = require('axios');
const multer = require('multer');
const fs = require('fs');
const expressLayouts = require('express-ejs-layouts');

// Create Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Configuration
const PORT = process.env.PORT || 3000;
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
const SESSION_SECRET = process.env.SESSION_SECRET || 'dudoxx-extraction-secret';

// Set up temporary file storage for uploads
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));
app.use(flash());

// Set up EJS as the view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Set up EJS layouts
app.use(expressLayouts);
app.set('layout', 'layout');
app.set('layout extractScripts', true);
app.set('layout extractStyles', true);

// Serve static files
app.use('/static', express.static(path.join(__dirname, 'public')));
app.use('/bootstrap', express.static(path.join(__dirname, 'node_modules/bootstrap/dist')));

// Authentication middleware
const isAuthenticated = (req, res, next) => {
  if (req.session.apiKey) {
    return next();
  }
  req.flash('error', 'Please log in with your API key');
  res.redirect('/login');
};

// Socket.io connection
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Routes
app.get('/', (req, res) => {
  res.redirect('/dashboard');
});

app.get('/login', (req, res) => {
  res.render('login', { 
    error: req.flash('error'),
    success: req.flash('success')
  });
});

app.post('/login', async (req, res) => {
  const apiKey = req.body.apiKey;
  
  if (!apiKey) {
    req.flash('error', 'API key is required');
    return res.redirect('/login');
  }
  
  try {
    // Verify API key with a test request to Dudoxx API
    const response = await axios.get(`${API_BASE_URL}/health`, {
      headers: { 'X-API-Key': apiKey }
    });
    
    if (response.status === 200) {
      req.session.apiKey = apiKey;
      req.flash('success', 'Successfully logged in');
      res.redirect('/dashboard');
    } else {
      req.flash('error', 'Invalid API key');
      res.redirect('/login');
    }
  } catch (error) {
    console.error('Login error:', error.message);
    req.flash('error', 'Invalid API key or API server is not available');
    res.redirect('/login');
  }
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/login');
});

app.get('/dashboard', isAuthenticated, (req, res) => {
  res.render('dashboard', {
    user: { apiKey: req.session.apiKey }
  });
});

app.get('/extract', isAuthenticated, (req, res) => {
  res.render('extract', {
    user: { apiKey: req.session.apiKey },
    socketId: null,
    type: req.query.type || 'text'
  });
});

// API proxy routes
app.post('/api/extract/text', isAuthenticated, async (req, res) => {
  try {
    const { text, query, domain, useParallel, outputFormats } = req.body;
    
    // Emit progress updates
    io.emit('progress', { status: 'starting', message: 'Starting extraction...' });
    
    // Forward request to Dudoxx API
    const response = await axios.post(`${API_BASE_URL}/extract/text`, {
      text,
      query,
      domain: domain || undefined,
      output_formats: outputFormats || ['json', 'text']
    }, {
      headers: { 'X-API-Key': req.session.apiKey },
      params: { use_parallel: useParallel === 'true' }
    });
    
    io.emit('progress', { status: 'completed', message: 'Extraction completed' });
    res.json(response.data);
  } catch (error) {
    console.error('Text extraction error:', error.message);
    io.emit('progress', { status: 'error', message: 'Extraction failed' });
    res.status(500).json({ 
      error: error.message,
      details: error.response?.data || 'Unknown error'
    });
  }
});

app.post('/api/extract/file', isAuthenticated, upload.single('file'), async (req, res) => {
  try {
    const { query, domain, useParallel, outputFormats } = req.body;
    const filePath = req.file.path;
    
    // Emit progress updates
    io.emit('progress', { status: 'starting', message: 'Starting extraction...' });
    
    // Create form data for file upload
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('query', query);
    if (domain) formData.append('domain', domain);
    if (outputFormats) formData.append('output_formats', outputFormats);
    formData.append('use_parallel', useParallel === 'true');
    
    // Forward request to Dudoxx API
    const response = await axios.post(`${API_BASE_URL}/extract/file`, formData, {
      headers: { 
        'X-API-Key': req.session.apiKey,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // Clean up temporary file
    fs.unlinkSync(filePath);
    
    io.emit('progress', { status: 'completed', message: 'Extraction completed' });
    res.json(response.data);
  } catch (error) {
    console.error('File extraction error:', error.message);
    
    // Clean up temporary file if it exists
    if (req.file && req.file.path) {
      fs.unlinkSync(req.file.path);
    }
    
    io.emit('progress', { status: 'error', message: 'Extraction failed' });
    res.status(500).json({ 
      error: error.message,
      details: error.response?.data || 'Unknown error'
    });
  }
});

app.post('/api/extract/multi-query', isAuthenticated, async (req, res) => {
  try {
    const { text, queries, domain, useParallel, outputFormats } = req.body;
    
    // Emit progress updates
    io.emit('progress', { status: 'starting', message: 'Starting multi-query extraction...' });
    
    // Forward request to Dudoxx API
    const response = await axios.post(`${API_BASE_URL}/extract/multi-query`, {
      text,
      queries,
      domain: domain || undefined,
      output_formats: outputFormats || ['json', 'text']
    }, {
      headers: { 'X-API-Key': req.session.apiKey },
      params: { use_parallel: useParallel === 'true' }
    });
    
    io.emit('progress', { status: 'completed', message: 'Multi-query extraction completed' });
    res.json(response.data);
  } catch (error) {
    console.error('Multi-query extraction error:', error.message);
    io.emit('progress', { status: 'error', message: 'Extraction failed' });
    res.status(500).json({ 
      error: error.message,
      details: error.response?.data || 'Unknown error'
    });
  }
});

app.post('/api/extract/document', isAuthenticated, upload.single('file'), async (req, res) => {
  try {
    const { domain, outputFormats } = req.body;
    const filePath = req.file.path;
    
    // Emit progress updates
    io.emit('progress', { status: 'starting', message: 'Starting document extraction...' });
    
    // Create form data for file upload
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('domain', domain);
    if (outputFormats) formData.append('output_formats', outputFormats);
    
    // Forward request to Dudoxx API
    const response = await axios.post(`${API_BASE_URL}/extract/document`, formData, {
      headers: { 
        'X-API-Key': req.session.apiKey,
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // Clean up temporary file
    fs.unlinkSync(filePath);
    
    io.emit('progress', { status: 'completed', message: 'Document extraction completed' });
    res.json(response.data);
  } catch (error) {
    console.error('Document extraction error:', error.message);
    
    // Clean up temporary file if it exists
    if (req.file && req.file.path) {
      fs.unlinkSync(req.file.path);
    }
    
    io.emit('progress', { status: 'error', message: 'Extraction failed' });
    res.status(500).json({ 
      error: error.message,
      details: error.response?.data || 'Unknown error'
    });
  }
});

// Results page
app.get('/results', isAuthenticated, (req, res) => {
  res.render('results', {
    user: { apiKey: req.session.apiKey },
    result: req.session.lastResult || null
  });
});

app.post('/results/save', isAuthenticated, (req, res) => {
  req.session.lastResult = req.body;
  res.json({ success: true });
});

// Error handling
app.use((req, res, next) => {
  res.status(404).render('error', {
    error: {
      status: 404,
      message: 'Page not found'
    }
  });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).render('error', {
    error: {
      status: 500,
      message: 'Internal server error',
      details: err.message
    }
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`Dudoxx Extraction Frontend running on http://localhost:${PORT}`);
});
