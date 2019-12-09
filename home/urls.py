from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^logout$', views.userlogout),
    url(r'^login$', views.userLogin),

    ###### Nightly ########
    url(r'^nightly/$', views.nightly),
    # url(r'^nightly/add$', views.nightly_add),
    url(r'^nightly/status$', views.nightly_status),
    url(r'^nightly/precision$', views.nightly_pre),
    url(r'^nightly/premodify$', views.nightly_premod),
    url(r'^nightly/plot$', views.nightly_plot),
    url(r'^nightly/compare$', views.nightly_compare),
    url(r'^nightly/library$', views.nightly_library),
    #url(r'^nightly/plot/graph$', ChartView.as_view()),
    #url(r'^nightly/plot/graph$', ChartData.as_view()),
    #url(r'^nightly/plot/graph$', views.nightly_graph),
    #url(r'^nightly/plot/graph$', MorrisView.as_view()),

    ###### Infrastructure ########
    url(r'^infra/$', views.infra),
    url(r'^infra/storage$', views.infra_storage),
    url(r'^infra/status$', views.infra_status),
    url(r'^datarequest/$', views.datarequest),
    url(r'^datarequest/search$', views.datarequest_search),

    ###### Nitification ########
    url(r'^notification/$', views.notification),
    url(r'^notification/add$', views.notification_add),
    url(r'^notification/modify$', views.notification_modify),
    url(r'^notification/remove$', views.notification_remove),

    ###### Production ########
    url(r'^production/$', views.production),
    url(r'^production/chains$', views.production_chains),
    url(r'^production/disks$', views.production_disks),
    url(r'^production/picoprogress$', views.production_pico),
    url(r'^production/prediction$', views.production_pred),
]