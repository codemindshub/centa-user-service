"""
Module: permissions

This module provides utilities for checking user permissions based on their roles.
It assumes a relationship between users, roles, and permissions where each user
is assigned one or more roles, and each role has a set of permissions.

Models used:
- `UserRole`: A model linking users to their roles.
- `RolePermission`: A model linking roles to their associated permissions.
"""

