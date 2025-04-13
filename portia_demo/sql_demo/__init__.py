"""
SQL Demo - A collection of SQL tools and demos for Portia integration.

This package provides SQL database examples and tools for working with
Portia AI agents.

Components:
- sql_server_demo: Basic SQLite database with customer data
- portia_direct: Direct integration with GPT-4o for SQL analysis
"""

from .sql_server_demo import (
    create_table,
    insert_sample_data,
    query_customers,
    display_customers,
    execute_sql_query,
)

from .portia_direct import query_llm

__all__ = [
    "create_table",
    "insert_sample_data",
    "query_customers",
    "display_customers",
    "execute_sql_query",
    "query_llm",
]
