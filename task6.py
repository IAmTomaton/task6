import poplib, email, email.contentmanager
import argparse
import base64
from email.header import decode_header
import quopri
import re


server = "pop.mail.ru"
port = "995"
login = ""
password = ""


class Head:

	def __init__(self, index, frm, to, date, subject):
		self.index = index
		self.frm = frm
		self.to = to
		self.date = date
		self.subject = subject

	def __str__(self):
		return "Index: %s\nFrom: %s\nTo: %s\nDate: %s\nSubject: %s\n" % (self.index, self.frm, self.to, self.date, self.subject)


def decode(text):
	s = ''
	for j in text.split('\n'):
		d = decode_header(j)
		for g in d:
			if g[1]:
				s += g[0].decode(g[1])
			elif type(g[0]) == bytes:
				s += g[0].decode()
			else:
				s += g[0]
	return s


def arg_parser():
	parser = argparse.ArgumentParser(allow_abbrev=True)
	parser.add_argument('-l', '--last', type=int, default=0, help='Сколько заголовков последних писем загрузить для ознакомления')
	parser.add_argument('-i', '--index', type=int, default=-1, help='Индекс загружаемого письма')
	parser.add_argument('-t', '--top', type=int, default=0, help='Сколько первых строк текста письма загрузить')
	parser.add_argument('-e', '--header', action='store_true', help='Загрузить заголовок письма')
	parser.add_argument('-f', '--file', type=str, action='append', help='Указать какие файлы из письма нужно скачать')
	parser.add_argument('-o', '--outfile', type=str, default='', help='Файл в который будуть сохранятся заголовок и текст письма')
	parser.add_argument('-p', '--pathattached', type=str, default='', help='Дерриктория в которую будут сохранены прикреплённые файлы')
	parser.add_argument('-a', '--attached', action='store_true', help='Показать список прикреплённых к письму файлов')

	return parser


def get_head(index, message):
	# Получение данных из заголовков
	subject = decode(message['Subject']) if message['Subject'] else ''
	fr = decode(message['From']) if message['From'] else ''
	to = decode(message['To']) if message['To'] else ''

	return Head(index, fr, to, message['Date'], subject)


def lines_to_meggsge(lines):
	msg = ''
	for l in lines:
		msg += l.decode('utf-8') + '\n'
	# Превращение текста в класс Message
	message = email.message_from_string(msg)
	return message


def get_message_by_index(box, index, length=-1):
	# Получение письма с указанным индексом и указанным количеством строк
	lines = []
	if length == -1:
		# Получение всего письма
		resp, lines, octets = box.retr(index)
	else:
		# Получение первых строк письма
		resp, lines, octets = box.top(index, length)
	msg = lines_to_meggsge(lines)
	return msg


def get_heders(box, count):
	# Получение списка индексов писем
	response, lst, octets = box.list()

	last_indexes = []
	i = 1
	while i < count + 1 and i < len(lst) + 1:
		last_indexes.append(int(lst[-1 * i].split()[0]))
		i += 1

	headers = []
	for i in last_indexes:
		head = get_head(i, get_message_by_index(box, i, 0))
		headers.append(head)

	return headers


def enter():
	# Авторизация на сервере
	box = poplib.POP3_SSL(server, port)
	box.user(login)
	box.pass_(password)
	return box


def get_text_plain(msg):
	# Поиск текстовой части письма
	for i in msg.walk():
		if i.get_content_type() == 'text/plain':
			return i


def get_text(msg):
	text = get_text_plain(msg)
	if not text:
		return ''
	# Получение контента из части письма
	return text.get_payload()


def get_names_attached(msg):
	files = []
	for i in msg.walk():
		if i.get_filename():
			files.append((i.get_filename(), i.get_payload()))
	return files


def write_file(text, path):
	with open(path, 'wb') as file:
		file.write(base64.b64decode(text.encode()))


def write_msg(args, text):
	if not args.outfile:
		for i in text:
			print(i)
	else:
		with open(args.outfile, 'w') as file:
			for i in text:
				file.write(str(i) + '\n')


def parse_config(path):
	with open(path, encoding='utf-8') as file:
		for line in file.readlines():
			command = line.split(' ')
			command[-1] = command[-1][0:-1]
			if len(command) == 2: two_command(command)
		
def two_command(command):
	global login
	global password
	if command[0] == 'from':
		login = command[1]
	elif command[0] == 'password':
		password = command[1]
	else:
		raise Exception('Unknown command: ' + command[0])


def main():
	parse_config('config.cnf')
	parser = arg_parser()
	args = parser.parse_args()
	box = enter()
	if args.last > 0:
		headers = get_heders(box, args.last)
		write_msg(args, headers)
	elif args.index > 0:
		msg = get_message_by_index(box, args.index, args.top + 20)
		data = []

		if args.header:
			head = get_head(args.index, msg)
			data.append(head)

		text = get_text(msg).split('\n')[:args.top]
		new_text = ''
		for l in text:
			new_text += l + '\n'
		data.append(new_text)

		if args.attached or args.file:
			all_msg = get_message_by_index(box, args.index)
			files = get_names_attached(all_msg)

		if args.attached:
			attached = 'Attached: '
			for f in files:
				attached += f[0] + ' '
			data.append(attached)

		write_msg(args, data)

		if args.file:
			for file in files:
				write_file(file[1], args.pathattached + file[0])

	box.quit()


if __name__ == '__main__':
	main()
