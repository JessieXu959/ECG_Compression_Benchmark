# ECG Compression Challenge - Mini Backend

A lightweight FastAPI backend for the ECG Compression Challenge that handles submissions, evaluation, and leaderboard management.

## Features

- 🚀 **FastAPI Backend**: Modern, fast web framework
- 📁 **File Upload**: Handle algorithm submissions (ZIP files)
- 🔄 **Async Evaluation**: Background processing of submissions
- 🏆 **Leaderboard**: Real-time ranking system
- 💾 **Data Storage**: JSON/CSV-based persistence
- 🔐 **User Management**: Registration and authentication
- 📊 **Scoring Integration**: Uses Codabench scoring programs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
python start_backend.py
```

The server will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/register` - Register new user/team
- `POST /api/login` - User login

### Submissions
- `POST /api/submit-to-codabench` - Submit algorithm for evaluation
- `GET /api/submission-status/{submission_id}` - Check submission status
- `GET /api/user-submissions/{team_name}` - Get user's submissions

### Leaderboard
- `GET /api/leaderboard` - Get current leaderboard

### Health
- `GET /health` - Health check endpoint

## Directory Structure

```
mini-backend/
├── main.py              # FastAPI application
├── evaluate.py          # Evaluation module
├── storage.py           # Data storage manager
├── requirements.txt     # Python dependencies
├── start_backend.py     # Startup script
├── README.md           # This file
├── data/               # Data storage (created automatically)
├── uploads/            # Uploaded files (created automatically)
├── temp/               # Temporary files (created automatically)
└── scoring/            # Scoring workspace (created automatically)
```

## Configuration

The backend uses the following default settings:
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8000
- **Data Storage**: JSON files in `data/` directory
- **File Uploads**: Stored in `uploads/` directory

## Data Storage

The backend stores data in JSON files:
- `data/submissions.json` - All submissions
- `data/leaderboard.json` - Current leaderboard
- `data/users.json` - User accounts
- `data/submissions.csv` - Submissions in CSV format

## Evaluation Process

1. **File Upload**: User submits algorithm file (ZIP)
2. **Validation**: File is validated for format and size
3. **Queue**: Submission is queued for evaluation
4. **Processing**: Background task extracts and evaluates submission
5. **Scoring**: Uses Codabench scoring program
6. **Results**: Updates leaderboard and user history

## Development

### Running in Development Mode

The backend runs with auto-reload enabled by default. Any changes to the code will automatically restart the server.

### Testing the API

You can test the API using:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **curl** or **Postman** for direct API calls

### Example API Calls

#### Register a User
```bash
curl -X POST "http://localhost:8000/api/register" \
     -H "Content-Type: application/json" \
     -d '{"team_name": "MyTeam", "email": "team@example.com", "password": "mypassword"}'
```

#### Submit Algorithm
```bash
curl -X POST "http://localhost:8000/api/submit-to-codabench" \
     -F "algorithm_name=MyAlgorithm" \
     -F "team_name=MyTeam" \
     -F "file=@algorithm.zip"
```

#### Get Leaderboard
```bash
curl "http://localhost:8000/api/leaderboard"
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in `start_backend.py` or kill the process using port 8000

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`

3. **File Upload Errors**
   - Check file size (max 100MB)
   - Ensure file format is supported (.zip, .py, .tar.gz)

4. **Evaluation Failures**
   - Check that Codabench bundle files are present in `../codabench_bundle/`
   - Verify scoring.py is working correctly

### Logs

The backend logs are displayed in the console. For production deployment, consider using proper logging configuration.

## Production Deployment

For production deployment:

1. **Use a Production ASGI Server**:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set Environment Variables**:
   - Configure database connection
   - Set secret keys for authentication
   - Configure CORS origins

3. **Use a Reverse Proxy**:
   - Nginx or Apache for serving static files
   - SSL/TLS termination

4. **Database**:
   - Replace JSON storage with PostgreSQL/MySQL
   - Use Redis for caching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the ECG Compression Challenge and follows the same license terms.