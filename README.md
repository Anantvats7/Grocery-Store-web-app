🛒 Grocery Store Application
 
 A multi-user grocery store management system.
 It allows users to buy groceries from multiple categories and an admin to manage 		categories and products.

🚀 Features

👤 User

Sign up and login.

	Browse categories/sections.
	
	Search products by:
	
	Category
	
	Price
	
	Manufacture/Expiry date
	
	Add multiple products to a shopping cart.
	
	Buy products from one or multiple categories.
	
	See out of stock status for unavailable products.
	
	View the total amount payable before checkout.

🛠️ Admin

 Login.

	Manage Categories/Sections:

	Create, Edit, Delete categories.

	Categories stored in UTF-8 encoding to support multiple languages.

	Manage Products:

		Add new products with details:

			ID, Name, Manufacture Date, Expiry Date, Price per Unit (₹/Kg, ₹/Litre,etc.)

		Edit product details (title, description, category).

		Remove products (with confirmation).

	Assign categories to products.

	System automatically shows the latest products added.

📖 Terminology

Inventory → Complete list of all products.

Section/Category → A group of products (e.g., Vegetables, Dairy, Snacks).

Product → Individual item with name, price, expiry date, etc.

🖥️ Technology Stack

	Backend → Flask (Python)

	Database → SQLite

	UI → Bootstrap

	Templating → Jinja2

⚙️ Installation & Setup

#Clone the repository

		git clone <your-repo-url>
		cd reponame


#Create and activate a virtual environment

		python3 -m venv venv3
		source venv3/bin/activate


#Install dependencies

		pip install -r requirements.txt


#Run the application

		python main.py

	Visit `http://localhost:5000` in your web browser.
