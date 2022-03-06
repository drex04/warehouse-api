# Warehouse Inventory REST API

## Context

This API was built as a take-home technical interview with the assignment to build a back-end API to manage warehouse inventory.

Note to reviewer: I have removed the 'art_id' field from the provided JSON input because I have used an auto-generated sequential ID for the primary key (PK) of the Article database table. If the ID is created manually through JSON uploads there is a risk of creating multiple Article records with the same ID.

## Functional Requirements

- Ingest semi-structured JSON data describing articles and stock, via POST endpoint
- Ingest semi-structured JSON data describing products and component articles, via POST endpoint
- Ingest JSON file upload (products and articles) via POST endpoint
- Parse data and store in relational database
- Serve data via GET endpoint to show current product inventory
- "Sell" a product and decrement the stock of its component articles by the required amount

## Non-functional Requirements

- Since this is an interview assignment with a limited timeframe and not a real production environment, I will assume that designing for high scalability, reliability, availability, etc. is not required at this stage. In addition, since this is an internal business application it will probably have thousands of users rather than millions of users which could be expected for a consumer-facing application.
- Since this project is created and maintained by a single developer I will optimize for maintainability by utilizing a small set of popular and well-documented tools that are designed to play well together.

## Tech Stack

- **Flask** - I decided to use Flask because it is a lightweight and simple framework which makes it easy to prototype functionality for small interview assignments. It also is compatible with the SQL Alchemy ORM which makes database operations easier, prevents SQL injection attacks, and makes future migration to a different database easier.
- **SQLite** - I decided to use SQLite, a local file-based database instead of a real external database for this project. This is because I want to build a rapid prototype that can be cloned from Github and easily reviewed by an interviewer without needing to manage external database permissions. Since I am using an ORM, this project could be migrated from SQLite to e.g. PostgreSQL fairly easily.
- **Conexxion** - I decided to add the Connexxion library to provide a Swagger GUI page to make the API more usable for consumers/reviewers.

## Data Model

![Warehouse API Data Model](/images/data-model.png)

# Run Instructions

- Clone or download the repository to your local environment
- Navigate to the project root directory.
- Create a virtual environment with your tool of choice (e.g. venv, Anaconda) and install the dependencies listed in 'requirements.txt' (e.g. with `pip install -r requirements.txt`)
- Navigate to the 'app' folder in your terminal
- Then, in your terminal, run:
  `python create_db.py` to initialize the SQLite database.
- Then, run:
  `python server.py` to start the Flask API server.

Open the link provided by the API server in your web browser and:

- At `/` you'll see the homepage with file upload form
- At `/api/inventory` you can view the list of all products with their current inventory
- At `/api/products` you can view the list of all products with name and price
- At `/api/articles` you can view the list of all articles with their current stock level
- At `/api/ui` you can explore a Swagger GUI of the OpenAPI specification
  ![Swagger UI](/images/swagger.png)

## API Endpoints

- Read current product inventory
  - Send `GET` request to `/api/inventory`
- Read all products
  - Send `GET` request to `/api/products`
- Read all articles
  - Send `GET` request to `/api/articles`
- Create new products
  - Send `POST` request to `/api/products`
- Create new articles and/or add stock
  - Send `POST` request to `/api/articles`
- Update inventory by "selling" a product:
  - Send `PATCH` request to `/api/inventory/<productId>`
- Upload file to create new products, create new articles, or add article stock
  - Send `POST` request to `/api/upload`

A Postman collection file with these requests preconfigured can be found in the `/test` folder of this project. Sample JSON files for testing the upload function are contained in the same folder.

![Postman](/images/postman.png)

## Compromises / Further Development

If I were building this API for a production environment instead of for a time-limited interview assignment, I would add:

- Unit tests
- Integration tests
- End-to-end tests
- Logging

I would also migrate the database to PostgreSQL hosted on a cloud db service like AWS RDS or Google Cloud SQL. If this POC were to be extended to a more fully-featured application with authentication flow and many more database tables, I would consider migrating this project from Flask to Django to take advantage of its extensive built-in features.
