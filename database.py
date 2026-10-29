
import os
import psycopg2


def get_connection():
    """Create a PostgreSQL connection using environment settings."""

    try:
        # Streamlit Cloud secrets, if available
        try:
            import streamlit as st
            config = st.secrets.get("postgres", {})
        except Exception:
            config = {}

        # Environment variables take priority
        host = os.getenv("PGHOST") or config.get("host")
        port = os.getenv("PGPORT") or config.get("port", "5432")
        database = os.getenv("PGDATABASE") or config.get("database")
        user = os.getenv("PGUSER") or config.get("user")
        password = os.getenv("PGPASSWORD") or config.get("password")

        if not all([host, database, user, password]):
            raise ValueError(
                "Database credentials are not configured."
            )

        return psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
            connect_timeout=10,
            sslmode="require"
        )

    except Exception as error:
        print(f"Database connection error: {error}")
        return None
