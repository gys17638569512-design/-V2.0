from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ApiException
from app.models import Site, User, UserRole
from app.repositories.customer_repository import CustomerRepository
from app.repositories.site_repository import SiteRepository
from app.schemas.common import PagePayload
from app.schemas.site import SiteCreateRequest, SiteDeletePayload, SitePayload, SiteUpdateRequest


class SiteService:
    def __init__(
        self,
        session: Session,
        repository: SiteRepository | None = None,
        customer_repository: CustomerRepository | None = None,
    ) -> None:
        self.session = session
        self.repository = repository or SiteRepository()
        self.customer_repository = customer_repository or CustomerRepository()

    def list_page(
        self,
        *,
        customer_id: int,
        current_user: User,
        page: int,
        page_size: int,
    ) -> PagePayload[SitePayload]:
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
        payload: SiteCreateRequest,
        current_user: User,
    ) -> SitePayload:
        self._get_customer_or_404(customer_id=customer_id, current_user=current_user)

        site = Site(
            customer_id=customer_id,
            name=payload.name,
            address=payload.address,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            remark=payload.remark,
            is_active=True,
        )
        try:
            created = self.repository.create(self.session, site=site)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc

        return self._to_payload(created)

    def update(
        self,
        *,
        site_id: int,
        payload: SiteUpdateRequest,
        current_user: User,
    ) -> SitePayload:
        site = self._get_site_or_404(site_id=site_id, current_user=current_user)

        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            site.name = updates["name"]
        if "address" in updates:
            site.address = updates["address"]
        if "contact_name" in updates:
            site.contact_name = updates["contact_name"]
        if "contact_phone" in updates:
            site.contact_phone = updates["contact_phone"]
        if "remark" in updates:
            site.remark = updates["remark"]

        try:
            updated = self.repository.update(self.session, site=site)
        except IntegrityError as exc:
            raise self._translate_integrity_error(exc) from exc

        return self._to_payload(updated)

    def delete(self, *, site_id: int, current_user: User) -> SiteDeletePayload:
        site = self._get_site_or_404(site_id=site_id, current_user=current_user)
        self.repository.delete(self.session, site=site)
        return SiteDeletePayload(deleted=True)

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

    def _get_site_or_404(self, *, site_id: int, current_user: User) -> Site:
        manager_scope = self._resolve_customer_scope(current_user)
        site = self.repository.get_by_id(
            self.session,
            site_id,
            manager_id=manager_scope,
        )
        if site is None:
            raise ApiException(404, "厂区不存在")
        return site

    def _translate_integrity_error(self, exc: IntegrityError) -> ApiException:
        message = str(exc.orig)
        if "sites.customer_id, sites.active_name" in message or "uq_sites_active_customer_id_name" in message:
            return ApiException(400, "同一客户下厂区名称不允许重复")
        raise ApiException(400, "厂区数据冲突")

    def _to_payload(self, site: Site) -> SitePayload:
        return SitePayload(
            id=site.id,
            customer_id=site.customer_id,
            name=site.name,
            address=site.address,
            contact_name=site.contact_name,
            contact_phone=site.contact_phone,
            remark=site.remark,
        )
