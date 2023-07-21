from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from dynamicforms.action import Actions, TableAction, TablePosition
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import fields

from main.models import InternalMail
from main.rest_api_config.rest_api_config import REST_API_CONFIG
from main.rest_df.serializers.mars_serializer import MarsSerializer


class InternalMailSerializer(MarsSerializer):
    template_name = 'mail/internal_mail/mail_template.html'  # custom template for form
    template_context = dict(url_reverse=REST_API_CONFIG.InternalMail.basename)
    show_filter = True

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.fields['id'].display = DisplayMode.HIDDEN
        self.fields['message'].display_table = DisplayMode.SUPPRESS
        if 'request' in self.context and self.context[
            'request'] and self.context['request'].META.get('HTTP_X_DF_RENDER_TYPE') == 'dialog':
            self.fields['title'].display_form = DisplayMode.SUPPRESS
            self.fields['recipients'].display_form = DisplayMode.SUPPRESS
            self.fields['sender'].display_form = DisplayMode.SUPPRESS
            self.fields['created_at'].display_form = DisplayMode.SUPPRESS
        self.fields.pop('report_sent_at', None)
        self.fields.pop('parent_mail', None)
        self.fields.fields.move_to_end('report_for_internal_mail_sent_at')

    form_titles = {
        'table': 'Internal Emails',
        'edit': 'View email',
    }

    actions = Actions(
        TableAction(TablePosition.ROW_CLICK, _('Edit'), title=_('Edit record'), name='edit',
                    action_js="dynamicforms.editRow('{% url url_reverse|add:'-detail' pk='__ROWID__' "
                              "format='html' %}'.replace('__ROWID__', $(event.target).parents('tr')."
                              "attr('data-id')), 'record', __TABLEID__);"),
        TableAction(TablePosition.FILTER_ROW_END, label='', title=_('Filter'), name='filter',
                    icon='/static/main/svg/search-outline.svg',
                    btn_classes='dynamicforms-actioncontrol',
                    action_js="dynamicforms.defaultFilter(event);"),
        # this action is just for placeholder to format table
        TableAction(TablePosition.ROW_END, '', title='', name='', action_js=''),
        add_form_buttons=False,
        add_default_crud=False,
        add_default_filter=False,
    )

    report_for_internal_mail_sent_at = fields.SerializerMethodField(label=_('Report sent at'),
                                                                    display_form=DisplayMode.SUPPRESS)

    def get_report_for_internal_mail_sent_at(self, rec: InternalMail) -> str:
        if rec.pk:
            reports: QuerySet = rec.reports.all()
            reports_times: list = list(map(lambda r: r.report_sent_at, reports))
            reports_times.sort()
            return ",".join(list(map(lambda r: str(r), reports_times)))
        return ''

    class Meta:
        model = InternalMail
        exclude = ('origin_server', 'mail_content_entity_context',)
