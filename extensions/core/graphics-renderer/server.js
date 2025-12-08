/**
 * uDOS Graphics Renderer Service
 * Version: 1.2.15
 * Port: 5555
 * 
 * Node.js service providing rendering for 5 graphics formats:
 * - ASCII (direct pass-through)
 * - Teletext (8-color rendering)
 * - SVG (AI-assisted generation)
 * - Sequence (js-sequence-diagrams)
 * - Flow (flowchart.js)
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');

// Import renderers
const asciiRenderer = require('./renderers/ascii');
const teletextRenderer = require('./renderers/teletext');
const svgRenderer = require('./renderers/svg');
const sequenceRenderer = require('./renderers/sequence');
const flowRenderer = require('./renderers/flow');

const app = express();
const PORT = process.env.GRAPHICS_PORT || 5555;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    version: '1.2.15',
    service: 'uDOS Graphics Renderer',
    formats: ['ascii', 'teletext', 'svg', 'sequence', 'flow'],
    port: PORT,
    uptime: process.uptime()
  });
});

// Format-specific rendering endpoints
app.post('/render/ascii', async (req, res) => {
  try {
    const { template, data, options } = req.body;
    const result = await asciiRenderer.render(template, data, options);
    res.json({ success: true, output: result });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message,
      format: 'ascii'
    });
  }
});

app.post('/render/teletext', async (req, res) => {
  try {
    const { content, palette, options } = req.body;
    const result = await teletextRenderer.render(content, palette, options);
    res.json({ success: true, output: result });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message,
      format: 'teletext'
    });
  }
});

app.post('/render/svg', async (req, res) => {
  try {
    const { description, style, options } = req.body;
    const result = await svgRenderer.render(description, style, options);
    res.json({ success: true, output: result });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message,
      format: 'svg'
    });
  }
});

app.post('/render/sequence', async (req, res) => {
  try {
    const { source, options } = req.body;
    const result = await sequenceRenderer.render(source, options);
    res.json({ success: true, output: result, format: 'svg' });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message,
      format: 'sequence'
    });
  }
});

app.post('/render/flow', async (req, res) => {
  try {
    const { source, options } = req.body;
    const result = await flowRenderer.render(source, options);
    res.json({ success: true, output: result, format: 'svg' });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message,
      format: 'flow'
    });
  }
});

// Template listing endpoints
app.get('/templates/:format', (req, res) => {
  const { format } = req.params;
  const fs = require('fs');
  const basePath = path.join(__dirname, '../../../core/data/diagrams', format);
  
  try {
    const files = fs.readdirSync(basePath);
    const templates = files.filter(f => f.endsWith('.txt') || f.endsWith('.json'));
    res.json({ success: true, format, templates });
  } catch (error) {
    res.status(404).json({ 
      success: false, 
      error: 'Format not found or no templates available',
      format
    });
  }
});

// Unified render endpoint (auto-detects format)
app.post('/render', async (req, res) => {
  try {
    const { format, ...params } = req.body;
    
    let result;
    switch (format) {
      case 'ascii':
        result = await asciiRenderer.render(params.template, params.data, params.options);
        break;
      case 'teletext':
        result = await teletextRenderer.render(params.content, params.palette, params.options);
        break;
      case 'svg':
        result = await svgRenderer.render(params.description, params.style, params.options);
        break;
      case 'sequence':
        result = await sequenceRenderer.render(params.source, params.options);
        break;
      case 'flow':
        result = await flowRenderer.render(params.source, params.options);
        break;
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
    
    res.json({ success: true, format, output: result });
  } catch (error) {
    res.status(400).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Error handling
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error',
    message: err.message 
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ uDOS Graphics Renderer v1.2.15 running on port ${PORT}`);
  console.log(`📊 Formats: ASCII, Teletext, SVG, Sequence, Flow`);
  console.log(`🔗 Health check: http://localhost:${PORT}/health`);
});

module.exports = app;
