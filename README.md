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

## GraphQL Queries & Mutations Examples

### Get list of ingredients
```graphql
query {
  allIngredients {
    edges {
      cursor
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

### Get list of recipes with ingredients and ingredient count
```graphql
query {
  allRecipes {
    edges {
      node {
        id
        title
        ingredientCount
        ingredients {
          edges {
            node {
              id
              name
            }
          }
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Get details of a recipe using ID
```graphql
query {
  recipe(id: "UmVjaXBlVHlwZTo0") {
    id
    title
    ingredients {
      edges {
        node {
          id
          name
        }
      }
    }
    ingredientCount
  }
}
```

---

### Create ingredient
```graphql
mutation {
  createIngredient(name: "third ingredient") {
    ingredient {
      id
      name
    }
  }
}
```

### Update ingredient
```graphql
mutation {
  updateIngredient(id: "SW5ncmVkaWVudFR5cGU6NA==", name: "latest ingredient updated one") {
    ingredient {
      id
      name
    }
  }
}
```

### Delete ingredient
```graphql
mutation {
  deleteIngredient(id: "SW5ncmVkaWVudFR5cGU6Mw==") {
    success
  }
}
```

---

### Create recipe and connect ingredients
```graphql
mutation {
  createRecipe(title: "Third Test Recipe", ingredientIds: ["SW5ncmVkaWVudFR5cGU6Mg==", "SW5ncmVkaWVudFR5cGU6Mw=="]) {
    recipe {
      id
      title
      ingredients {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
}
```

---

### Add ingredients to recipe
```graphql
mutation {
  addIngredientsToRecipe(recipeId: "UmVjaXBlVHlwZTo0", ingredientIds: ["SW5ncmVkaWVudFR5cGU6Mg==", "SW5ncmVkaWVudFR5cGU6Ng=="]) {
    recipe {
      id
      ingredients {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
}
```

---

### Remove ingredient from recipe
```graphql
mutation {
  removeIngredientsFromRecipe(recipeId: "UmVjaXBlVHlwZTo0", ingredientIds: ["SW5ncmVkaWVudFR5cGU6Ng=="]) {
    recipe {
      id
      ingredients {
        edges {
          node {
            id
            name
          }
        }
      }
    }
  }
}
```

---

**Note:**  
- The IDs like `UmVjaXBlVHlwZTo0` or `SW5ncmVkaWVudFR5cGU6Mg==` are Relay-style global IDs and need to be used as-is.
- Use the GraphiQL interface for easy exploration and testing.

---

Thank you for testing the APIs!

---

## 📘 Notes

- Static files (including admin panel styles) are served correctly using Nginx.
- Gunicorn is used as the application server and Nginx as the reverse proxy.
- This project follows production-ready best practices for deployment on **AWS EC2**.

---