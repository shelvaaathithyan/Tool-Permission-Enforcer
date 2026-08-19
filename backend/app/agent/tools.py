# Define the strict tools available to the Agent

agent_tools = [
    {
        "name": "search_customers",
        "description": "Search for customers by name, email, or other text.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search term."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_customer",
        "description": "Get detailed information about a specific customer by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique ID of the customer, or their name if ID is not known."
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "list_customers",
        "description": "List all customers, with optional pagination.",
        "parameters": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "description": "The page number.",
                    "default": 1
                },
                "page_size": {
                    "type": "integer",
                    "description": "Items per page.",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "create_customer",
        "description": "Create a new customer record.",
        "parameters": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "company": {"type": "string"},
                "designation": {"type": "string"}
            },
            "required": ["first_name", "last_name", "email"]
        }
    },
    {
        "name": "update_customer",
        "description": "Update an existing customer record.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique ID of the customer to update, or their name if ID is not known."
                },
                "fields": {
                    "type": "object",
                    "description": "The fields to update (first_name, last_name, email, phone, company, designation).",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "company": {"type": "string"},
                        "designation": {"type": "string"}
                    }
                }
            },
            "required": ["customer_id", "fields"]
        }
    },
    {
        "name": "delete_customer",
        "description": "Delete a customer record.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique ID of the customer to delete, or their name if ID is not known."
                }
            },
            "required": ["customer_id"]
        }
    }
]

# Map tools to their corresponding operation and resource
TOOL_METADATA = {
    "search_customers": {"operation": "READ", "resource": "CUSTOMER"},
    "get_customer": {"operation": "READ", "resource": "CUSTOMER"},
    "list_customers": {"operation": "READ", "resource": "CUSTOMER"},
    "create_customer": {"operation": "CREATE", "resource": "CUSTOMER"},
    "update_customer": {"operation": "UPDATE", "resource": "CUSTOMER"},
    "delete_customer": {"operation": "DELETE", "resource": "CUSTOMER"},
}
