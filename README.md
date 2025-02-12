# E-Commerce Website

A full-featured e-commerce website built with Flask, featuring user authentication, product management, shopping cart, PayPal integration, and an admin panel.

## Features

- User Authentication (Login/Register)
- Product Catalog with Categories
- Shopping Cart
- PayPal Payment Integration
- Order Management
- User Profile Management
- Admin Panel
- Responsive Design

## Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- PayPal SDK
- Other dependencies (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ecommerce
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following content:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Admin Access

- URL: `/s/e/c/r/e/t/a/d/m/i/n/p/a/g/e`
- Username: admin
- Password: root

## Project Structure

```
ecommerce/
├── app.py              # Main application file
├── routes.py           # Route definitions
├── models.py           # Database models
├── static/
│   ├── css/           # CSS files
│   ├── js/            # JavaScript files
│   └── uploads/       # Uploaded images
├── templates/         # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── products.html
│   └── admin.html
└── requirements.txt   # Project dependencies
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
