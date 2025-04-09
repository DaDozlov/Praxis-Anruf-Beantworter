# SWPWS24_Praxis-Anrufbeantworter-Transkription

## Getting started and Prerequisites

Ensure you have the following software installed on your system:
- **Python 3.10+** (For Python setup and dependencies)
- **Node.js** and **npm** (For the React frontend setup)
- **Poetry** (For managing Python dependencies)
- **Linux** (For example WSL Ubuntu or similar)
- **Ollama** (For LLM local requests)

### To install Node.js and npm, run:
```bash
sudo apt update
sudo apt install nodejs npm
```

### To install Ollama:
```bash
curl -sSfL https://ollama.ai/install.sh | sh
```

### To install Torch for CPU and FFMPEG (needed for Whisper):
```bash
sudo apt update && sudo apt install ffmpeg
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### To install poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Installation:

### Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

## Python Backend Setup

1. **Create a virtual environment using Python 3.12:**

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies using Poetry:**

   ```bash
   poetry install
   ```

3. **Install pre-commit hooks for code formatting and linting:**

   ```bash
   poetry run pre-commit install
   ```

## React Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install the required npm packages:**

   ```bash
   npm install
   npm install axios
   npm install @types/axios --save-dev
   ```

3. **Optionally, run `npm audit fix`:**

   ```bash
   npm audit fix
   ```

## Running the Application (Backend and Frontend at the same time)

### 1. Enable concurrent application start.

```bash
npm install concurrently --save-dev
```

### 2. Start the App

Open a new terminal and navigate to the `frontend` directory and start the servers.

```bash
cd frontend/
npm run dev
```

The frontend should now be running on `http://localhost:3000`
The backend should now be running on `http://localhost:5000`


---

## To add a new python library use:
```bash
poetry add name_of_library
```

## How to merge your PR/Branch to the Main:

### 1. Switch to the Main Branch
Run the following command to switch to the `main` branch:
```bash
git checkout Main
```

### 2. Pull all the latest changes from main

```bash
git pull
```

### 3. Switch to your branch

```bash
git checkout <your-branch-name>
```

### 4. Bring the latest changes from main into your branch

```bash
git merge Main
```

### 5. Push the changes to the GitLab

```bash
git push
```

Then all is left in GitLab:

- Click "Create merge request".
- Set your branch as the source branch and main as the target branch.
- Link your created issue and current milestone
- Merge (and after it will be merged to Main be sure that it is not shown anymore)


## Other Git Examples usages

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab2.informatik.uni-wuerzburg.de/softwarepraktikum/swpws24_praxis-anrufbeantworter-transkription.git
git branch -M main
git push -uf origin main
```
