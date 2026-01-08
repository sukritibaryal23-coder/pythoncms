from articles.models import Article
# from pages.models import Page
# from products.models import Product

RECYCLE_MODELS = {
    "article": {
        "model": Article,
        "title_field": "title",
    },
    # "page": {
    #     "model": Page,
    #     "title_field": "title",
    # },
}
