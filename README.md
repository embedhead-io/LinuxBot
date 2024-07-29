# LinuxBot Application

## Overview

LinuxBot is a Python-based chat application powered by OpenAI's API, designed to run on Linux systems. It utilizes PyQt5 for the GUI, enabling users to interact with the OpenAI model through a friendly interface. This application serves as a tool to demonstrate the integration of AI into desktop applications.

## Features

- **OpenAI Integration**: Communicate directly with OpenAI's models to generate responses.
- **Customizable UI**: Light and dark themes available, with the ability to toggle between them.
- **Multiple Chats**: Manage multiple chat sessions simultaneously.
- **Threaded Responses**: Utilizes Python threading to ensure the UI remains responsive while processing requests.

## Prerequisites

Before setting up the project, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

## Installation

Follow these steps to set up the LinuxBot application:

1. **Clone the Repository**
   ```
   git clone https://github.com/embedheadio/linuxbot.git
   cd linuxbot
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

To run the application, execute the shell script provided:

```bash
./linuxbot.sh
```

Alternatively, you can run the application directly using Python:

```bash
python3 app/core/run.py
```

## Usage

- **Starting the Application**: Launch the application using the above command.
- **Interacting with the Bot**: Enter your queries in the text box and press send or hit enter.
- **Managing Chats**: Use the sidebar to switch between different chats or start new ones.
- **Toggling Themes**: Switch between light and dark mode using the toggle button in the UI.

## Contributing

Contributions to the LinuxBot project are welcome. Please ensure to follow the existing code style and add unit tests for any new or changed functionality. Fork the repository and submit pull requests for review.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Contact

For bugs, feature requests, or additional questions, please file an issue in the GitHub repository.
