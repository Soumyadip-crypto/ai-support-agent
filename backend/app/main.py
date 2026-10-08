import os
import json

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request
)

from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from pydantic import (
    BaseModel,
    Field,
    EmailStr
)

from passlib.context import CryptContext

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from slowapi import (
    Limiter,
    _rate_limit_exceeded_handler
)

from slowapi.util import get_remote_address

from slowapi.errors import RateLimitExceeded

from .database import (
    Base,
    engine,
    SessionLocal
)

from . import models

import chromadb

from sentence_transformers import (
    CrossEncoder,
    SentenceTransformer
)

from openai import OpenAI

from jose import jwt, JWTError


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not configured."
    )

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured."
    )


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# RATE LIMITER
# =========================================================

limiter = Limiter(
    key_func=get_remote_address
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI()

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    print(
        f"Unexpected error: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error."
        }
    )


# =========================================================
# OPENAI
# =========================================================

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# =========================================================
# AI MODELS
# =========================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# =========================================================
# CHROMA
# =========================================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="support_knowledge"
)


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# JWT
# =========================================================

ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# =========================================================
# PASSWORD HASHING
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# REQUEST MODELS
# =========================================================

class CustomerCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    email: EmailStr


class OrderCreate(BaseModel):

    product: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    status: str = Field(
        ...,
        min_length=1,
        max_length=50
    )


class UserCreate(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=72
    )

    email: EmailStr


class LoginRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=72
    )


class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )


class AgentRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )

    conversation_id: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


# =========================================================
# CUSTOMER HELPER
# =========================================================

def get_customer_for_user(
    user_id: int,
    db: Session
):

    customer = db.query(
        models.Customer
    ).filter(
        models.Customer.user_id == user_id
    ).first()

    return customer


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Customer Support API is running"
    }


# =========================================================
# CREATE CUSTOMER
# =========================================================

@app.post("/customers")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    existing_customer = get_customer_for_user(
        user_id,
        db
    )

    if existing_customer:

        raise HTTPException(
            status_code=400,
            detail="Customer profile already exists."
        )

    new_customer = models.Customer(
        user_id=user_id,
        name=customer.name,
        email=str(customer.email)
    )

    db.add(new_customer)

    db.commit()

    db.refresh(new_customer)

    return {
        "message": "Customer created successfully",
        "customer_id": new_customer.id,
        "name": new_customer.name,
        "email": new_customer.email
    }


# =========================================================
# GET CUSTOMER
# =========================================================

@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    customer = db.query(
        models.Customer
    ).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if customer.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized "
                "to access this customer."
            )
        )

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "email": customer.email
    }


# =========================================================
# CREATE ORDER
# =========================================================

@app.post("/orders")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found."
        )

    new_order = models.Order(
        customer_id=customer.id,
        product=order.product,
        status=order.status
    )

    db.add(new_order)

    db.commit()

    db.refresh(new_order)

    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "customer_id": customer.id,
        "product": new_order.product,
        "status": new_order.status
    }


# =========================================================
# GET ORDER
# =========================================================

@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    order = (
        db.query(models.Order)
        .join(
            models.Customer,
            models.Order.customer_id
            == models.Customer.id
        )
        .filter(
            models.Order.id == order_id,
            models.Customer.user_id == user_id
        )
        .first()
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found or unauthorized."
        )

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "product": order.product,
        "status": order.status
    }


# =========================================================
# CUSTOMER ORDERS
# =========================================================

@app.get(
    "/customers/{customer_id}/orders"
)
def get_customer_orders_api(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    customer = db.query(
        models.Customer
    ).filter(
        models.Customer.id == customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if customer.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized "
                "to access these orders."
            )
        )

    orders = db.query(
        models.Order
    ).filter(
        models.Order.customer_id == customer.id
    ).all()

    return [
        {
            "order_id": order.id,
            "product": order.product,
            "status": order.status
        }
        for order in orders
    ]


# =========================================================
# REGISTER
# =========================================================

@app.post("/register")
@limiter.limit("5/minute")
def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):

    try:

        existing_user = db.query(
            models.User
        ).filter(
            models.User.username
            == user.username
        ).first()

        if existing_user:

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        existing_email = db.query(
            models.Customer
        ).filter(
            models.Customer.email
            == str(user.email)
        ).first()

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        hashed_password = pwd_context.hash(
            user.password
        )

        new_user = models.User(
            username=user.username,
            password=hashed_password
        )

        db.add(new_user)

        db.flush()

        new_customer = models.Customer(
            user_id=new_user.id,
            name=user.username,
            email=str(user.email)
        )

        db.add(new_customer)

        db.commit()

        db.refresh(new_user)

        db.refresh(new_customer)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "customer_id": new_customer.id,
            "username": new_user.username
        }

    except HTTPException:

        raise

    except Exception as exc:

        db.rollback()

        print(
            f"Registration error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Registration failed."
        )


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    db_request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(
        models.User
    ).filter(
        models.User.username
        == db_request.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not pwd_context.verify(
        db_request.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token_expires = timedelta(
        minutes=30
    )

    token = jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "exp": (
                datetime.now(timezone.utc)
                + access_token_expires
            )
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800
    }


# =========================================================
# PROFILE
# =========================================================

@app.get("/profile")
def profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "user_id": user_id,
        "username": current_user.get(
            "username"
        ),
        "customer_id": customer.id,
        "name": customer.name,
        "email": customer.email
    }


# =========================================================
# RAG SEARCH
# =========================================================

def search_knowledge(
    question: str
):

    query_embedding = (
        embedding_model
        .encode(question)
        .tolist()
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=10
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    if not documents:

        return {
            "answer": (
                "No relevant information found."
            )
        }

    pairs = [
        [question, document]
        for document in documents
    ]

    scores = reranker.predict(
        pairs
    )

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    top_results = ranked[:3]

    best_score = top_results[0][1]

    if best_score < -5:

        return {
            "answer": (
                "I could not find reliable "
                "information in the knowledge base."
            )
        }

    context = "\n\n".join(
        document
        for document, score in top_results
    )

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=(
            "Answer the customer's question "
            "using only the provided knowledge "
            "base context. If the answer is not "
            "present, say you do not know."
        ),
        input=f"""
Knowledge Base:

{context}

Customer Question:

{question}
"""
    )

    return {
        "answer": response.output_text
    }


# =========================================================
# SAVE CONVERSATION
# =========================================================

def save_conversation(
    conversation_id: str,
    user_id: int,
    db: Session
):

    conversation = db.query(
        models.Conversation
    ).filter(
        models.Conversation.conversation_id
        == conversation_id
    ).first()

    if conversation:

        if conversation.user_id != user_id:

            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not authorized "
                    "to access this conversation."
                )
            )

        return conversation

    conversation = models.Conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        title="AI Support Conversation"
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# =========================================================
# SAVE MESSAGE
# =========================================================

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    user_id: int,
    db: Session
):

    conversation = db.query(
        models.Conversation
    ).filter(
        models.Conversation.conversation_id
        == conversation_id
    ).first()

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    if conversation.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized "
                "to access this conversation."
            )
        )

    message = models.Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)

    db.commit()

    db.refresh(message)

    return message


# =========================================================
# GET CONVERSATION MESSAGES
# =========================================================

def get_conversation_messages(
    conversation_id: str,
    user_id: int,
    db: Session
):

    conversation = db.query(
        models.Conversation
    ).filter(
        models.Conversation.conversation_id
        == conversation_id
    ).first()

    if not conversation:

        return []

    if conversation.user_id != user_id:

        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized "
                "to access this conversation."
            )
        )

    messages = db.query(
        models.Message
    ).filter(
        models.Message.conversation_id
        == conversation_id
    ).order_by(
        models.Message.id
    ).all()

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]


# =========================================================
# AI TOOLS
# =========================================================

order_tool = {
    "type": "function",
    "name": "get_order_details",
    "description": (
        "Get details of one of the currently "
        "authenticated customer's orders "
        "using the order ID."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "integer",
                "description": "The ID of the order"
            }
        },
        "required": [
            "order_id"
        ]
    }
}


customer_tool = {
    "type": "function",
    "name": "get_customer_details",
    "description": (
        "Get details of the currently "
        "authenticated customer."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


customer_orders_tool = {
    "type": "function",
    "name": "get_customer_orders",
    "description": (
        "Get all orders belonging to the "
        "currently authenticated customer."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


knowledge_tool = {
    "type": "function",
    "name": "search_knowledge",
    "description": (
        "Search the company knowledge base "
        "for policies, shipping information, "
        "refund rules, return rules, payment "
        "information, and other customer "
        "support information."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "The customer's question "
                    "that should be searched "
                    "in the knowledge base."
                )
            }
        },
        "required": [
            "question"
        ]
    }
}


# =========================================================
# TOOL FUNCTIONS
# =========================================================

def get_order_details(
    order_id: int,
    user_id: int,
    db: Session
):

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        return {
            "error": (
                "Customer profile not found."
            )
        }

    order = db.query(
        models.Order
    ).filter(
        models.Order.id == order_id
    ).first()

    if not order:

        return {
            "error": "Order not found"
        }

    if order.customer_id != customer.id:

        return {
            "error": (
                "You are not authorized "
                "to access this order."
            )
        }

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "product": order.product,
        "status": order.status
    }


def get_customer_details(
    user_id: int,
    db: Session
):

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        return {
            "error": "Customer not found"
        }

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "email": customer.email
    }


def get_customer_orders(
    user_id: int,
    db: Session
):

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        return {
            "error": "Customer not found"
        }

    orders = db.query(
        models.Order
    ).filter(
        models.Order.customer_id
        == customer.id
    ).all()

    return {
        "customer_id": customer.id,
        "orders": [
            {
                "order_id": order.id,
                "product": order.product,
                "status": order.status
            }
            for order in orders
        ]
    }


# =========================================================
# SECURE TOOL WRAPPERS
# =========================================================

def secure_get_order_details(
    order_id: int,
    user_id: int,
    db: Session
):

    return get_order_details(
        order_id=order_id,
        user_id=user_id,
        db=db
    )


def secure_get_customer_details(
    user_id: int,
    db: Session
):

    return get_customer_details(
        user_id=user_id,
        db=db
    )


def secure_get_customer_orders(
    user_id: int,
    db: Session
):

    return get_customer_orders(
        user_id=user_id,
        db=db
    )


# =========================================================
# AI AGENT
# =========================================================

def run_order_agent(
    message: str,
    conversation_id: str,
    db: Session,
    user_id: int
):

    customer = get_customer_for_user(
        user_id,
        db
    )

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer profile not found."
        )

    save_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content=message,
        user_id=user_id,
        db=db
    )

    history = get_conversation_messages(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    instructions = f"""
You are an AI customer support agent.

You are assisting the authenticated customer.

Customer ID:
{customer.id}

Customer Name:
{customer.name}

Important security rules:

1. Never ask the customer for their customer ID.
2. Never trust a customer ID provided by the customer.
3. Use the authenticated user's identity.
4. Customers can only access their own orders.
5. Never reveal another customer's information.
6. Use tools whenever order or customer information is required.
7. Use the knowledge base for company policies.
8. Do not invent order information.
"""

    tools = [
        order_tool,
        customer_tool,
        customer_orders_tool,
        knowledge_tool
    ]

    messages = []

    for item in history:

        messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=messages,
        tools=tools
    )

    while True:

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            break

        messages.extend(
            response.output
        )

        for function_call in function_calls:

            tool_name = function_call.name

            arguments = json.loads(
                function_call.arguments
            )

            if tool_name == "get_order_details":

                result = secure_get_order_details(
                    order_id=arguments[
                        "order_id"
                    ],
                    user_id=user_id,
                    db=db
                )

            elif tool_name == "get_customer_details":

                result = secure_get_customer_details(
                    user_id=user_id,
                    db=db
                )

            elif tool_name == "get_customer_orders":

                result = secure_get_customer_orders(
                    user_id=user_id,
                    db=db
                )

            elif tool_name == "search_knowledge":

                result = search_knowledge(
                    arguments[
                        "question"
                    ]
                )

            else:

                result = {
                    "error": "Unknown tool"
                }

            messages.append({
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": json.dumps(result)
            })

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=instructions,
            input=messages,
            tools=tools
        )

    final_answer = response.output_text

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=final_answer,
        user_id=user_id,
        db=db
    )

    return final_answer


# =========================================================
# TEST AGENT
# =========================================================

@app.post("/test-agent")
@limiter.limit("10/minute")
def test_agent(
    request: Request,
    agent_request: AgentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    return {
        "response": run_order_agent(
            message=agent_request.message,
            conversation_id=(
                agent_request.conversation_id
            ),
            db=db,
            user_id=user_id
        )
    }


# =========================================================
# TEST ORDER TOOL
# =========================================================

@app.get(
    "/test-order-tool/{order_id}"
)
def test_order_tool(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    return secure_get_order_details(
        order_id=order_id,
        user_id=user_id,
        db=db
    )


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
@limiter.limit("10/minute")
def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="User ID missing from token."
        )

    result = search_knowledge(
        chat_request.message
    )

    return result