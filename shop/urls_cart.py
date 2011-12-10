from django.conf.urls.defaults import url, patterns

from shop.views.cart import CartDetails, CartItemDetail


urlpatterns = patterns('',
    url(r'^cart/delete/$', CartDetails.as_view(action='delete'),  # DELETE
        name='cart_delete'),
    url('^cart/item/$', CartDetails.as_view(action='post'),  # POST
        name='cart_item_add'),
    url(r'^cart/$', CartDetails.as_view(), name='cart'),  # GET
    url(r'^cart/update/$', CartDetails.as_view(action='put'),
        name='cart_update'),

    # CartItems
    url('^cart/item/(?P<id>[0-9A-Za-z-_.//]+)$', CartItemDetail.as_view(),
        name='cart_item'),
    url('^cart/item/(?P<id>[0-9A-Za-z-_.//]+)/delete$',
        CartItemDetail.as_view(action='delete'),
        name='cart_item_delete'),
)
