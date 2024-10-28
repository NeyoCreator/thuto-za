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
        user_data[user_id]["responses"]["main_colour"] = user_input
        user_data[user_id]["phase"] = 3
        logger.info(f"Phase 2 completed. User {user_id} selected the main colour: {user_input}")
        return jsonify({
            "message": "Please select the main colour of your website.",
            "suggestions": functionality_options,
            "nextStep": 3
        })

    elif phase == 3:
        user_data[user_id]["responses"]["content"] = user_input
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
        website_description = f"Could you generate a {response_summary['website_type']} website. Make it have the {response_summary['main_colour']} as the primary colour and als generate a color pallet that matches. It should have {response_summary['content']} as its conten"
        website_metadata = [{"website_type":response_summary['website_type']},["main_colour"]]
        logger.debug(f"Website metadata: {website_metadata}")

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
            # "message": "Your website has been generated! You can view it using the following link: https://thuto-chat.azurewebsites.net/view_website",
            "message": "Your website has been generated! You can view it using the following link: http://localhost:5000//view_website",
            
            "link": "/view_website",
            "phase": 5
        })

def generate_website_files(website_title, website_description):
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-pro-latest", api_key=api_key)
    
    portfolio=""""
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Portfolio</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <header>
            <h1>Neo M</h1>
            <p>Software Engineer & Web Developer</p>
        </header>

        <nav>
            <ul>
                <li><a href="#about">About Me</a></li>
                <li><a href="#skills">Skills</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>

        <section id="about">
            <h2>About Me</h2>
            <p>Hello! I'm Neo, a passionate web developer with experience in creating responsive and modern websites. My journey started with building small applications, and now I'm focused on helping businesses grow through digital solutions.</p>
        </section>

        <section id="skills">
            <h2>Skills</h2>
            <div class="skills-grid">
                <div>HTML</div>
                <div>CSS</div>
                <div>JavaScript</div>
                <div>React</div>
                <div>Python</div>
                <div>Flask</div>
                <div>SQL</div>
                <div>Firebase</div>
            </div>
        </section>

        <section id="projects">
            <h2>Projects</h2>
            <div class="project-grid">
                <div class="project">
                    <h3>Project 1</h3>
                    <p>A website builder designed for small businesses.</p>
                </div>
                <div class="project">
                    <h3>Project 2</h3>
                    <p>An AI-driven chatbot that provides customer support.</p>
                </div>
                <div class="project">
                    <h3>Project 3</h3>
                    <p>A platform that automates IT audit tasks for efficiency.</p>
                </div>
            </div>
        </section>

        <section id="contact">
            <h2>Contact Me</h2>
            <p>If you'd like to work together or just say hello, feel free to reach out!</p>
            <button><a href="mailto:neo@example.com">Send Email</a></button>
        </section>

        <footer>
            <p>&copy; 2024 Neo M. All rights reserved.</p>
        </footer>
    </body>
    </html>
    ============
    /* Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* General Styles */
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f4f4f9;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }

    /* Header */
    header {
        text-align: center;
        margin-bottom: 20px;
    }

    header h1 {
        font-size: 2.5em;
        color: #444;
    }

    header p {
        font-size: 1.2em;
        color: #666;
    }

    /* Navigation */
    nav {
        margin: 20px 0;
    }

    nav ul {
        display: flex;
        list-style: none;
        gap: 15px;
    }

    nav ul li a {
        text-decoration: none;
        color: #444;
        font-weight: bold;
    }

    nav ul li a:hover {
        color: #007bff;
    }

    /* Sections */
    section {
        margin: 40px 0;
        width: 100%;
        max-width: 800px;
        text-align: center;
    }

    section h2 {
        font-size: 1.8em;
        color: #333;
        margin-bottom: 10px;
    }

    section p {
        color: #666;
    }

    /* Skills Section */
    .skills-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }

    .skills-grid div {
        padding: 10px;
        background: #007bff;
        color: white;
        border-radius: 5px;
    }

    /* Projects Section */
    .project-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 10px;
    }

    .project {
        background: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .project h3 {
        font-size: 1.2em;
        color: #333;
    }

    .project p {
        font-size: 0.9em;
        color: #555;
    }

    /* Contact Section */
    button {
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 1em;
        cursor: pointer;
        margin-top: 15px;
    }

    button a {
        text-decoration: none;
        color: white;
    }

    button:hover {
        background: #0056b3;
    }

    /* Footer */
    footer {
        margin-top: 40px;
        text-align: center;
        color: #777;
    }


        """


    blog="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Blog</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <header>
            <h1>Neo's Blog</h1>
            <p>Insights, stories, and updates from my journey in tech.</p>
        </header>

        <nav>
            <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#posts">Blog Posts</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>

        <section id="about">
            <h2>About Me</h2>
            <p>Hello! I'm Neo, a software engineer with a passion for coding, learning, and sharing knowledge. Through this blog, I share my insights and experiences on topics ranging from web development to AI.</p>
        </section>

        <section id="posts">
            <h2>Latest Blog Posts</h2>
            <div class="post">
                <h3>Understanding Responsive Design</h3>
                <p>Responsive design is essential for modern web development. In this post, I'll cover the basics of making your website adaptable to different screen sizes...</p>
                <button><a href="#">Read More</a></button>
            </div>
            <div class="post">
                <h3>Getting Started with React Native</h3>
                <p>React Native is a popular framework for building mobile apps. Here’s a beginner’s guide to get you up and running...</p>
                <button><a href="#">Read More</a></button>
            </div>
            <div class="post">
                <h3>The Power of Flask for Back-end Development</h3>
                <p>Flask is a lightweight web framework for Python. In this article, I explore why Flask is a great choice for backend projects...</p>
                <button><a href="#">Read More</a></button>
            </div>
        </section>

        <section id="contact">
            <h2>Contact</h2>
            <p>Have questions or want to connect? Feel free to reach out!</p>
            <button><a href="mailto:neo@example.com">Send Email</a></button>
        </section>

        <footer>
            <p>&copy; 2024 Neo's Blog. All rights reserved.</p>
        </footer>
    </body>
    </html>
    =============
    /* Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* General Styles */
    body {
        font-family: Arial, sans-serif;
        color: #333;
        background-color: #f4f4f9;
        line-height: 1.6;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }

    /* Header */
    header {
        text-align: center;
        margin-bottom: 20px;
    }

    header h1 {
        font-size: 2.5em;
        color: #444;
    }

    header p {
        font-size: 1.2em;
        color: #666;
    }

    /* Navigation */
    nav {
        margin: 20px 0;
    }

    nav ul {
        display: flex;
        list-style: none;
        gap: 15px;
    }

    nav ul li a {
        text-decoration: none;
        color: #444;
        font-weight: bold;
    }

    nav ul li a:hover {
        color: #007bff;
    }

    /* Sections */
    section {
        margin: 40px 0;
        width: 100%;
        max-width: 800px;
        text-align: center;
    }

    section h2 {
        font-size: 1.8em;
        color: #333;
        margin-bottom: 10px;
    }

    section p {
        color: #666;
    }

    /* Blog Posts Section */
    .post {
        background: #e9ecef;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .post h3 {
        font-size: 1.5em;
        color: #333;
        margin-bottom: 5px;
    }

    .post p {
        font-size: 1em;
        color: #555;
        margin-bottom: 10px;
    }

    button {
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 1em;
        cursor: pointer;
    }

    button a {
        text-decoration: none;
        color: white;
    }

    button:hover {
        background: #0056b3;
    }

    /* Footer */
    footer {
        margin-top: 40px;
        text-align: center;
        color: #777;
    }

        """
        
        
    landingpage="""
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Landing Page</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <header>
            <h1>Welcome to Neo's Solutions</h1>
            <p>Your partner in building digital success.</p>
            <button><a href="#features">Learn More</a></button>
        </header>

        <nav>
            <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#testimonials">Testimonials</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>

        <section id="features">
            <h2>Features</h2>
            <div class="features-grid">
                <div class="feature">
                    <h3>Custom Websites</h3>
                    <p>Beautiful, responsive websites designed to elevate your brand.</p>
                </div>
                <div class="feature">
                    <h3>Mobile Applications</h3>
                    <p>Cross-platform mobile apps tailored to your business needs.</p>
                </div>
                <div class="feature">
                    <h3>AI Solutions</h3>
                    <p>Unlock the power of AI to streamline and scale your business operations.</p>
                </div>
            </div>
        </section>

        <section id="testimonials">
            <h2>What Our Clients Say</h2>
            <div class="testimonial">
                <p>"Neo's Solutions transformed our online presence with a stunning website!"</p>
                <span>- Alex, Business Owner</span>
            </div>
            <div class="testimonial">
                <p>"Their mobile app development is top-notch. We've seen a 30% increase in customer engagement."</p>
                <span>- Taylor, Startup Founder</span>
            </div>
            <div class="testimonial">
                <p>"The AI solutions provided by Neo's team have saved us countless hours and improved productivity."</p>
                <span>- Jordan, Operations Manager</span>
            </div>
        </section>

        <section id="contact">
            <h2>Get in Touch</h2>
            <p>Ready to take your business to the next level? Contact us today!</p>
            <button><a href="mailto:neo@example.com">Contact Us</a></button>
        </section>

        <footer>
            <p>&copy; 2024 Neo's Solutions. All rights reserved.</p>
        </footer>
    </body>
    </html>
    ==========================================
    /* Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    /* General Styles */
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f4f4f9;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }

    /* Header */
    header {
        text-align: center;
        padding: 60px 20px;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }

    header h1 {
        font-size: 2.5em;
    }

    header p {
        font-size: 1.2em;
        margin-top: 10px;
    }

    header button {
        padding: 10px 20px;
        background: white;
        color: #007bff;
        border: none;
        border-radius: 5px;
        font-size: 1em;
        cursor: pointer;
        margin-top: 20px;
    }

    header button a {
        text-decoration: none;
        color: #007bff;
    }

    header button:hover {
        background: #0056b3;
        color: white;
    }

    /* Navigation */
    nav {
        margin: 20px 0;
    }

    nav ul {
        display: flex;
        list-style: none;
        gap: 15px;
    }

    nav ul li a {
        text-decoration: none;
        color: #444;
        font-weight: bold;
    }

    nav ul li a:hover {
        color: #007bff;
    }

    /* Features Section */
    #features {
        text-align: center;
        margin: 40px 0;
        width: 100%;
        max-width: 800px;
    }

    #features h2 {
        font-size: 1.8em;
        color: #333;
    }

    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }

    .feature {
        background: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .feature h3 {
        font-size: 1.2em;
        color: #333;
    }

    /* Testimonials Section */
    #testimonials {
        text-align: center;
        margin: 40px 0;
        width: 100%;
        max-width: 800px;
    }

    #testimonials h2 {
        font-size: 1.8em;
        color: #333;
    }

    .testimonial {
        margin: 20px 0;
        padding: 15px;
        background: #f4f4f9;
        border-left: 4px solid #007bff;
        color: #555;
    }

    .testimonial span {
        display: block;
        margin-top: 10px;
        font-size: 0.9em;
        color: #777;
    }

    /* Contact Section */
    #contact {
        text-align: center;
        margin: 40px 0;
        width: 100%;
        max-width: 800px;
    }

    button {
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 1em;
        cursor: pointer;
        margin-top: 15px;
    }

    button a {
        text-decoration: none;
        color: white;
    }

    button:hover {
        background: #0056b3;
    }

    /* Footer */
    footer {
        margin-top: 40px;
        text-align: center;
        color: #777;
    }
        """
            
            
            
    prompt = f"""
    Generate a simple website with HTML and CSS:

    - Description: "{website_description}".

    If the user stated that they wanted a Portfolio use the following content as a guide : {portfolio},
    If the user stated that they wanted a blog use the following content as a guide : {blog},
    If the user stated that they wanted a landingpage use the following content as a guide : {landingpage},

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


# Endpoint to handle chat updates and modify userwebsite.html
@app.route('/update_website', methods=['POST'])
def update_website():
    data = request.json
    instruction = data.get("instruction", "")

    # Example logic to modify HTML content based on instruction
    # You could expand this to recognize specific instructions
    with open(USER_WEBSITE_TEMPLATE, 'r+') as f:
        content = f.read()
        # Replace or append HTML based on the instruction
        if "change title" in instruction.lower():
            new_title = instruction.split("change title to ")[1]
            content = content.replace("<title>.*</title>", f"<title>{new_title}</title>")
        # Other modifications can be added here
        f.seek(0)
        f.write(content)
        f.truncate()

    return jsonify({"message": "Website updated successfully!"})


if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(debug=True)
