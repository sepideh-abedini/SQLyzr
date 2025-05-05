import os
from src.web.server import app

if __name__ == '__main__':
    # Create the static directories if they don't exist
    os.makedirs('src/web/static', exist_ok=True)
    os.makedirs('src/web/static/vue', exist_ok=True)

    print("SQLyzr Web UI is running at http://localhost:5000")
    print("API endpoints are available at http://localhost:5000/api/")

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
