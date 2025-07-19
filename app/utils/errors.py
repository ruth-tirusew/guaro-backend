from fastapi import HTTPException, status


NotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Request resource doesn't exist",
)

# ValidationError = HTTPException(
#     status_code=status.HTTP_404_NOT_FOUND,
#     detail="Request resource doesn't exist",
# )