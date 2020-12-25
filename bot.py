#coding=utf-8
import os
import re
import telebot
import urllib
import json
import requests
from datetime import datetime
from html_sanitizer import Sanitizer

print(os.getenv("SPACE_BOT_TOKEN"))
bot = telebot.TeleBot(os.environ["SPACE_BOT_TOKEN"])

defaultPath = "http://sisav.uem.br/sav"
rSplitMaterias = r"\s\d\d\d\d\s"
htmlTags = r"(<[^>]*>|\s{2,10}|:|Matriculado|Notas)"

class User:
	session = requests.Session()
	notas = []
	def __init__(self,t_user,username,password):
		self.t_user = t_user
		self.username = username
		self.password = password

def prettyPrint(materia):
	nome = "📚 {0}\n".format(materia[0])
	faltas = "Faltas: {0}\n".format(materia[1].strip())
	avaliacoes = ""
	for i in range(2,len(materia)-1,2):
		avaliacoes += "{0}: {1}\n".format(materia[i],materia[i+1])
	return nome+faltas+avaliacoes+"\n"

@bot.message_handler(commands=['start', 'help'])
def send_start_message(message):
	bot.reply_to(message,"Eae meu chapa, manda um /notas raxxxxxx <senha> pra acessar as notas")

@bot.message_handler(commands=['notas','nota'],content_types=['text'])
def send_notas_message(message):
	# mensagem /notas raxxxxxx <senha>
	_, username, password = message.text.split()
	currentYear = str(datetime.now().year)
	urlNota = defaultPath+'/consultaNotas/notasAno?ano='+currentYear

	sanitizer = Sanitizer()
	usuario = User(t_user=message.from_user,username=username,password=password)
	reqController = usuario.session
	# faz login
	payload = {'username': username,'password':password}
	response = reqController.post('http://sisav.uem.br/sav/auth/signIn/frmLogin',data=payload)
	
	# pega a mensagem e tokeniza
	response = reqController.get(urlNota)
	cleaned = sanitizer.sanitize(response.text)
	tokenized = re.split(rSplitMaterias,cleaned)
	# faz o parse das informacoes
	materiasComNotas = [re.sub(htmlTags,"|",element) for element in tokenized if("Notas" in element and "_tabelaNotas" not in element)]
	materiasComNotas = [materia.split("|") for materia in materiasComNotas]
	materiasComNotas = [list(filter((lambda x: not(x == '' or x==' ' or x==' Aprovado ')), i)) for i in materiasComNotas] 
	materiasComNotas = materiasComNotas[:7]
	usuario.notas = materiasComNotas
	parsedResult = ""
	for materia in materiasComNotas:
		parsedResult += prettyPrint(materia)
	bot.reply_to(message,parsedResult)
			
bot.polling()