import csv
import os
import hashlib

class UserAuth:
    def __init__(self, csv_file='users.csv'):
        self.csv_file = csv_file
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Make sure the CSV file exists with proper headers"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password_hash'])
    
    def user_exists(self, username):
        """Check if a user exists in the CSV file"""
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                if row[0] == username:
                    return True
        return False
    
    def register_user(self, username, password_hash):
        """Register a new user in the CSV file"""
        if self.user_exists(username):
            return False, "USER_EXISTS"
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password_hash])
        return True, "REGISTER_SUCCESS"
    
    def verify_user(self, username, password_hash):
        """Verify a user's credentials against the CSV file"""
        if not self.user_exists(username):
            return False, "USER_NOT_FOUND"
        
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                if row[0] == username and row[1] == password_hash:
                    return True, "LOGIN_SUCCESS"
                elif row[0] == username:
                    return False, "AUTH_FAILED"
        
        return False, "AUTH_FAILED" 