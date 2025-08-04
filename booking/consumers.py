import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Move import here to avoid early model loading
        from django.contrib.auth.models import User
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        receiver_id = text_data_json['receiver_id']
        apartment_id = text_data_json.get('apartment_id')  # Optional

        sender = self.scope['user']
        if not sender.is_authenticated:
            return  # Handle unauthorized access

        # Save message to database
        message = await self.save_message(sender, receiver_id, message_content, apartment_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_username': sender.username,
                'timestamp': message.timestamp.isoformat(),
                'message_id': message.id,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    @sync_to_async
    def save_message(self, sender, receiver_id, content, apartment_id):
        # Move imports here
        from django.contrib.auth.models import User
        from .models import Message, Apartment
        try:
            receiver = User.objects.get(id=receiver_id)
            apartment = None
            if apartment_id:
                apartment = Apartment.objects.get(id=apartment_id)
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                apartment=apartment
            )
            return message
        except User.DoesNotExist:
            raise ValueError("Receiver does not exist")
        except Apartment.DoesNotExist:
            raise ValueError("Apartment does not exist")