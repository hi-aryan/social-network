from dotenv import load_dotenv
import os

load_dotenv()

from flasknetwork import create_app

app = create_app()

# if file is run directly only
if __name__ == '__main__':
    print(f"SECRET_KEY is set: {app.config.get('SECRET_KEY') is not None}")
    app.run(debug=True, port=8000)