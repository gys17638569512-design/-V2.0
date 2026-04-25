from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ApiException
from app.models import Contact, User, UserRole
from app.repositories.contact_repository import ContactRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.common import PagePayload
from app.schemas.contact import (
    ContactCreateRequest,
    ContactDeletePayload,
    ContactPayload,
    ContactUpdateRequest,
)


class ContactService:
    def __init__(
        self,
        session: Session,
        repository: ContactRepository | None = None,
        customer_repository: CustomerRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or ContactRepository()
        self.customer_repository = customer_repository or CustomerRepository()

    def list_page(
        self,
        *,
        customer_id: int,
        current_user: User,
        page: int,
        page_size: int,
    ) -> PagePayload[ContactPayload]:
        self._get_customer_or_404(customer_id=customer_id, current_user=current_user)

        items, total = self.repository.list_page(
            self.session,
            customer_id=customer_id,
            page=page,
            page_size=page_size,
        )
        return PagePayload(
            items=[self._to_payload(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create(
        self,
        *,
        customer_id: int,
        payload: ContactCreateRequest,
        current_user: User,
    ) -> ContactPayload:
        self._get_customer_or_404(customer_id=customer_id, current_user=current_user)

        contact = Contact(
            customer_id=customer_id,
            name=payload.name,
            mobile=payload.mobile,
            phone=payload.phone,
            position=payload.position,
            is_primary=payload.is_primary,
            remark=payload.remark,
            is_active=True,
        )
        try:
            created = self.repository.create(self.session, contact=contact)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc

        return self._to_payload(created)

    def update(
        self,
        *,
        contact_id: int,
        payload: ContactUpdateRequest,
        current_user: User,
    ) -> ContactPayload:
        contact = self._get_contact_or_404(contact_id=contact_id, current_user=current_user)

        contact.name = payload.name
        contact.mobile = payload.mobile
        contact.phone = payload.phone
        contact.position = payload.position
        contact.is_primary = payload.is_primary
        contact.remark = payload.remark

        try:
            updated = self.repository.update(self.session, contact=contact)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc

        return self._to_payload(updated)

    def delete(self, *, contact_id: int, current_user: User) -> ContactDeletePayload:
        contact = self._get_contact_or_404(contact_id=contact_id, current_user=current_user)
        self.repository.delete(self.session, contact=contact)
        return ContactDeletePayload(deleted=True)

    def _resolve_customer_scope(self, current_user: User) -> int | None:
        if current_user.role in {UserRole.SUPER_ADMIN, UserRole.ADMIN}:
            return None
        if current_user.role == UserRole.MANAGER:
            return current_user.id
        raise ApiException(403, "无权限")

    def _get_customer_or_404(self, *, customer_id: int, current_user: User) -> object:
        manager_scope = self._resolve_customer_scope(current_user)
        customer = self.customer_repository.get_by_id(
            self.session,
            customer_id,
            manager_id=manager_scope,
        )
        if customer is None:
            raise ApiException(404, "客户不存在")
        return customer

    def _get_contact_or_404(self, *, contact_id: int, current_user: User) -> Contact:
        manager_scope = self._resolve_customer_scope(current_user)
        contact = self.repository.get_by_id(
            self.session,
            contact_id,
            manager_id=manager_scope,
        )
        if contact is None:
            raise ApiException(404, "联系人不存在")
        return contact

    def _translate_integrity_error(self, exc: IntegrityError) -> ApiException:
        message = str(exc.orig)
        if "contacts.customer_id, contacts.mobile" in message or "ix_contacts_customer_id_mobile" in message:
            return ApiException(400, "同一客户下手机号不允许重复")
        if "contacts.active_primary_customer_id" in message or "uq_contacts_active_primary_customer_id" in message:
            return ApiException(400, "同一客户最多只能有一个主联系人")
        raise ApiException(400, "联系人数据冲突")

    def _to_payload(self, contact: Contact) -> ContactPayload:
        return ContactPayload(
            id=contact.id,
            customer_id=contact.customer_id,
            name=contact.name,
            mobile=contact.mobile,
            phone=contact.phone,
            position=contact.position,
            is_primary=contact.is_primary,
            remark=contact.remark,
        )
