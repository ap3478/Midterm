1. Install Homebrew (Mac Only)

Skip this step if you're on Windows.
Homebrew is a package manager for macOS.
You’ll use it to easily install Git, Python, Docker, etc.

Install Homebrew:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Verify Homebrew:

brew --version
If you see a version number, you're good to go.

🧩 2. Install and Configure Git

Install Git

MacOS (using Homebrew)
brew install git
Windows
Download and install Git for Windows.
Accept the default options during installation.

Verify Git:

git --version
Configure Git Globals

Set your name and email so Git tracks your commits properly:

git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
Confirm the settings:

git config --list
Generate SSH Keys and Connect to GitHub

Only do this once per machine.
Generate a new SSH key:
ssh-keygen -t ed25519 -C "your_email@example.com"
(Press Enter at all prompts.)

Start the SSH agent:
eval "$(ssh-agent -s)"
Add the SSH private key to the agent:
ssh-add ~/.ssh/id_ed25519
Copy your SSH public key:
Mac/Linux:
cat ~/.ssh/id_ed25519.pub | pbcopy
Windows (Git Bash):
cat ~/.ssh/id_ed25519.pub | clip
Add the key to your GitHub account:

Go to GitHub SSH Settings
Click New SSH Key, paste the key, save.
Test the connection:

ssh -T git@github.com
You should see a success message.


🛠️ 3. Install Python 3.10+

Install Python

MacOS (Homebrew)
brew install python
Windows
Download and install Python for Windows.
✅ Make sure you check the box Add Python to PATH during setup.

Verify Python:

python3 --version
or

python --version
Create and Activate a Virtual Environment

(Optional but recommended)

python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
Install Required Packages

pip install -r requirements.txt

🚀 4. Running the Project

Without Docker:
python main.py
(or update this if the main script is different.)

With Docker:
docker run -it --rm <image-name>
📝 5. Submission Instructions

After finishing your work:

git add .
git commit -m "Complete Module X"
git push origin main
Then submit the GitHub repository link as instructed.

🔥 Useful Commands Cheat Sheet

Action	Command
Install Homebrew (Mac)	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Install Git	brew install git or Git for Windows installer
Configure Git Global Username	git config --global user.name "Your Name"
Configure Git Global Email	git config --global user.email "you@example.com"
Clone Repository	git clone <repo-url>
Create Virtual Environment	python3 -m venv venv
Activate Virtual Environment	source venv/bin/activate / venv\Scripts\activate.bat
Install Python Packages	pip install -r requirements.txt
Build Docker Image	docker build -t <image-name> .
Run Docker Container	docker run -it --rm <image-name>
Push Code to GitHub	git add . && git commit -m "message" && git push
