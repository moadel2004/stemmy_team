# STEMMY: The Emotion-Aware AI STEM Tutor

Welcome to STEMMY! This is an intelligent tutoring system designed to help users learn STEM subjects by adapting to their emotional state.

This guide will help you set up and run the project on your local machine.

---

## How It Works

The project has two main parts that work together:
1.  **Backend (Python/FastAPI):** An API server that handles all the logic. It runs on `http://localhost:8000`.
2.  **Frontend (React/JavaScript ):** A web interface in the `Chatbot-UI` folder that the user interacts with. It runs on `http://localhost:3000`.

The frontend sends requests to the backend, which then communicates with the OpenAI API to generate intelligent responses.

---

## 🚀 Getting Started: Running the Project Locally

Follow these steps carefully to run the entire application on your computer.

### **Step 1: Prerequisites (What you need first )**

- **Python 3.10+**
- **Node.js and npm**
- **Git**
- An **OpenAI API Key**. You can get one from the [OpenAI Platform](https://platform.openai.com/account/api-keys ).

### **Step 2: Clone the Repository**

Open your terminal or command prompt and run this command:
```bash
git clone https://github.com/moadel2004/stemmy_team.git
cd stemmy_team
```

### **Step 3: Set Up the Backend (The "Brain" )**

1.  **Create a Python Virtual Environment:** This isolates the project's dependencies.
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **❗ IMPORTANT: Configure Your API Keys**

    The application cannot work without your OpenAI API keys. You must provide them in a special file that is kept private on your machine.

    - In the main project folder (`stemmy_team`), create a **new file** and name it exactly **`.env`**.
    - Open this new `.env` file with your code editor.
    - Copy and paste the following lines into it, replacing the placeholder text with your actual keys:

      ```env
      # This file stores your secret keys. It will NOT be uploaded to GitHub.
      OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      OPENAI_PROJECT="proj_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      ```

    > **Why do we do this?** The `.gitignore` file is configured to ignore `.env` files, ensuring your secret keys are **never** accidentally uploaded to GitHub. This is a critical security practice.

4.  **Run the Backend Server:**
    ```bash
    uvicorn backend_api:app --host 0.0.0.0 --port 8000 --reload
    ```
    Leave this terminal window open. The backend is now running and listening for requests on `http://localhost:8000`.

### **Step 4: Set Up the Frontend (The "Face" )**

1.  **Open a new, separate terminal window.**
2.  **Navigate to the Frontend Directory:**
    ```bash
    cd Chatbot-UI
    ```

3.  **Install JavaScript Dependencies:**
    ```bash
    npm install
    ```

4.  **Run the Frontend Application:**
    ```bash
    npm start
    ```
    This command will automatically open a new tab in your web browser with the address `http://localhost:3000`.

---

## ✅ You're All Set!

If you have followed all the steps, you should now have:
- A terminal window running the backend server.
- Another terminal window running the frontend server.
- Your web browser open at `http://localhost:3000`, showing the STEMMY chat interface.

You can now start interacting with your local version of the STEMMY AI Tutor!
