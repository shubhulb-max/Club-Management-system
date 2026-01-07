# Cricket Club Management API

This repository hosts the backend for the Cricket Club Management System, built with Django and Django Rest Framework. The API handles data management for players, teams, matches, tournaments, grounds, financials, and inventory.

## Authentication

The API uses Token Authentication. To authenticate requests, include the `Authorization` header with the token obtained from the `/api-token-auth/` endpoint.

**Header Format:**
```
Authorization: Token <your_token>
```

## API Endpoints

All API endpoints are prefixed with `/api/`.

### 1. Players
**Endpoint:** `/api/players/`

*   **GET**: List all players.
*   **POST**: Create a new player.
*   **PUT/PATCH**: Update player details.
*   **DELETE**: Remove a player.

**Request Payload (POST/PUT):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 25,
  "role": "Batsman",
  "profile_picture": null,
  "phone_number": "1234567890"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "age": 25,
  "role": "Batsman",
  "profile_picture": "http://localhost:8000/media/players/profile.jpg",
  "phone_number": "1234567890",
  "membership_active": true
}
```
*Note: `membership_active` is read-only.*

### 2. Teams
**Endpoint:** `/api/teams/`

*   **GET**: List all teams.
*   **POST**: Create a new team.
*   **PUT/PATCH**: Update team details.
*   **DELETE**: Remove a team.

**Request Payload (POST/PUT):**
```json
{
  "name": "Thunderbolts",
  "captain": 1
}
```
*Note: `captain` is the ID of a player.*

**Response Payload:**
```json
{
  "id": 1,
  "name": "Thunderbolts",
  "captain": 1,
  "players": [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "..." : "..."
    }
  ]
}
```
*Note: `players` list is read-only and populated based on team assignments.*

### 3. Matches
**Endpoint:** `/api/matches/`

*   **GET**: List all matches.
*   **POST**: Schedule a new match.
*   **PUT/PATCH**: Update match details (e.g., result).
*   **DELETE**: Cancel a match.

**Request Payload (POST/PUT):**
```json
{
  "team1": 1,
  "team2": 2,
  "external_opponent": null,
  "ground": 1,
  "date": "2023-10-27T10:00:00Z",
  "result": "Team 1 won by 20 runs",
  "winner": 1
}
```
*Validation Rule: A match must have either `team2` (for internal matches) OR `external_opponent` (string name for external matches), but NOT both.*

**Response Payload:**
```json
{
  "id": 1,
  "team1": 1,
  "team2": 2,
  "external_opponent": null,
  "ground": 1,
  "date": "2023-10-27T10:00:00Z",
  "result": "Team 1 won by 20 runs",
  "winner": 1
}
```

### 4. Tournaments
**Endpoint:** `/api/tournaments/`

*   **GET**: List all tournaments.
*   **POST**: Create a new tournament.
*   **PUT/PATCH**: Update tournament details.
*   **DELETE**: Cancel a tournament.

**Request Payload (POST/PUT):**
```json
{
  "name": "Summer Cup 2023",
  "start_date": "2023-11-01",
  "entry_fee": "50.00"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "name": "Summer Cup 2023",
  "start_date": "2023-11-01",
  "entry_fee": "50.00",
  "participants": []
}
```

### 5. Tournament Participations
**Endpoint:** `/api/tournament-participations/`

Registers a player for a tournament.

**Request Payload (POST):**
```json
{
  "player": 1,
  "tournament": 1
}
```

**Response Payload:**
```json
{
  "id": 1,
  "player": 1,
  "tournament": 1
}
```

### 6. Grounds
**Endpoint:** `/api/grounds/`

*   **GET**: List all grounds.
*   **POST**: Add a new ground.
*   **PUT/PATCH**: Update ground details.
*   **DELETE**: Remove a ground.

**Request Payload (POST/PUT):**
```json
{
  "name": "Main Stadium",
  "location": "123 Cricket Lane"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "name": "Main Stadium",
  "location": "123 Cricket Lane"
}
```

### 7. Transactions
**Endpoint:** `/api/transactions/`

Tracks financial transactions (fees, payments, etc.).

**Request Payload (POST/PUT):**
```json
{
  "player": 1,
  "category": "monthly",
  "amount": "100.00",
  "due_date": "2023-10-31",
  "paid": false,
  "payment_date": null
}
```
*Categories examples: 'monthly', 'registration', 'tournament', 'merchandise'.*

**Response Payload:**
```json
{
  "id": 1,
  "player": 1,
  "category": "monthly",
  "amount": "100.00",
  "due_date": "2023-10-31",
  "paid": false,
  "payment_date": null
}
```

### 8. Inventory Items
**Endpoint:** `/api/inventory-items/`

**Request Payload (POST/PUT):**
```json
{
  "name": "Cricket Bat",
  "description": "Professional Willow Bat",
  "quantity": 10,
  "price": "150.00",
  "type": "equipment"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "name": "Cricket Bat",
  "description": "Professional Willow Bat",
  "quantity": 10,
  "price": "150.00",
  "type": "equipment"
}
```

### 9. Item Assignments
**Endpoint:** `/api/item-assignments/`

Assigns inventory items to teams (e.g., kits).

**Request Payload (POST):**
```json
{
  "item": 1,
  "team": 1,
  "quantity_assigned": 5,
  "date_assigned": "2023-10-27"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "item": 1,
  "team": 1,
  "quantity_assigned": 5,
  "date_assigned": "2023-10-27"
}
```

### 10. Sales
**Endpoint:** `/api/sales/`

Records sales of inventory items to players.

**Request Payload (POST):**
```json
{
  "item": 1,
  "player": 1,
  "quantity_sold": 1,
  "sale_date": "2023-10-27"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "item": 1,
  "player": 1,
  "quantity_sold": 1,
  "sale_date": "2023-10-27"
}
```
