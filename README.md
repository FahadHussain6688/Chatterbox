# ChatterBox

ChatterBox is a real-time chat web application built with Django, Django Channels, and PostgreSQL. It supports 1-to-1 messaging, user presence, WhatsApp-style status sharing, and user profiles with avatars and bios.

## Features

- Real-time 1-to-1 chat
- User presence and online status
- Status sharing (à la WhatsApp)
- User profiles with avatars and bios
- REST API endpoints for chat and status management

## Tech Stack

- Django & Django Channels
- Daphne ASGI server
- PostgreSQL
- Pillow (image handling)
- python-decouple (environment variables)

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update values as needed.

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## License

This project is licensed under the MIT License.
