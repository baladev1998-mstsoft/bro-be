from app.services.base import BaseService
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate

class PolicyService(BaseService[Policy, PolicyCreate, PolicyUpdate]):
    pass

policy_service = PolicyService(Policy)
