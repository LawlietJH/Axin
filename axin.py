from discord_components import Button, ButtonStyle, DiscordComponents
from keep_alive import keep_alive
#from discord.ext import commands
import requests
import asyncio
import discord
import json
import os

VERSION = 'v1.0.2'

#==================================================================================

class AxIn:
	def __init__(self):
		self.client = discord.Client()
		self.msg = ''
		self.Cmd = self.Cmd()
		self.commands = [cmd.lower() for cmd in self.Cmd.cmds]
		self.API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd'
		self.API_URL_ALL = 'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'
		self.TOKENS = {
			'SLP': {
				'usd': 0.0,
				'id': 'smooth-love-potion'
			},
			'AXS': {
				'usd': 0.0,
				'id': 'axie-infinity'
			},
			'ETH': {
				'usd': 0.0,
				'id': 'ethereum'
			}
		}

	#----------------------------------------------------------------------

	class Cmd:
		def __init__(self):
			self.prefix = '!Axin'
			with open('cmds.json', 'r') as f:
				self.cmds = json.loads(f.read())
			self.cmds['version']['help'] = self.cmds['version']['help'].format(VERSION)
			self.cmds['version']['content'] = self.cmds['version']['content'].format(VERSION)
			self.cmds['help']['content'] = self.prettyText(
				''' Description: {desc}
					
					Lista de Comandos:
					{cmds}
				'''.format(desc='', cmds=self.addCmds))

		@property
		def addCmds(self):
			out = ''
			for cmd, value in self.cmds.items():
				cmd_ = value['cmd']
				desc = value['help']
				if cmd_ == '' and desc == '':
					continue
				out += f'**`{self.prefix} {cmd_}`** ─ {desc}\n'
			return out

		def prettyText(self, text):

			while text.startswith('\n'):
				text = text[1:]
			while text.endswith('\n'):
				text = text[:-1]

			text = text.split('\n')
			out = []

			for t in text:
				while t.startswith((
						'\t',
						' ',
				)):
					t = t[1:]
				while t.startswith(':'):
					t = t[1:]
				out.append(t)

			return '\n'.join(out)

	#----------------------------------------------------------------------

	def sendMsg(self, msg, reply=True):
		if reply:
			return self.msg.reply(msg)
		else: 
			return self.msg.channel.send(msg)

	def getTokenPrice(self, token_name: str) -> str:
		token_id = self.TOKENS[token_name]['id']
		response = requests.get(self.API_URL.format(id=token_id))
		json_data = json.loads(response.text)
		token_price = json_data[token_id]['usd']
		self.TOKENS[token_name]['usd'] = token_price
		return f'`{token_name} = $`**`{token_price}`**'

	def getAllTokenPrice(self) -> str:
		ids = []
		for value in self.TOKENS.values():
			id = value['id']
			ids.append(id)
		token_ids = '%2C'.join(ids)
		response = requests.get(self.API_URL_ALL.format(ids=token_ids))
		json_data = json.loads(response.text)
		tokens_price = []
		for token_name, value in self.TOKENS.items():
			token_id = value['id']
			token_price = json_data[token_id]['usd']
			self.TOKENS[token_name]['usd'] = token_price
			text = f'`{token_name} = $`**`{token_price}`**'
			tokens_price.append(text)
		tokens_price = '\n'.join(tokens_price)
		return tokens_price
	
	def getAxieStats(self, num: int) -> list:
		stats = {
			'HEALTH': 0,
			'SPEED':  0,
			'SKILL':  0,
			'MORALE': 0,
		}
		return stats

	def getAxieInfo(self, num: int) -> str:
		axie_img = self.getAxieImg(num)
		axie_stats = self.getAxieStats(num)
		pages = [
			{
				'title': f'Axie #{num}',
				'desc': self.Cmd.prettyText(
					f'''
						Ξ 0.0
						$0.00
					'''
				),
				'url': f'https://marketplace.axieinfinity.com/axie/{num}/',
				'image': axie_img,
				'color': discord.Color.blue(),
				'author': {
					'name': 'Axie Infinity',
					'icon_url': 'https://cdn.axieinfinity.com/landing-page/_next/static/images/logo-f3b5c962671a2516bc9fef42ad9e9145@1x.webp',
					'url': 'https://axieinfinity.com/'
				},
				'thumbnail': '',
				'fields': [
					{
						'name': 'Stats',
						'value': f'''
							:green_heart: `{axie_stats['HEALTH']}` :zap: `{axie_stats['SPEED']}` :star: `{axie_stats['SKILL']}` :fire: `{axie_stats['MORALE']}`
						'''
					}
				],
				'footer': ''
			}
		]
		return pages

	def getAxieImg(self, num: int) -> str:
		out = f'https://storage.googleapis.com/assets.axieinfinity.com/axies/{num}/axie/axie-full-transparent.png'
		return out

	def embedPages(self, pags):

		pages = []

		for i, pag in enumerate(pags):
			pages.append(discord.Embed())
			empty = discord.Embed.Empty
			if pag.get('title'): pages[i].title = pag['title']
			if pag.get('desc'):  pages[i].description = pag['desc']
			if pag.get('url'):   pages[i].url = pag['url']
			if pag.get('image'): pages[i].set_image(url=pag['image'])
			if pag.get('color'): pages[i].color = pag['color']
			if pag.get('author'):
				if not pag['author'].__class__ == bool:
					name = pag['author'].get('name')
					url = pag['author'].get('url')
					icon_url = pag['author'].get('icon_url')
					if name in [None, '', 'default']:
						name = self.msg.author.display_name
					if icon_url in [None, '', 'default']:
						icon_url = self.msg.author.avatar_url
					if url in [None, '', 'default']:
						url = empty
					pages[i].set_author(
						name = name,
						url = url,
						icon_url = icon_url
					)
				else:
					if pag['author']:
						name = self.msg.author.display_name
						icon_url = self.msg.author.avatar_url
						url = empty
						pages[i].set_author(
							name = name,
							url = url,
							icon_url = icon_url
						)
			if pag.get('thumbnail'):
				pages[i].set_thumbnail(url=pag['thumbnail'])
			if pag.get('fields'):
				for field in pag.get('fields'):
					name = field.get('name')
					value = field.get('value')
					inline = field.get('inline')
					if name and value:
						if not inline:
							inline = False
						pages[i].add_field(
							name = name,
							value = value,
							inline = inline
						)
			if pag.get('footer'):
				pages[i].set_footer(text = pag['footer'])
		
		return pages

	async def sendMsgPags(self, pags: list, current=0, timeout=10):
		
		if current > len(pags) or len(pags) < 1: return

		UpdateMessage = 7
		
		pages = self.embedPages(pags)
		
		if len(pags) == 1:
			await self.msg.channel.send(embed=pages[0])
			return

		components = [
			[
				Button(
					label = 'Prev',
					id = 'back',
					style = ButtonStyle.blue
				),
				Button(
					label = f'Página {current+1}/{len(pages)}',
					id = 'cur',
					style = ButtonStyle.grey,
					disabled = True
				),
				Button(
					label = 'Next',
					id = 'front',
					style = ButtonStyle.blue
				)
			]
		]

		mainMsg = await self.msg.channel.send(embed=pages[current], components=components)
		
		while True:
			try:
				
				interaction = await self.client.wait_for(
					'button_click',
					check = lambda i: i.component.id in ['back', 'front'],
					timeout = timeout
				)
				
				if interaction.component.id == 'back': current -= 1
				elif interaction.component.id == 'front': current += 1
				if current == len(pages): current = 0
				elif current < 0: current = len(pages) - 1

				components[0][1].label = f'Página {current+1}/{len(pages)}'

				await interaction.respond(
					type = UpdateMessage,
					embed=pages[current],
					components = components)

			except asyncio.TimeoutError:
				components[0][0].disabled = True
				components[0][2].disabled = True
				await mainMsg.edit(embed=pages[current], components=components)
				break
			


#==================================================================================

axin = AxIn()
DiscordComponents(axin.client)

@axin.client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(axin.client))


@axin.client.event
async def on_message(msg):

	axin.msg = msg

	if axin.msg.author == axin.client.user:
		return

	content = axin.msg.content.lower()

	if content.startswith(axin.Cmd.prefix.lower()):

		command = content[6:]

		if command in axin.commands:

			if command.upper() in axin.TOKENS:
				text = axin.getTokenPrice(command.upper())
			elif command == 'tokens':
				text = axin.getAllTokenPrice()
			else:
				text = axin.Cmd.cmds[command]['content']
			
			await axin.sendMsg(text)

		else:
			if command.startswith('#'):
				try:
					num = int(command[1:].strip())
				except:
					return
				
				pages = axin.getAxieInfo(num)
				await axin.sendMsgPags(pages)

#========================================================================

keep_alive()
axin.client.run(os.environ['TOKEN'])
