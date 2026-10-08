**# AI Support Agent**



**An AI-powered customer support backend that combines \*\*FastAPI, RAG, ChromaDB, OpenAI, tool calling, JWT authentication, and SQLAlchemy\*\* to provide intelligent and context-aware customer support.**



**## 🚀 Project Overview**



**The AI Support Agent is designed to automate customer support operations.**



**Users can ask questions about:**



**\* Orders**

**\* Order status**

**\* Customer information**

**\* Refund policies**

**\* Return policies**

**\* Payment policies**

**\* Shipping policies**



**The system uses an AI agent that can retrieve relevant knowledge through \*\*RAG\*\* and access customer/order information through backend tools.**



**---**



**## ✨ Key Features**



**\* 🤖 AI-powered customer support**

**\* 🔐 JWT-based authentication**

**\* 👤 Customer management**

**\* 📦 Order management**

**\* 🧠 Retrieval-Augmented Generation (RAG)**

**\* 🔎 ChromaDB vector database**

**\* 🛠️ AI tool calling**

**\* 💬 Conversation and message storage**

**\* 🗄️ SQLAlchemy + SQLite**

**\* 🚀 FastAPI REST APIs**

**\* 🐳 Docker \& Docker Compose**

**\* 📚 Automatic Swagger API documentation**



**---**



**## 🏗️ Architecture**



**```text**

&#x20;                        **User**

&#x20;                          **│**

&#x20;                          **▼**

&#x20;                   **FastAPI Backend**

&#x20;                          **│**

&#x20;             **┌────────────┴────────────┐**

&#x20;             **│                         │**

&#x20;             **▼                         ▼**

&#x20;         **JWT Auth                  AI Agent**

&#x20;                                       **│**

&#x20;                        **┌──────────────┼──────────────┐**

&#x20;                        **│              │              │**

&#x20;                        **▼              ▼              ▼**

&#x20;                      **RAG         Tool Calling       LLM**

&#x20;                        **│              │              │**

&#x20;                        **▼              ▼              ▼**

&#x20;                    **ChromaDB       SQLite          OpenAI**

&#x20;                        **│              │**

&#x20;                        **└──────────────┘**

**```**



**---**



**## 🧠 AI Agent Flow**



**When a user sends a support query:**



**```text**

**User Question**

&#x20;     **│**

&#x20;     **▼**

**FastAPI /chat**

&#x20;     **│**

&#x20;     **▼**

**AI Agent**

&#x20;     **│**

&#x20;     **├──────────────► Knowledge Search**

&#x20;     **│                    │**

&#x20;     **│                    ▼**

&#x20;     **│                 ChromaDB**

&#x20;     **│**

&#x20;     **├──────────────► Customer/Order Tools**

&#x20;     **│                    │**

&#x20;     **│                    ▼**

&#x20;     **│                  SQLite**

&#x20;     **│**

&#x20;     **▼**

**OpenAI LLM**

&#x20;     **│**

&#x20;     **▼**

**Final Support Response**

**```**



**---**



**## 🔎 RAG Pipeline**



**The project uses Retrieval-Augmented Generation to answer questions from internal support knowledge.**



**Knowledge documents include:**



**\* Refund Policy**

**\* Return Policy**

**\* Payment Policy**

**\* Shipping Policy**



**The documents are converted into embeddings and stored in ChromaDB.**



**During a user query:**



**```text**

**User Query**

&#x20;   **↓**

**Embedding**

&#x20;   **↓**

**Vector Search**

&#x20;   **↓**

**Relevant Documents**

&#x20;   **↓**

**AI Agent**

&#x20;   **↓**

**LLM**

&#x20;   **↓**

**Answer**

**```**



**This helps the model generate responses based on the application's support knowledge instead of relying only on general model knowledge.**



**---**



**## 🛠️ AI Tools**



**The AI agent can interact with backend tools to retrieve customer and order information.**



**### Customer Details**



**```text**

**get\_customer\_details()**

**```**



**Retrieves customer information for the authenticated user.**



**### Customer Orders**



**```text**

**get\_customer\_orders()**

**```**



**Retrieves orders belonging to the authenticated customer.**



**### Order Details**



**```text**

**get\_order\_details(order\_id)**

**```**



**Retrieves information about a specific order after validating ownership.**



**The tools use the authenticated user's identity to prevent unauthorized access to other customers' data.**



**---**



**## 🔐 Authentication**



**The application uses JWT-based authentication.**



**Authentication flow:**



**```text**

**Register**

&#x20;  **↓**

**Login**

&#x20;  **↓**

**JWT Token**

&#x20;  **↓**

**Authorization Header**

&#x20;  **↓**

**Protected APIs**

**```**



**Example:**



**```text**

**Authorization: Bearer <JWT\_TOKEN>**

**```**



**Protected APIs validate the token before accessing customer-specific data.**



**---**



**## 📡 API Endpoints**



**### Authentication**



**| Method | Endpoint    | Description                    |**

**| ------ | ----------- | ------------------------------ |**

**| POST   | `/register` | Register a new user            |**

**| POST   | `/login`    | Login and receive JWT token    |**

**| GET    | `/profile`  | Get authenticated user profile |**



**### Customers**



**| Method | Endpoint                   | Description          |**

**| ------ | -------------------------- | -------------------- |**

**| POST   | `/customers`               | Create customer      |**

**| GET    | `/customers`               | Get customers        |**

**| GET    | `/customers/{customer\_id}` | Get customer details |**



**### Orders**



**| Method | Endpoint                          | Description         |**

**| ------ | --------------------------------- | ------------------- |**

**| POST   | `/orders`                         | Create order        |**

**| GET    | `/orders/{order\_id}`              | Get order details   |**

**| GET    | `/customers/{customer\_id}/orders` | Get customer orders |**



**### AI**



**| Method | Endpoint                      | Description                   |**

**| ------ | ----------------------------- | ----------------------------- |**

**| POST   | `/chat`                       | Send a customer support query |**

**| POST   | `/test-agent`                 | Test AI agent                 |**

**| GET    | `/test-order-tool/{order\_id}` | Test order tool               |**



**---**



**## 💬 Example AI Queries**



**### Policy Question**



**```text**

**User:**

**What is your refund policy?**



**AI:**

**According to the refund policy, eligible refunds are processed**

**within the specified refund period...**

**```**



**### Order Question**



**```text**

**User:**

**Where is my order?**



**AI:**

**I can check your order information using your authenticated**

**customer account.**

**```**



**### Customer Support**



**```text**

**User:**

**Can I return my product?**



**AI:**

**The system retrieves the relevant return policy from the**

**knowledge base and provides the applicable information.**

**```**



**---**



**## 🧰 Tech Stack**



**### Backend**



**\* Python**

**\* FastAPI**

**\* SQLAlchemy**

**\* SQLite**

**\* JWT Authentication**



**### AI / GenAI**



**\* OpenAI**

**\* RAG**

**\* Embeddings**

**\* ChromaDB**

**\* Sentence Transformers**

**\* Cross Encoder**



**### DevOps**



**\* Docker**

**\* Docker Compose**

**\* Git**

**\* GitHub**



**---**



**## 📁 Project Structure**



**```text**

**ai-support-agent/**

**│**

**├── backend/**

**│   │**

**│   ├── app/**

**│   │   ├── \_\_init\_\_.py**

**│   │   ├── database.py**

**│   │   ├── embeddings.py**

**│   │   ├── ingest.py**

**│   │   ├── main.py**

**│   │   ├── models.py**

**│   │   ├── reranker.py**

**│   │   └── search.py**

**│   │**

**│   ├── knowledge/**

**│   │   ├── payment\_policy.txt**

**│   │   ├── refund\_policy.txt**

**│   │   ├── return\_policy.txt**

**│   │   └── shipping\_policy.txt**

**│   │**

**│   ├── tests/**

**│   │   └── test\_auth.py**

**│   │**

**│   ├── Dockerfile**

**│   ├── docker-compose.yml**

**│   ├── pytest.ini**

**│   └── requirements.txt**

**│**

**├── .gitignore**

**└── README.md**

**```**



**---**



**## 🐳 Run with Docker**



**Clone the repository:**



**```bash**

**git clone https://github.com/Soumyadip-crypto/ai-support-agent.git**

**```**



**Go to the backend:**



**```bash**

**cd ai-support-agent/backend**

**```**



**Create a `.env` file and configure the required environment variables.**



**Build and start the application:**



**```bash**

**docker-compose up -d --build**

**```**



**The API will run on:**



**```text**

**http://localhost:8001**

**```**



**Swagger documentation:**



**```text**

**http://localhost:8001/docs**

**```**



**---**



**## 🔑 Environment Variables**



**The application uses environment variables for sensitive configuration.**



**Example:**



**```env**

**OPENAI\_API\_KEY=your\_api\_key**

**SECRET\_KEY=your\_secret\_key**

**```**



**Sensitive files such as `.env`, database files, and vector database files are excluded from Git using `.gitignore`.**



**---**



**## 🧪 Testing**



**The project includes API authentication tests using Pytest.**



**Run:**



**```bash**

**pytest**

**```**



**---**



**## 🎯 What This Project Demonstrates**



**This project demonstrates practical experience with:**



**\* Building REST APIs using FastAPI**

**\* Designing JWT authentication**

**\* Working with SQLAlchemy**

**\* Building RAG pipelines**

**\* Using vector databases**

**\* Integrating LLM APIs**

**\* Implementing AI agents**

**\* Implementing backend tool calling**

**\* Securing customer-specific data**

**\* Containerizing AI applications with Docker**

**\* Designing AI-powered backend systems**



**---**



**## 🔮 Future Improvements**



**Possible future improvements include:**



**\* React frontend**

**\* Streaming AI responses**

**\* PostgreSQL**

**\* Redis caching**

**\* Background task processing**

**\* Production monitoring**

**\* Cloud deployment**

**\* CI/CD pipeline**

**\* Advanced agent orchestration**

**\* Conversation memory improvements**



**---**



**## 👨‍💻 Author**



**\*\*Soumyadip Parui\*\***



**AI / Backend Developer**



**GitHub:**

**https://github.com/Soumyadip-crypto**



