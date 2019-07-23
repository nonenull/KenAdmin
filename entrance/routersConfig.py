# coding=utf-8
"""
Routes 所有参数说明
    rtype   # 按钮类型
    filter  # 生成按钮, 添加一个my-filter属性, 作为触发按钮js用
    icon    # 生成按钮的图标, 具体图标列表请访问 https://www.layui.com/doc/element/icon.html
    link    # 生成的按钮类型, 是纯按钮还是链接按钮
    color   # 按钮颜色, 具体请查看 class BtnColor
    display # 路由的名称
"""


class BtnColor:
    """
    作为 渲染 按钮 颜色使用
    """
    Primary = 'layui-btn-primary'
    Green = ''
    Blue = 'layui-btn-normal'
    Yellow = 'layui-btn-warm'
    Red = 'layui-btn-danger'
    Disable = 'layui-btn-disabled'


class Link:
    """
    作为 链接类型
    """
    # layer 最大化
    LayerMax = 'layerMax'
    # 用layer.panel打开
    LayerPanel = 'layerPanel'
    # 新标签页打开
    Tab = 'tab'
    # 新窗口打开
    Window = 'window'
    Default = 'default'


class Type:
    # 菜单
    menu = "menu"
    # 普通按钮
    button = "button"
    # 面板按钮, 会自动生成到pannel的右上角
    panelButton = "panelButton"
    # 普通父菜单, 生成后不带有链接
    title = "title"
    # 顶级菜单
    include = "include"
