from notifications_python_client.base import BaseAPIClient


class NotificationsAPIClient(BaseAPIClient):
    def send_sms_notification(self, to, template_id, personalisation=None):
        notification = {
            "to": to,
            "template": template_id
        }
        if personalisation:
            notification.update({'personalisation': personalisation})
        return self.post(
            '/notifications/sms',
            data=notification)

    def send_email_notification(self, to, template_id, personalisation=None):
        notification = {
            "to": to,
            "template": template_id
        }
        if personalisation:
            notification.update({'personalisation': personalisation})
        return self.post(
            '/notifications/email',
            data=notification)

    def get_notification_by_id(self, id):
        return self.get('/notifications/{}'.format(id))

    def get_all_notifications(self, status=None, template_type=None):
        data = {}
        if status:
            data.update({
                'status': status
            })
        if template_type:
            data.update({
                'template_type': template_type
            })
        return self.get(
            '/notifications'.format(id),
            params=data
        )