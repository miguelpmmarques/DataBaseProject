# DataBaseProject

Requisitos:
	Python(3.6.*) e Pip
	Django (seguindo a documentação para a correta instalação)

Procedimentos:

0)	instalar o virtual environment no sistema:
		na shell:
			pip install virtualenv

1)	Abrir cmd e aceder à pasta do projeto

2)	criar um environment e entrar nele
		na shell:
			/DataBaseProject$ virtualenv env
			/DataBaseProject$ source env/bin/activate

3)	no cmd tem correr a seguinte linha de comandoo:
		(env)	...	/DataBaseProject$ pip install -r requirements.txt

5)	criar base de dados no pgadmin com nome "UniLeague"

6)	no cmd, entrar em UniLeague (cd UniLeague)

7)	correr as seguintes linhas de comandos:
		(env)	...	/DataBaseProject/UniLeague$ python manage.py makemigrations main
		(env)	...	/DataBaseProject/UniLeague$ python manage.py migrate
		(env)	...	/DataBaseProject/UniLeague$ python manage.py loaddata db.json

8)	por fim, deverá correr
		(env)	...	/DataBaseProject/UniLeague$ python manage.py runserver


9)	abrir o browser e ir ao link:
		http://127.0.0.1:8000/



10)	abrir uma nova consola

11)	na shell novamente:
			/DataBaseProject$ source env/bin/activate
			cd UniLeague
			celery -A UniLeague beat


12)	abrir uma nova consola

13)	na shell novamente:
			/DataBaseProject$ source env/bin/activate
			cd UniLeague
			celery -A UniLeague worker --loglevel=info
