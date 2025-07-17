// Simple test to check if React app is responsive
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/',
  method: 'GET',
  timeout: 5000
};

console.log('🧪 Testing React Frontend...');

const req = http.request(options, (res) => {
  console.log(`✅ React app is running - Status: ${res.statusCode}`);
  console.log(`📄 Content-Type: ${res.headers['content-type']}`);
  
  if (res.statusCode === 200) {
    console.log('🎉 Frontend is working correctly!');
    console.log('🌐 Access at: http://localhost:3000');
  } else {
    console.log('⚠️  Frontend returned non-200 status');
  }
  
  process.exit(0);
});

req.on('error', (err) => {
  console.log('❌ Frontend test failed:', err.message);
  console.log('💡 Make sure React app is running with: npm start');
  process.exit(1);
});

req.on('timeout', () => {
  console.log('⏱️  Request timed out');
  console.log('💡 Frontend might be starting up, try again in a moment');
  process.exit(1);
});

req.end();