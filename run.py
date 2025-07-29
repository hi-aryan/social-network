from flasknetwork import create_app

app = create_app()

# if file is run directly only
if __name__ == '__main__':
    app.run(debug=True)