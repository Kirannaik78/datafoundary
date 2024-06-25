import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from processor.email_fetch import fetch_emails, authenticate_gmail  # Import your functions here
from models.emailModels import Email, SessionLocal

class TestEmailFetch(unittest.TestCase):

    @patch('processor.email_fetch.build')
    @patch('processor.email_fetch.Credentials')
    @patch('processor.email_fetch.os.path.exists')
    def test_authenticate_gmail(self, mock_exists, mock_credentials, mock_build):
        """Test the Gmail authentication function"""
        # Mock the os.path.exists to always return True
        mock_exists.return_value = True

        # Mock the Credentials to return a mock object
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock the build function to return a mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Call the function
        service = authenticate_gmail()

        # Assert the service is returned
        self.assertEqual(service, mock_service)

    @patch('processor.email_fetch.authenticate_gmail')
    @patch('processor.email_fetch.SessionLocal')
    def test_fetch_emails(self, mock_session_local, mock_authenticate_gmail):
        """Test the email fetching function"""
        # Mock the authenticate_gmail to return a mock service
        mock_service = MagicMock()
        mock_authenticate_gmail.return_value = mock_service

        # Mock the response of the Gmail API list and get calls
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test_id'}]
        }
        mock_service.users().messages().get().execute.return_value = {
            'id': 'test_id',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'}
                ],
                'body': {'data': 'Test Body'}
            },
            'internalDate': '1625011200000'  # Example timestamp
        }

        # Mock the database session
        mock_db_session = MagicMock()
        mock_session_local.return_value = mock_db_session

        # Call the function to test
        fetch_emails()

        # Assert that an Email object was merged into the session
        args, kwargs = mock_db_session.merge.call_args
        email = args[0]
        self.assertIsInstance(email, Email)
        self.assertEqual(email.id, 'test_id')
        self.assertEqual(email.from_email, 'test@example.com')
        self.assertEqual(email.subject, 'Test Subject')
        self.assertEqual(email.body, 'Test Body')
        self.assertEqual(email.received_datetime, datetime.fromtimestamp(1625011200000 / 1000))

        # Assert that the session was committed and closed
        mock_db_session.commit.assert_called_once()
        mock_db_session.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
