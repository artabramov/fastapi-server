from fastapi import APIRouter

router = APIRouter()


@router.get('/category', tags=['categories'])
async def category_select():
    return {'category_name': 'category name'}
