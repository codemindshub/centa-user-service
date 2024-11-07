# centa-user-service
Manages user authentication, authorization, and profile information within the Centa system, supporting secure access control.


## Technologies Used

- **Backend**: Django (Python) with Django REST Framework for building APIs.
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens) for secure user authentication.
- **Jobs and Automation**: Celery, Redis
- **Caching**: Redis
- **HTML to PDF**: xhtml2pdf


## Installation

To install and run ICenta User Management Service locally, follow these steps:

1. **Set up the virtual environment**:

   ```bash
   python -m venv centa_ims
   source centa_ims/bin/activate  # On Windows use `centa_ims\Scripts\activate`
   ```

2. **Clone the repository**:

	*** SSH ***
   ```bash
   git clone git@github.com:codemindshub/centa_user_service.git
   cd centa_user_service
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Additional SetUp**:
	- Create a Secret Key for Django
	   ```bash
	   python -c "import secrets; print(secrets.token_urlsafe())"
	   ```
	- Create a `.env` file
	- Put the generated secret key into the `.env` file:
		```text
		SECRET_KEY=<put secret key here>
		```
		
5. **Run the migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

## Contributing

Contributions are welcome! If you would like to contribute to InventoryWise, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your branch and create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
