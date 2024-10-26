from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from langchain_google_genai import GoogleGenerativeAI
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# In-memory store for user sessions
user_data = {}

# Folder where generated files will be stored
GENERATED_FOLDER = "generated_sites"

if not os.path.exists(GENERATED_FOLDER):
    os.makedirs(GENERATED_FOLDER)

# Existing user website template path
USER_WEBSITE_TEMPLATE = os.path.join(app.root_path, 'templates', 'userwebsite.html')

# Phase 1 suggestions
website_types = ["Portfolio/CV", "Business", "Blog", "Webstore", "Landing Page"]
# Phase 2 color palette options
color_palettes = ["Dark-Mode", "Light-Mode "]
# Phase 3 functionality options
functionality_options = ["Red", "Green", "Blue", "Orange", "purple"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    logger.info("Received a POST request to /chat")
    user_input = request.json.get("message")
    user_id = request.json.get("user_id")

    # Log the received input
    logger.debug(f"Received input from user {user_id}: {user_input}")

    # Initialize session for new user
    if user_id not in user_data:
        logger.debug(f"Initializing session for new user: {user_id}")
        user_data[user_id] = {"phase": 1, "responses": {}}
    else:
        logger.debug(f"User {user_id} already exists. Current phase: {user_data[user_id]['phase']}")

    phase = user_data[user_id]["phase"]
    logger.debug(f"Current phase for user {user_id}: {phase}")

    if phase == 1:
        user_data[user_id]["responses"]["website_type"] = user_input
        user_data[user_id]["phase"] = 2
        logger.info(f"Phase 1 completed. User {user_id} selected website type: {user_input}")
        return jsonify({
            "message": "Please select the background theme of your website.",
            "suggestions": color_palettes,
            "nextStep": 2
        })

    elif phase == 2:
        user_data[user_id]["responses"]["color_palette"] = user_input
        user_data[user_id]["phase"] = 3
        logger.info(f"Phase 2 completed. User {user_id} selected color palette: {user_input}")
        return jsonify({
            "message": "Please select the main colour of your website.",
            "suggestions": functionality_options,
            "nextStep": 3
        })

    elif phase == 3:
        user_data[user_id]["responses"]["functionality"] = user_input
        user_data[user_id]["phase"] = 4
        logger.info(f"Phase 3 completed. User {user_id} selected functionality: {user_input}")
        return jsonify({
            "message": "Is there any additional information you'd like to add about your website?",
            "phase": 4,
            "nextStep": 4
        })

    elif phase == 4:
        user_data[user_id]["responses"]["additional_info"] = user_input
        response_summary = user_data[user_id]["responses"]
        logger.info(f"Phase 4 completed. User {user_id} provided additional info: {user_input}")

        # Generate the website
        website_title = f"{response_summary['website_type']} Website"
        website_description = f"A {response_summary['color_palette']} {response_summary['website_type']} website with {response_summary['functionality']} functionality. {response_summary['additional_info']}"
        logger.debug(f"Generating website with title: {website_title} and description: {website_description}")

        generated_files = generate_website_files(website_title, website_description)
        if generated_files:
            populate_user_website(generated_files)
            logger.info(f"Website generated successfully for user {user_id}.")
        else:
            logger.error("There was an error generating the website.")
            return jsonify({"message": "There was an error generating the website."}), 500

        # Reset the user data after completion
        user_data.pop(user_id, None)
        logger.debug(f"User data for {user_id} has been reset after website generation.")

        return jsonify({
            "message": "Your website has been generated! You can view it using the following link: https://thuto-chat.azurewebsites.net/view_website",
            "link": "/view_website",
            "phase": 5
        })

def generate_website_files(website_title, website_description):
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=api_key)
    prompt = f"""
    Generate a simple website with HTML and CSS:
    - Title: "{website_title}"
    - Description: "{website_description}"

    Provide the output as a JSON object with two fields:
    1. 'html': The HTML content of the webpage.
    2. 'css': The CSS content for styling the webpage.
    """

    response = llm.invoke(prompt)
    try:
        print("Response: ", response)
        json_response = json.loads(response)
        return {
            "html": json_response.get("html"),
            "css": json_response.get("css")
        }
    except json.JSONDecodeError as e:
        print(f"Error: Unable to parse JSON response. Details: {str(e)}")
        return None

def populate_user_website(generated_files):
    # Populate the 'userwebsite.html' file with the generated HTML and CSS content
    html_content = generated_files.get("html", "<h1>Error generating HTML content</h1>")
    css_content = generated_files.get("css", "body { font-family: Arial; }")
    
    # Write HTML to userwebsite.html
    with open(USER_WEBSITE_TEMPLATE, 'w') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Generated Website</title>
    <style>{css_content}</style>
</head>
<body>
    {html_content}
</body>
</html>
        """)

@app.route('/view_website')
def view_website():
    # Render the user-generated website from the 'userwebsite.html' file
    return render_template('userwebsite.html')

def create_flask_app(website_title, generated_files):
    logger.info(f"Creating Flask app for {website_title}")
    logger.debug(f"Keys in generated_files: {generated_files.keys()}")
    
    app_dir = os.path.join('generated_sites', website_title)
    os.makedirs(app_dir, exist_ok=True)
    logger.debug(f"Created directory: {app_dir}")

    # Create the templates directory if it doesn't exist
    os.makedirs(os.path.join(app_dir, 'templates'), exist_ok=True)
    logger.debug(f"Created templates directory: {os.path.join(app_dir, 'templates')}")
    
    # Write the index.html file
    if 'templates/index.html' in generated_files:
        with open(os.path.join(app_dir, 'templates', 'index.html'), 'w') as f:
            f.write(generated_files['templates/index.html'])
        logger.info("Successfully wrote index.html")
    else:
        logger.warning("'templates/index.html' not found in generated_files")
        # You might want to handle this error case appropriately
        # For example, you could create a default index.html content
        with open(os.path.join(app_dir, 'templates', 'index.html'), 'w') as f:
            f.write("<html><body><h1>Default Page</h1><p>Content not generated.</p></body></html>")
        logger.info("Wrote default index.html")
    
    # Write the app.py file
    if 'app.py' in generated_files:
        with open(os.path.join(app_dir, 'app.py'), 'w') as f:
            f.write(generated_files['app.py'])
        logger.info("Successfully wrote app.py")
    else:
        logger.warning("'app.py' not found in generated_files")
    
    # Create the static directory and write the style.css file
    if 'static/style.css' in generated_files:
        os.makedirs(os.path.join(app_dir, 'static'), exist_ok=True)
        with open(os.path.join(app_dir, 'static', 'style.css'), 'w') as f:
            f.write(generated_files['static/style.css'])
        logger.info("Successfully wrote style.css")
    else:
        logger.warning("'static/style.css' not found in generated_files")
        # You might want to handle this error case appropriately
        # For example, you could create a default style.css content
        os.makedirs(os.path.join(app_dir, 'static'), exist_ok=True)
        with open(os.path.join(app_dir, 'static', 'style.css'), 'w') as f:
            f.write("/* Default styles */\nbody { font-family: Arial, sans-serif; }")
        logger.info("Wrote default style.css")
    
    logger.info(f"Flask app creation for {website_title} completed")


def generate_website_files(website_title, website_description):
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=api_key)
    print("website description :", website_description)
    prompt = f"""
    Generate a simple website with HTML and CSS:
    - Title: "{website_title}"
    - Description: "{website_description}"

    Provide the output as a JSON object with two fields:
    1. 'html': The HTML content of the webpage.
    2. 'css': The CSS content for styling the webpage.
    
    Please only include the chtml and css no explanations.
    """

    response = llm.invoke(prompt)
    print("Response:", response[3])


    # If the response starts with 'j', remove the first four characters
    if response[3]=='j':
        print("yes there is json")
        response = response[7:]
        # Clean the last 3 characters
        response = response[:-3]
        print("Modified response after removing the last 3 characters:", response)

    try:
        # print("Response:", response)
        json_response = json.loads(response)
        return {
            "html": json_response.get("html"),
            "css": json_response.get("css")
        }
    except json.JSONDecodeError as e:
        print(f"Error: Unable to parse JSON response. Details: {str(e)}")
        return None

def populate_user_website(generated_files):
    # Populate the 'userwebsite.html' file with the generated HTML and CSS content
    html_content = generated_files.get("html", "<h1>Error generating HTML content</h1>")
    css_content = generated_files.get("css", "body { font-family: Arial; }")
    
    # Write HTML to userwebsite.html
    with open(USER_WEBSITE_TEMPLATE, 'w') as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Generated Website</title>
    <style>{css_content}</style>
</head>
<body>
    {html_content}
</body>
</html>
        """)

# @app.route('/view_website')
# def view_website():
#     # Render the user-generated website from the 'userwebsite.html' file
#     return render_template('userwebsite.html')

def create_flask_app(website_title, generated_files):
    logger.info(f"Creating Flask app for {website_title}")
    logger.debug(f"Keys in generated_files: {generated_files.keys()}")
    
    app_dir = os.path.join('generated_sites', website_title)
    os.makedirs(app_dir, exist_ok=True)
    logger.debug(f"Created directory: {app_dir}")

    # Create the templates directory if it doesn't exist
    os.makedirs(os.path.join(app_dir, 'templates'), exist_ok=True)
    logger.debug(f"Created templates directory: {os.path.join(app_dir, 'templates')}")
    
    # Write the index.html file
    if 'templates/index.html' in generated_files:
        with open(os.path.join(app_dir, 'templates', 'index.html'), 'w') as f:
            f.write(generated_files['templates/index.html'])
        logger.info("Successfully wrote index.html")
    else:
        logger.warning("'templates/index.html' not found in generated_files")
        # You might want to handle this error case appropriately
        # For example, you could create a default index.html content
        with open(os.path.join(app_dir, 'templates', 'index.html'), 'w') as f:
            f.write("<html><body><h1>Default Page</h1><p>Content not generated.</p></body></html>")
        logger.info("Wrote default index.html")
    
    # Write the app.py file
    if 'app.py' in generated_files:
        with open(os.path.join(app_dir, 'app.py'), 'w') as f:
            f.write(generated_files['app.py'])
        logger.info("Successfully wrote app.py")
    else:
        logger.warning("'app.py' not found in generated_files")
    
    # Create the static directory and write the style.css file
    if 'static/style.css' in generated_files:
        os.makedirs(os.path.join(app_dir, 'static'), exist_ok=True)
        with open(os.path.join(app_dir, 'static', 'style.css'), 'w') as f:
            f.write(generated_files['static/style.css'])
        logger.info("Successfully wrote style.css")
    else:
        logger.warning("'static/style.css' not found in generated_files")
        # You might want to handle this error case appropriately
        # For example, you could create a default style.css content
        os.makedirs(os.path.join(app_dir, 'static'), exist_ok=True)
        with open(os.path.join(app_dir, 'static', 'style.css'), 'w') as f:
            f.write("/* Default styles */\nbody { font-family: Arial, sans-serif; }")
        logger.info("Wrote default style.css")
    
    logger.info(f"Flask app creation for {website_title} completed")

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(debug=True)
