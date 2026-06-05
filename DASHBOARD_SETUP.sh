#!/bin/bash

# Dashboard Setup Script for CIO Briefing System

echo "🚀 Setting up Streamlit Dashboard..."
echo ""

cd /Users/patriciobravoknobloch/cio-briefing

# Install dependencies
echo "📦 Installing Streamlit & Plotly..."
python3 -m pip install --upgrade streamlit plotly 2>&1 | grep -v "WARNING"

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 To run your dashboard:"
echo ""
echo "   streamlit run dashboard.py"
echo ""
echo "   Then open your browser to: http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Or for quick setup, just copy-paste this:"
echo "   cd /Users/patriciobravoknobloch/cio-briefing && streamlit run dashboard.py"
echo ""
