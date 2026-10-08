# AI Support Agent

An AI-powered customer support backend built with **FastAPI, RAG, ChromaDB, OpenAI, AI Agent Tool Calling, JWT Authentication, and SQLAlchemy**.

The system allows authenticated customers to ask questions about their orders, customer information, and company policies while ensuring that customer-specific data is protected through authentication and ownership validation.


The AI Support Agent combines traditional backend APIs with AI capabilities to provide context-aware customer support.

Users can ask questions about:

* Orders
* Order status
* Customer information
* Refund policies
* Return policies
* Payment policies
* Shipping policies

The system uses:

* **RAG** to retrieve relevant knowledge from policy documents
* **AI Agent Tool Calling** to retrieve customer and order information
* **JWT Authentication** to identify users
* **SQLAlchemy + SQLite** for data persistence
* **FastAPI** for REST APIs
* **Docker** for containerization

---



---


```text
                         User
                           |
                           v
                    FastAPI Backend
                           |
             +-------------+-------------+
             |                           |
             v                           v
        JWT Authentication          AI Agent
                                         |
                         +---------------+---------------+
                         |               |               |
                         v               v               v
                       RAG          Customer Tool    Order Tool
                         |               |               |
                         v               v               v
                    ChromaDB         SQLite DB       SQLite DB
                         |
                         v
                  Policy Documents
```

### AI Request Flow

```text
User Question
      |
      v
FastAPI /chat
      |
      v
Authenticated User
      |
      v
AI Agent
      |
      +----------------------+
      |                      |
      v                      v
   RAG Search           Backend Tools
      |                      |
      v                      v
 ChromaDB              Customer / Orders
      |                      |
      +----------+-----------+
                 |
                 v
              LLM
                 |
                 v
          Final AI Response
```

---


The AI agent can use backend tools to retrieve authenticated customer data.

### Customer Details

```text
get_customer_details()
```

Retrieves customer information for the authenticated user.

### Customer Orders

```text
get_customer_orders()
```

Retrieves orders belonging to the authenticated customer.

### Order Details

```text
get_order_details(order_id)
```

Retrieves information about a specific order after validating customer ownership.

Customer identity is obtained from the authenticated JWT rather than trusting a customer ID supplied by the client.

This prevents users from accessing another customer's information.

---


The project uses Retrieval-Augmented Generation to answer questions based on company knowledge.

```text
Policy Documents
       |
       v
Sentence Transformer
       |
       v
Embeddings
       |
       v
ChromaDB
       |
       v
Similarity Search
       |
       v
CrossEncoder Reranking
       |
       v
Relevant Context
       |
       v
OpenAI LLM
       |
       v
Final Answer
```

Knowledge sources include:

* Refund policy
* Return policy
* Payment policy
* Shipping policy

---


The application implements several security controls:

* JWT authentication
* Authenticated customer ownership checks
* Protected customer APIs
* Protected order APIs
* Secure AI tool access
* Password hashing
* Login rate limiting
* Registration rate limiting
* Chat endpoint rate limiting
* Input validation
* Generic internal error responses
* Environment-based secret management

Example:

```text
User A
  |
  | Request Order #101
  v
JWT Authentication
  |
  v
Ownership Validation
  |
  +---- Owner ------> Return Order
  |
  +---- Not Owner --> 404
```

The AI tools also perform ownership validation before returning customer-specific information.

---


| Method | Endpoint                 | Description                    | Auth |
| ------ | ------------------------ | ------------------------------ | ---- |
| GET    | `/`                      | API health check               | No   |
| POST   | `/register`              | Register new user              | No   |
| POST   | `/login`                 | Login and receive JWT          | No   |
| GET    | `/profile`               | Get authenticated user profile | Yes  |
| POST   | `/customers`             | Create customer                | Yes  |
| GET    | `/customers/{id}`        | Get customer details           | Yes  |
| POST   | `/orders`                | Create order                   | Yes  |
| GET    | `/orders/{id}`           | Get order details              | Yes  |
| GET    | `/customers/{id}/orders` | Get customer's orders          | Yes  |
| POST   | `/chat`                  | AI customer support            | Yes  |
| POST   | `/test-agent`            | Test AI agent                  | Yes  |
| GET    | `/test-order-tool/{id}`  | Test order tool                | Yes  |

Swagger documentation:

```text
http://localhost:8001/docs
```

---


```text
ai-support-agent/
â”‚
â”œâ”€â”€ backend/
â”‚   â”‚
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ database.py
â”‚   â”‚   â”œâ”€â”€ embeddings.py
â”‚   â”‚   â”œâ”€â”€ ingest.py
â”‚   â”‚   â”œâ”€â”€ main.py
â”‚   â”‚   â”œâ”€â”€ models.py
â”‚   â”‚   â”œâ”€â”€ reranker.py
â”‚   â”‚   â””â”€â”€ search.py
â”‚   â”‚
â”‚   â”œâ”€â”€ knowledge/
â”‚   â”‚   â”œâ”€â”€ payment_policy.txt
â”‚   â”‚   â”œâ”€â”€ refund_policy.txt
â”‚   â”‚   â”œâ”€â”€ return_policy.txt
â”‚   â”‚   â””â”€â”€ shipping_policy.txt
â”‚   â”‚
â”‚   â”œâ”€â”€ tests/
â”‚   â”‚   â””â”€â”€ test_auth.py
â”‚   â”‚
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â”œâ”€â”€ docker-compose.yml
â”‚   â”œâ”€â”€ pytest.ini
â”‚   â””â”€â”€ requirements.txt
â”‚
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```

---


### 1. Clone the repository

```bash
git clone https://github.com/Soumyadip-crypto/ai-support-agent.git
```

### 2. Navigate to backend

```bash
cd ai-support-agent/backend
```

### 3. Create `.env`

Create a `.env` file inside the `backend` directory:

```env
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

### 4. Build and start the application

```bash
docker compose up -d --build
```

### 5. Check container status

```bash
docker compose ps
```

### 6. Access the API

```text
http://localhost:8001
```

### 7. Open Swagger

```text
http://localhost:8001/docs
```

---


The application uses environment variables for sensitive configuration.

```env
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

Sensitive files are excluded from Git using `.gitignore`.

The following are not committed:

```text
.env
support.db
chroma_db/
__pycache__/
.venv/
```

---


The project includes authentication/API tests using Pytest.

Run:

```bash
pytest
```

The backend was also manually tested for:

* Successful registration
* Successful login
* Invalid login
* Duplicate username
* Duplicate email
* Invalid JWT
* Missing authentication
* Invalid customer ID
* Invalid order ID
* Unauthorized order access
* Request validation
* API rate limiting
* Authenticated AI chat
* Customer-specific AI tool access

---


A key design principle of this project is that the AI agent does not blindly trust IDs provided by users.

For example:

```text
JWT
 |
 v
Authenticated User ID
 |
 v
Customer Ownership Check
 |
 +---- Valid ----> Access Data
 |
 +---- Invalid --> Reject Request
```

This authorization layer is applied to:

* Customer details
* Customer orders
* Individual orders
* AI agent tools

This prevents one authenticated user from accessing another customer's data.

---


### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* JWT
* Passlib

### AI / Machine Learning

* OpenAI
* RAG
* Sentence Transformers
* CrossEncoder
* ChromaDB
* Embeddings
* AI Agents
* Tool Calling

### DevOps

* Docker
* Docker Compose
* Pytest

---


This project demonstrates practical experience with:

* Building REST APIs using FastAPI
* Designing JWT authentication
* Implementing authorization and ownership checks
* Working with SQLAlchemy
* Building RAG pipelines
* Generating and storing embeddings
* Working with vector databases
* Semantic search and reranking
* Integrating LLM APIs
* Building AI agents
* Implementing backend tool calling
* Securing AI-powered applications
* Storing conversations and messages
* Containerizing AI applications with Docker
* Implementing API rate limiting
* Designing AI-powered backend systems

---


Possible future improvements include:

* React frontend
* Streaming AI responses
* PostgreSQL
* Redis caching
* Background task processing
* Production monitoring
* CI/CD pipeline
* Advanced agent orchestration
* Improved conversation memory
* Cloud deployment

---


**Soumyadip Parui**

AI / Backend Developer

GitHub:

https://github.com/Soumyadip-crypto
