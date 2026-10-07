from components.domain.errors.core.base import DomainError


class ProviderError(DomainError):
    pass


class ProviderTemporaryError(ProviderError):
    """Сбой, после которого запрос имеет смысл повторить."""


class ProviderPermanentError(ProviderError):
    """Провайдер отказал окончательно, повтор не поможет."""
