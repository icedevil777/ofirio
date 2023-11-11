from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from api_property.common.errors import NoPropertyError
from api_property.emails import ContactAgentEmail, ThanksForInterestEmail
from api_property.contact_agent_serializers import (
    ScheduleTourSerializer,
    CheckAvailabilitySerializer,
    RebateSerializer,
    AskQuestionSerializer,
    OnlyParamsRebateSerializer,
    ContactSaleLPSerializer,
    GetHelpSerializer
)
from common.sheets import add_to_google_sheets
from common.utils import notify_telegram


class CommonContactAgentView(APIView):
    serializer_class = None
    tg_fields = (
        "full_name",
        "email",
        "phone",
        "prop_class",
        "url",
    )
    additional_tg_fields = ()
    tg_label = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except NoPropertyError:
            raise NotFound

        self.data = serializer.validated_data
        self.prop_class = self.data["prop_class"]

        contact_agent = serializer.save()
        contact_agent.order_number = self.data["order_number"] = self.gen_order_num(
            self.prop_class, contact_agent
        )

        contact_agent.save()
        self.notify_tg()
        self.data.pop('user')
        ContactAgentEmail.send(self.data)
        prop = self.data.get("prop") or {}
        add_to_google_sheets.delay(self.data, prop)
        ThanksForInterestEmail.send(contact_agent=contact_agent)

        if (
                'phone' in self.data and
                request.user.is_authenticated and
                request.user.phone != self.data['phone']
        ):
            self.request.user.phone = self.data['phone']
            self.request.user.save(update_fields=('phone',))

        return Response({}, status=status.HTTP_200_OK)

    def notify_tg(self):
        tg_data = {
            k: v
            for k, v in self.data.items()
            if k in self.tg_fields + self.additional_tg_fields
        }
        notify_telegram.delay(f"#{self.tg_label}", tg_data)

    @staticmethod
    def gen_order_num(prop_class, contact_agent):
        letter = "S"
        if prop_class == "rent":
            letter = "R"

        order_num = f"{letter}{int(contact_agent.id * 223 / 19)}"
        return order_num


class ScheduleTourView(CommonContactAgentView):
    serializer_class = ScheduleTourSerializer
    additional_tg_fields = (
        "price",
        "schedule_tour_date",
        "schedule_tour_time",
        "tour_type",
    )
    tg_label = "schedule_a_tour"


class RebateView(CommonContactAgentView):
    serializer_class = RebateSerializer
    additional_tg_fields = ("price", "rebate", "best_time_to_call")
    tg_label = "rebate"


class AskQuestionView(CommonContactAgentView):
    serializer_class = AskQuestionSerializer
    additional_tg_fields = ("price", "request")
    tg_label = "ask_a_question"


class CheckAvailabilityView(CommonContactAgentView):
    serializer_class = CheckAvailabilitySerializer
    additional_tg_fields = ("price", "move_in_date")
    tg_label = "check_availability"


class OnlyParamsRebateView(CommonContactAgentView):
    serializer_class = OnlyParamsRebateSerializer
    additional_tg_fields = ("best_time_to_call",)
    tg_label = "cashback_popup"


class ContactSaleLPView(CommonContactAgentView):
    """
    Contact agent from sales landing page
    """
    serializer_class = ContactSaleLPSerializer
    additional_tg_fields = ("request",)
    tg_label = "sale_landing_page"

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if '/buyer-cashback' in url:
            self.tg_label = 'buyer_cashback_page'
        elif '/b/' in url:
            self.tg_label = 'building_page'
        return super().post(request, *args, **kwargs)


class GetHelpView(CommonContactAgentView):
    serializer_class = GetHelpSerializer
    additional_tg_fields = ("request",)
    tg_label = "faq_search"

    def post(self, request, *args, **kwargs):
        url = request.data.get('url')
        if '/earn-with-ofirio' in url:
            self.tg_label = 'earn_money_landing'
        elif '/b/' in url:
            self.tg_label = 'faq_building_page'
        return super().post(request, *args, **kwargs)
