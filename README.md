# Appliance Energy Advisor ⚡

A backend application that helps users track appliance electricity consumption and estimate monthly energy costs.

## Features

* User signup and login
* JWT-based authentication
* Add, view, update, and delete appliances
* Calculate daily and monthly electricity consumption
* Estimate electricity costs
* Identify high-energy appliances
* User-specific appliance data
* RESTful APIs built with FastAPI
* MySQL database integration

## Tech Stack

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **MySQL**
* **Pydantic**
* **JWT Authentication**
* **Uvicorn**

## Project Structure

```text
appliance_energy_advisor/
│
├── main.py
├── api.py
├── auth.py
├── database.py
├── models.py
├── functions.py
├── create_tables.py
├── requirements.txt
└── .gitignore
```

## How It Works

The application takes an appliance's power consumption in watts and its daily usage hours to estimate electricity consumption.

**Daily Units:**

`Power (W) × Hours / 1000`

**Monthly Units:**

`Daily Units × 30`

The application can then use the calculated consumption to estimate the electricity cost and provide usage advice.

## API

The project provides REST API endpoints for authentication and appliance management.

You can test the APIs using **Swagger UI** available through FastAPI.

After starting the server, open:

`http://127.0.0.1:8000/docs`

## Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure your environment variables in a `.env` file.

Then run the application:

```bash
uvicorn main:app --reload
```

## Learning Project

This project was built to practice Python backend development, FastAPI, database integration, authentication, CRUD operations, and API development.
