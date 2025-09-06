#!/usr/bin/env python3
"""
Simple API test script to verify comment endpoints are working
Run this script to test all comment API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8080/api"

def create_test_account():
    """Create a test account and return account data"""
    account_data = {
        "username": "testuser@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/accounts", json=account_data)
    print(f"Create Account: {response.status_code}")
    return response.json()

def get_access_token():
    """Get access token for authentication"""
    auth_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    
    response = requests.post(f"{BASE_URL}/access-tokens", json=auth_data)
    print(f"Get Token: {response.status_code}")
    return response.json()["access_token"]

def create_test_task(account_id, token):
    """Create a test task"""
    task_data = {
        "title": "Test Task for Comments",
        "description": "This task will have comments"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/accounts/{account_id}/tasks", 
                           json=task_data, headers=headers)
    print(f"Create Task: {response.status_code}")
    return response.json()

def test_comment_apis(task_id, token):
    """Test all comment API endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Comment APIs ===")
    
    # 1. Create a comment
    comment_data = {"content": "This is my first comment on this task!"}
    response = requests.post(f"{BASE_URL}/tasks/{task_id}/comments", 
                           json=comment_data, headers=headers)
    print(f"1. Create Comment: {response.status_code}")
    if response.status_code == 201:
        comment = response.json()
        comment_id = comment["id"]
        print(f"   Created comment ID: {comment_id}")
        print(f"   Comment content: {comment['content']}")
    else:
        print(f"   Error: {response.text}")
        return
    
    # 2. Get the comment
    response = requests.get(f"{BASE_URL}/tasks/{task_id}/comments/{comment_id}", 
                          headers=headers)
    print(f"2. Get Comment: {response.status_code}")
    if response.status_code == 200:
        print(f"   Retrieved content: {response.json()['content']}")
    
    # 3. Create more comments for pagination test
    for i in range(2, 4):
        comment_data = {"content": f"This is comment number {i}"}
        response = requests.post(f"{BASE_URL}/tasks/{task_id}/comments", 
                               json=comment_data, headers=headers)
        print(f"3.{i}. Create Additional Comment: {response.status_code}")
    
    # 4. Get paginated comments
    response = requests.get(f"{BASE_URL}/tasks/{task_id}/comments?page=1&size=2", 
                          headers=headers)
    print(f"4. Get Paginated Comments: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total comments: {data['total_count']}")
        print(f"   Comments on page 1: {len(data['items'])}")
    
    # 5. Update the first comment
    update_data = {"content": "This is my UPDATED first comment!"}
    response = requests.patch(f"{BASE_URL}/tasks/{task_id}/comments/{comment_id}", 
                            json=update_data, headers=headers)
    print(f"5. Update Comment: {response.status_code}")
    if response.status_code == 200:
        print(f"   Updated content: {response.json()['content']}")
    
    # 6. Delete the comment
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}/comments/{comment_id}", 
                             headers=headers)
    print(f"6. Delete Comment: {response.status_code}")
    if response.status_code == 200:
        print(f"   Deletion success: {response.json()['success']}")
    
    # 7. Try to get deleted comment (should fail)
    response = requests.get(f"{BASE_URL}/tasks/{task_id}/comments/{comment_id}", 
                          headers=headers)
    print(f"7. Get Deleted Comment: {response.status_code} (should be 404)")

def main():
    """Main test function"""
    print("🧪 Testing Comment APIs")
    print("=" * 40)
    
    try:
        # Setup
        account = create_test_account()
        token = get_access_token()
        task = create_test_task(account["id"], token)
        
        # Test comment APIs
        test_comment_apis(task["id"], token)
        
        print("\n✅ All tests completed!")
        print("Check the results above to see if APIs are working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the server.")
        print("Make sure the Flask app is running on http://localhost:8080")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
