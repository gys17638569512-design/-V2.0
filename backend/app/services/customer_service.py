from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import Customer, User, UserRole
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PagePayload
from app.schemas.customer import (
    CustomerCreateRequest,
    CustomerDeletePayload,
    CustomerPayload,
    CustomerUpdateRequest,
)


class CustomerService:
    def __init__(
        self,
        session: Session,
        repository: CustomerRepository | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or CustomerRepository()
        self.user_repository = user_repository or UserRepository()

    def list_page(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
    ) -> PagePayload[CustomerPayload]:
        manager_id = self._resolve_manager_scope(current_user)
        items, total = self.repository.list_page(
            self.session,
            manager_id=manager_id,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_detail(self, *, customer_id: int, current_user: User) -> CustomerPayload:
        manager_id = self._resolve_manager_scope(current_user)
        customer = self.repository.get_by_id(
            self.session,
            customer_id,
            manager_id=manager_id,
        )
        if customer is None:
            raise ApiException(404, "客户不存在")
        return self._to_payload(customer)

    def create(self, *, payload: CustomerCreateRequest, current_user: User) -> CustomerPayload:
        customer = Customer(
            name=payload.name,
            manager_id=self._resolve_create_manager_id(
                current_user=current_user,
                requested_manager_id=payload.manager_id,
            ),
            is_active=True,
        )
        created = self.repository.create(self.session, customer=customer)
        return self._to_payload(created)

    def update(
        self,
        *,
        customer_id: int,
        payload: CustomerUpdateRequest,
        current_user: User,
    ) -> CustomerPayload:
        manager_scope = self._resolve_manager_scope(current_user)
        customer = self.repository.get_by_id(
            self.session,
            customer_id,
            manager_id=manager_scope,
        )
        if customer is None:
            raise ApiException(404, "客户不存在")

        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            customer.name = updates["name"]
        if "manager_id" in updates:
            customer.manager_id = self._resolve_update_manager_id(
                current_user=current_user,
                requested_manager_id=updates["manager_id"],
            )

        updated = self.repository.update(self.session, customer=customer)
        return self._to_payload(updated)

    def delete(self, *, customer_id: int, current_user: User) -> CustomerDeletePayload:
        manager_scope = self._resolve_manager_scope(current_user)
        customer = self.repository.get_by_id(
            self.session,
            customer_id,
            manager_id=manager_scope,
        )
        if customer is None:
            raise ApiException(404, "客户不存在")

        self.repository.delete(self.session, customer=customer)
        return CustomerDeletePayload(deleted=True)

    def _resolve_manager_scope(self, current_user: User) -> int | None:
        if current_user.role == UserRole.MANAGER:
            return current_user.id
        return None

    def _resolve_create_manager_id(
        self,
        *,
        current_user: User,
        requested_manager_id: int | None,
    ) -> int | None:
        if current_user.role != UserRole.MANAGER:
            return self._validate_manager_id(requested_manager_id)
        if requested_manager_id is None:
            return current_user.id
        if requested_manager_id != current_user.id:
            raise ApiException(403, "无权限")
        return current_user.id

    def _resolve_update_manager_id(
        self,
        *,
        current_user: User,
        requested_manager_id: int | None,
    ) -> int | None:
        if current_user.role != UserRole.MANAGER:
            return self._validate_manager_id(requested_manager_id)
        if requested_manager_id != current_user.id:
            raise ApiException(403, "无权限")
        return current_user.id

    def _validate_manager_id(self, manager_id: int | None) -> int | None:
        if manager_id is None:
            return None

        manager = self.user_repository.get_by_id(self.session, manager_id)
        if manager is None or not manager.is_active or manager.role != UserRole.MANAGER:
            raise ApiException(400, "客户负责人必须是有效的项目经理")
        return manager_id

    def _to_payload(self, customer: Customer) -> CustomerPayload:
        return CustomerPayload(
            id=customer.id,
            name=customer.name,
            manager_id=customer.manager_id,
        )
