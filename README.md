# Blockchain API - Anonymous Reports

A blockchain-based API for anonymous reporting, built with FastAPI and Polygon blockchain.

## Project Structure

```
app/
├── adapters/          # Adapters for external services
├── blockchain/        # Blockchain interaction code
├── controllers/       # API endpoints
├── core/              # Core configuration
├── db/                # Database configuration and seed data
├── factories/         # Object creation factories
├── models/            # Database models
├── repositories/      # Data access layer
├── schemas/           # DTOs (Data Transfer Objects)
├── services/          # Business logic layer
├── strategies/        # Strategy implementations
└── utils.py           # Utility functions
```

## Design Patterns

### Repository Pattern

The Repository pattern creates an abstraction layer between the data access and the business logic layers of an application. This helps with:

- Centralizing data access logic
- Making the application more maintainable and testable
- Enabling easy switching between different data sources

Example: `app/repositories/denuncia.py`

### Service Layer Pattern

The Service Layer pattern provides a set of application services that define the boundary of the application and its set of available operations from the perspective of client layers. This helps with:

- Ensuring business logic is not spread across controllers
- Abstracting complex operations
- Enabling easier testing and maintenance

Example: `app/services/denuncia_service.py`

### Factory Pattern

The Factory pattern provides an interface for creating objects without specifying their concrete classes. This helps with:

- Encapsulating object creation logic
- Making it easier to change implementations
- Supporting the Open/Closed Principle

Example: `app/factories/blockchain_factory.py`

### Strategy Pattern

The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. This helps with:

- Supporting multiple implementations of the same interface
- Making algorithms independent from clients that use them
- Adding new strategies without modifying existing code

Example: `app/strategies/blockchain_provider.py` and implementations

### Adapter Pattern

The Adapter pattern allows objects with incompatible interfaces to collaborate. This helps with:

- Integrating third-party libraries with different interfaces
- Making legacy code work with modern systems
- Isolating client code from implementation details

Example: `app/adapters/ipfs_adapter.py`

### Dependency Injection

Using FastAPI's dependency injection system to inject repositories and services into controllers. This helps with:

- Loose coupling between components
- Easier testing through mocking
- Cleaner code

Example: Controllers using `Depends(get_auth_service)`

### DTOs (Data Transfer Objects)

Using Pydantic models to validate and transform data between the API and the application. This helps with:

- Input validation
- Separation of API models from domain models
- Clearer API documentation

Example: `app/schemas/denuncia.py`

## Getting Started

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure the `.env` file with your Polygon credentials
6. Run the application: `uvicorn app.main:app --reload`

## API Documentation

Once running, access the Swagger UI documentation at: <http://localhost:8000/docs>
