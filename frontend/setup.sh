#!/bin/bash

echo "🚀 Setting up Shift-Left Compliance Dashboard..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Check if database exists
if [ ! -f "../compliance_memory.db" ]; then
    echo "⚠️  Warning: compliance_memory.db not found in parent directory"
    echo "   The application will create it automatically if it doesn't exist."
else
    echo "✅ Database found: ../compliance_memory.db"
fi

echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Next steps:"
echo "   1. Run 'npm run dev' to start the development server"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Check the README.md for more information"
echo ""
echo "Happy coding! 🚀"

