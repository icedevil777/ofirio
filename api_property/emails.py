from common.emails import BaseEmail, EmailToAdmin


class ContactAgentEmail(EmailToAdmin):
    subject = 'Contact Agent'
    template = 'api_property/email_contact_agent.html'


class ThanksForInterestEmail(BaseEmail):
    subject = 'Ofirio - Contact Agent'
    template = 'account/email_thanks_for_interest.html'

    @classmethod
    def send(cls, contact_agent):
        context = cls.get_context()
        context['property_address'] = contact_agent.prop_address
        context['name'] = contact_agent.full_name
        context['phone'] = contact_agent.phone
        context['email'] = contact_agent.email
        return cls._send(contact_agent, context)
