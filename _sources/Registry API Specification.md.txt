## Agent Registry API Specification

### Status Codes

- `SUCCESS`: The operation completed successfully.
- `ERROR`: An error occurred during the operation.

### 1. Add Agent

**Endpoint:** `/add_agent`

**Method:** `POST`

**Description:** Adds an agent to the registry.

**Request Body:**

```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "endpoint": "string",
  "tools": [
    {
      "tool_id": "string",
      "name": "string",
      "description": "string",
      "endpoint": "string"
    }
  ]
}
```

**Response:**

```json
{
  "status": "SUCCESS",
  "agent_id": "string"
}
```

### 2. Update Tools

**Endpoint:** `/update_tools`

**Method:** `PUT`

**Description:** Updates the tools of a registered agent.

**Request Body:**

```json
{
  "agent_id": "string",
  "tools": [
    {
      "tool_id": "string",
      "name": "string",
      "description": "string",
      "endpoint": "string"
    }
  ]
}
```

**Response:**

```json
{
  "status": "SUCCESS",
  "agent_id": "string"
}
```

### 3. Remove Agent

**Endpoint:** `/remove_agent`

**Method:** `DELETE`

**Description:** Removes an agent from the registry.

**Query Parameters:**

- `agent_id`: The ID of the agent to remove.

**Response:**

```json
{
  "status": "SUCCESS",
  "agent_id": "string"
}
```

### 4. Search Agents

**Endpoint:** `/search_agents`

**Method:** `GET`

**Description:** Searches for agents by ID or based on a semantic search of tool descriptions.

**Query Parameters:**

- `agent_id`: The ID of the agent to search for.
- `search_query`: The search query for semantic search based on tool descriptions.

**Response:**

When searching by agent ID:

```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "endpoint": "string",
  "tools": [
    {
      "tool_id": "string",
      "name": "string",
      "description": "string",
      "endpoint": "string"
    }
  ]
}
```

When searching by tool description:

```json
[
  {
    "agent_id": "string",
    "name": "string",
    "description": "string",
    "endpoint": "string",
    "tools": [
      {
        "tool_id": "string",
        "name": "string",
        "description": "string",
        "endpoint": "string"
      }
    ]
  }
]
```

These specifications detail the endpoints, request methods, and input/output formats for the Agent Registry API.
