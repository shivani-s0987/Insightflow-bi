from rest_framework.exceptions import PermissionDenied, NotFound
from apps.workspaces.models import Membership
WRITE_ROLES={'owner','administrator','analyst'}
def membership_for(user, workspace_id):
    m=Membership.objects.filter(user=user,workspace_id=workspace_id).select_related('workspace').first()
    if not m: raise NotFound('Workspace not found.')
    return m
def require_role(user, workspace_id, write=False):
    m=membership_for(user,workspace_id)
    if write and m.role not in WRITE_ROLES: raise PermissionDenied('Your workspace role does not permit this operation.')
    return m
