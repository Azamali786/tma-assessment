# TMA Assessment – Python Backend Developer

This is a backend assessment project for **Twisted Mountain Animation**. The project is developed using **Django**, **Graphene-Django** for GraphQL APIs, and includes token-based authentication, pagination, and filtering.

---

## 🚀 Features

- Django + GraphQL API using Graphene
- Token-based authentication (`TokenAuthentication`)
- Cursor-based pagination (Relay-style)
- Filtering support for querysets
- Admin panel access

---

## 🔧 Project Structure

```
tma-assessment/
│
├── manage.py
├── tmaconfig/          # Django project settings
├── your_apps/          # App modules (e.g., ingredients, recipes)
└── staticfiles/        # Collected static files (after running collectstatic)
```

---

## 🧪 How to Test the APIs

### 🔐 Authentication

A superuser has been created using the `createsuperuser` command:

- **Username**: `admin`
- **Password**: `admin`

To obtain the token for authenticated requests:

**POST**:  
`http://44.203.136.51/api/token-auth/`  
**Request Body**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response**:
```json
{
  "token": "<your_token_here>"
}
```

---

### 🧬 Access GraphQL Playground

Once you have the token:

- **GraphQL endpoint**: [`http://44.203.136.51/graphql/`](http://44.203.136.51/graphql/)
- Open this URL in your browser to access the **GraphiQL Playground**
- In the playground, add the following header to your requests:

```
{
  "Authorization": "Token <your_token_here>"
}
```

You can now test all available **queries**, **mutations**, and use **filters** and **cursor-based pagination**.

---

## 📘 Notes

- Static files (including admin panel styles) are served correctly using Nginx.
- Gunicorn is used as the application server and Nginx as the reverse proxy.
- This project follows production-ready best practices for deployment on **AWS EC2**.

---