from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from base.models import *
import pytz
class Chatconsumer(WebsocketConsumer):
    def connect(self):
        
        self.room_id=self.scope['url_route']['kwargs']['pk']
        
        
        async_to_sync(self.channel_layer.group_add)(self.room_id,self.channel_name)
        self.accept()
    def disconnect(self, code):
        print('disconnect')
        async_to_sync(self.channel_layer.group_discard)(self.room_id,self.channel_name)
    
    def receive(self, text_data=None, bytes_data=None):
        text_data_json=json.loads(text_data)
        print(text_data_json)
       
        message=text_data_json['data']
        sender=BetaUser.objects.get(id=text_data_json['sender'])
        receiver=BetaUser.objects.get(id=text_data_json['received'])
        chatbox=Chatbox.objects.get(id=self.room_id)
        msg=Chat.objects.create(chatbox=chatbox,sender=sender,receiver=receiver,data=message)
        msg.save()
        async_to_sync(self.channel_layer.group_send)(self.room_id,{'type':'sendback','message':message,'sender':sender.id,'receiver':receiver.id,'time':msg.created_at.strftime("%I:%M %p, %B %d")})
        
    def sendback(self,event):
        message=event['message']
        sender=event['sender']
        receiver=event['receiver']
        time=event['time']
        self.send(text_data=json.dumps({'message':message,'sender':sender,'receiver':receiver,'time':time}))