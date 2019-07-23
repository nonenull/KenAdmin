# coding=utf-8
import json
import pickle
from django import template
from django.db import models
from django.db.models import TextField, IntegerField, DateTimeField, DateField, BooleanField, AutoField, ForeignKey, ManyToOneRel, ManyToManyRel, \
    ManyToManyField, Q
from django.template import loader
from django.template.defaultfilters import safe
from django.urls import reverse
from django_mysql.models import JSONField, SetCharField, ListCharField

from apps.Platform.config import Filter as HelpTextFilter, Form as HelpTextForm

from utils.convUtil import conv, StorageUnit
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

register = template.Library()


@register.filter
def toFilterForm(queryset, argsStr=None):
    if not argsStr:
        argsStr = '{}'

    argsDict = json.loads(argsStr)
    filterForm = FilterForm(queryset, **argsDict)
    logger.debug('filterForm======== %s', filterForm)
    html = loader.render_to_string('platform/filter.html', {
        'filters': filterForm.filters,
    }, using=None)
    return safe(html)


class FilterForm(object):
    """
    通过 遍历检测 queryset的_meta.fields中的字段, 如果含有help_text['filter']的, 则 生成 filter form item
    """

    def __init__(self, queryset, **kwargs):
        self.model = queryset.model
        self.filters = self.getFilterData()

    def getFilterData(self):
        tmp = {}
        for field in self.model._meta.fields:
            helpText = field.help_text or {}
            filterKey = HelpTextFilter.__name__
            if filterKey not in helpText:
                continue
            filterInfo = helpText.get(filterKey)
            if filterInfo:
                filterInfo = pickle.loads(filterInfo)
            else:
                filterInfo = HelpTextFilter()

            # logger.debug("filterInfo====", filterInfo)
            name = filterInfo.name = field.name
            filterInfo.cname = field.verbose_name
            choices = field.choices
            if choices:
                filterInfo.choices = choices
            # 当模型字段配置了choices参数, 则直接使用
            # 如果字段是个外键, 则拉取外键的数据当 choices
            else:
                # 当配置的筛选字段是一个外键
                if isinstance(field, ForeignKey):
                    datas = []
                    logger.debug("\n\n\nself.model=====%s\n\n\n", self.model)
                    dataList = self.model.objects.exclude(**{
                        name: None
                    }).values_list(name, flat=True)
                    dataList = set(dataList)
                    foreignKeyModel = field.related_model
                    foreignDatas = foreignKeyModel.objects.filter(**{
                        'id__in': dataList
                    })
                    for data in foreignDatas:
                        # logger.debug("foreignKey: %s %s", data, name)
                        try:
                            datas.append((data.id, data))
                        except field.related_model.DoesNotExist as e:
                            logger.error("filter 功能拉取关联信息发生错误: %s", e)
                            data.delete()
                    filterInfo.choices = datas
                else:
                    filterInfo.options = self.getFilterSelectVal(filterInfo)
            # logger.debug('filterInfoDict====', filterInfoDict)
            tmp[field.name] = filterInfo
        # logger.debug("tmp=======", tmp)
        return tmp

    def getFilterSelectVal(self, filterInfo):
        """
        获取 字段 作为 options 的值列表
        如果指定了换算单位, 则执行换算, 返回换算完的列表
        :param filterInfoDict:
        :return:
        """

        def isValidVal(i):
            return not (i == '' or i == ' ')

        name = filterInfo.name
        dataList = self.model.objects.exclude(
            Q(**{name: None})
        ).values_list(name, flat=True)
        datas = sorted(set(dataList))
        datas = filter(isValidVal, datas)

        # 如果存在单位 需要换算的话
        if filterInfo.toUnit:
            tmp = []
            for data in datas:
                tmp.append(
                    conv(data, filterInfo.unit, filterInfo.toUnit, StorageUnit)
                )
            datas = tmp
        return datas


@register.filter
def toForm(queryset, argsStr=''):
    """
    此处参数是使用json字符串传入, 需要显式转为字典
    :param queryset:
    :param argsStr:
                action: 手动指定 form action
                filling: 表单是否填充数据
                batch:  是否批量编辑表单
    :return:
    """
    if not argsStr:
        argsStr = '{}'

    argsDict = json.loads(argsStr)
    if 'batch' in argsDict.keys():
        form = BatchForm(queryset, **argsDict)
    else:
        form = Form(queryset, **argsDict)
    return safe(form.render())


class BaseForm(object):
    formKey = HelpTextForm.__name__

    def __init__(self, queryset, **kwargs):
        self.queryset = queryset
        # 存储所有字段的验证器
        self.validators = {}
        # action  等同于 form action
        self.action = self.getAction(kwargs.get('action'))
        # 强行 手动指定 字段
        self.fields = kwargs.get('fields')
        # filling 用来标识是否需要填充数据到表单中, 可作用于区分 新建表单和编辑表单
        self.filling = self.getFilling(kwargs.get('filling'))
        self.batch = self.getFilling(kwargs.get('batch'))
        self.forms = self.cleanFormItem(queryset, self.filling)

    def getFilling(self, booleanStr):
        return booleanStr == 'True'

    def getBatch(self, booleanStr):
        return booleanStr == 'True'

    def getAction(self, urlName):
        return urlName and reverse(urlName) or ''

    def _getHelpText(self, field):
        originalHelpText = field.help_text
        helpText = isinstance(originalHelpText, dict) and originalHelpText or {}
        return helpText

    @staticmethod
    def _getFormInfo(helpText):
        helpText = isinstance(helpText, dict) and helpText or {}
        formInfo = helpText.get(HelpTextForm.__name__)
        if formInfo:
            formInfo = pickle.loads(formInfo)
        else:
            formInfo = HelpTextForm()

        return helpText, formInfo

    def ___handleFieldForManyToOneRel(self, field: ManyToOneRel):
        relatedField = field.field
        originalHelpText = relatedField.help_text
        helpText, formInfo = Form._getFormInfo(originalHelpText)
        if not formInfo.related:
            return
        choices = []
        relatedName = field.get_accessor_name()
        if self.filling:
            relatedData = getattr(self.queryset, relatedName).all()
            logger.debug("relatedData======= %s ", relatedData)
            for i in relatedData:
                choices.append((i.id, i))
        formInfo.formType = 'multiReleted'
        formInfo.choices = choices
        formInfo.name = relatedName
        formInfo.cname = field.related_model.__cname__
        formInfo.label = str(field.related_model._meta.label).lower()
        return formInfo

    def _handleField(self, field):
        name = field.name
        logger.debug("开始转换字段: {}".format(name))

        # 用来判断, 强行手动指定字段列表的情况
        if self.fields and name not in self.fields:
            return

        # 如果是 多对一的 反查外键
        if isinstance(field, ManyToOneRel) and not self.filling:
            formInfo = self.___handleFieldForManyToOneRel(field)
            if not formInfo:
                return
            return formInfo

        if isinstance(field, (ManyToOneRel, ManyToManyRel, ManyToManyField)):
            return

        # 此处 利用了Field 类的 help_text 属性, 原有的help_text类型为str
        # 需要加入表单的字段, 需要添加 help_text['form'] key
        # 将它改成dict, 用来标识 form 信息
        helpText, formInfo = self._getFormInfo(field.help_text)
        if not (self.formKey in helpText) and not (isinstance(field, AutoField) and self.filling):
            logger.debug("忽略掉的字段: {}".format(name))
            return

        formInfo.name = name
        formInfo.cname = field.verbose_name
        # 判断下值的类型, 如果是None, 改为空字符串
        try:
            value = getattr(self.queryset, field.name)
        except field.related_model.DoesNotExist as e:
            value = ''

        if value is not None:
            formInfo.value = value
        else:
            formInfo.value = ''

        # 默认值
        formInfo.defaultValue = field.has_default() and field.default or ''

        formType = formInfo.formType
        logger.debug("原始 formType == {}".format(formType))
        if not formType:
            formInfo.formType = self.__getType(field, formInfo)

        logger.debug("配置后的 form type======= {}".format(formInfo.formType))

        proxy = formInfo.proxy
        if isinstance(field, ForeignKey):
            name = field.attname
            formInfo.name = name
            if formInfo.related:
                return

            formInfo.formType = 'select'
            foreignKeyChoices = []
            for i in field.related_model.objects.all().order_by('-id'):
                foreignKeyChoices.append([i.id, i])
            formInfo.choices = foreignKeyChoices

        elif proxy:
            # 如果字段设置了代理字段, 则需要覆盖上新的数据
            if isinstance(proxy, models.base.ModelBase):
                # 指定的是模型
                formInfo.formType = 'select'
                proxyChoices = []
                for i in proxy.objects.all():
                    proxyChoices.append([i.id, i])
                formInfo.choices = proxyChoices
            else:
                # 指定的是字段名
                formInfo.value = getattr(self.queryset, proxy)
        else:
            formInfo.choices = field.choices

        # 如果字段是JSON list类型, 且没有指定placeholder属性
        if isinstance(field, JSONField) and formInfo.jsonType == 'list':
            formInfo.value = ';'.join(formInfo.value)
            if not formInfo.placeholder:
                formInfo.placeholder = '多个请用 ; 隔开'
        elif isinstance(field, (SetCharField, ListCharField)):
            formInfo.value = ';'.join(formInfo.value)
            formInfo.placeholder = '多个请用 ; 隔开, 不能重复'

        required = formInfo.required
        if not required:
            formInfo.required = not (getattr(field, 'null') or getattr(field, 'blank'))

        # 添加js验证器
        verifyList = formInfo.verify
        if isinstance(verifyList, str):
            formInfo.verify = [verifyList]

        # 验证器
        validators = self._getValidators(field)
        if validators:
            formInfo.validators = validators
            # 存储所有字段的验证器, 此处用于自动生成 js 验证器代码
            self.validators.update(validators)

        return formInfo

    def cleanFormItem(self, queryset, filling):
        """
        将表单数据清洗一遍, 生成完整的信息
        :return:
        """
        tmp = []

        for field in queryset._meta.get_fields():
            formInfo = self._handleField(field)
            if formInfo:
                logger.debug('formInfo=========%s', formInfo)
                tmp.append(formInfo)
        return tmp

    @staticmethod
    def _getValidators(item):
        """
        获取字段的所有验证器, 生成dict格式返回
        :param item: models Field字段对象
        :return:
        """
        validatorDict = {}
        # 判断验证器 个数
        validators = item.validators
        # logger.debug('validators==', item.name, validators)
        if len(validators):
            for validator in validators:
                # logger.debug('validator==', validator)
                regex = getattr(validator, 'regex', False)
                # logger.debug('validator regex==', regex)
                if regex:
                    message = getattr(validator, 'message')
                    name = validator.__class__.__name__
                    validatorDict[name] = [regex.pattern, str(message)]
                    # validatorDict[name] = ['/{}/'.format(regex.pattern), str(message)]

        return validatorDict

    def __getType(self, item, formInfo):
        """
        如果 Platform.config.Form 类实例指定了formType属性, 则直接返回该属性的值
        否则根据模型字段类型来区分类型, 默认为input
        :param item: 模型字段
        :param formInfo:  Platform.config.Form 类实例
        :return: 表单字段类型
        """
        itemType = type(item)
        logger.debug("{} itemType 字段类型 == {}".format(item.name, itemType))
        if item.choices:
            # 多选
            if formInfo.multipleChoice:
                logger.debug("formInfo.multipleChoice====%s", formInfo.__dict__)
                return 'multipleChoice'
            # 单选
            if formInfo.switchChoice:
                return 'switch'
            return 'select'

        if itemType == AutoField:
            return 'id'
        if itemType == TextField:
            return 'textarea'
        if itemType == IntegerField:
            return 'number'
        if itemType in [DateField, DateTimeField]:
            return 'date'
        if itemType == BooleanField:
            return 'switch'
        return 'input'


#
class Form(BaseForm):
    """
    自动生成 新增 和 编辑 表单
    """
    formHtml = """
        <form class="layui-form" action="{action}" method="post" lay-filter="auto-form">{formItem}</form>
    """
    formBtn = """
        <div class="layui-form-item">
            <div class="layui-input-block">
                <button class="layui-btn" lay-submit lay-filter="{filter}">立即提交</button>
                <button type="reset" class="layui-btn layui-btn-primary">重置</button>
            </div>
        </div>
    """
    jsHTML = """
    <script>
        layui.use(['form'], function(){
            let $ = layui.jquery;
            let form = layui.form;
            let validators = %s;
            let verifys = {};
            
            $.each(validators, function(k, v){
                verifys[k] = function(value, item){
                    if(!value) return false;
                    if(!new RegExp(v[0]).test(value)){   
                        return v[1];
                    }
                        
                };
                //regx = v[0];
                //validators[k][0] = eval(regx);
            });
            form.verify(verifys);            
        })
    </script>
    """

    def __init__(self, queryset, **kwargs):
        super().__init__(queryset, **kwargs)

    def render(self):
        itemHTML = ''
        logger.debug("self.forms=== {}".format(self.forms))
        for item in self.forms:
            itemType = item.formType
            logger.debug("item type === %s", itemType)
            if not itemType:
                logger.warning("itemType ========= %s %s", item.__dict__, itemType)
                continue
            # 此处根据表单字段类型, 自动生成调用的函数名, 并调用, 聚合结果
            itemHTML += getattr(self, 'render{}'.format(itemType[0].upper() + itemType[1:]))(item)
        # logger.debug('itemHTML======', itemHTML)
        return self.formHtml.format(
            action=self.action,
            formItem=itemHTML + self.formBtn.format(
                filter=self.filling and 'update' or 'add',
            ),
        ) + self.jsHTML % self.validators

    def renderId(self, item):
        return """<input type="hidden" name="{name}" value="{value}">""".format(
            name=item.name,
            value=item.value,
        )

    def renderPassword(self, item):
        html = """
            <div class="layui-form-item layui-form-password">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-inline">
                    <input type="password" name="{name}" {disabled} {verify} autocomplete placeholder="{placeholder}" value="{filling}" class="layui-input">
                </div>
                <div class="layui-form-mid layui-word-aux">
                </div>
            </div>
        """

        cname = item.cname
        return html.format(
            cname=cname,
            name=item.name,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            filling=self.getFillingValue(item),
            placeholder=item.placeholder or '请输入 {}'.format(cname)
        )

    def renderInput(self, item, inputType='text'):
        html = """
            <div class="layui-form-item">
                {input}
            </div>
        """

        normalHTML = """
            <label class="layui-form-label {required}">{cname}</label>
            <div class="layui-input-block">
                <input type="{inputType}" name="{name}" {disabled} {verify} placeholder="{placeholder}" value="{filling}" class="layui-input">
            </div>
        """

        unitHTML = """
            <label class="layui-form-label {required}">{cname}</label>
            <div class="layui-input-inline">
                <input type="{inputType}" name="{name}" {disabled} {verify} placeholder="{placeholder}" value="{filling}" class="layui-input">
                <input type="hidden" name="{name}HiddenUnit" value="{toUnit}" class="layui-input">
            </div>
            <div class="layui-form-mid layui-word-aux">{toUnit}</div>
        """
        toUnit = item.toUnit
        unit = item.unit
        cname = item.cname
        fillingVal = self.getFillingValue(item)
        logger.debug('fillingVal========== %s', fillingVal)
        contentDict = {
            'cname': cname,
            'name': item.name,
            'required': item.required and 'my-required' or '',
            'disabled': item.disabled and 'disabled' or '',
            'verify': self.getVerify(item),
            'inputType': inputType,
            'filling': fillingVal,
            'placeholder': item.placeholder or '请输入 {}'.format(cname)
        }

        if toUnit:
            contentDict.update(**{
                'toUnit': toUnit,
            })
            inputHTML = unitHTML.format(**contentDict)
        elif unit:
            contentDict.update(**{
                'toUnit': unit,
            })
            inputHTML = unitHTML.format(**contentDict)
        else:
            inputHTML = normalHTML.format(**contentDict)

        return html.format(input=inputHTML)

    def renderNumber(self, item):
        return self.renderInput(item, inputType='number')

    def renderSwitch(self, item):
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <input type="checkbox" name="{name}" lay-skin="switch" {checked} lay-text="{switchText}" value="True" dis-value="False">
                </div>
            </div>
        """

        switchList = []
        for value, title in item.choices:
            switchList.append(title)
        switchText = '|'.join(switchList)

        checked = item.value and 'checked' or ''

        return html.format(
            cname=item.cname,
            name=item.name,
            checked=checked,
            switchText=switchText,
            required=item.required and 'my-required' or '',
        )

    def renderRadio(self, item):
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    {radio}
                </div>
            </div>
        """

        radio = ''
        logger.debug("item====%s  %s", item.name, item.__dict__)
        for value, title in item.choices:
            radio += '<input type="radio" name="{name}" value="{value}" title="{title}" {checked} lay-skin="switch">'.format(
                name=item.name,
                title=title,
                value=value,
                checked=(item.value == value) and 'checked' or '',
            )

        return html.format(
            cname=item.cname,
            required=item.required and 'my-required' or '',
            radio=radio,
        )

    def renderMultipleChoice(self, item):
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label">{cname}</label>
                <div class="layui-input-block">
                    {radio}
                </div>
            </div>
        """

        def isCheck():
            checked = ''
            if self.filling:
                if value in item.value:
                    checked = 'checked'
            else:
                if value in item.defaultValue:
                    checked = 'checked'
            return checked

        radio = ''
        for value, title in item.choices:
            radio += '<input type="checkbox" name="{name}" title="{title}" value="{value}" {checked}>'.format(
                name=item.name,
                required=item.required and 'my-required' or '',
                title=title,
                value=value,
                checked=isCheck(),
            )

        return html.format(
            cname=item.cname,
            radio=radio,
        )

    def renderDate(self, item):
        return """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <input type="text" name="{name}" {disabled} {verify} value="{value}" placeholder="{placeholder}" class="layui-input my-date">
                </div>
            </div>
        """.format(
            name=item.name,
            cname=item.cname,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            value=self.getFillingValue(item),
            placeholder=item.placeholder or '点击输入日期'
        )

    def renderSelect(self, item):
        formMidHtml = '<div class="layui-form-mid layui-word-aux"><i class="foreignKey-add layui-icon layui-icon-add-1" href="{createRouteHref}"></i></div>'
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="{inputTypeCss}">
                    <select name="{name}" {disabled} {verify} lay-search>
                        {defaultOption}
                        {options}
                    </select>
                </div>
                {formMid}
            </div>
        """
        options = ''

        itemValue = item.value
        logger.debug("\n\n当前 字段: {}, 值: {}".format(item.cname, repr(item.value)))
        for value, title in item.choices:
            if isinstance(itemValue, models.Model):
                # logger.debug("选择项值为模型字段: {}, 表单项值: {}".format(itemValue.id, value))
                isEq = (itemValue.id == value)
            else:
                # logger.debug("选择项值: {} 表单项值: {}".format(itemValue, value))
                isEq = (itemValue == value)

            options += '<option value="{value}" {selected}>{title}</option>'.format(
                value=value,
                selected=isEq and 'selected' or '',
                title=title,
            )

        relatedCreateRoute = item.relatedCreateRoute

        if relatedCreateRoute:
            route = reverse(relatedCreateRoute)
        else:
            route = ''

        formMidHtml = formMidHtml.format(
            createRouteHref=route
        )

        return html.format(
            cname=item.cname,
            name=item.name,
            inputTypeCss=relatedCreateRoute and 'layui-input-inline' or 'layui-input-block',
            formMid=relatedCreateRoute and formMidHtml or '',
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            options=options,
            verify=self.getVerify(item),
            defaultOption=self.filling and "" or "<option title='请选择'></option>"
        )

    def renderMultiReleted(self, item):
        logger.warning("renderMultiReleted===========")
        relateDataLi = """
            <li>
                {data}
                <i class="layui-icon layui-icon-close-fill" href="{relateDataDeleteHref}"></i>
                <input type="hidden" name="{name}[]" value="{itemId}">
            </li>
        """
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label">{cname}</label>
                <div class="layui-input-block">
                    <div class="relate-btn">
                        <button class="layui-btn layui-btn-xs layui-btn-normal" name="{name}" delHref="{relateDataDeleteHref}" addHref="{relateBtnAddHref}"><i class="layui-icon layui-icon-add-1"></i></button>
                    </div>
                    <ul class="relate-data">{relateDatas}</ul>
                </div>
            </div>
        """
        name = item.name
        label = item.label

        delHref = reverse('platform:model.delete', args=(label,))

        def generateLiData():
            tmp = ''
            for itemId, data in item.choices:
                tmp += relateDataLi.format(data=data, name=name, itemId=itemId, relateDataDeleteHref=delHref)
            return tmp

        return html.format(
            name=name,
            cname=item.cname,
            relateBtnAddHref='{}?name={}'.format(reverse('platform:model.add', args=(label,)), name),
            relateDataDeleteHref=delHref,
            relateDatas=self.filling and generateLiData() or '',
        )

    def renderTextarea(self, item):
        html = """
            <div class="layui-form-item layui-form-text">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <textarea name="{name}" placeholder="{placeholder}" {verify} {disabled} class="layui-textarea">{filling}</textarea>
                </div>
            </div>
        """
        cname = item.cname
        return html.format(
            cname=item.cname,
            name=item.name,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            filling=self.getFillingValue(item),
            placeholder=item.placeholder or '请输入 {}'.format(cname)
        )

    def getFillingValue(self, item):
        """
        如果指定了self.filling 填充表单字段
        :param filling:
        :param item:
        :return:
        """
        value = item.value
        defaultValue = item.defaultValue
        logger.debug("getFillingValue  value====  %s ===== %s ---默认值: %s", item.name, value, defaultValue)
        if not self.filling:
            if defaultValue == dict:
                return ''
            return defaultValue
        elif self.filling and value is not None:
            unit = item.unit
            toUnit = item.toUnit
            if item.toUnit:
                return conv(value, unit, toUnit, StorageUnit)
            return value
        elif not isinstance(defaultValue, str):
            return ''

    @staticmethod
    def getVerify(item):
        """
        根据validator属性动态生成 lay-verify
        :return: 用|当分隔符, 生成所有验证器
        """
        verifyHTML = 'lay-verify="{verify}"'

        validators = getattr(item, 'validators', None)
        verify = item.verify
        required = item.required
        if not validators and not verify and not required:
            return ''

        validatorList = []
        if required:
            validatorList.append('required')

        if validators:
            validatorList += list(
                validators.keys()
            )

        if verify:
            validatorList.extend(verify)

        setValidatorList = list(set(validatorList))
        setValidatorList.sort(key=validatorList.index)
        return verifyHTML.format(
            verify="|".join(setValidatorList)
        )


class BatchForm(Form):
    """
    批量编辑表单
    """

    def __init__(self, queryset, **kwargs):
        super().__init__(queryset, **kwargs)

    def render(self):
        itemHTML = ''
        logger.debug("self.forms==={}".format(self.forms))
        for item in self.forms:
            itemType = item.formType
            if not itemType:
                logger.warning("itemType ========= ", item.__dict__, itemType)
                continue
            # 此处根据表单字段类型, 自动生成调用的函数名, 并调用
            itemHTML += getattr(self, 'render{}'.format(itemType.capitalize()))(item)
        # logger.debug('itemHTML======', itemHTML)
        return self.formHtml.format(
            action=self.action,
            formItem=itemHTML + self.formBtn.format(filter=self.filling and 'update' or 'add'),
        ) + self.jsHTML % self.validators

    def renderId(self, item):
        return ""

    def renderNumber(self, item):
        return """
            <div class="layui-form-item">
                <div class="fff">
                    <input type="checkbox"">
                </div>
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <input type="number" name="{name}" {disabled} {verify} placeholder="请输入" value="{value}" class="layui-input">
                </div>
            </div>
        """.format(
            name=item.name,
            cname=item.cname,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            value=item.value,
        )

    def renderSwitch(self, item):
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    {radio}
                </div>
            </div>
        """

        radio = ''
        for value, title in item.choices:
            radio += '<input type="radio" name="{name}" value="{value}" title="{title}" {checked} lay-skin="switch">'.format(
                name=item.name,
                required=item.required and 'my-required' or '',
                title=title,
                value=value,
                checked=(item.value == value) and 'checked' or '',
            )

        return html.format(
            cname=item.cname,
            radio=radio,
        )

    def renderDate(self, item):
        return """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <input type="text" name="{name}" {disabled} {verify} value="{value}" placeholder="{placeholder}" class="layui-input my-date">
                </div>
            </div>
        """.format(
            name=item.name,
            cname=item.cname,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            value=self.getFillingValue(item),
            placeholder=item.placeholder or '点击输入日期'
        )

    def renderSelect(self, item):
        formMidHtml = '<div class="layui-form-mid layui-word-aux"><i class="foreignKey-add layui-icon layui-icon-add-1" href="{createRouteHref}"></i></div>'
        html = """
            <div class="layui-form-item">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="{inputTypeCss}">
                    <select name="{name}" {disabled} {verify} lay-search>
                        {defaultOption}
                        {options}
                    </select>
                </div>
                {formMid}
            </div>
        """
        options = ''

        itemValue = item.value
        logger.debug("\n\n当前 字段: {}, 值: {}".format(item.cname, repr(item.value)))
        for value, title in item.choices:
            if isinstance(itemValue, models.Model):
                logger.debug("选择项值为模型字段: {}, 表单项值: {}".format(itemValue.id, value))
                isEq = (itemValue.id == value)
            else:
                logger.debug("选择项值: {} 表单项值: {}".format(itemValue, value))
                isEq = (itemValue == value)

            options += '<option value="{value}" {selected}>{title}</option>'.format(
                value=value,
                selected=isEq and 'selected' or '',
                title=title,
            )

        relatedCreateRoute = item.relatedCreateRoute

        if relatedCreateRoute:
            route = reverse(relatedCreateRoute)
        else:
            route = ''

        formMidHtml = formMidHtml.format(
            createRouteHref=route
        )

        return html.format(
            cname=item.cname,
            name=item.name,
            inputTypeCss=relatedCreateRoute and 'layui-input-inline' or 'layui-input-block',
            formMid=relatedCreateRoute and formMidHtml or '',
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            options=options,
            verify=self.getVerify(item),
            defaultOption=self.filling and "" or "<option title='请选择'></option>"
        )

    def renderPassword(self, item):
        html = """
            <div class="layui-form-item layui-form-password">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-inline">
                    <input type="password" name="{name}" {disabled} {verify} autocomplete placeholder="{placeholder}" value="{filling}" class="layui-input">
                </div>
                <div class="layui-form-mid layui-word-aux">
                </div>
            </div>
        """

        cname = item.cname
        return html.format(
            cname=cname,
            name=item.name,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            filling=self.getFillingValue(item),
            placeholder=item.placeholder or '请输入 {}'.format(cname)
        )

    def renderInput(self, item, inputType='text'):
        html = """
            <div class="layui-form-item">
                {input}
            </div>
        """

        normalHTML = """
            <label class="layui-form-label {required}">{cname}</label>
            <div class="layui-input-block">
                <input type="text" name="{name}" {disabled} {verify} placeholder="请输入 {cname}" value="{filling}" class="layui-input">
            </div>
        """

        unitHTML = """
            <label class="layui-form-label {required}">{cname}</label>
            <div class="layui-input-inline">
                <input type="text" name="{name}" {disabled} {verify} placeholder="请输入 {cname}" value="{filling}" class="layui-input">
            </div>
            <div class="layui-form-mid layui-word-aux">{unit}</div>
        """
        unit = item.unit
        value = item.value

        contentDict = {
            'cname': item.cname,
            'name': item.name,
            'required': item.required and 'my-required' or '',
            'disabled': item.disabled and 'disabled' or '',
            'verify': self.getVerify(item),
            'unit': unit,
            'filling': self.getFillingValue(item),
        }

        if unit:
            inputHTML = unitHTML.format(**contentDict)
        else:
            inputHTML = normalHTML.format(**contentDict)

        return html.format(input=inputHTML)

    def renderTextarea(self, item):
        html = """
            <div class="layui-form-item layui-form-text">
                <label class="layui-form-label {required}">{cname}</label>
                <div class="layui-input-block">
                    <textarea name="{name}" placeholder="{placeholder}" {verify} {disabled} class="layui-textarea">{filling}</textarea>
                </div>
            </div>
        """
        cname = item.cname
        return html.format(
            cname=item.cname,
            name=item.name,
            required=item.required and 'my-required' or '',
            disabled=item.disabled and 'disabled' or '',
            verify=self.getVerify(item),
            filling=self.getFillingValue(item),
            placeholder=item.placeholder or '请输入 {}'.format(cname)
        )


@register.filter
def generateValidatorJS(queryset, fieldName):
    """
    获取固定字段的验证器, 返回js代码
    :param queryset:
    :param fieldName: 字段名
    :return:
    """
    jsHTML = Form.jsHTML
    fields = queryset._meta.fields
    for field in fields:
        if fieldName != field.name:
            continue
        validators = Form._getValidators(field)
        return safe(
            (jsHTML % validators).strip().strip('<script>').strip('</script>')
        )


@register.filter
def generateLayVerify(queryset, fieldName):
    form = Form(queryset, fields=[fieldName])
    return safe(form.getVerify(form.forms[0]))
