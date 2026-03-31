import pytest
import os
import sys
from unittest.mock import patch, MagicMock, PropertyMock

# Ensure we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, limiter

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Reset rate limiters before each test
    limiter.reset()

    # Disable the teardown to prevent connection errors when mocking
    app.teardown_appcontext_funcs.clear()

    with app.test_client() as client:
        yield client

@patch('flask_mysqldb.MySQL.connection', new_callable=PropertyMock)
def test_rate_limiting_login(mock_conn_prop, client):
    """
    Test that the /login endpoint throws a 429 Too Many Requests
    after 5 attempts within a minute.
    """
    mock_conn = MagicMock()
    mock_conn_prop.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    for _ in range(5):
        response = client.post('/login', data={'username': 'test_user', 'password': 'test_password'})
        # As long as it's not 429, the request went through
        assert response.status_code != 429

    # The 6th request should be blocked
    response = client.post('/login', data={'username': 'test_user', 'password': 'test_password'})
    assert response.status_code == 429
    assert b"Too Many Requests" in response.data

@patch('flask_mysqldb.MySQL.connection', new_callable=PropertyMock)
def test_xss_sanitization_contact_form(mock_conn_prop, client):
    """
    Test that inputs to the contact form are stripped of malicious HTML tags
    before being saved to the database.
    """
    mock_conn = MagicMock()
    mock_conn_prop.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulate a logged-in user
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    malicious_payload = "<script>alert('XSS')</script>Hello"
    
    response = client.post('/contact.html', data={
        'name': malicious_payload,
        'email': 'test@example.com',
        'subject': malicious_payload,
        'message': malicious_payload
    })

    # Ensure the request was processed (should redirect back to contact upon success)
    assert response.status_code == 302
    
    # Get the arguments that were passed to cur.execute()
    assert mock_cursor.execute.called
    args, _ = mock_cursor.execute.call_args
    # The query is args[0], the tuple of parameters is args[1]
    inserted_params = args[1]
    
    # Assert that the malicious script tags were sanitized by bleach
    # bleach.clean("<script>alert('XSS')</script>Hello") results in "&lt;script&gt;alert('XSS')&lt;/script&gt;Hello"
    # The raw string '<script>' should NOT be present in the inserted data
    for param in inserted_params:
        assert "<script>" not in param

@patch('flask_mysqldb.MySQL.connection', new_callable=PropertyMock)
def test_sql_injection_resilience(mock_conn_prop, client):
    """
    Test that injecting generic SQL payloads into the login field does not cause
    a server error, because parameterized queries protect against it.
    """
    mock_conn = MagicMock()
    mock_conn_prop.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Return nothing from the DB for this user
    mock_cursor.fetchone.return_value = None
    
    sql_payload = "admin' OR '1'='1"

    response = client.post('/login', data={
        'username': sql_payload,
        'password': 'any_password'
    })
    
    # The application should handle this gracefully and redirect back to login
    # or flash an invalid credentials message, avoiding a 500 Internal Server Error
    assert response.status_code == 200
    
    # Also verify that the query was parameterized
    args, _ = mock_cursor.execute.call_args
    query_string = args[0]
    # Check that %s is used instead of string formatting
    assert "%s" in query_string
