import boto3
from botocore.errorfactory import ClientError

from ..component import Component


class IAMRole(Component):

    def __init__(self, name, trust_document, **options):
        self.name = name
        self.trust_document = trust_document
        self.attach_policies = options.get('attach_policies', [])
        super().__init__(**options)
        self.iam = boto3.client('iam')

    def __str__(self):
        return f"IAM role {self.name}"

    def is_setup(self):
        try:
            self.iam.get_role(RoleName=self.name)
            return True
        except ClientError:
            return False

    def set_it_up(self):
        self.iam.create_role(RoleName=self.name, AssumeRolePolicyDocument=self.trust_document)

    def tear_it_down(self):
        for policy in self.iam.list_attached_role_policies(RoleName=self.name)['AttachedPolicies']:
                self.iam.detach_role_policy(RoleName=self.name, PolicyArn=policy['PolicyArn'])

        self.iam.delete_role(RoleName=self.name)


class RoleInlinePolicy(Component):

    def __init__(self, role_name, name, policy_document, **options):
        self.role_name = role_name
        self.name = name
        self.policy_document = policy_document
        super().__init__(**options)
        self.iam = boto3.client('iam')

    def __str__(self):
        return f"IAM role {self.role_name} inline policy {self.name}"

    def is_setup(self):
        try:
            return self.name in self.iam.list_role_policies(RoleName=self.role_name)['PolicyNames']
        except ClientError:
            return False

    def set_it_up(self):
        self.iam.put_role_policy(RoleName=self.name, PolicyName=self.name, PolicyDocument=self.policy_document)

    def tear_it_down(self):
        self.iam.delete_role_policy(RoleName=self.role_name, PolicyName=self.name)

