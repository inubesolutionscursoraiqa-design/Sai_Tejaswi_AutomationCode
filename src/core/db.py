import logging
import json
import os
import subprocess

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config):
        """Initialize database connection"""
        self.config = config
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            logger.info("Database integration ready - using psql command line")
            self.conn = "ready"
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def get_latest_otp(self, email=None):
        """Get latest OTP for given email using psql command"""
        try:
            if email is None:
                email = self.config.get('forget_username', 'default_user')

            logger.info(f"Fetching OTP for email: {email}")

            # Check if psql is available (check both system PATH and pgAdmin path)
            psql_path = self._get_psql_path()
            if not psql_path:
                raise Exception("PostgreSQL client (psql) is not installed. Please install PostgreSQL client tools.")

            # Use psql command to query database
            # Build query dynamically using username from config
            username = email  # Use the passed email parameter
            logger.info(f"Querying database for username: {username}")
            query = f"SELECT otp_code FROM password_reset_requests WHERE username = '{username}' ORDER BY created_at DESC LIMIT 1;"

            cmd = [
                psql_path,
                '-h', self.config['db_host'],
                '-p', str(self.config['db_port']),
                '-d', self.config['db_name'],
                '-U', self.config['db_user'],
                '-t',  # tuples only
                '-c', query
            ]

            logger.info(f"Running psql command: {' '.join(cmd)}")
            logger.info(f"Querying OTP for username: {username}")

            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['db_password']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )

            if result.returncode == 0:
                # Clean up the output (remove whitespace)
                otp = result.stdout.strip()
                if otp:
                    logger.info(f"Retrieved OTP from database: {otp}")
                    return otp
                else:
                    logger.warning(f"No OTP found for {email}")
                    return None
            else:
                logger.error(f"psql command failed: {result.stderr}")
                raise Exception(f"Database query failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("psql command timed out")
            raise Exception("Database query timed out")
        except FileNotFoundError:
            logger.error("psql command not found - PostgreSQL client not installed")
            raise Exception("PostgreSQL client tools not installed. Please install PostgreSQL client.")
        except Exception as e:
            logger.error(f"Error getting OTP: {str(e)}")
            raise

    def get_otp_digits(self, username=None):
        """Get latest OTP and return as dictionary of individual digits for form inputs"""
        try:
            if username is None:
                username = self.config.get('forget_username', 'default_user')

            logger.info(f"Fetching OTP digits for username: {username}")

            # Get the latest OTP
            otp = self.get_latest_otp(username)

            if not otp:
                logger.warning(f"No OTP found for username: {username}")
                return None

            # Convert OTP string to dictionary of individual digits
            otp_digits = {}
            for i, digit in enumerate(otp):
                otp_digits[f"otp_digit_{i}"] = digit

            logger.info(f"OTP digits for {username}: {otp_digits}")
            return otp_digits

        except Exception as e:
            logger.error(f"Error getting OTP digits: {str(e)}")
            raise

    def _get_psql_path(self):
        """Get the path to psql executable"""
        # Try system PATH first
        try:
            result = subprocess.run(['psql', '--version'],
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                return 'psql'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Try pgAdmin path
        pgadmin_psql = r"C:\Users\sai.tejaswi\AppData\Local\Programs\pgAdmin 4\runtime\psql.exe"
        try:
            result = subprocess.run([pgadmin_psql, '--version'],
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                return pgadmin_psql
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _is_psql_available(self):
        """Check if psql command is available"""
        return self._get_psql_path() is not None

    def close(self):
        """Close database connection"""
        if self.conn:
            logger.info("Database connection closed")
