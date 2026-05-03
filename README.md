# 🚗 Road Accident Prediction and Severity Classification System

An AI-powered web application that predicts road accident severity based on various risk factors using machine learning.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Test Cases](#test-cases)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- 🔐 **User Authentication** - Secure registration and login with JWT
- 🤖 **AI-Powered Prediction** - Severity classification (Low/Medium/High)
- 📊 **Interactive Dashboard** - Real-time statistics and analytics
- 💡 **Safety Recommendations** - Actionable safety tips based on risk level
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🗄️ **Prediction History** - Track all past predictions
- 🎨 **Modern UI** - Beautiful, high-visibility interface

## 🛠️ Tech Stack

### Backend
- **Python 3.11** - Core programming language
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database (can be switched to PostgreSQL)
- **JWT** - Authentication
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript (ES6+)** - Interactive features
- **Chart.js** - Data visualization
- **Font Awesome** - Icons

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/road-accident-prediction.git
cd road-accident-prediction/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python app.py