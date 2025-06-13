# ECG Compression Challenge - Complete Local System

A complete local implementation of the ECG Compression Challenge with frontend web interface and backend API server.

## 🚀 Quick Start

### One-Command Setup

```bash
python setup_complete_system.py
```

This will:
- ✅ Install all dependencies
- ✅ Start the backend API server (port 8000)
- ✅ Start the frontend web server (port 3000)
- ✅ Open your browser to the application

### Manual Setup

If you prefer to set up components individually:

1. **Install Backend Dependencies**:
   ```bash
   cd mini-backend
   pip install -r requirements.txt
   ```

2. **Start Backend**:
   ```bash
   cd mini-backend
   python start_backend.py
   ```

3. **Start Frontend** (in a new terminal):
   ```bash
   python -m http.server 3000
   ```

4. **Open Browser**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## 📁 Project Structure

```
ecg-compression/
├── 📄 index.html                    # Main web interface
├── 📄 scripts.js                    # Frontend JavaScript (updated for local backend)
├── 📄 styles.css                    # Frontend styles
├── 📄 setup_complete_system.py      # One-command setup script
├── 📄 README.md                     # This file
├── 📁 mini-backend/                 # Backend API server
│   ├── 📄 main.py                   # FastAPI application
│   ├── 📄 evaluate.py               # Submission evaluation
│   ├── 📄 storage.py                # Data storage manager
│   ├── 📄 start_backend.py          # Backend startup script
│   ├── 📄 requirements.txt          # Python dependencies
│   └── 📄 README.md                 # Backend documentation
└── 📁 codabench_bundle/             # Original Codabench files
    ├── 📄 ingestion.py              # Codabench ingestion program
    ├── 📄 scoring.py                # Codabench scoring program
    ├── 📄 ecg_model.py              # Example ECG model
    ├── 📄 solve.py                  # Example solution
    └── 📄 competition.yaml          # Competition configuration
```

## 🌟 Features

### Frontend (Web Interface)
- 🎨 **Modern UI**: Clean, responsive design
- 👥 **User Management**: Registration and login
- 📤 **File Upload**: Submit algorithm ZIP files
- 🏆 **Leaderboard**: Real-time rankings
- 📊 **Submission History**: Track your submissions
- 📱 **Mobile Friendly**: Works on all devices

### Backend (API Server)
- ⚡ **FastAPI**: Modern, fast web framework
- 🔄 **Async Processing**: Background evaluation tasks
- 💾 **Data Storage**: JSON/CSV-based persistence
- 🔐 **Authentication**: User registration and login
- 📊 **Scoring Integration**: Uses original Codabench scoring
- 📖 **API Documentation**: Auto-generated docs at `/docs`

### Evaluation System
- 📁 **File Validation**: Checks file format and size
- 🔍 **Algorithm Extraction**: Handles ZIP files
- 🧮 **Scoring**: Uses original Codabench scoring program
- 📈 **Metrics**: Compression ratio, reconstruction error, etc.
- 🏆 **Ranking**: Automatic leaderboard updates

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - Register new team
- `POST /api/login` - User login

### Submissions
- `POST /api/submit-to-codabench` - Submit algorithm
- `GET /api/submission-status/{id}` - Check submission status
- `GET /api/user-submissions/{team}` - Get user submissions

### Leaderboard
- `GET /api/leaderboard` - Get current rankings

### System
- `GET /health` - Health check

## 💾 Data Storage

The system stores data locally in JSON files:

```
mini-backend/data/
├── submissions.json     # All submissions
├── leaderboard.json     # Current rankings
├── users.json          # User accounts
└── submissions.csv     # Submissions in CSV format
```

## 🔄 Evaluation Process

1. **Upload**: User submits algorithm file (ZIP)
2. **Validation**: File format and size checks
3. **Queue**: Submission queued for processing
4. **Extract**: ZIP file extracted to temporary directory
5. **Score**: Original Codabench scoring program runs
6. **Results**: Leaderboard and history updated
7. **Notify**: User sees results in real-time

## 🛠️ Development

### Frontend Development
- Edit `scripts.js` for functionality changes
- Edit `styles.css` for styling changes
- Edit `index.html` for structure changes
- Refresh browser to see changes

### Backend Development
- Backend runs with auto-reload enabled
- Edit Python files in `mini-backend/`
- Changes automatically restart the server
- View logs in the terminal

### Testing
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Submission Format

Your algorithm submission should be a ZIP file containing:

```
algorithm.zip
├── solve.py              # Main algorithm file
├── requirements.txt      # Dependencies (optional)
└── other_files/          # Additional files (optional)
```

The `solve.py` file should implement your ECG compression algorithm according to the Codabench specifications.

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process using port 8000
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Dependencies Not Installing**
   ```bash
   # Upgrade pip first
   python -m pip install --upgrade pip
   cd mini-backend
   pip install -r requirements.txt
   ```

3. **Frontend Not Loading**
   - Check if port 3000 is available
   - Try a different port: `python -m http.server 8080`

4. **Backend Errors**
   - Check the terminal for error messages
   - Verify all files in `codabench_bundle/` exist
   - Check `mini-backend/data/` directory permissions

### Logs and Debugging

- **Backend logs**: Displayed in the terminal running the backend
- **Frontend logs**: Browser developer console (F12)
- **API testing**: Use the Swagger UI at http://localhost:8000/docs

## 🚀 Production Deployment

For production use:

1. **Use a production ASGI server**:
   ```bash
   pip install gunicorn
   gunicorn mini-backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Use a proper database**:
   - Replace JSON storage with PostgreSQL/MySQL
   - Update `storage.py` accordingly

3. **Add security**:
   - Use proper password hashing
   - Implement JWT tokens
   - Add rate limiting
   - Configure CORS properly

4. **Use a reverse proxy**:
   - Nginx or Apache for static files
   - SSL/TLS termination

## 📝 License

This project is part of the ECG Compression Challenge and follows the same license terms as the original Codabench competition.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you encounter issues:

1. Check this README and the troubleshooting section
2. Review the backend README at `mini-backend/README.md`
3. Check the API documentation at http://localhost:8000/docs
4. Look at the browser console for frontend errors
5. Check the terminal output for backend errors

---

**Happy coding! 🏥💻**