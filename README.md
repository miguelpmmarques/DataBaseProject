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
		no windows e linux:
			/DataBaseProject$ virtualenv env
		na shell de linux:
			/DataBaseProject$ source env/bin/activate

			( no windows command line:
				DataBaseProject> cd env/Scripts
				DataBaseProject> activate 
				DataBaseProject> cd ../..
			)

			( na powershell do windows:
				DataBaseProject> . env/Scripts/activate 
			)

3)	na shell em Windows e linux tem correr a seguinte linha de comando:
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


ADVERTÊNCIA: O pacote psycopg2 necessário à integração de postgresql no Django 
	é notório pelos seus problemas na instalação. Caso esse pacote em especial dê problemas
 	a instalar, recomendamos a sua instalação via package managers generalistas como o
	"apt" do ubuntu, ou "chocolatey" do windows (
						experimentar o seguinte:
						$ sudo apt-get update
						$ sudo apt-get install libpq-dev python-dev
						$ sudo pip install psycopg2
						)


//-------------------------------------------------------------------------------------------------------------------------

OPCIONAL, MAS MUITAS FEATUTRES ESTÃO IMPLEMENTADAS COM RECURSO A ESTAS FERRAMENTAS:


10)	abrir uma nova consola

11)	na shell novamente:
			/DataBaseProject$ source env/bin/activate (ou equivalente para o OS como explicado acima)
			cd UniLeague
			celery -A UniLeague beat


12)	abrir uma nova consola

13)	na shell novamente:
			/DataBaseProject$ source env/bin/activate (ou equivalente para o OS como explicado acima)
			cd UniLeague
			celery -A UniLeague worker --loglevel=info
		caso a connecção seja recusada é necessário abrir uma nova consola e executar o comando:
			$ redis-server
		


14) 	O mesmo que acontece com o "psycopg2" se aplica ao "Redis", embora a instalação inicial deva já conter este programa. (

						$ sudo apt install redis-server
						)
