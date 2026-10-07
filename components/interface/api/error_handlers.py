from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from components.domain.errors.billing.errors import InsufficientCreditsError
from components.domain.errors.generation.errors import GenerationNotFoundError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(InsufficientCreditsError)
    async def insufficient_credits(
        request: Request,
        exc: InsufficientCreditsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "detail": "Insufficient credits",
                "required": exc.required,
                "available": exc.available,
            },
        )

    @app.exception_handler(GenerationNotFoundError)
    async def generation_not_found(
        request: Request,
        exc: GenerationNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Generation not found"},
        )
