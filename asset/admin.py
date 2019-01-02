from django.contrib import admin
from asset.models import ServerAsset, AssetLoginUser
from guardian.admin import GuardedModelAdmin


class ServerAssetAdmin(GuardedModelAdmin):
    search_fields = ('hostname', 'nodename', 'public_ip')  # 定义搜索框以哪些字段可以搜索
    list_display = ('hostname', 'private_ip', 'public_ip', 'os', 'owner', 'user')  # 每行的显示信息
    list_display_links = ('hostname', 'owner', 'user')  # 设置哪些字段可以点击进入编辑界面
    list_filter = ("hostname", 'os')


class AssetLoginUserAdmin(GuardedModelAdmin):
    search_fields = ('username', 'ctime',)
    list_display = ('username', 'ps')
    list_display_links = ('username',)
    list_filter = ('username',)


admin.site.register(ServerAsset, ServerAssetAdmin)
admin.site.register(AssetLoginUser, AssetLoginUserAdmin)
