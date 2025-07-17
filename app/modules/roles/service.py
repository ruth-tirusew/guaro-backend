from typing import Dict, Any

from app.adapters.role.interface import IRoleRepository

class RoleService:
    def __init__(self, role_repository: IRoleRepository):
        self.repository = role_repository
