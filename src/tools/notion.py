import os
from typing import Dict, List, Optional, Union
from notion_client import Client
import src.clients
from src.tool_calling.tool_calling import openai_function_wrapper
import dotenv
import pprint
import src

dotenv.load_dotenv()

notion = Client(auth=os.environ["NOTION_TOKEN"])

# Database IDs
PROJECTS_TABLE_ID = "918affd4ce0d4b8eb7604d972fd24826"
TASKS_TABLE_ID = "ed8ba37a719a47d7a796c2d373c794b9"
DOCUMENTS_TABLE_ID = "55909df81f5640c49327bab99b4f97f5"

# Common Functions
def _format_rich_text(text: str) -> List[Dict]:
    """Helper to format text for Notion API"""
    return [{"type": "text", "text": {"content": text}}]

def _format_title(text: str) -> List[Dict]:
    """Helper to format title for Notion API"""
    return [{"type": "title", "text": {"content": text}}]

# Database Operations
@openai_function_wrapper(
    function_description="Query projects database to get projects that are on-going",
    parameter_descriptions={}
)
def query_projects_database():
    return notion.databases.query(
        database_id=PROJECTS_TABLE_ID,
        filter={
            "and": [
                {
                    "property": "Type",
                    "select": {
                        "equals": "Project"
                    }
                },
                {
                    "property": "Progress",
                    "select": {
                        "equals": "On-Going"
                    }
                }
            ]
        }
    )

@openai_function_wrapper(
    function_description="Create a new database",
    parameter_descriptions={
        "title": "Title of the database",
        "parent_page_id": "ID of the parent page",
        "properties": "Dictionary of database properties"
    }
)
def create_database(title: str, parent_page_id: str, properties: Dict):
    return notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=_format_title(title),
        properties=properties
    )

@openai_function_wrapper(
    function_description="Update database properties",
    parameter_descriptions={
        "database_id": "ID of the database to update",
        "properties": "New properties configuration"
    }
)
def update_database(database_id: str, properties: Dict):
    return notion.databases.update(
        database_id=database_id,
        properties=properties
    )

# Page Operations
@openai_function_wrapper(
    function_description="Create a new page in a database",
    parameter_descriptions={
        "database_id": "ID of the database",
        "properties": "Page properties matching database schema",
        "content": "Optional content blocks for the page"
    }
)
def create_page(database_id: str, properties: Dict, content: Optional[List[Dict]] = None):
    page = notion.pages.create(
        parent={"database_id": database_id},
        properties=properties
    )
    
    if content:
        notion.blocks.children.append(
            block_id=page["id"],
            children=content
        )
    return page

@openai_function_wrapper(
    function_description="Update a page's properties",
    parameter_descriptions={
        "page_id": "ID of the page to update",
        "properties": "New properties values"
    }
)
def update_page(page_id: str, properties: Dict):
    return notion.pages.update(
        page_id=page_id,
        properties=properties
    )

@openai_function_wrapper(
    function_description="Archive (delete) a page",
    parameter_descriptions={
        "page_id": "ID of the page to archive"
    }
)
def archive_page(page_id: str):
    return notion.pages.update(
        page_id=page_id,
        archived=True
    )


# Block Operations
@openai_function_wrapper(
    function_description="Add blocks to a page",
    parameter_descriptions={
        "page_id": "ID of the page",
        "blocks": "List of block objects to add"
    }
)
def add_blocks(page_id: str, blocks: List[Dict]):
    return notion.blocks.children.append(
        block_id=page_id,
        children=blocks
    )

@openai_function_wrapper(
    function_description="Update a block's content",
    parameter_descriptions={
        "block_id": "ID of the block to update",
        "block_content": "New content for the block"
    }
)
def update_block(block_id: str, block_content: Dict):
    return notion.blocks.update(
        block_id=block_id,
        **block_content
    )

@openai_function_wrapper(
    function_description="Delete a block",
    parameter_descriptions={
        "block_id": "ID of the block to delete"
    }
)
def delete_block(block_id: str):
    return notion.blocks.delete(block_id=block_id)

# Search Operations
@openai_function_wrapper(
    function_description="Search across all content",
    parameter_descriptions={
        "query": "Search query string",
        "filter": "Optional filter parameters"
    }
)
def search_notion(query: str, filter: Optional[Dict] = None):
    params = {"query": query}
    if filter:
        params["filter"] = filter
    return notion.search(**params)

# Original Project-specific Functions
@openai_function_wrapper(
    function_description="Query tasks database to get tasks for a project",
    parameter_descriptions={"project_id": "The project ID to get tasks for"}
)
def get_project_tasks(project_id: str):
    return notion.databases.query(
        database_id=TASKS_TABLE_ID,
        filter={
            "property": "Event/Project",
            "relation": {
                "contains": project_id
            }
        }
    )

@openai_function_wrapper(
    function_description="Query documents database to get documents for a project",
    parameter_descriptions={"project_id": "The project ID to get documents for"}
)
def get_project_documents(project_id: str):
    return notion.databases.query(
        database_id=DOCUMENTS_TABLE_ID,
        filter={
            "property": "Events/Projects",
            "relation": {
                "contains": project_id
            }
        }
    )

@openai_function_wrapper(
    function_description="Read inside a document",
    parameter_descriptions={"document_id": "The document ID to read"}
)
def read_document(document_id: str):
    return notion.blocks.children.list(block_id=document_id)

def local():
    """Local testing function"""
    client = src.ClientOpenAI.create_openai(os.getenv("OPENAI_API_KEY"))
    engine = src.main.engine.ToolEngine(client, "gpt-4")
    
    # Register all tools
    tools = [
        query_projects_database, create_database, update_database,
        create_page, update_page, archive_page,
        add_blocks, update_block, delete_block,
        search_notion, get_project_tasks, get_project_documents,
        read_document
    ]
    
    for tool in tools:
        engine.add_tool(tool)
    
    # Test queries
    test_queries = [
        "Is there an ongoing project called Notion LLM Read Test?",
        "Can you get all the tasks for this project?",
        "Can you name all the documents for this project?",
        "Can you read the contents of how to rule the world? What is the 2nd step?"
    ]
    
    for query in test_queries:
        engine.add_instruction(query)
        engine.run()
        pprint.pprint(engine.store.chat_history[-1]["content"])

if __name__ == "__main__":
    local()
