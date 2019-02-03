import os
import requests, json

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

username=""
channels=[]

class Channel:
    def __init__(self, channel_name, creator):
        self.channel_name = channel_name
        self.creator = creator
        self.messages = {}

    def add_message(self, message, author):
        self.messages.update({author : message})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatpage", methods=["POST","GET"])
def channelhome():
    global channels_web
    if request.form.get("username"):
        global username
        username = request.form.get("username")
    return render_template("chatpage.html", username = username)

@app.route("/chatpage/<channel_name>")
def channel(channel_name):
    return render_template("channel.html", username = username, channel_name = channel_name)

@socketio.on("load channels")
def load_channels():
    global channels
    channels_web = []
    creators_web = []
    for c in channels:
        channels_web.append(c.channel_name)
        creators_web.append(c.creator)
    channels_all = {'channels_name': channels_web, 'channels_creators': creators_web}
    emit("show channels", channels_all, broadcast=True)

@socketio.on("create channel")
def create_channel(data):
    global channels
    global username
    channel_name = data["new_channel_name"]
    channel_creator = username
    channel = Channel(channel_name, channel_creator)
    channels.append(channel)
    channel_web = {'channel_name': channel_name, 'channel_creator': channel_creator}
    emit("add channel", channel_web, broadcast=True)

@socketio.on("create message")
def create_message(data2):
    global channels
    channel_name = data2["channel_name"]
    new_message = data2["new_message"]
    for c in channels:
        if c.channel_name == channel_name:
            c.add_message(new_message)
            channel = c.messages
        else:
            channel = ["error"]
    emit("display messages", channel, broadcast=True)
