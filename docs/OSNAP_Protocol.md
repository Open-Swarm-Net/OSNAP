## 1. OSNAP Protocol

This paper proposes a communication protocol designed specifically for OutboundAgents in an AI-driven multi-agent system. The protocol defines a standardized message structure, various message types, and the processes for handling communication between agents. The purpose of this protocol is to facilitate efficient and effective communication between AI agents, enabling them to collaborate, delegate tasks, and share information.

## 2. Background

OutboundAgents are AI systems that have tools they can execute on behalf of a user. These tools might include gathering information, performing tasks, or interacting with other agents to complete complex actions. In order to collaborate effectively and efficiently, agents need a well-defined communication protocol that allows them to exchange messages, delegate tasks, and share status updates.

## 3. Protocol Design

### 3.1 Message Structure

To facilitate efficient communication between agents, we propose a standardized message structure that includes the following components: sender and receiver agent identifiers, message type, payload, and metadata. This structure ensures that each message exchanged between agents is organized, easily parsed, and extensible to accommodate future changes in agent communication requirements.

#### 3.1.1 Components of the Message Structure

1. Sender Agent Identifier
2. Receiver Agent Identifier
3. Message Type
4. Payload
5. Metadata

#### 3.1.2 Example of Message Structure

```json
{
  "sender_agent_id": "agent-123",
  "receiver_agent_id": "agent-456",
  "message_type": "task_request",
  "payload": {
    "task_id": "task-789",
    "task_name": "schedule_meeting",
    "task_data": {
      "participants": ["personA@example.com", "personB@example.com"],
      "date": "2023-05-01",
      "time": "14:00"
    }
  },
  "metadata": {
    "timestamp": "2023-04-29T10:30:00Z",
    "priority": "medium"
  }
}
```


#### 3.1.3 Benefits of the Proposed Message Structure

1. Standardization
2. Extensibility
3. Readability
4. Platform Independence

### 3.2 Message Types

The protocol supports a variety of message types to cater to different aspects of agent communication. These message types include request, response, task execution, status updates, and error handling. Each message type serves a specific purpose and is crucial for efficient agent interaction.

1. Request
2. Response
3. Task Execution
4. Status Update
5. Error Handling

#### 3.2.1 Examples of Message Types

* Request Message Example

```json
{
  "sender_agent_id": "agent-123",
  "receiver_agent_id": "agent-456",
  "message_type": "request",
  "payload": {
    "request_id": "request-789",
    "request_action": "get_weather",
    "request_data": {
      "location": "New York",
      "date": "2023-05-01"
    }
  },
  "metadata": {
    "timestamp": "2023-04-29T10:30:00Z",
    "priority": "medium"
  }
}
```


* Response Message Example

```json
{
  "sender_agent_id": "agent-456",
  "receiver_agent_id": "agent-123",
  "message_type": "response",
  "payload": {
    "request_id": "request-789",
    "status": "success",
    "response_data": {
      "temperature": "72°F",
      "weather_condition": "Sunny"
    }
  },
  "metadata": {
    "timestamp": "2023-04-29T10:32:00Z"
  }
}
```

* Task Execution Message Example
  
```json
{
  "sender_agent_id": "agent-123",
  "receiver_agent_id": "agent-456",
  "message_type": "task_execution",
  "payload": {
    "task_id": "task-789",
    "task_invoke_url": "https://example.com/agent-456/task/789",
    "task_name": "schedule_meeting",
    "task_data": {
      "participants": ["personA@example.com", "personB@example.com"],
      "date": "2023-05-01",
      "time": "14:00"
    }
  },
  "metadata": {
    "timestamp": "2023-04-29T10:30:00Z",
    "priority": "high"
  }
}
```


* Status Update Message Example
```json
{
  "sender_agent_id": "agent-456",
  "receiver_agent_id": "agent-123",
  "message_type": "status_update",
  "payload": {
    "task_id": "task-789",
    "task_status": "completed",
    "task_result": {
      "meeting_url": "https://example.com/meeting/12345"
    }
  },
  "metadata": {
    "timestamp": "2023-04-29T10:35:00Z"
  }
}
```


* Error Handling Message Example
```json
{
  "sender_agent_id": "agent-456",
  "receiver_agent_id": "agent-123",
  "message_type": "error_handling",
  "payload": {
    "request_id": "request-789",
    "error_code": "1001",
    "error_description": "Failed to fetch weather data",
    "additional_info": "API key is invalid"
  },
  "metadata": {
    "timestamp": "2023-04-29T10:33:00Z"
  }
}
```

### 3.3 Agents Query and Response

Providing an endpoint to get a list of available agents is required to implement the protocol. This endpoint can be used by agents to discover other agents and their tools. To enable this functionality, we can introduce a new message type called "agents_query" and its corresponding response message, "agents_response".

1. Agents Query
GET /agents

?capability=example_capability
?scope=public|private


2. Agents Response
```json
[
  {
    "agent_id": "f287b6e8-8a67-4c10-9a45-12a05a8f1b87",
    "agent_name": "Example Agent",
    "agent_description": "Does lots of nice agent things",
    "agent_endpoint": "https://example.com/run/f287b6e8-8a67-4c10-9a45-12a05a8f1b87",
    "tools": {
      "example_capability": {
        "description": "An example capability.",
        "plugin": "ExamplePlugin"
      }
    },
    "scope": "public"
  },
  {
    "agent_id": "184755d2-2f40-4563-96a9-9d30fd6b69ca",
    "tools": {
      "example_capability": {
        "description": "Another example capability.",
        "plugin": "AnotherExamplePlugin"
      }
    },
    "scope": "private",
    "authorized_agents": ["c6a2f2e9-0689-4e7d-8a04-6b3abefc1e3d"]
  }
]
```

### 3.4 Tools Query and Response

To enable agents to query the tools of other agents, we can introduce a new message type called "tools_query" and its corresponding response message, "tools_response". These messages allow agents to request and provide information about their supported tools, tasks, and SLAs.

1. Get All Agent Tools Query
   
```json
{
  "sender_agent_id": "agent-123",
  "receiver_agent_id": "agent-456",
  "message_type": "tools_query",
  "metadata": {
    "timestamp": "2023-04-29T10:30:00Z",
    "priority": "low",
    "order": 1
  }
}
```

1. Get All Agent Tools Response

```json
{
  "sender_agent_id": "agent-456",
  "receiver_agent_id": "agent-123",
  "message_type": "tools_response",
  "payload": {
    "information_tools": [
      {
        "name": "get_weather",
        "description": "Provides weather information for a given location and date",
        "request_format": {
          "location": "string",
          "date": "string (YYYY-MM-DD)"
        }
      }
    ],
    "task_tools": [
      {
        "name": "schedule_meeting",
        "description": "Schedules a meeting with the specified participants, date, and time",
        "request_format": {
          "participants": "list of email addresses",
          "date": "string (YYYY-MM-DD)",
          "time": "string (HH:mm)"
        },
        "SLA": "60 minutes"
      }
    ]
  },
  "metadata": {
    "timestamp": "2023-04-29T10:32:00Z"
  }
}
```

## 4. Conclusion

The proposed agent communication protocol provides a standardized and efficient means for AI agents to collaborate, delegate tasks, and share information within a multi-agent system. By implementing this protocol, AI systems can dynamically discover the tools of other agents and work together to complete complex tasks and actions


