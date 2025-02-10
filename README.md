# SoundRiseV2

Welcome to **SoundRiseV2**!  
A modern and sleek platform for beatmaking and music production, providing seamless user authentication and advanced features.

---

## 📄 API Documentation

### **Authentication Endpoints**

---

### **Login**

**Endpoint**:  
`POST /api/auth/login/`

**Request Body**:

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response on Success**:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczOTc5NzY4NywiaWF0IjoxNzM5MTkyODg3LCJqdGkiOiIwYjg2MDE0MTJjYTM0MzgzYjgzMjM2MTQ3NWFlMGQ3YSIsInVzZXJfaWQiOjN9.vT5E4iSrgDFttGnNgoJmG6-888QDn6E5dUZd1A2Sq9o",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MTk0Njg3LCJpYXQiOjE3MzkxOTI4ODcsImp0aSI6IjE1MTAyN2Y2ZGNlODRjZDNiMTEzZTlhNjY3N2JlOThlIiwidXNlcl9pZCI6M30.LRp9aH8P8Xtd5FDb0d11eYscj3O9uIFO4UejpG9LP0s"
}
```

**Response on Error**:

```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### **Register**

**Endpoint**:  
`POST /api/auth/register/`

**Request Body**:

```json
{
  "username": "new_user",
  "email": "newuser@example.com",
  "password": "YourPassword123"
}
```

**Response on Error**:

- **Email Already Exists**:

```json
{
  "email": ["custom user with this email already exists."]
}
```

- **Username Already Exists**:

```json
{
  "username": ["custom user with this username already exists."]
}
```

- **Password Too Short**:

```json
{
  "password": ["Ensure this field has at least 8 characters."]
}
```

- **Password Needs a Digit**:

```json
{
  "password": ["Le mot de passe doit contenir au moins un chiffre."]
}
```

- **Password Needs an Uppercase Letter**:

```json
{
  "password": ["Le mot de passe doit contenir au moins une majuscule."]
}
```

**Response on Success**:

```json
{
  "message": "Inscription réussie. Vérifiez votre email pour activer votre compte."
}
```

---

## ⚙️ Setup Instructions

### **Installation**

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/SoundRiseV2.git
   ```

2. Install dependencies:
   ```bash
   cd SoundRiseV2
   pip install -r requirements.txt
   ```

### **Run the Development Server**

Start the Django server:

```bash
python manage.py runserver
```

### **Testing API**

You can test the API endpoints using tools like **Postman** or **cURL**.

---

## 🧑‍💻 Contributing

We welcome contributions! Feel free to fork this repository and submit a pull request.
