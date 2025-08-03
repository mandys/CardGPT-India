# Gemini Project Overview: CardGPT

This document provides a high-level overview of the CardGPT project, a full-stack AI assistant for querying Indian credit card terms and conditions.

## 1. Project Purpose

CardGPT is designed to provide users with instant, AI-powered answers about Indian credit cards. It allows users to ask questions in natural language regarding rewards, fees, eligibility, and spending optimization. The project aims to deliver this service using ultra-low-cost AI models.

## 2. Technology Stack

The project is a modern full-stack application with a clear separation between the frontend and backend.

*   **Frontend (`cardgpt-ui/`)**:
    *   **Framework**: React with TypeScript
    *   **Styling**: Tailwind CSS
    *   **State Management**: Zustand and React Context
    *   **Deployment**: Vercel

*   **Backend (`backend/`)**:
    *   **Framework**: FastAPI (Python)
    *   **Database**:
        *   PostgreSQL (Production on Railway)
        *   SQLite (Local Development)
    *   **AI/ML**:
        *   **LLM**: Google Gemini family (including Gemini 2.5 Flash-Lite)
        *   **Search**: Google Vertex AI Search for Retrieval-Augmented Generation (RAG)
    *   **Authentication**: Google OAuth with JWT
    *   **Deployment**: Railway

## 3. Key Features

*   **AI-Powered Chat**: A real-time, streaming chat interface for users to ask questions.
*   **Smart Comparisons**: AI-driven recommendations and comparisons between different credit cards.
*   **Cost Transparency**: The frontend displays live token usage and cost tracking for queries.
*   **Hybrid Database System**: Seamlessly switches between SQLite for local development and PostgreSQL for production.
*   **Query Enhancement**: The backend enhances user queries to improve the accuracy of search results from Vertex AI.
*   **Authentication**: Secure user authentication via Google OAuth, with query limits for guest users.
*   **Admin Interface**: Endpoints for viewing logs, stats, and exporting data for analysis.
*   **User Preferences**: Users can set their preferences for travel, fees, and spending to receive personalized recommendations.
*   **Responsive Design**: A mobile-first design ensures a seamless experience on all devices.

## 4. Project Structure

The project is organized into two main directories:

*   `cardgpt-ui/`: Contains the React frontend application.
    *   `src/components/`: Reusable React components for UI elements like chat bubbles, modals, and layout components.
    *   `src/contexts/`: Application-wide state management for authentication (`AuthContext`) and theme (`ThemeContext`).
    *   `src/hooks/`: Custom React hooks for managing state and logic, including `useStreamingChat` for chat functionality and `useTips` for contextual suggestions.
    *   `src/services/`: API clients (`api.ts`, `streamingApi.ts`) for communicating with the backend.
    *   `src/stores/`: Zustand stores for managing application state, such as `usePreferenceStore` for user preferences.
    *   `src/index.tsx`: The main entry point for the React application, which sets up routing and providers.

*   `backend/`: Contains the FastAPI backend application.
    *   `api/`: Defines the API endpoints for chat (`chat.py`, `chat_stream.py`), authentication (`auth.py`), configuration (`config.py`), and other functionalities.
    *   `services/`: Contains the business logic for different parts of the application, including the LLM service (`llm.py`), authentication service (`auth_service.py`), and Vertex AI retriever (`vertex_retriever.py`).
    *   `models.py`: Pydantic models for request and response validation.
    *   `main.py`: The main entry point for the FastAPI application, which initializes services and sets up middleware.
*   `data/`: Contains the raw JSON data for credit cards, which is used to feed the Vertex AI Search data store.

## 5. Getting Started

To run the project locally, you need to:

1.  **Set up the backend**:
    *   Navigate to the `backend` directory.
    *   Create a virtual environment and install the dependencies from `requirements.txt`.
    *   Set up the necessary environment variables in a `.env` file (e.g., `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`).
    *   Run `./start_backend.sh`.
2.  **Set up the frontend**:
    *   Navigate to the `cardgpt-ui` directory.
    *   Install the dependencies using `npm install`.
    *   Run `./start_frontend.sh`.