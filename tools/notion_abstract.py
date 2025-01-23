import os
from typing import Dict, List, Optional, Any
from notion_client import Client

from src.framework.tool_calling import openai_function_wrapper

# Instantiate your Notion client. Expect that NOTION_TOKEN is set in your environment.
notion = Client(auth=os.environ.get("NOTION_TOKEN"))

def _format_rich_text(text: str) -> List[Dict[str, Any]]:
    """
    Helper to format rich text content for the Notion API.
    """
    return [{"type": "text", "text": {"content": text}}]

def _format_title(text: str) -> List[Dict[str, Any]]:
    """
    Helper to format a title property for the Notion API.
    """
    return [{"type": "text", "text": {"content": text}}]


# --------------------------------------------------------------------
# 1) Databases
# --------------------------------------------------------------------

@openai_function_wrapper(
    funct_descript="Retrieve the schema (structure and properties) of a Notion database by ID.",
    param_descript={
        "database_id": "The ID of the database to retrieve the schema for"
    }
)
def get_database_schema(database_id: str) -> dict:
    """
    Retrieve the schema of a Notion database, including its title, description,
    and property configurations.

    Args:
        database_id (str): The ID of the database to retrieve

    Returns:
        dict: The full database object containing its schema and metadata
    """
    return notion.databases.retrieve(database_id=database_id)

@openai_function_wrapper(
    funct_descript="Query a Notion database by ID, with optional filter, sorts, start_cursor, and page_size.",
    param_descript={
        "database_id": "The Notion database ID to query",
        "filter": "(Optional) A Notion filter object (dict) to narrow results",
        "sorts": "(Optional) A list of sorting instructions (dicts) for the query",
        "start_cursor": "(Optional) Cursor to paginate from",
        "page_size": "(Optional) Maximum number of results to return"
    }
)
def query_database(
        database_id: str,
        filter: Optional[dict] = None,
        sorts: Optional[list] = None,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None
) -> dict:
    """
    Query a Notion database with optional filter, sorts, start cursor, and page size.
    """
    query_kwargs = {
        "database_id": database_id
    }
    if filter is not None:
        query_kwargs["filter"] = filter
    if sorts is not None:
        query_kwargs["sorts"] = sorts
    if start_cursor is not None:
        query_kwargs["start_cursor"] = start_cursor
    if page_size is not None:
        query_kwargs["page_size"] = page_size

    return notion.databases.query(**query_kwargs)


@openai_function_wrapper(
    funct_descript="Create a new Notion database under a given parent page, with a title and properties.",
    param_descript={
        "parent_page_id": "The ID of the parent page under which the database will be created",
        "title": "The title of the new database",
        "properties": "A dictionary describing the database's property schema"
    }
)
def create_database(parent_page_id: str, title: str, properties: dict) -> dict:
    """
    Create a new Notion database under a given parent page.
    Example 'properties':
        {
          'Name': {
            'title': {}
          },
          'Tags': {
            'multi_select': {}
          }
        }
    """
    return notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=_format_title(title),
        properties=properties
    )


@openai_function_wrapper(
    funct_descript="Update a Notion database's properties or title by passing a new property schema.",
    param_descript={
        "database_id": "The database ID to update",
        "properties": "A dictionary with updated properties configuration (title, etc.)"
    }
)
def update_database(database_id: str, properties: dict) -> dict:
    """
    Update an existing Notion database (title, properties, etc.).
    """
    return notion.databases.update(
        database_id=database_id,
        properties=properties
    )


# --------------------------------------------------------------------
# 2) Pages
# --------------------------------------------------------------------

@openai_function_wrapper(
    funct_descript="Retrieve a page's metadata (properties, parent, etc.) by ID.",
    param_descript={
        "page_id": "ID of the page to retrieve"
    }
)
def retrieve_page(page_id: str) -> dict:
    """
    Retrieve metadata and properties of a single Notion page.
    """
    return notion.pages.retrieve(page_id=page_id)

@openai_function_wrapper(
    funct_descript="Create a new Notion page in a given database (or under a page) with properties and optional content blocks.",
    param_descript={
        "parent_id": "The database_id (or page_id) where this page should be created",
        "is_database_parent": "True if parent_id is a database, False if it's a page",
        "properties": "A dictionary of Notion properties that match the schema of the parent DB or page",
        "blocks": "Optional list of content blocks to attach to this page"
    }
)
def create_page(
        parent_id: str,
        is_database_parent: bool,
        properties: dict,
        blocks: Optional[List[dict]] = None
) -> dict:
    """
    Create a new page either inside a database or as a child page.
    If `is_database_parent` is True, `parent_id` is a database_id.
    If `is_database_parent` is False, `parent_id` is a page_id.
    """
    parent_dict = {}
    if is_database_parent:
        parent_dict = {"database_id": parent_id}
    else:
        parent_dict = {"page_id": parent_id}

    page = notion.pages.create(
        parent=parent_dict,
        properties=properties
    )

    # If blocks are provided, append them to the page
    if blocks:
        notion.blocks.children.append(
            block_id=page["id"],
            children=blocks
        )

    return page


@openai_function_wrapper(
    funct_descript="Update a Notion page's properties by ID.",
    param_descript={
        "page_id": "The ID of the page to update",
        "properties": "Dictionary of new property values"
    }
)
def update_page(page_id: str, properties: dict) -> dict:
    """
    Update an existing page's properties.
    """
    return notion.pages.update(
        page_id=page_id,
        properties=properties
    )


@openai_function_wrapper(
    funct_descript="Archive (delete) a Notion page by ID, which effectively removes it.",
    param_descript={
        "page_id": "The ID of the page to archive"
    }
)
def archive_page(page_id: str) -> dict:
    """
    Archive (soft-delete) a page in Notion.
    """
    return notion.pages.update(
        page_id=page_id,
        archived=True
    )


# --------------------------------------------------------------------
# 3) Blocks
# --------------------------------------------------------------------

@openai_function_wrapper(
    funct_descript="Append child blocks to a given Notion block (often a page).",
    param_descript={
        "block_id": "ID of the page or block to which children will be appended",
        "children": "List of block objects to append"
    }
)
def append_blocks(block_id: str, children: List[dict]) -> dict:
    """
    Append child blocks to a parent block (commonly a page).
    """
    return notion.blocks.children.append(
        block_id=block_id,
        children=children
    )

@openai_function_wrapper(
    funct_descript="Retrieve the children of a block (for example, to read a page's content).",
    param_descript={
        "block_id": "ID of the parent block or page",
        "start_cursor": "(Optional) Pagination cursor",
        "page_size": "(Optional) Max number of results to fetch"
    }
)
def retrieve_block_children(block_id: str, start_cursor: Optional[str] = None, page_size: Optional[int] = None) -> dict:
    """
    Retrieve child blocks of a given Notion block or page.
    """
    kwargs = {}
    if start_cursor:
        kwargs["start_cursor"] = start_cursor
    if page_size:
        kwargs["page_size"] = page_size
    return notion.blocks.children.list(block_id=block_id, **kwargs)

@openai_function_wrapper(
    funct_descript="Update a Notion block by ID (for example, to update a paragraph's text).",
    param_descript={
        "block_id": "ID of the block to update",
        "block_content": "A dictionary describing the block update payload"
    }
)
def update_block(block_id: str, block_content: dict) -> dict:
    """
    Update an existing block's content or type.
    'block_content' must follow the structure required by the Notion API.
    """
    return notion.blocks.update(block_id=block_id, **block_content)

@openai_function_wrapper(
    funct_descript="Delete a block entirely by ID.",
    param_descript={
        "block_id": "ID of the block to delete"
    }
)
def delete_block(block_id: str) -> dict:
    """
    Permanently delete a block from Notion.
    """
    return notion.blocks.delete(block_id=block_id)


# --------------------------------------------------------------------
# 4) Search
# --------------------------------------------------------------------

@openai_function_wrapper(
    funct_descript="Search across all pages and databases in the workspace, optionally filtering by object type or condition.",
    param_descript={
        "query": "The search query string",
        "filter": "Optional filter dict with keys like { 'value': 'page', 'property': 'object' }"
    }
)
def search_notion(query: str, filter: Optional[dict] = None) -> dict:
    """
    Search across the entire Notion workspace.
    The filter might look like: { 'value': 'page', 'property': 'object' }
    for limiting results to pages only.
    """
    params = {"query": query}
    if filter:
        params["filter"] = filter
    return notion.search(**params)
